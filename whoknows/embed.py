"""Embedding tiers (DESIGN.md §7).

    emb = get_embedder("text")       # spaCy word vectors + SIF over the sentences
    emb = get_embedder("minilm")     # all-MiniLM-L6-v2, a sentence-embedding model
    emb = get_embedder("synthetic")  # vectors built from the sentence's facts
    vecs = emb.embed([sentence, ...])  # unit vectors, one row per sentence

The "text" tier uses spaCy `en_core_web_md` word vectors combined with SIF
weighting (Arora, Liang & Ma, 2017): a frequency-weighted average of word
vectors with the corpus' first principal component removed. The "minilm" tier
runs all-MiniLM-L6-v2 from local files (see MiniLMEmbedder). Text vectors are
cached on disk because the same sentences come back in every run.
"""

from __future__ import annotations

import hashlib
import os
import re
from functools import lru_cache

import numpy as np

from . import text as T

CACHE_DIR = os.environ.get("WHOKNOWS_CACHE", os.path.join(os.path.dirname(__file__), "..", ".cache"))


def _unit(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(n == 0, 1, n)


# --------------------------------------------------------------------------
# synthetic tier: vectors from the facts a sentence is about
# --------------------------------------------------------------------------

class SyntheticEmbedder:
    """Sum of random unit components (domain, topic, client, item, kind)
    plus phrasing noise for questions. Analogues share everything but the
    client component, so they are close but not identical."""

    name = "synthetic"

    def __init__(self, dim: int = 64, seed: int = 7, phrasing_noise: float = 0.5):
        rng = np.random.default_rng(seed)
        self.dim = dim
        self.noise = phrasing_noise

        def comps(n):
            return _unit(rng.normal(size=(n, dim)))

        n_topics = len(T.DOMAINS) * T.N_TOPICS_PER_DOMAIN
        self.D = comps(len(T.DOMAINS))
        self.Tp = comps(n_topics)
        self.C = comps(len(T.CLIENT_NAMES) + 2)    # last two: core platform, company-wide
        self.K = comps(n_topics * T.N_ASPECTS * 2)  # item aspect, separately for client and core items
        self.R = comps(1)[0]                       # "decides on ..."
        self.Q = {q: v for q, v in zip(T.QUESTION_TEMPLATES, comps(len(T.QUESTION_TEMPLATES)))}
        self.seed = seed

    def _client(self, c):
        if c is None:
            return self.C[-1]
        return self.C[-2] if c < 0 else self.C[c]

    def _one(self, s: T.Sentence) -> np.ndarray:
        v = np.zeros(self.dim)
        if s.domain >= 0:
            v += self.D[s.domain]
        if s.topic is not None:
            v += self.Tp[s.topic]
        if s.kind == "decision-role":
            v += 1.2 * self._client(s.client) + 1.0 * self.R
            return _unit(v)
        v += 0.5 * self._client(s.client)
        if s.k is not None and s.topic is not None:
            core = 1 if (s.client is not None and s.client < 0) else 0
            v += 0.8 * self.K[(s.topic * T.N_ASPECTS + s.k) * 2 + core]
        if s.kind.startswith("question:"):
            qtype = s.kind.split(":")[1]
            v = _unit(v) + 0.3 * self.Q[qtype]
            if qtype == "decision":
                v += 0.8 * self.R
            h = int(hashlib.sha1(s.text.encode()).hexdigest()[:8], 16)
            v = _unit(v) + self.noise * _unit(np.random.default_rng(h).normal(size=self.dim))
        return _unit(v)

    def embed(self, sentences: list[T.Sentence]) -> np.ndarray:
        return np.stack([self._one(s) for s in sentences])


# --------------------------------------------------------------------------
# text tier
# --------------------------------------------------------------------------

def all_sentences(n_clients: int = len(T.CLIENT_NAMES)) -> list[T.Sentence]:
    """Every sentence the simulator can ask for; the SIF statistics use this corpus."""
    out = []
    n_topics = len(T.DOMAINS) * T.N_TOPICS_PER_DOMAIN
    for t in range(n_topics):
        for c in list(range(n_clients)) + [-1]:
            out.append(T.work_sentence(t, c))
            for k in range(T.N_ASPECTS):
                out.append(T.item_sentence(t, c, k))
                for qtype in T.QUESTION_TEMPLATES:
                    for v in range(3):
                        out.append(T.question_sentence(qtype, t, c, k, v))
        for v in range(3):
            out.append(T.question_sentence("decision", t, None, 0, v))
    for c in range(n_clients):
        out.append(T.role_sentence(("lead", c)))
    for d in range(len(T.DOMAINS)):
        out.append(T.role_sentence(("owner", d)))
    out.append(T.role_sentence(("leadership",)))
    return out


class _CachedTextEmbedder:
    name = "text"

    def __init__(self):
        self._vec: dict[str, np.ndarray] = {}
        self._load_cache()

    @property
    def _cache_path(self) -> str:
        return os.path.join(CACHE_DIR, f"emb_{self.name}.npz")

    def _load_cache(self):
        if os.path.exists(self._cache_path):
            d = np.load(self._cache_path, allow_pickle=False)
            for t, v in zip(d["texts"], d["vecs"]):
                self._vec[str(t)] = v
        missing = [s.text for s in all_sentences() if s.text not in self._vec]
        if missing:
            self._compute_all()

    def _compute_all(self):
        texts = sorted({s.text for s in all_sentences()})
        vecs = self._encode(texts)
        self._vec = dict(zip(texts, vecs))
        os.makedirs(CACHE_DIR, exist_ok=True)
        np.savez_compressed(self._cache_path, texts=np.array(texts), vecs=np.stack(vecs))

    def embed(self, sentences: list[T.Sentence]) -> np.ndarray:
        return np.stack([self._vec[s.text] for s in sentences])


MINILM_DIR = os.environ.get(
    "WHOKNOWS_MINILM", os.path.join(os.path.dirname(__file__), "..", "models", "all-MiniLM-L6-v2"))


class MiniLMEmbedder(_CachedTextEmbedder):
    """all-MiniLM-L6-v2, a sentence-embedding model, run with onnxruntime.

    Needs two files in MINILM_DIR (from the model's Hugging Face page):
    `model.onnx` (the network) and `tokenizer.json` (how text becomes tokens).
    A sentence vector is the average of its token vectors, then unit length,
    exactly as sentence-transformers does it for this model.
    """

    name = "text:all-MiniLM-L6-v2"

    def _encode(self, texts):
        import onnxruntime
        from tokenizers import Tokenizer

        tokenizer = Tokenizer.from_file(os.path.join(MINILM_DIR, "tokenizer.json"))
        tokenizer.enable_padding(pad_id=0, pad_token="[PAD]")
        tokenizer.enable_truncation(max_length=256)
        session = onnxruntime.InferenceSession(os.path.join(MINILM_DIR, "model.onnx"),
                                               providers=["CPUExecutionProvider"])
        input_names = {i.name for i in session.get_inputs()}

        vectors = []
        for start in range(0, len(texts), 256):
            batch = tokenizer.encode_batch(texts[start:start + 256])
            ids = np.array([e.ids for e in batch], dtype=np.int64)
            mask = np.array([e.attention_mask for e in batch], dtype=np.int64)
            inputs = {"input_ids": ids, "attention_mask": mask}
            if "token_type_ids" in input_names:
                inputs["token_type_ids"] = np.zeros_like(ids)
            token_vectors = session.run(None, inputs)[0]          # (batch, tokens, 384)
            weights = mask[:, :, None].astype(np.float32)
            mean = (token_vectors * weights).sum(axis=1) / weights.sum(axis=1)
            vectors.extend(_unit(mean))
        return vectors


class SpacySIFEmbedder(_CachedTextEmbedder):
    name = "text:spacy-md-sif"

    def _encode(self, texts):
        import spacy
        nlp = spacy.load("en_core_web_md", exclude=["parser", "ner", "tagger", "lemmatizer",
                                                     "attribute_ruler", "senter"])
        token_lists = [[w for w in re.findall(r"[a-z]+", t.lower())] for t in texts]
        counts: dict[str, int] = {}
        for toks in token_lists:
            for w in toks:
                counts[w] = counts.get(w, 0) + 1
        total = sum(counts.values())
        a = 1e-3
        dim = nlp.vocab.vectors.shape[1]
        rows = []
        for toks in token_lists:
            v = np.zeros(dim)
            n = 0
            for w in toks:
                lex = nlp.vocab[w]
                if not lex.has_vector:
                    continue
                v += a / (a + counts[w] / total) * lex.vector
                n += 1
            rows.append(v / max(1, n))
        X = np.array(rows)
        # remove the common component every sentence shares
        u = np.linalg.svd(X - 0.0, full_matrices=False)[2][0]
        X = X - np.outer(X @ u, u)
        return list(_unit(X))


@lru_cache(maxsize=None)
def get_embedder(tier: str = "text"):
    """'text' = spaCy word vectors + SIF (every v3 result was run with it),
    'minilm' = all-MiniLM-L6-v2 (the check added after the first paper),
    'synthetic' = vectors built from the facts."""
    if tier == "synthetic":
        return SyntheticEmbedder()
    if tier == "text":
        return SpacySIFEmbedder()
    if tier == "minilm":
        return MiniLMEmbedder()
    raise ValueError(tier)

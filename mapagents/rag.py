"""Hybrid retrieval over local OSM/mobility documents and observed map features."""
from __future__ import annotations

import csv
import json
import re
import time
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


def tokens(text):
    return re.findall(r"[a-z0-9_:=.-]+", text.lower())


class KnowledgeIndex:
    def __init__(self, root: Path, cache_dir: Path, embedding_config=None):
        self.root, self.cache_dir = Path(root), Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.documents = self._documents()
        texts = [d["text"] for d in self.documents]
        if not texts: raise ValueError(f"No RAG documents found under {root}")
        self.vectorizer = TfidfVectorizer(tokenizer=tokens, token_pattern=None, sublinear_tf=True)
        self.tfidf = self.vectorizer.fit_transform(texts)
        self.term_counts = self.tfidf.copy()
        self.token_lists = [tokens(t) for t in texts]
        self.lengths = np.array([len(t) for t in self.token_lists])
        from collections import Counter
        self.counts = [Counter(t) for t in self.token_lists]
        self.df = Counter(t for c in self.counts for t in c)
        self.embedding_config = embedding_config or {}
        self.embeddings = None
        self.embedding_client = None
        if self.embedding_config.get("enabled", False): self._build_embeddings()

    def _documents(self):
        docs = []
        inventory = self.root / "inventories" / "osm_map_features.csv"
        if inventory.exists():
            with inventory.open(encoding="utf-8-sig", newline="") as f:
                for n, row in enumerate(csv.DictReader(f)):
                    text = f"OSM {row.get('key')}={row.get('value')}. Group: {row.get('feature_group')}; subgroup: {row.get('subgroup')}. Geometry: {row.get('elements')}. {row.get('comment')}"
                    docs.append({"id": f"osm:{n}", "source": str(inventory.relative_to(self.root)), "text": text})
        for path in sorted((self.root / "catalogs").glob("*.md")):
            if path.stem == "osm": continue  # already indexed at tag granularity
            text = path.read_text(encoding="utf-8-sig")
            paragraphs = re.split(r"\n\s*\n", text)
            chunk = ""; n = 0
            for p in paragraphs:
                if len(chunk) + len(p) > 2600 and chunk:
                    docs.append({"id": f"{path.stem}:{n}", "source": str(path.relative_to(self.root)), "text": chunk})
                    n += 1; chunk = ""
                while len(p) > 3000:
                    docs.append({"id": f"{path.stem}:{n}", "source": str(path.relative_to(self.root)), "text": p[:3000]})
                    n += 1; p = p[3000:]
                chunk += p + "\n\n"
            if chunk: docs.append({"id": f"{path.stem}:{n}", "source": str(path.relative_to(self.root)), "text": chunk})
        for name in ("catalog_to_tasks.md",):
            path = self.root / name
            if path.exists():
                text = path.read_text(encoding="utf-8-sig")
                for n in range(0, len(text), 2400):
                    docs.append({"id": f"tasks:{n//2400}", "source": name, "text": text[n:n+2400]})
        return docs

    def _build_embeddings(self):
        import os
        from openai import OpenAI
        cfg = self.embedding_config
        key = os.environ.get(cfg.get("api_key_env", "QWEN_API_KEY"))
        base = os.environ.get(cfg.get("base_url_env", "QWEN_BASE_URL"), cfg.get("base_url", ""))
        model = os.environ.get(cfg.get("model_env", "QWEN_EMBEDDING_MODEL"), cfg.get("model", ""))
        if not key or not base or not model: raise RuntimeError("Embedding configuration is incomplete")
        self.embedding_client = OpenAI(api_key=key, base_url=base, timeout=90, max_retries=2)
        self.embedding_model = model
        cache = self.cache_dir / "document_embeddings.npz"
        texts = [d["text"] for d in self.documents]
        if cache.exists():
            with np.load(cache, allow_pickle=False) as saved:
                if saved["model"].item() == model and saved["texts"].tolist() == texts:
                    self.embeddings = saved["vectors"].copy(); return
        vectors = []
        batch_size = int(cfg.get("batch_size", 16))
        for start in range(0, len(texts), batch_size):
            result = self.embedding_client.embeddings.create(model=model, input=texts[start:start+batch_size])
            vectors.extend(x.embedding for x in sorted(result.data, key=lambda x: x.index))
            if start % (batch_size * 10) == 0:
                print(f"RAG embeddings: {min(start+batch_size,len(texts))}/{len(texts)}", flush=True)
        self.embeddings = np.asarray(vectors, dtype=np.float32)
        self.embeddings /= np.maximum(np.linalg.norm(self.embeddings, axis=1, keepdims=True), 1e-12)
        np.savez_compressed(cache, vectors=self.embeddings, texts=np.asarray(texts), model=np.asarray(model))

    def retrieve(self, query: str, k=12):
        n = len(self.documents)
        bm25 = np.zeros(n)
        length_norm = 1.2 * (1-.75 + .75 * self.lengths / max(float(self.lengths.mean()), 1))
        for t in set(tokens(query)):
            freq = np.array([c.get(t, 0) for c in self.counts], dtype=float)
            df = self.df.get(t, 0)
            idf = np.log(1 + (n-df+.5)/(df+.5))
            bm25 += idf * freq * 2.2 / (freq + length_norm)
        cosine = (self.tfidf @ self.vectorizer.transform([query]).T).toarray().ravel()
        scores = []
        for values in (bm25, cosine):
            scores.append(np.argsort(-values, kind="stable"))
        if self.embeddings is not None:
            response = self.embedding_client.embeddings.create(model=self.embedding_model, input=[query])
            q = np.asarray(response.data[0].embedding, dtype=np.float32)
            q /= max(np.linalg.norm(q), 1e-12)
            scores.append(np.argsort(-(self.embeddings @ q), kind="stable"))
        rrf = np.zeros(n)
        for ranking in scores: rrf[ranking] += 1/(60+np.arange(n)+1)
        chosen = np.argsort(-rrf)[:k]
        return [{**self.documents[i], "retrieval_score": float(rrf[i])} for i in chosen]

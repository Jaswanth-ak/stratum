"""
Stratum — Hybrid Retrieval Engine
===================================
BM25 sparse + semantic dense retrieval with company/domain filtering.
"""

from ollama import Client
import chromadb
import pdfplumber
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from dataclasses import dataclass
from typing import Optional
import numpy as np


# ─── Config ───────────────────────────────────────────────────────────────────

COMPANIES            = ["NVIDIA", "Google", "IBM", "Oracle", "Microsoft", "Meta"]
DOMAINS              = ["financial", "technical", "hr", "strategy", "news"]
EMBED_MODEL          = "all-MiniLM-L6-v2"
CHUNK_SIZE           = 800
CHUNK_OVERLAP        = 100
TOP_K                = 6
BM25_WEIGHT          = 0.3
CONFIDENCE_THRESHOLD = 0.35
OLLAMA_MODEL = "gemma3:4b"

# ─── Data structures ──────────────────────────────────────────────────────────

@dataclass
class Chunk:
    text:     str
    company:  str
    domain:   str
    year:     int
    source:   str
    page:     int
    chunk_id: str


@dataclass
class RetrievedChunk:
    chunk: Chunk
    score: float


# ─── Ingestion ────────────────────────────────────────────────────────────────

class StratumIngester:
    """Load PDFs, chunk them, tag with metadata, store in ChromaDB."""

    def __init__(self, chroma_path: str = "./stratum_db"):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " "],
        )
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBED_MODEL
        )

    def _get_collection(self, domain: str):
        return self.client.get_or_create_collection(
            name=f"stratum_{domain}",
            embedding_function=self.embed_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def ingest_pdf(
        self,
        pdf_path: str,
        company: str,
        domain: str,
        year: int,
        source_name: str,
    ):
        assert company in COMPANIES, f"Unknown company: {company}"
        assert domain in DOMAINS,    f"Unknown domain: {domain}"

        pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                pages.append(Document(
                    page_content=text,
                    metadata={"page": i},
                ))

        collection = self._get_collection(domain)
        ids, docs, metas = [], [], []

        for page in pages:
            chunks   = self.splitter.split_text(page.page_content)
            page_num = page.metadata.get("page", 0) + 1

            for i, chunk_text in enumerate(chunks):
                if len(chunk_text.strip()) < 50:
                    continue

                chunk_id = f"{company}_{domain}_{year}_p{page_num}_c{i}"
                ids.append(chunk_id)
                docs.append(chunk_text)
                metas.append({
                    "company":  company,
                    "domain":   domain,
                    "year":     year,
                    "source":   source_name,
                    "page":     page_num,
                    "chunk_id": chunk_id,
                })

        collection.add(documents=docs, ids=ids, metadatas=metas)
        print(f"  Ingested {len(ids)} chunks from {source_name}")
        return len(ids)


# ─── Retrieval ────────────────────────────────────────────────────────────────

class StratumRetriever:
    """Hybrid BM25 + semantic retrieval with company/domain filters."""

    def __init__(self, chroma_path: str = "./stratum_db"):
        self.client   = chromadb.PersistentClient(path=chroma_path)
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBED_MODEL
        )
        self.encoder = SentenceTransformer(EMBED_MODEL)

    def _get_collection(self, domain: str):
        return self.client.get_or_create_collection(
            name=f"stratum_{domain}",
            embedding_function=self.embed_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def _build_where_filter(
        self,
        companies:  Optional[list]  = None,
        year_range: Optional[tuple] = None,
    ) -> dict:
        conditions = []

        if companies and len(companies) == 1:
            conditions.append({"company": {"$eq": companies[0]}})
        elif companies:
            conditions.append({"company": {"$in": companies}})

        if year_range:
            conditions.append({"year": {"$gte": year_range[0]}})
            conditions.append({"year": {"$lte": year_range[1]}})

        if not conditions:
            return {}
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}

    def _semantic_search(
        self,
        query:        str,
        domain:       str,
        where_filter: dict,
        n_results:    int = TOP_K * 2,
    ) -> list:
        collection = self._get_collection(domain)

        try:
            count = collection.count()
        except Exception:
            return []

        if count == 0:
            return []

        kwargs = {
            "query_texts": [query],
            "n_results":   min(n_results, count),
            "include":     ["documents", "metadatas", "distances"],
        }
        if where_filter:
            kwargs["where"] = where_filter

        results = collection.query(**kwargs)

        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunks.append({
                "text":           doc,
                "meta":           meta,
                "semantic_score": 1 - dist,
            })
        return chunks

    def _bm25_rerank(self, query: str, candidates: list) -> list:
        if not candidates:
            return []

        tokenized   = [c["text"].lower().split() for c in candidates]
        bm25        = BM25Okapi(tokenized)
        bm25_scores = bm25.get_scores(query.lower().split())
        max_score   = max(bm25_scores) if max(bm25_scores) > 0 else 1
        bm25_norm   = bm25_scores / max_score

        for i, c in enumerate(candidates):
            c["bm25_score"]   = float(bm25_norm[i])
            c["hybrid_score"] = (
                BM25_WEIGHT * c["bm25_score"]
                + (1 - BM25_WEIGHT) * c["semantic_score"]
            )

        return sorted(candidates, key=lambda x: x["hybrid_score"], reverse=True)

    def retrieve(
        self,
        query:      str,
        companies:  Optional[list]  = None,
        domains:    Optional[list]  = None,
        year_range: Optional[tuple] = None,
        top_k:      int             = TOP_K,
    ) -> tuple:
        search_domains = domains if domains else DOMAINS
        where_filter   = self._build_where_filter(companies, year_range)

        all_candidates = []
        for domain in search_domains:
            candidates = self._semantic_search(query, domain, where_filter)
            all_candidates.extend(candidates)

        if not all_candidates:
            return [], 0.0

        ranked = self._bm25_rerank(query, all_candidates)
        top    = ranked[:top_k]

        results = []
        for c in top:
            m = c["meta"]
            chunk = Chunk(
                text=c["text"],
                company=m["company"],
                domain=m["domain"],
                year=m["year"],
                source=m["source"],
                page=m["page"],
                chunk_id=m["chunk_id"],
            )
            results.append(RetrievedChunk(chunk=chunk, score=c["hybrid_score"]))

        confidence = results[0].score if results else 0.0
        return results, confidence


# ─── Generation ───────────────────────────────────────────────────────────────

class StratumGenerator:
    """Ollama-powered answer generator with source citations."""

    SYSTEM_PROMPT = """You are Stratum, an enterprise intelligence assistant.
You answer questions about major corporations using the provided source documents.

Rules:
1. Every factual claim must end with [Source: document_name, p.page_number]
2. If multiple companies are compared, use a markdown table.
3. Use the raw numbers from the documents to CALCULATE percentages yourself if needed.
4. If R&D spending and total revenue are both present, divide them to get the percentage.
5. Do not use knowledge outside the provided context.
6. Keep answers concise and structured.
7. Never say data is unavailable if the raw numbers exist — calculate it yourself."""
    def __init__(self):
        self.client = Client(host="http://localhost:11434")

    def _format_context(self, chunks: list) -> str:
        parts = []
        for i, rc in enumerate(chunks, 1):
            c = rc.chunk
            parts.append(
                f"[{i}] Source: {c.source}, p.{c.page} | "
                f"Company: {c.company} | Domain: {c.domain} | Year: {c.year}\n"
                f"{c.text}"
            )
        return "\n\n---\n\n".join(parts)

    def generate(
        self,
        query:      str,
        chunks:     list,
        confidence: float,
    ) -> dict:
        if not chunks:
            return {
                "answer":          "No relevant documents found. Try broadening your selection.",
                "citations":       [],
                "confidence_flag": True,
            }

        context         = self._format_context(chunks)
        confidence_flag = confidence < CONFIDENCE_THRESHOLD

        user_message = (
            f"Context documents:\n\n{context}\n\n"
            f"Question: {query}\n\n"
            f"Answer with citations."
            + (" Note: confidence is low — acknowledge uncertainty." if confidence_flag else "")
        )

        response = self.client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user",   "content": user_message},
            ],
        )

        answer = response.message.content

        citations = []
        seen = set()
        for rc in chunks:
            key = (rc.chunk.source, rc.chunk.page)
            if key not in seen:
                seen.add(key)
                citations.append({
                    "source":  rc.chunk.source,
                    "page":    rc.chunk.page,
                    "company": rc.chunk.company,
                    "year":    rc.chunk.year,
                    "score":   round(rc.score, 3),
                })

        return {
            "answer":          answer,
            "citations":       citations,
            "confidence":      round(confidence, 3),
            "confidence_flag": confidence_flag,
        }


# ─── Main pipeline ────────────────────────────────────────────────────────────

class Stratum:
    """Full pipeline: retrieve + generate."""

    def __init__(self, chroma_path: str = "./stratum_db"):
        self.retriever = StratumRetriever(chroma_path)
        self.generator = StratumGenerator()

    def query(
        self,
        question:   str,
        companies:  Optional[list]  = None,
        domains:    Optional[list]  = None,
        year_range: Optional[tuple] = None,
    ) -> dict:
        chunks, confidence = self.retriever.retrieve(
            query=question,
            companies=companies,
            domains=domains,
            year_range=year_range,
        )

        result = self.generator.generate(question, chunks, confidence)
        result["question"]  = question
        result["companies"] = companies or COMPANIES
        result["domains"]   = domains or DOMAINS
        return result
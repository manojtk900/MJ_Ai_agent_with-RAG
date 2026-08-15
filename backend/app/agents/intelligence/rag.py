"""
Local Zero-Cost RAG Engine for MJ AI Assistant.
Uses sentence-transformers/all-MiniLM-L6-v2 for local embeddings and cosine similarity search.
Includes source attribution, semantic chunking, and direct synthesis fallback.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import structlog

from app.agents.intelligence.schemas import RAGChunk, RAGSearchResult, SourceCitation

log = structlog.get_logger(__name__)

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
DOCS_DIR = BASE_DIR / "docs"


class LocalRAGEngine:
    """
    Singleton RAG Engine for local vector search and document ingestion.
    """
    _instance: Optional[LocalRAGEngine] = None

    def __init__(self) -> None:
        self.embedder: Optional[Any] = None
        self.chunks: List[RAGChunk] = []
        self.embeddings: Optional[np.ndarray] = None
        self._is_indexed: bool = False
        self._load_embedder()

    @classmethod
    def get_instance(cls) -> LocalRAGEngine:
        if cls._instance is None:
            cls._instance = LocalRAGEngine()
        return cls._instance

    def _load_embedder(self) -> None:
        """Initialize sentence-transformers model."""
        try:
            from sentence_transformers import SentenceTransformer
            log.info("Loading sentence-transformers/all-MiniLM-L6-v2 model for RAG...")
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
            log.info("Embedding model loaded successfully")
        except Exception as e:
            log.warning("Failed to load SentenceTransformer embedder, fallback mode active", error=str(e))
            self.embedder = None

    def _chunk_text(self, text: str, source_file: str, chunk_size: int = 500, overlap: int = 50) -> List[RAGChunk]:
        """Split text into overlapping character chunks with metadata."""
        cleaned_text = re.sub(r"\n{3,}", "\n\n", text).strip()
        if not cleaned_text:
            return []

        chunks: List[RAGChunk] = []
        start = 0
        chunk_idx = 0
        text_len = len(cleaned_text)

        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunk_content = cleaned_text[start:end].strip()

            if chunk_content:
                rel_path = source_file
                try:
                    rel_path = str(Path(source_file).relative_to(BASE_DIR)).replace("\\", "/")
                except Exception:
                    pass

                category = "project"
                if "architecture" in rel_path:
                    category = "architecture"
                elif "training" in rel_path:
                    category = "training"
                elif "academic" in rel_path:
                    category = "academic"
                elif "tools" in rel_path:
                    category = "tools"

                chunks.append(
                    RAGChunk(
                        id=f"chunk_{len(self.chunks) + len(chunks):05d}",
                        text=chunk_content,
                        source_file=rel_path,
                        chunk_index=chunk_idx,
                        category=category,
                        metadata={"char_start": start, "char_end": end},
                    )
                )
                chunk_idx += 1

            start += chunk_size - overlap
            if start >= text_len:
                break

        return chunks

    def ingest_file(self, file_path: Path) -> int:
        """Extract text from supported file and add to chunk registry."""
        if not file_path.exists() or file_path.is_dir():
            return 0

        text = ""
        suffix = file_path.suffix.lower()

        try:
            if suffix in {".md", ".txt", ".json", ".py", ".html", ".csv"}:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            elif suffix == ".pdf":
                from pypdf import PdfReader
                reader = PdfReader(str(file_path))
                text = "\n".join([page.extract_text() or "" for page in reader.pages])
            elif suffix == ".docx":
                import docx
                doc = docx.Document(str(file_path))
                text = "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            log.warning("Failed to extract text from file", file=str(file_path), error=str(e))
            return 0

        new_chunks = self._chunk_text(text, str(file_path))
        self.chunks.extend(new_chunks)
        return len(new_chunks)

    def build_index(self) -> int:
        """Scan knowledge/ and docs/ directories and compute vector embeddings."""
        self.chunks = []
        target_dirs = [KNOWLEDGE_DIR, DOCS_DIR]
        root_files = [BASE_DIR / "README.md", BASE_DIR / "ARCHITECTURE.md"]

        for rf in root_files:
            if rf.exists():
                self.ingest_file(rf)

        for d in target_dirs:
            if d.exists():
                for root, _, files in os.walk(d):
                    for file in files:
                        p = Path(root) / file
                        if not any(ign in str(p) for ign in [".git", "node_modules", "venv", "__pycache__", ".env"]):
                            self.ingest_file(p)

        if not self.chunks:
            log.warning("No knowledge chunks found to index")
            return 0

        # Compute embeddings
        if self.embedder is not None:
            try:
                texts = [c.text for c in self.chunks]
                raw_embeds = self.embedder.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
                self.embeddings = raw_embeds
                self._is_indexed = True
                log.info("RAG Index built successfully", total_chunks=len(self.chunks), shape=self.embeddings.shape)
            except Exception as e:
                log.error("Failed to compute embeddings", error=str(e))
                self._is_indexed = False
        else:
            self._is_indexed = True

        return len(self.chunks)

    def search(self, query: str, top_k: int = 3, min_similarity: float = 0.25) -> RAGSearchResult:
        """
        Search knowledge base for relevant chunks and return source citations.
        """
        if not self._is_indexed or not self.chunks:
            self.build_index()

        if not self.chunks:
            return RAGSearchResult(query=query, chunks=[], citations=[], confidence=0.0)

        # 1. Dense Semantic Vector Search
        if self.embedder is not None and self.embeddings is not None:
            try:
                q_embed = self.embedder.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
                scores = np.dot(self.embeddings, q_embed)
                top_indices = np.argsort(scores)[::-1][:top_k]

                matched_chunks: List[RAGChunk] = []
                citations: List[SourceCitation] = []
                max_score = 0.0

                for idx in top_indices:
                    score = float(scores[idx])
                    if score >= min_similarity:
                        chunk = self.chunks[idx]
                        matched_chunks.append(chunk)
                        citations.append(
                            SourceCitation(
                                source_file=chunk.source_file,
                                chunk_index=chunk.chunk_index,
                                score=round(score, 4),
                                excerpt=chunk.text[:120].strip() + "...",
                            )
                        )
                        max_score = max(max_score, score)

                return RAGSearchResult(
                    query=query,
                    chunks=matched_chunks,
                    citations=citations,
                    confidence=round(max_score, 4),
                )
            except Exception as e:
                log.error("Vector search failed, falling back to lexical search", error=str(e))

        # 2. Lexical Keyword Fallback
        q_words = set(re.findall(r"\w+", query.lower()))
        scores_lex = []
        for c in self.chunks:
            c_words = set(re.findall(r"\w+", c.text.lower()))
            overlap = len(q_words.intersection(c_words))
            score = overlap / max(1, len(q_words))
            scores_lex.append(score)

        top_indices = np.argsort(scores_lex)[::-1][:top_k]
        matched_chunks = []
        citations = []
        for idx in top_indices:
            score = float(scores_lex[idx])
            if score > 0:
                chunk = self.chunks[idx]
                matched_chunks.append(chunk)
                citations.append(
                    SourceCitation(
                        source_file=chunk.source_file,
                        chunk_index=chunk.chunk_index,
                        score=round(score, 4),
                        excerpt=chunk.text[:120].strip() + "...",
                    )
                )

        return RAGSearchResult(
            query=query,
            chunks=matched_chunks,
            citations=citations,
            confidence=round(scores_lex[top_indices[0]], 4) if len(top_indices) > 0 else 0.0,
        )

    def synthesize_answer(self, query: str, search_result: RAGSearchResult) -> str:
        """Direct deterministic synthesis from top chunks with citations."""
        if not search_result.chunks:
            return "I searched the project knowledge base, but couldn't find enough specific information on that topic."

        top_chunk = search_result.chunks[0].text
        source_links = "\n".join([f"- `{c.source_file}`" for c in search_result.citations])

        answer = (
            f"{top_chunk}\n\n"
            f"**Sources:**\n"
            f"{source_links}"
        )
        return answer


# Global Singleton instance
rag_engine = LocalRAGEngine.get_instance()

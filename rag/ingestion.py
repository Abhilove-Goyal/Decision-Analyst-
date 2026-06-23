import os
import re
import pdfplumber
import tiktoken
from pathlib import Path
from typing import List, Dict, Generator

from rag.toc_parser import extract_toc
from core.document_structure import set_toc

from core.settings import settings
from core.supabase_client import DatabaseConnectionError, DatabaseOperationError, insert_chunk, insert_ipo

from langchain_huggingface import HuggingFaceEmbeddings


# --------------------------------------------------
# Embedding model and tokenizer
# --------------------------------------------------

embed_model = HuggingFaceEmbeddings(
    model_name=settings.embedding_model
)

# Use cl100k_base tokenizer (used by most embedding models)
tokenizer = tiktoken.get_encoding("cl100k_base")


# --------------------------------------------------
# Section detection (semantic patterns)
# Works across different DRHP formats
# --------------------------------------------------

SECTION_PATTERNS = {
    "risk_factors": r"risk factors|principal risks|key risks",
    "business": r"our business|business overview|business model",
    "financials": r"financial information|financial statements|management discussion",
    "management": r"our management|board of directors|corporate governance",
    "legal": r"legal proceedings|litigation|legal matters",
    "industry": r"industry overview",
    "offer": r"details of the offer|offer structure"
}


def detect_section(text: str):

    text_lower = text.lower()

    for section, pattern in SECTION_PATTERNS.items():

        if re.search(pattern, text_lower):
            return section

    return None


# --------------------------------------------------
# Boilerplate filter
# --------------------------------------------------

def is_boilerplate(text):

    patterns = [
        r"table of contents",
        r"page\s+\d+",
        r"\.{5,}",
        r"draft red herring prospectus",
    ]

    text_lower = text.lower()

    return any(re.search(p, text_lower) for p in patterns)


# --------------------------------------------------
# Token counting utilities
# --------------------------------------------------

def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken."""
    try:
        return len(tokenizer.encode(text))
    except Exception as e:
        print(f"[TOKEN_COUNT] Error: {e}")
        # Fallback: approximate as 1 token per 4 characters
        return len(text) // 4


# --------------------------------------------------
# Semantic chunking with token-based boundaries
# --------------------------------------------------

def split_into_semantic_chunks(
    text: str,
    chunk_size: int = 400,
    overlap: int = 50
) -> List[str]:
    """
    Split text into semantic chunks with token-based sizing.
    
    Args:
        text: Text to chunk
        chunk_size: Target tokens per chunk (default 400)
        overlap: Token overlap between chunks (default 50)
    
    Returns:
        List of chunks, each approximately chunk_size tokens
    """
    chunks = []
    sentences = []
    
    # Split by sentence (more semantic than character boundaries)
    # Handle various sentence endings
    sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])(?=[A-Z])'
    parts = re.split(sentence_pattern, text)
    
    current_chunk = ""
    current_tokens = 0
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        part_tokens = count_tokens(part)
        
        # If adding this part would exceed chunk_size, save current chunk
        if current_tokens + part_tokens > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            
            # Start new chunk with overlap
            # Keep last few sentences for overlap
            overlap_sentences = []
            overlap_tokens = 0
            
            for sent in reversed(current_chunk.split('.')):
                sent = sent.strip()
                if not sent:
                    continue
                sent_tokens = count_tokens(sent)
                if overlap_tokens + sent_tokens <= overlap:
                    overlap_sentences.insert(0, sent)
                    overlap_tokens += sent_tokens
                else:
                    break
            
            current_chunk = '. '.join(overlap_sentences) + '. ' if overlap_sentences else ""
            current_tokens = overlap_tokens
        
        current_chunk += " " + part
        current_tokens += part_tokens
    
    # Add final chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return [c for c in chunks if c.strip()]  # Filter empty chunks


def split_into_chunks(text, chunk_size, overlap=200):
    """Legacy function - now uses semantic chunking."""
    return split_into_semantic_chunks(text, chunk_size, overlap)


# --------------------------------------------------
# Streaming batch embedding generation
# --------------------------------------------------

def batch_embed_documents(texts: List[str], batch_size: int = 32) -> List[List[float]]:
    """
    Generate embeddings with batching for memory efficiency.
    
    Args:
        texts: List of texts to embed
        batch_size: Number of texts per batch
    
    Returns:
        List of embedding vectors
    """
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            batch_embeddings = embed_model.embed_documents(batch)
            embeddings.extend(batch_embeddings)
            print(f"[EMBED] Batch {i//batch_size + 1}: {len(batch)} texts embedded")
        except Exception as e:
            print(f"[EMBED] Error embedding batch: {e}")
            # Use zero vectors as fallback
            embeddings.extend([[0.0] * 768 for _ in batch])
    
    return embeddings


# --------------------------------------------------
# Main ingestion pipeline (production-grade)
# --------------------------------------------------

def load_chunk_documents():
    """
    Production ingestion pipeline supporting:
    - Large PDFs (1000+ pages)
    - Semantic chunking with token counting
    - Memory-safe batch processing
    - Comprehensive metadata
    """

    docs_path: Path = settings.docs_dir

    if not docs_path.exists():
        raise RuntimeError(f"Docs path {docs_path} does not exist")

    chunks_created = 0
    total_tokens = 0

    for file in os.listdir(docs_path):

        if not file.lower().endswith(".pdf"):
            continue

        pdf_path = docs_path / file
        ipo_id = file.replace(".pdf", "").lower()
        document_name = file.replace(".pdf", "")

        print(f"\n[INGEST] ========================================")
        print(f"[INGEST] Processing PDF: {file}")
        print(f"[INGEST] IPO ID: {ipo_id}")
        print(f"[INGEST] ========================================\n")

        try:
            insert_ipo(ipo_id, str(pdf_path))
        except (DatabaseConnectionError, DatabaseOperationError):
            raise
        except Exception as e:
            raise RuntimeError(f"Could not save IPO metadata: {e}") from e

        current_section = "general"
        chunk_number = 0
        page_chunks_buffer = []  # Buffer for batch embedding
        batch_size = 32

        with pdfplumber.open(pdf_path) as pdf:

            # --------------------------------
            # Extract Table of Contents
            # --------------------------------
            # Extract Table of Contents
            # --------------------------------

            try:
                toc = extract_toc(pdf)

                if toc:
                    set_toc(ipo_id, toc)
                    print(f"[INGEST] TOC extracted: {len(toc)} sections detected")
                    for section in toc[:5]:
                        print(f"  - {section['section_name']}: pages {section['start_page']}-{section['end_page']}")
                else:
                    print(f"[INGEST] No TOC detected - using default sections")
            except Exception as e:
                print(f"[INGEST] TOC extraction error: {e}")
                toc = []

            # --------------------------------
            # Process document pages
            # --------------------------------

            total_pages = len(pdf.pages)
            print(f"[INGEST] Processing {total_pages} pages...")

            for page_idx, page in enumerate(pdf.pages):

                page_number = page.page_number

                # Progress indicator
                if (page_idx + 1) % 50 == 0:
                    print(f"[INGEST] Progress: {page_idx + 1}/{total_pages} pages processed")

                try:
                    text = page.extract_text()
                except Exception as e:
                    print(f"[INGEST] Error extracting text from page {page_number}: {e}")
                    continue

                if not text or len(text.strip()) < 20:
                    continue

                if is_boilerplate(text):
                    continue

                # Update section if detected
                detected_section = detect_section(text)
                if detected_section:
                    current_section = detected_section

                # Semantic chunking with tokens
                page_chunks = split_into_semantic_chunks(
                    text,
                    chunk_size=400,  # 400 tokens per chunk
                    overlap=50       # 50 token overlap
                )

                for chunk_text in page_chunks:

                    if not chunk_text.strip():
                        continue

                    chunk_tokens = count_tokens(chunk_text)
                    total_tokens += chunk_tokens

                    # Buffer chunk data for batch processing
                    page_chunks_buffer.append({
                        "ipo_id": ipo_id,
                        "chunk_text": chunk_text,
                        "chunk_number": chunk_number,
                        "page_number": page_number,
                        "section": current_section,
                        "document_name": document_name,
                        "chunk_tokens": chunk_tokens
                    })

                    chunk_number += 1

                    # Process buffer when it reaches batch_size
                    if len(page_chunks_buffer) >= batch_size:
                        chunks_created += _process_chunk_batch(page_chunks_buffer)
                        page_chunks_buffer = []

        # Process remaining chunks
        if page_chunks_buffer:
            chunks_created += _process_chunk_batch(page_chunks_buffer)
            page_chunks_buffer = []

        print(f"\n[INGEST] ========================================")
        print(f"[INGEST] {file} COMPLETE")
        print(f"[INGEST] Chunks created: {chunk_number}")
        print(f"[INGEST] Total tokens: {total_tokens}")
        print(f"[INGEST] ========================================\n")

    if chunks_created == 0:
        raise RuntimeError("No usable text chunks extracted from any PDF")

    print(f"\n[INGEST] ========================================")
    print(f"[INGEST] INGESTION COMPLETE")
    print(f"[INGEST] Total chunks created: {chunks_created}")
    print(f"[INGEST] Total tokens processed: {total_tokens}")
    print(f"[INGEST] ========================================\n")

    return chunks_created


# --------------------------------------------------
# Batch chunk processing helper
# --------------------------------------------------

def _process_chunk_batch(chunk_buffer: List[Dict]) -> int:
    """
    Process a batch of chunks: embed and insert into database.
    
    Args:
        chunk_buffer: List of chunk dictionaries with text and metadata
    """
    chunk_texts = [c["chunk_text"] for c in chunk_buffer]
    
    try:
        embeddings = batch_embed_documents(chunk_texts, batch_size=16)
    except Exception as e:
        print(f"[INGEST] Embedding error: {e}")
        embeddings = [[0.0] * 768 for _ in chunk_texts]
    
    inserted_count = 0

    # Insert into database
    for chunk_data, embedding in zip(chunk_buffer, embeddings):
        try:
            insert_chunk(
                ipo_id=chunk_data["ipo_id"],
                chunk_text=chunk_data["chunk_text"],
                chunk_number=chunk_data["chunk_number"],
                page_number=chunk_data["page_number"],
                section=chunk_data["section"],
                embedding=embedding,
                document_name=chunk_data["document_name"],
                chunk_tokens=chunk_data.get("chunk_tokens", 0)
            )
            inserted_count += 1
        except (DatabaseConnectionError, DatabaseOperationError):
            raise
        except Exception as e:
            raise RuntimeError(f"Database insertion error: {e}") from e

    return inserted_count

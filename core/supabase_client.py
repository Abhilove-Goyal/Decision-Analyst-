from supabase import create_client
from core.settings import settings


class DatabaseConnectionError(RuntimeError):
    """Raised when the configured Supabase endpoint cannot be reached."""


class DatabaseOperationError(RuntimeError):
    """Raised when a Supabase operation fails."""


def execute_supabase(operation: str, request):
    try:
        return request.execute()
    except Exception as e:
        message = str(e)
        if "getaddrinfo failed" in message or "Name or service not known" in message:
            raise DatabaseConnectionError(
                f"Could not resolve Supabase host while trying to {operation}. "
                "Check SUPABASE_URL in .env and your network/DNS connection."
            ) from e
        raise DatabaseOperationError(f"Supabase failed while trying to {operation}: {message}") from e


# --------------------------------------------------
# Supabase Client
# --------------------------------------------------

if not settings.supabase_url or not settings.supabase_anon_key:
    raise RuntimeError("Supabase credentials missing")

supabase = create_client(
    settings.supabase_url,
    settings.supabase_anon_key
)


# --------------------------------------------------
# Insert IPO metadata
# --------------------------------------------------

def insert_ipo(ipo_id: str, document_path: str):

    return execute_supabase("save IPO metadata", supabase.table("ipos").upsert({
        "ipo_id": ipo_id,
        "document_path": document_path
    }))


# --------------------------------------------------
# Insert chunk embeddings
# --------------------------------------------------

def insert_chunk(
    ipo_id: str,
    chunk_text: str,
    chunk_number: int,
    page_number: int,
    section: str,
    embedding: list,
    document_name: str = "unknown",
    chunk_tokens: int = 0
):

    data = {
        "ipo_id": ipo_id,
        "chunk_text": chunk_text,
        "chunk_number": chunk_number,
        "page_number": page_number,
        "section": section,
        "embedding": embedding,
        "document_name": document_name,
        "chunk_tokens": chunk_tokens
    }

    return execute_supabase("save document chunk", supabase.table("ipo_chunks").insert(data))


# --------------------------------------------------
# Vector retrieval using pgvector RPC
# --------------------------------------------------

def retrieve_chunks(query_embedding, ipo_id, limit):

    result = execute_supabase("retrieve matching chunks", supabase.rpc(
        "hybrid_match_chunks",
        {
            "query_embedding": query_embedding,
            "query_text": "",
            "ipo_filter": ipo_id,
            "match_count": limit
        }
    ))

    if not result.data:
        return []

    return result.data


# --------------------------------------------------
# Query logging
# --------------------------------------------------

def log_query(user_id, ipo_id, question, answer):

    return execute_supabase("log query", supabase.table("queries").insert({
        "user_id": user_id,
        "ipo_id": ipo_id,
        "question": question,
        "answer": answer
    }))


# --------------------------------------------------
# Admin utilities
# --------------------------------------------------

def list_ipos():
    return execute_supabase("list IPOs", supabase.table("ipos").select("*"))


def delete_ipo(ipo_id: str):

    execute_supabase("delete IPO chunks", supabase.table("ipo_chunks").delete().eq("ipo_id", ipo_id))

    return execute_supabase("delete IPO metadata", supabase.table("ipos").delete().eq("ipo_id", ipo_id))


def ipo_stats(ipo_id: str):

    return execute_supabase(
        "read IPO stats",
        supabase.table("ipo_chunks")
        .select("id", count="exact")
        .eq("ipo_id", ipo_id)
    )

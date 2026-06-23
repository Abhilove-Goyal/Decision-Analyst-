from pydantic_settings import BaseSettings 
from pathlib import Path
class Settings(BaseSettings):
    groq_api_key : str
    llm_model : str
    embedding_model : str 
    chroma_persist_dir : str
    collection_name : str
    chunk_size : int
    chunk_overlap : int
    top_k : int = 5
    vector_top_k : int = 20
    bm25_top_k : int = 20
    rerank_top_k : int = 5
    final_top_k : int = 5
    data_path : str
    log_path : str
    docs_dir: Path
    vector_dir: Path
    supabase_url : str
    supabase_anon_key : str
    
    class Config :
        env_file = ".env"
settings = Settings()
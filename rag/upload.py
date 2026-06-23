import os
from fastapi import APIRouter, UploadFile, File
from core.settings import settings
from core.supabase_client import supabase
import asyncio

# Ensure directory exists
os.makedirs(settings.data_path, exist_ok=True)

def list_all_ipos():
    response = supabase.table("ipos").select("ipo_id, ipo_name").execute()
    ipos = []
    for row in response.data:
        ipo_id = row['ipo_id']
        # Get chunk count
        count_response = supabase.table("ipo_chunks").select("*", count="exact").eq("ipo_id", ipo_id).execute()
        chunks = count_response.count
        ipos.append({"ipo_id": ipo_id, "chunks": chunks})
    return ipos

def delete_ipo_vectors(ipo_id: str):
    # Delete from ipo_chunks
    supabase.table("ipo_chunks").delete().eq("ipo_id", ipo_id).execute()
    # Also delete from ipos
    supabase.table("ipos").delete().eq("ipo_id", ipo_id).execute()
    print(f"IPO {ipo_id} vectors and metadata deleted")

def get_ipo_stats(ipo_id: str):
    response = supabase.table("ipo_chunks").select("*", count="exact").eq("ipo_id", ipo_id).execute()
    return {"total_chunks": response.count}

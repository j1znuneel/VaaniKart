import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_product_link(product_id: str) -> str:
    """
    Fetches a link for the given product_id from the Supabase table.
    """
    response = supabase.table("product_links").select("*").eq("product_id", product_id).execute()
    if response.data and len(response.data) > 0:
        return response.data[0].get("link")
    return None

import os
from supabase import create_client
from dotenv import load_dotenv

# טען את משתני הסביבה
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(url, key)

# ניסיון פשוט לקרוא טבלה לדוגמה
res = supabase.table("articles").select("*").limit(1).execute()
print(res)

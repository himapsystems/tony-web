import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def salvar_resultado(tipo, f1, f2, f0, arquivo):
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        dados = {
            "tipo_usuario": tipo,
            "f1_medio": f1,
            "f2_medio": f2,
            "f0_medio": f0,
            "nome_arquivo": arquivo
        }
        
        result = supabase.table("analises_acusticas").insert(dados).execute()
        print(f"✅ Dados salvos no Supabase com sucesso!")
        return result
    except Exception as e:
        print(f"❌ Erro ao salvar no banco: {e}")
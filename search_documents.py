import os
from typing import List, Optional
from supabase import create_client, Client
import google.generativeai as genai
from dotenv import load_dotenv

# Import indexing functions
from index_documents import index_file

# ===== Load environment variables =====
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")   # service_role key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY or not GEMINI_API_KEY:
    raise ValueError("❌ Missing environment variables. Please check your .env file.")

# ===== Settings =====
EMBEDDING_MODEL = "models/embedding-001"      # 768-dim embeddings
GENERATION_MODEL = "gemini-1.5-flash"         # Can also use "gemini-1.5-pro"

# ===== Clients =====
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)
gen_model = genai.GenerativeModel(GENERATION_MODEL)

# ===== Embeddings =====
def embed_text(text: str) -> List[float]:
    """Create an embedding vector for a given text using Gemini."""
    res = genai.embed_content(model=EMBEDDING_MODEL, content=text)
    return res["embedding"]

# ===== Vector search (via Supabase RPC) =====
def vector_search(query: str, top_k: int = 5, filename: Optional[str] = None):
    """Call the `match_documents` RPC function in Supabase to get top-k similar chunks."""
    q_emb = embed_text(query)
    payload = {
        "query_embedding": q_emb,
        "match_count": top_k,
        "filter_filename": filename
    }
    resp = supabase.rpc("match_documents", payload).execute()
    return resp.data or []

# ===== Prompt building =====
SYSTEM_INSTRUCTIONS = (
    "You are a helpful assistant. "
    "Rely strictly on the provided context. "
    "If the context is insufficient, explicitly say so."
)

def build_context(chunks: List[dict], max_chars: int = 6000) -> str:
    """Assemble the most relevant chunks into a context string."""
    out = []
    size = 0
    for r in chunks:
        piece = f"[{r.get('filename','unknown')} | score={round(r.get('similarity',0.0),3)}]\n{r['chunk_text']}\n"
        if size + len(piece) > max_chars:
            break
        out.append(piece)
        size += len(piece)
    return "\n---\n".join(out)

def answer_with_rag(query: str, chunks: List[dict]) -> str:
    """
    Generate a RAG answer using Gemini.
    Hybrid Mode: 
    1. Try to answer strictly from context.
    2. If insufficient, fallback to general knowledge (explicitly marked).
    """
    context = build_context(chunks)
    
    strict_prompt = (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{query}\n\n"
        "Answer concisely and ONLY from the provided context. "
        "If the context is insufficient, explicitly say: 'The context does not provide enough information.'"
    )
    res = gen_model.generate_content(strict_prompt)
    answer = res.text.strip()
    
    if (
        "not provide enough" in answer.lower() 
        or len(answer) < 40
    ):
        hybrid_prompt = (
            f"You are a helpful assistant. \n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{query}\n\n"
            "Step 1: Try to answer based on context.\n"
            "Step 2: If context is insufficient, add general knowledge but clearly mark it as: "
            "'[General Knowledge] ...'."
        )
        res2 = gen_model.generate_content(hybrid_prompt)
        return res2.text.strip()
    
    return answer

# ===== Public API =====
def search(query: str, top_k: int = 5, filename: Optional[str] = None) -> dict:
    """Perform a full RAG pipeline."""
    matches = vector_search(query, top_k=top_k, filename=filename)
    answer = answer_with_rag(query, matches)

    sources = []
    for m in matches:
        sources.append({
            "filename": m.get("filename", "unknown"),
            "similarity": round(m.get("similarity", 0.0), 3),
            "snippet": m.get("chunk_text", "")[:200]
        })

    return {
        "answer": answer,
        "sources": sources
    }

# ===== Interactive CLI =====
if __name__ == "__main__":
    print("📂 Document ingestion phase. Enter file paths (PDF/DOCX). Type 'done' when finished.")
    while True:
        path = input("Enter file path (or 'done' to finish): ").strip()
        if path.lower() == "done":
            break
        if not os.path.exists(path):
            print("❌ File not found, try again.")
            continue
        try:
            index_file(path)
        except Exception as e:
            print(f"❌ Error indexing {path}: {e}")

    print("\n🔍 Search phase. Ask questions. Type 'exit' to quit.")
    while True:
        q = input("Your question: ").strip()
        if q.lower() == "exit":
            print("👋 Exiting. Goodbye!")
            break
        result = search(q, top_k=5)
        print("\nAnswer:\n", result["answer"])
        print("\nSources:")
        for s in result["sources"]:
            print(f"- {s['filename']} (score: {s['similarity']}) → {s['snippet']}")
        print("\n" + "="*60 + "\n")

import os
import pdfplumber
import docx
import nltk
from nltk.tokenize import sent_tokenize
from datetime import datetime
import google.generativeai as genai
from supabase import create_client
from dotenv import load_dotenv

# ===== Load environment variables =====
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")   # service_role key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY or not GEMINI_API_KEY:
    raise ValueError("❌ Missing environment variables. Please check your .env file.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

EMBEDDING_MODEL = "models/embedding-001"

# ===== Ensure NLTK sentence tokenizer =====
nltk.download("punkt", quiet=True)

# ===== Helpers =====
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""
    doc = docx.Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

def split_into_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    return sent_tokenize(text)

def embed_text(text: str) -> list[float]:
    """Generate embeddings for a given text using Gemini."""
    result = genai.embed_content(model=EMBEDDING_MODEL, content=text)
    return result["embedding"]

def save_to_supabase(filename: str, strategy: str, sentences: list[str]):
    """Save sentences and embeddings into Supabase."""
    for sentence in sentences:
        if not sentence.strip():
            continue
        embedding = embed_text(sentence)
        supabase.table("documents").insert({
            "chunk_text": sentence,
            "embedding": embedding,
            "filename": filename,
            "split_strategy": strategy,
            "created_at": datetime.now().isoformat()
        }).execute()

def index_file(file_path: str):
    """Main function to index a file into Supabase."""
    filename = os.path.basename(file_path)
    if file_path.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Use PDF or DOCX.")

    sentences = split_into_sentences(text)
    save_to_supabase(filename, "sentence", sentences)
    print(f"✅ Indexed {len(sentences)} chunks from {filename}")

# RAG_Proccess_Jeen
RAG Demo with Supabase + Gemini

This project implements a **Retrieval-Augmented Generation (RAG)** pipeline using:

- **Supabase** (with `pgvector`) for vector storage and similarity search  
- **Google Gemini** for embeddings and text generation  
- **NLTK** for sentence-level chunking  
- **Python** utilities for PDF/DOCX parsing  

---

## Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/your-username/rag-demo.git
   cd rag-demo
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. ### Supabase Setup (required)

Before running the project, you must set up your own Supabase project:

1. Create a new project at [https://supabase.com](https://supabase.com).
2. Enable the **pgvector** extension in your project database.
3. Create a table `documents` with the following schema:
   ```sql
   - `id` (uuid, primary key, default: gen_random_uuid())
   - `chunk_text` (text)
   - `embedding` (vector(768))
   - `filename` (text)
   - `split_strategy` (text)
   - `created_at` (timestamptz)
   ```
5. Create the RPC function `match_documents` for vector similarity search:
   ```sql
   create or replace function match_documents(
     query_embedding vector(768),
     match_count int default 5,
     filter_filename text default null
   )
   returns table (
     id uuid,
     chunk_text text,
     filename text,
     similarity float
   )
   language sql stable
   as $$
     select
       id,
       chunk_text,
       filename,
       1 - (documents.embedding <=> query_embedding) as similarity
     from documents
     where filter_filename is null or filename = filter_filename
     order by documents.embedding <=> query_embedding
     limit match_count;
   $$;
   ```

   Copy your project’s SUPABASE_URL and service_role_key (from Project Settings → API).
   
   Insert these values into your .env file.
   
   
4. **Environment variables (.env):**
   A `.env` file is already included in this repository with placeholder values.  

   ⚠️ You must replace these placeholders with your own keys:  
   - `SUPABASE_URL` → your Supabase project URL  
   - `SUPABASE_KEY` → your Supabase **service_role** key (from Project Settings → API)  
   - `GEMINI_API_KEY` → your Gemini API key (from Google AI Studio)  

   Example:  
   ```env
   # Supabase settings
   SUPABASE_URL="https://<YOUR_PROJECT>.supabase.co"
   SUPABASE_KEY="<YOUR_SERVICE_ROLE_KEY>"

   # Gemini API
   GEMINI_API_KEY="<YOUR_GEMINI_API_KEY>"
   ```

6. **Download NLTK tokenizer (first run only):**
   Download NLTK tokenizer (first run only):
   The first run will automatically trigger the download of punkt.
   You can also download it manually in Python:
   ```bash
   import nltk
   nltk.download("punkt")
   ```
   
   After the first download, you can comment out this line in the code if desired (optional).

## Usage

**Step 1 – Index your documents:**
Run the script and provide PDF/DOCX files one by one.
When you are done, type done (case-insensitive) to switch to Q&A mode.

**Example:**
```bash
Enter file path (PDF/DOCX) or 'done' to finish: data/Google_PromptEngineering.pdf
✅ Indexed 125 chunks from Google_PromptEngineering.pdf
Enter file path (PDF/DOCX) or 'done' to finish: done
```

**Step 2 – Ask questions:**
Once documents are indexed, you can query them interactively:
```bash
Enter your question (or type 'exit' to quit): What are the core principles of prompt engineering?

Answer:
1. Iterative Process  
2. Model Selection  
3. Best Practices

Sources:
- Google_PromptEngineering.pdf (score: 0.862)
- Google_PromptEngineering.pdf (score: 0.857)

Type exit to quit.
```
## Example Session
```bash
Enter file path (PDF/DOCX) or 'done' to finish: data/Google_PromptEngineering.pdf
✅ Indexed 125 chunks from Google_PromptEngineering.pdf

Enter file path (PDF/DOCX) or 'done' to finish: done

Enter your question (or type 'exit' to quit): What does top-k mean?
Answer: Top-k refers to retrieving the k most similar results to a query based on cosine similarity.
Sources:
- Google_PromptEngineering.pdf (score: 0.912)

Enter your question (or type 'exit' to quit): exit
```
## Requirements
All dependencies are in **requirements.txt:**
```bash
python-docx
pdfplumber
nltk
google-generativeai
python-dotenv
supabase
```

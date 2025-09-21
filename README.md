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

4. **Environment variables (.env):**
   A .env file is already included in this repository with the required keys.
  ⚠️ Make sure this .env file is placed in the root project folder (same directory as index_documents.py).

5. **Environment variables (.env):**
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

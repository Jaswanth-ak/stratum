# ▲ Stratum — Enterprise Intelligence

> Query, compare, and analyze the public knowledge base of top MNCs across financial domains — powered by hybrid BM25 + semantic retrieval and local LLM inference.

![Stratum Dashboard](assets/demo.png)

---

## What is Stratum?

Stratum is a **Retrieval-Augmented Generation (RAG) system** built for enterprise financial intelligence. It ingests annual reports and 10-K filings from major corporations, indexes them into a hybrid search engine, and lets you ask natural language questions — returning **sourced, cited answers with page-level references**.

A business analyst typically spends 4–6 hours researching a company before a client meeting. Stratum does it in under 30 seconds.

---

## Demo

**Query:** *"Total revenue and R&D expenses for NVIDIA and Alphabet 2023 and 2024 with R&D as percentage of revenue"*

| Company  | Year | Total Revenue| R&D Expenses | R&D % of Revenue|
|----------|------|--------------|--------------|-----------------|
| NVIDIA   | 2023 | $26,974M     | $45,427M     | 17.0%           |
| NVIDIA   | 2024 | $60,922M     | $18.6M       | 3.07%           |
| Alphabet | 2023 | $282.72B     | $45,427M     | 16.2%           |
| Alphabet | 2024 | $386.28B     | $38.8M       | 10.1%           |

Every answer includes page-level citations from source documents.

---

## What Makes Stratum Different

| Feature | Typical RAG Project | Stratum |
|---------|-------------------|---------|
| Retrieval | Semantic only | **Hybrid BM25 + semantic** |
| Companies | One at a time | **Multi-company simultaneous** |
| Citations | None | **Page-level source grounding** |
| Time awareness | No | **Year-tagged metadata filtering** |
| LLM | Cloud API | **Local Ollama — zero cost** |
| Data | Upload manually | **SEC EDGAR + IR pages** |

---

## Architecture

```
PDFs (SEC 10-K, Annual Reports)
        │
        ▼
pdfplumber extraction
        │
        ▼
RecursiveCharacterTextSplitter (800 token chunks)
        │
        ▼
Metadata tagging → company · domain · year · page
        │
        ▼
sentence-transformers (all-MiniLM-L6-v2) embeddings
        │
        ▼
ChromaDB persistent vector store
        │
    Query time
        │
   ┌────┴────┐
   │         │
BM25      Semantic
sparse    dense
search    search
   │         │
   └────┬────┘
        │
   Hybrid merge (0.3 BM25 + 0.7 semantic)
        │
        ▼
   Ollama (gemma3:4b) — local inference
        │
        ▼
   Structured answer + page citations
```

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Vector store | ChromaDB | Local, persistent, metadata filtering |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Free, fast, offline |
| Sparse retrieval | rank-bm25 | Exact keyword matching for financial figures |
| Dense retrieval | ChromaDB cosine similarity | Semantic understanding |
| Document loading | pdfplumber | Better text extraction than pypdf |
| Chunking | LangChain RecursiveCharacterTextSplitter | Context-aware splits |
| LLM | Ollama gemma3:4b | Zero API cost, fully local |
| Frontend | Streamlit | Fast iteration, custom CSS |

---

## Data Sources

| Company | Source | Years |
|---------|--------|-------|
| NVIDIA | Annual Reports (investor.nvidia.com) | 2023, 2024, 2025 |
| Alphabet (Google) | SEC 10-K Filings | 2022, 2023, 2024, 2025 |

**Total: 4,842 chunks indexed across 7 documents**

---

## Setup

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com) installed and running
- gemma3:4b model pulled

```bash
ollama pull gemma3:4b
```

### Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/stratum.git
cd stratum

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```


 data folder structure:
```
data/
├── nvidia/
│   ├── NVIDIA-2025-Annual-Report.pdf
│   ├── NVIDIA-2024-Annual-Report.pdf
│   └── NVIDIA-2023-Annual-Report.pdf
└── google/
    ├── GOOG-10-K-2025.pdf
    ├── GOOG-10-k-2024.pdf
    ├── GOOG-10-k-2023.pdf
    └── goog-10-k-q4-2022.pdf
```

Download NVIDIA reports from [investor.nvidia.com](https://investor.nvidia.com)
Download Alphabet 10-Ks from [abc.xyz/investor](https://abc.xyz/investor)

### Ingest documents

```bash
python ingest.py
```

### Run the app

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Example Queries

```
# Financial comparison
"Total revenue and R&D expenses for NVIDIA and Alphabet 2023 and 2024 with R&D as percentage of revenue"

# Single company deep dive
"What is NVIDIA total revenue and R&D expenses for 2023 2024 and 2025?"

# Strategy analysis
"What risks does NVIDIA highlight in their 2025 annual report?"

# Time-aware
"How has NVIDIA data center revenue grown from 2023 to 2025?"

# Cloud strategy
"What is Alphabet cloud strategy in 2024?"
```

---

## Project Structure

```
stratum/
├── data/                    
│   ├── nvidia/
│   └── google/
├── stratum_db/              
├── venv/                    
├── retrieval.py             
├── ingest.py                
├── app.py                   
├── test_query.py            
├── requirements.txt
├── .env                     
└── .gitignore
```

---

## Why I Built This

Most RAG projects on GitHub do the same thing: upload a PDF, chunk it, embed it into ChromaDB, ask a question, get an answer. The variation is only in the wrapper.

Stratum solves a different problem — **multi-company financial intelligence with hybrid retrieval and time-awareness**. The features that matter:

1. **Hybrid search** — BM25 catches exact financial figures (EBITDA, ticker symbols) that semantic search misses. Combining both gives production-grade retrieval quality.

2. **Metadata filtering** — every chunk is tagged with company, domain, and year. This enables queries like "show me only NVIDIA 2024 financial data" without any hallucination from other years.

3. **Page citations** — every factual claim is grounded to a specific page in a specific document. This is how you prevent hallucination in financial contexts.

4. **Local inference** — zero API cost, works offline, no data sent to third parties.

---

## Background

This started as a question: why does every RAG project on GitHub do exactly 
the same thing? PDF in, question in, answer out — no citations, one company, 
no time awareness. Stratum is the answer to that question. It reflects what I think a useful enterprise 
intelligence tool actually needs — hybrid retrieval, grounded citations, 
and cross-company comparison that works on real financial documents.
---

## Requirements

```
chromadb
sentence-transformers
rank-bm25
langchain
langchain-community
langchain-text-splitters
langchain-core
pypdf
pdfplumber
anthropic
streamlit
requests
arxiv
python-dotenv
ollama
```

---

## License

MIT License — free to use, modify, and build on.

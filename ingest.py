from dotenv import load_dotenv
load_dotenv()

from retrieval import StratumIngester        

ingester = StratumIngester(chroma_path="./stratum_db")  

print("Starting ingestion...")
print("=" * 50)

# ── NVIDIA ────────────────────────────────────────
ingester.ingest_pdf(
    pdf_path="data/nvidia/NVIDIA-2025-Annual-Report.pdf",
    company="NVIDIA",
    domain="financial",
    year=2025,
    source_name="NVIDIA Annual Report 2025",
)

ingester.ingest_pdf(
    pdf_path="data/nvidia/NVIDIA-2024-Annual-Report.pdf",
    company="NVIDIA",
    domain="financial",
    year=2024,
    source_name="NVIDIA Annual Report 2024",
)

ingester.ingest_pdf(
    pdf_path="data/nvidia/NVIDIA-2023-Annual-Report.pdf",
    company="NVIDIA",
    domain="financial",
    year=2023,
    source_name="NVIDIA Annual Report 2023",
)

# ── Google / Alphabet ─────────────────────────────
ingester.ingest_pdf(
    pdf_path="data/google/GOOG-10-K-2025.pdf",
    company="Google",
    domain="financial",
    year=2025,
    source_name="Alphabet 10-K 2025",
)

ingester.ingest_pdf(
    pdf_path="data/google/GOOG-10-k-2024.pdf",
    company="Google",
    domain="financial",
    year=2024,
    source_name="Alphabet 10-K 2024",
)

ingester.ingest_pdf(
    pdf_path="data/google/GOOG-10-k-2023.pdf",
    company="Google",
    domain="financial",
    year=2023,
    source_name="Alphabet 10-K 2023",
)

ingester.ingest_pdf(
    pdf_path="data/google/goog-10-k-q4-2022.pdf",
    company="Google",
    domain="financial",
    year=2022,
    source_name="Alphabet 10-K 2022",
)

print("=" * 50)
print("All done! stratum_db is ready.")
print("Run test_query.py to verify everything works.")
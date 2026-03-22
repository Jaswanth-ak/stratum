from dotenv import load_dotenv
load_dotenv()

from retrieval import Stratum

stratum = Stratum(chroma_path="./stratum_db")

result = stratum.query(
    question="What is the total revenue and research and development expenses for NVIDIA and Alphabet for 2023 and 2024? Show as a comparison table and calculate R&D as percentage of revenue.",
    companies=["NVIDIA", "Google"],
    domains=["financial"],
)

print("\n=== Stratum Answer ===")
print(result["answer"])

if result["confidence_flag"]:
    print("\n  Low confidence — answer may be incomplete.")

print("\n=== Sources ===")
for c in result["citations"]:
    print(f"  [{c['company']} | {c['year']}] {c['source']}, p.{c['page']}  (score: {c['score']})")
import sys
from chat_app_gpt_example import backend

def print_entry(entry, idx=None):
    prefix = f"[{idx+1}] " if idx is not None else ""
    print(f"{prefix}Title: {entry.get('title')}")
    print(f"  Description: {entry.get('description')}")
    print(f"  Authors: {', '.join(entry.get('authors', []) or [])}")
    print(f"  Keywords: {', '.join(entry.get('keywords', []) or [])}")
    print(f"  Data Source: {entry.get('data_source')}")
    print(f"  Chunk Index: {entry.get('chunk_index')}")
    print(f"  Distance: {entry.get('distance'):.4f}")
    print(f"  Chunk Text: {entry.get('chunk_text')[:300]}{'...' if entry.get('chunk_text') and len(entry.get('chunk_text')) > 300 else ''}")
    print("-" * 60)

def main():
    print("Data Catalog Chat Client (CLI)")
    print("Type your query or question. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        if not user_input:
            continue

        print("\nSearching catalog...")
        results = backend.search_catalog(user_input, top_k=5)
        if not results:
            print("No relevant catalog entries found.")
            continue

        print("\nTop relevant catalog entries:")
        for idx, entry in enumerate(results):
            print_entry(entry, idx)

        # Q&A: If the input ends with a question mark, try to answer
        if user_input.strip().endswith("?"):
            print("\nQ&A:")
            answer = backend.answer_question(user_input, results)
            print(answer)

if __name__ == "__main__":
    main()

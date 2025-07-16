import os
import sys
import argparse
import psycopg2
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Database connection setup
dbname = os.environ.get("PG_DBNAME") or "postgres"
dbuser = os.environ.get("POSTGRES_USER")
dbpass = os.environ.get("POSTGRES_PASSWORD")
pg_connection_string = f"dbname={dbname} user={dbuser} password={dbpass} host='0.0.0.0'"

# Initialize console for rich output
console = Console()

def get_query_embedding(query: str, model_name: str = 'all-MiniLM-L6-v2') -> List[float]:
    """Generate embedding for the query text."""
    model = SentenceTransformer(model_name)
    embedding = model.encode(query)
    return embedding.tolist()

def search_similar_documents(
    query_embedding: List[float],
    top_k: int = 5,
    data_source: Optional[str] = None,
    threshold: float = 0.5
) -> List[Dict]:
    """
    Search for similar documents using vector similarity.
    Uses cosine similarity (1 - cosine distance).
    """
    with psycopg2.connect(pg_connection_string) as conn:
        cur = conn.cursor()

        # Build the query with optional filters
        base_query = """
        SELECT
            id,
            doc_id,
            title,
            description,
            chunk_text,
            chunk_index,
            data_source,
            keywords,
            1 - (embedding <=> %s::vector) as similarity
        FROM documents
        WHERE 1=1
        """

        params = [query_embedding]

        if data_source:
            base_query += " AND data_source = %s"
            params.append(data_source)

        base_query += """
        AND 1 - (embedding <=> %s::vector) > %s
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """
        params.extend([query_embedding, threshold, query_embedding, top_k])

        cur.execute(base_query, params)

        results = []
        for row in cur.fetchall():
            results.append({
                'id': row[0],
                'doc_id': row[1],
                'title': row[2],
                'description': row[3],
                'chunk_text': row[4],
                'chunk_index': row[5],
                'data_source': row[6],
                'keywords': row[7],
                'similarity': row[8]
            })

        cur.close()
        return results

def query_llm(query: str, context: List[Dict], model: str = "ollama/llama3.1") -> str:
    """
    Query the LLM with the user's question and retrieved context.
    Uses LiteLLM proxy for Ollama.
    """
    # Prepare context from retrieved documents
    context_text = "\n\n".join([
        f"Document {i+1} (Similarity: {doc['similarity']:.3f}):\n"
        f"Title: {doc['title']}\n"
        f"Description: {doc['description']}\n"
        f"Content: {doc['chunk_text']}\n"
        f"Keywords: {', '.join(doc['keywords']) if doc['keywords'] else 'None'}"
        for i, doc in enumerate(context)
    ])

    # Construct the prompt
    prompt = f"""You are a helpful assistant that answers questions based on the provided context.
Use the following documents to answer the user's question. If the answer cannot be found in the context, say so.

Context:
{context_text}

User Question: {query}

Please provide a comprehensive answer based on the above context. Include relevant details and cite which documents you're drawing information from."""

    # Call LiteLLM proxy
    litellm_url = os.environ.get("LITELLM_URL", "http://localhost:4000")

    try:
        response = requests.post(
            f"{litellm_url}/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.environ.get('LITELLM_MASTER_KEY', '')}"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
        )

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"Error querying LLM: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Error connecting to LLM: {str(e)}"

def display_results(query: str, results: List[Dict], llm_response: str):
    """Display search results and LLM response in a formatted way."""
    console.print(f"\n[bold blue]Query:[/bold blue] {query}\n")

    # Display retrieved documents
    if results:
        table = Table(title="Retrieved Documents", show_header=True, header_style="bold magenta")
        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Title", style="green", width=40)
        table.add_column("Similarity", style="yellow", width=10)
        table.add_column("Source", style="blue", width=15)

        for i, doc in enumerate(results):
            table.add_row(
                str(i + 1),
                doc['title'][:40] + "..." if len(doc['title']) > 40 else doc['title'],
                f"{doc['similarity']:.3f}",
                doc['data_source'] or "Unknown"
            )

        console.print(table)
        console.print()

        # Display LLM response
        console.print(Panel(
            llm_response,
            title="[bold green]AI Response[/bold green]",
            border_style="green"
        ))

        # Display detailed results if requested
        console.print("\n[bold]Detailed Results:[/bold]")
        for i, doc in enumerate(results):
            console.print(f"\n[bold cyan]Document {i+1}:[/bold cyan]")
            console.print(f"[yellow]Title:[/yellow] {doc['title']}")
            console.print(f"[yellow]Description:[/yellow] {doc['description']}")
            console.print(f"[yellow]Chunk:[/yellow] {doc['chunk_text']}")
            console.print(f"[yellow]Keywords:[/yellow] {', '.join(doc['keywords']) if doc['keywords'] else 'None'}")
            console.print(f"[yellow]Similarity Score:[/yellow] {doc['similarity']:.3f}")
            console.print("-" * 80)
    else:
        console.print("[red]No similar documents found.[/red]")

def run_query(
    query: str,
    top_k: int = 5,
    data_source: Optional[str] = None,
    use_llm: bool = True,
    similarity_threshold: float = 0.5
):
    """Main function to run the query pipeline."""
    try:
        # Generate embedding for the query
        console.print("[yellow]Generating query embedding...[/yellow]")
        query_embedding = get_query_embedding(query)

        # Search for similar documents
        console.print("[yellow]Searching for similar documents...[/yellow]")
        results = search_similar_documents(
            query_embedding,
            top_k=top_k,
            data_source=data_source,
            threshold=similarity_threshold
        )

        # Query LLM if enabled and results found
        llm_response = ""
        if use_llm and results:
            console.print("[yellow]Querying LLM for comprehensive answer...[/yellow]")
            llm_response = query_llm(query, results)
        elif not use_llm:
            llm_response = "LLM querying disabled. Showing only vector search results."
        else:
            llm_response = "No similar documents found to provide context for LLM."

        # Display results
        display_results(query, results, llm_response)

    except Exception as e:
        console.print(f"[red]Error during query execution: {str(e)}[/red]")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Query documents using vector embeddings and LLM")
    parser.add_argument("query", nargs="?", help="Query text")
    parser.add_argument("-k", "--top-k", type=int, default=5, help="Number of documents to retrieve (default: 5)")
    parser.add_argument("-s", "--source", help="Filter by data source")
    parser.add_argument("--no-llm", action="store_true", help="Disable LLM querying, only show vector search results")
    parser.add_argument("-t", "--threshold", type=float, default=0.5, help="Similarity threshold (0-1, default: 0.5)")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    # Ensure the script is run from the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Check if the required environment variable is set
    if 'CATALOG_ENV' not in os.environ:
        console.print("[red]Error: CATALOG_ENV environment variable is not set.[/red]")
        sys.exit(1)

    # Interactive mode
    if args.interactive:
        console.print("[bold green]Interactive Query Mode[/bold green]")
        console.print("Type 'exit' or 'quit' to stop.\n")

        while True:
            try:
                query = console.input("[bold blue]Enter your query:[/bold blue] ")
                if query.lower() in ['exit', 'quit']:
                    break

                run_query(
                    query=query,
                    top_k=args.top_k,
                    data_source=args.source,
                    use_llm=not args.no_llm,
                    similarity_threshold=args.threshold
                )
                console.print("\n" + "="*80 + "\n")

            except KeyboardInterrupt:
                console.print("\n[yellow]Exiting interactive mode.[/yellow]")
                break
    else:
        # Single query mode
        if not args.query:
            parser.print_help()
            sys.exit(1)

        run_query(
            query=args.query,
            top_k=args.top_k,
            data_source=args.source,
            use_llm=not args.no_llm,
            similarity_threshold=args.threshold
        )

if __name__ == "__main__":
    main()

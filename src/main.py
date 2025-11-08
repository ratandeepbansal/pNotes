"""CLI entrypoint for the Personal RAG Notes App."""
import argparse
import sys
from pathlib import Path

from .rag.qa import QASystem


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Personal RAG Notes App - Your AI-powered knowledge base"
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Index command
    subparsers.add_parser('index', help='Index all notes')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for notes')
    search_parser.add_argument('query', nargs='+', help='Search query')
    search_parser.add_argument('-k', '--top-k', type=int, default=5,
                              help='Number of results to return (default: 5)')

    # Ask command
    ask_parser = subparsers.add_parser('ask', help='Ask a question')
    ask_parser.add_argument('question', nargs='+', help='Your question')
    ask_parser.add_argument('-k', '--top-k', type=int, default=5,
                           help='Number of notes to consider (default: 5)')

    # Summarize command
    summarize_parser = subparsers.add_parser('summarize', help='Summarize a topic')
    summarize_parser.add_argument('topic', nargs='+', help='Topic to summarize')
    summarize_parser.add_argument('-k', '--top-k', type=int, default=5,
                                 help='Number of notes to include (default: 5)')

    # Stats command
    subparsers.add_parser('stats', help='Show knowledge base statistics')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize QA system
    qa = QASystem()

    try:
        if args.command == 'index':
            print("Indexing all notes...")
            count = qa.index_notes()
            print(f"\n✓ Successfully indexed {count} notes!")

        elif args.command == 'search':
            query = ' '.join(args.query)
            print(f"Searching for: '{query}'\n")

            results = qa.retriever.search_semantic(query, top_k=args.top_k)

            if not results:
                print("No results found.")
            else:
                print(f"Found {len(results)} results:\n")
                for i, result in enumerate(results, 1):
                    title = result.get('title', 'Untitled')
                    path = result.get('path', '')
                    score = result.get('relevance_score', 0.0)
                    tags = result.get('tags', '')

                    print(f"{i}. {title}")
                    print(f"   Path: {path}")
                    print(f"   Relevance: {score:.3f}")
                    if tags:
                        print(f"   Tags: {tags}")
                    print()

        elif args.command == 'ask':
            question = ' '.join(args.question)
            print(f"Question: {question}\n")

            result = qa.answer_question(question, top_k=args.top_k)

            print(result['answer'])
            print(f"\nConfidence: {result['confidence']:.3f}")

            if result['sources']:
                print(f"\nSources ({len(result['sources'])} notes):")
                for i, source in enumerate(result['sources'], 1):
                    print(f"  {i}. {source['title']} ({source['path']})")

        elif args.command == 'summarize':
            topic = ' '.join(args.topic)
            print(f"Summarizing topic: '{topic}'\n")

            result = qa.summarize_topic(topic, top_k=args.top_k)

            print(result['summary'])
            print(f"\nBased on {result['note_count']} note(s)")

        elif args.command == 'stats':
            stats = qa.get_stats()
            print("Knowledge Base Statistics:")
            print(f"  Total notes indexed: {stats['total_notes']}")
            print(f"  Notes in metadata DB: {stats['notes_in_db']}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        qa.close()


if __name__ == '__main__':
    main()

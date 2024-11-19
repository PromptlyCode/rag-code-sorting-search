import os
from sklearn.metrics.pairwise import cosine_similarity
import faiss
import argparse
import pickle
from pathlib import Path
from search.search_functions import search_code
from index.index_py import embed_code, build_index

def main():
    parser = argparse.ArgumentParser(description='Code Search Tool')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Build command
    build_parser = subparsers.add_parser('build', help='Build search index')
    build_parser.add_argument('directory', type=str, help='Directory containing Python files')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for code')
    search_parser.add_argument('query', type=str, help='Search query')

    args = parser.parse_args()

    if args.command == 'build':
        build_index(args.directory)
    elif args.command == 'search':
        results = search_code(args.query, embed_code)
        if isinstance(results, str):
            print(results)
        else:
            for result in results:
                print(f"\nRank: {result['rank']}")
                print(f"Score: {result['score']:.4f}")
                print(f"File: {result['file']}")
                print(f"Function: {result['function_name']} (lines {result['start_line']}-{result['end_line']})")
                print("\nCode with context:")
                # Print context before
                for i, line in enumerate(result['before_context'], start=result['context_start_line']):
                    print(f"{i:4d} | {line}")
                # Print function code
                for i, line in enumerate(result['function_code'], start=result['start_line']):
                    print(f"{i:4d} | {line}")
                # Print context after
                for i, line in enumerate(result['after_context'], start=result['end_line'] + 1):
                    print(f"{i:4d} | {line}")
                print("-" * 80)

if __name__ == "__main__":
    main()

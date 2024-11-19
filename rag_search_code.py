import os
import tree_sitter
import tree_sitter_python as tspython
from tree_sitter import Language, Parser
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import requests
import json
import faiss
import argparse
from pathlib import Path
import pickle

# Set up Tree-sitter for Python
PY_LANGUAGE = Language(tspython.language()) #Language(os.path.expanduser('~/.tree-sitter/python.so'), 'python')
parser = Parser(PY_LANGUAGE)

def extract_functions_from_file(file_path):
    """Extract all function definitions from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        tree = parser.parse(bytes(code, "utf8"))
        root_node = tree.root_node
        
        functions = []
        for node in root_node.children:
            if node.type == 'function_definition':
                function_name = node.child_by_field_name('name').text.decode('utf8')
                function_code = code[node.start_byte:node.end_byte]
                
                # Calculate line numbers
                start_line = node.start_point[0] + 1  # Convert to 1-based line numbering
                end_line = node.end_point[0] + 1
                
                functions.append({
                    'name': function_name,
                    'code': function_code,
                    'file': str(file_path),
                    'start_line': start_line,
                    'end_line': end_line,
                    'full_file_content': code  # Store the full file content
                })
        return functions
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def embed_code(code_snippets):
    """Embed code using Ollama Nomic Embed Text."""
    embeddings = []
    for snippet in code_snippets:
        response = requests.post('http://localhost:11434/api/embeddings',
                               json={
                                   "model": "nomic-embed-text",
                                   "prompt": snippet
                               })
        if response.status_code == 200:
            embedding = response.json()['embedding']
            embeddings.append(embedding)
        else:
            print(f"Error embedding snippet: {response.status_code}")
            embeddings.append([0] * 768)
    return np.array(embeddings, dtype=np.float32)

def build_index(directory):
    """Build FAISS index from Python files in directory."""
    functions = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                functions.extend(extract_functions_from_file(file_path))
    
    if not functions:
        print("No Python functions found in the directory.")
        return
    
    # Embed all function codes
    code_snippets = [f['code'] for f in functions]
    embeddings = embed_code(code_snippets)
    
    # Initialize FAISS index
    dimension = embeddings.shape[1]  # Should be 768 for nomic-embed-text
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Save index and metadata
    output_dir = Path('code_search_index')
    output_dir.mkdir(exist_ok=True)
    
    faiss.write_index(index, str(output_dir / 'code.index'))
    with open(output_dir / 'metadata.pkl', 'wb') as f:
        pickle.dump(functions, f)
    
    print(f"Index built successfully. Total functions indexed: {len(functions)}")

def get_context_lines(full_content, start_line, end_line, context_lines=3):
    """Get additional context lines before and after the function."""
    lines = full_content.splitlines()
    
    context_start = max(0, start_line - context_lines - 1)
    context_end = min(len(lines), end_line + context_lines)
    
    before_context = lines[context_start:start_line-1]
    function_lines = lines[start_line-1:end_line]
    after_context = lines[end_line:context_end]
    
    return {
        'before_context': before_context,
        'function': function_lines,
        'after_context': after_context,
        'context_start_line': context_start + 1,
        'context_end_line': context_end
    }

def search_code(query, top_k=5):
    """Search for similar code using the built index."""
    try:
        # Load index and metadata
        index = faiss.read_index('code_search_index/code.index')
        with open('code_search_index/metadata.pkl', 'rb') as f:
            functions = pickle.load(f)
        
        # Embed query
        query_embedding = embed_code([query])[0].reshape(1, -1)
        
        # Search
        D, I = index.search(query_embedding, top_k)
        
        # Format results
        results = []
        for i, (distance, idx) in enumerate(zip(D[0], I[0])):
            func = functions[idx]
            
            # Get context lines
            context = get_context_lines(
                func['full_file_content'],
                func['start_line'],
                func['end_line']
            )
            
            results.append({
                'rank': i + 1,
                'score': 1 / (1 + distance),  # Convert distance to similarity score
                'function_name': func['name'],
                'file': func['file'],
                'start_line': func['start_line'],
                'end_line': func['end_line'],
                'before_context': context['before_context'],
                'function_code': context['function'],
                'after_context': context['after_context'],
                'context_start_line': context['context_start_line'],
                'context_end_line': context['context_end_line']
            })
        
        return results
    
    except FileNotFoundError:
        return "Index not found. Please build the index first using the build command."

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
        results = search_code(args.query)
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


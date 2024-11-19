import tree_sitter
import tree_sitter_python as tspython
from tree_sitter import Language, Parser
import requests
import json
import numpy as np
import os
from pathlib import Path
import faiss
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

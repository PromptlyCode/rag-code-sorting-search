@ prunp rag_search_code.py search "search code"

Rank: 1
Score: 0.0020
Function: search_code
File: /Users/clojure/Desktop/1112AIlearn-interview/rag-code-sorting-search/rag_search_code.py
Code:
 Language, Parser
import nump
--------------------------------------------------------------------------------

Rank: 2
Score: 0.0019
Function: embed_code
File: /Users/clojure/Desktop/1112AIlearn-interview/rag-code-sorting-search/rag_search_code.py
Code:
sitter_python a
--------------------------------------------------------------------------------

Rank: 3
Score: 0.0019
Function: build_index
File: /Users/clojure/Desktop/1112AIlearn-interview/rag-code-sorting-search/rag_search_code.py
Code:
tspython
from tree_sitter impo
--------------------------------------------------------------------------------

Rank: 4
Score: 0.0018
Function: main
File: /Users/clojure/Desktop/1112AIlearn-interview/rag-code-sorting-search/rag_search_code.py
Code:
as np
from sklearn.metrics.p
--------------------------------------------------------------------------------

Rank: 5
Score: 0.0016
Function: extract_functions_from_file
File: /Users/clojure/Desktop/1112AIlearn-interview/rag-code-sorting-search/rag_search_code.py
Code:
tree_sitter
import tre
--------------------------------------------------------------------------------

## test 2 : get full code 
@ prunp rag_search_code.py search "search code"

Rank: 1
Score: 0.0037
File: /Users/clojure/Desktop/1112AIlearn-interview/rag-code-sorting-search/rag_search_code.py
Function: search_code (lines 118-161)

Code with context:
 115 |         'context_end_line': context_end
 116 |     }
 117 |
 118 | def search_code(query, top_k=5):
 119 |     """Search for similar code using the built index."""
 120 |     try:
 121 |         # Load index and metadata
 122 |         index = faiss.read_index('code_search_index/code.index')
 123 |         with open('code_search_index/metadata.pkl', 'rb') as f:
 124 |             functions = pickle.load(f)
 125 |
 126 |         # Embed query
 127 |         query_embedding = embed_code([query])[0].reshape(1, -1)
 128 |
 129 |         # Search
 130 |         D, I = index.search(query_embedding, top_k)
 131 |
 132 |         # Format results
 133 |         results = []
 134 |         for i, (distance, idx) in enumerate(zip(D[0], I[0])):
 135 |             func = functions[idx]
 136 |
 137 |             # Get context lines
 138 |             context = get_context_lines(
 139 |                 func['full_file_content'],
 140 |                 func['start_line'],
 141 |                 func['end_line']
 142 |             )
 143 |
 144 |             results.append({
 145 |                 'rank': i + 1,
 146 |                 'score': 1 / (1 + distance),  # Convert distance to similarity score
 147 |                 'function_name': func['name'],
 148 |                 'file': func['file'],
 149 |                 'start_line': func['start_line'],
 150 |                 'end_line': func['end_line'],
 151 |                 'before_context': context['before_context'],
 152 |                 'function_code': context['function'],
 153 |                 'after_context': context['after_context'],
 154 |                 'context_start_line': context['context_start_line'],
 155 |                 'context_end_line': context['context_end_line']
 156 |             })
 157 |
 158 |         return results
 159 |
 160 |     except FileNotFoundError:
 161 |         return "Index not found. Please build the index first using the build command."
 162 |
 163 | def main():
 164 |     parser = argparse.ArgumentParser(description='Code Search Tool')
--------------------------------------------------------------------------------

Rank: 2
Score: 0.0030
File: /Users/clojure/Desktop/1112AIlearn-interview/rag-code-sorting-search/rag_search_code.py
Function: main (lines 163-191)

Code with context:
 160 |     except FileNotFoundError:
 161 |         return "Index not found. Please build the index first using the build command."
 162 |
 163 | def main():
 164 |     parser = argparse.ArgumentParser(description='Code Search Tool')
 165 |     subparsers = parser.add_subparsers(dest='command', help='Commands')
 166 |
 167 |     # Build command
 168 |     build_parser = subparsers.add_parser('build', help='Build search index')
 169 |     build_parser.add_argument('directory', type=str, help='Directory containing Python files')
 170 |
 171 |     # Search command
 172 |     search_parser = subparsers.add_parser('search', help='Search for code')
 173 |     search_parser.add_argument('query', type=str, help='Search query')
 174 |
 175 |     args = parser.parse_args()
 176 |
 177 |     if args.command == 'build':
 178 |         build_index(args.directory)
 179 |     elif args.command == 'search':
 180 |         results = search_code(args.query)
 181 |         if isinstance(results, str):
 182 |             print(results)
 183 |         else:
 184 |             for result in results:
 185 |                 print(f"\nRank: {result['rank']}")
 186 |                 print(f"Score: {result['score']:.4f}")
 187 |                 print(f"Function: {result['function_name']}")
 188 |                 print(f"File: {result['file']}")
 189 |                 print("Code:")
 190 |                 print(result['code'])
 191 |                 print("-" * 80)
 192 |
 193 | if __name__ == "__main__":
 194 |     main()
--------------------------------------------------------------------------------

Rank: 3
Score: 0.0027
File: /Users/clojure/Desktop/1112AIlearn-interview/rag-code-sorting-search/rag_search_code.py
Function: build_index (lines 67-97)

Code with context:
  64 |             embeddings.append([0] * 768)
  65 |     return np.array(embeddings, dtype=np.float32)
  66 |
  67 | def build_index(directory):
  68 |     """Build FAISS index from Python files in directory."""
  69 |     functions = []
  70 |     for root, _, files in os.walk(directory):
  71 |         for file in files:
  72 |             if file.endswith('.py'):
  73 |                 file_path = Path(root) / file
  74 |                 functions.extend(extract_functions_from_file(file_path))
  75 |
  76 |     if not functions:
  77 |         print("No Python functions found in the directory.")
  78 |         return
  79 |
  80 |     # Embed all function codes
  81 |     code_snippets = [f['code'] for f in functions]
  82 |     embeddings = embed_code(code_snippets)
  83 |
  84 |     # Initialize FAISS index
  85 |     dimension = embeddings.shape[1]  # Should be 768 for nomic-embed-text
  86 |     index = faiss.IndexFlatL2(dimension)
  87 |     index.add(embeddings)
  88 |
  89 |     # Save index and metadata
  90 |     output_dir = Path('code_search_index')
  91 |     output_dir.mkdir(exist_ok=True)
  92 |
  93 |     faiss.write_index(index, str(output_dir / 'code.index'))
  94 |     with open(output_dir / 'metadata.pkl', 'wb') as f:
  95 |         pickle.dump(functions, f)
  96 |
  97 |     print(f"Index built successfully. Total functions indexed: {len(functions)}")
  98 |
  99 | def get_context_lines(full_content, start_line, end_line, context_lines=3):
 100 |     """Get additional context lines before and after the function."""
--------------------------------------------------------------------------------

Rank: 4
Score: 0.0026
File: /Users/clojure/Desktop/1112AIlearn-interview/rag-code-sorting-search/rag_search_code.py
Function: embed_code (lines 50-65)

Code with context:
  47 |         print(f"Error processing {file_path}: {e}")
  48 |         return []
  49 |
  50 | def embed_code(code_snippets):
  51 |     """Embed code using Ollama Nomic Embed Text."""
  52 |     embeddings = []
  53 |     for snippet in code_snippets:
  54 |         response = requests.post('http://localhost:11434/api/embeddings',
  55 |                                json={
  56 |                                    "model": "nomic-embed-text",
  57 |                                    "prompt": snippet
  58 |                                })
  59 |         if response.status_code == 200:
  60 |             embedding = response.json()['embedding']
  61 |             embeddings.append(embedding)
  62 |         else:
  63 |             print(f"Error embedding snippet: {response.status_code}")
  64 |             embeddings.append([0] * 768)
  65 |     return np.array(embeddings, dtype=np.float32)
  66 |
  67 | def build_index(directory):
  68 |     """Build FAISS index from Python files in directory."""
--------------------------------------------------------------------------------

Rank: 5
Score: 0.0022
File: /Users/clojure/Desktop/1112AIlearn-interview/rag-code-sorting-search/rag_search_code.py
Function: extract_functions_from_file (lines 18-48)

Code with context:
  15 | PY_LANGUAGE = Language(tspython.language()) #Language(os.path.expanduser('~/.tree-sitter/python.so'), 'python')
  16 | parser = Parser(PY_LANGUAGE)
  17 |
  18 | def extract_functions_from_file(file_path):
  19 |     """Extract all function definitions from a Python file."""
  20 |     try:
  21 |         with open(file_path, 'r', encoding='utf-8') as f:
  22 |             code = f.read()
  23 |
  24 |         tree = parser.parse(bytes(code, "utf8"))
  25 |         root_node = tree.root_node
  26 |
  27 |         functions = []
  28 |         for node in root_node.children:
  29 |             if node.type == 'function_definition':
  30 |                 function_name = node.child_by_field_name('name').text.decode('utf8')
  31 |                 function_code = code[node.start_byte:node.end_byte]
  32 |
  33 |                 # Calculate line numbers
  34 |                 start_line = node.start_point[0] + 1  # Convert to 1-based line numbering
  35 |                 end_line = node.end_point[0] + 1
  36 |
  37 |                 functions.append({
  38 |                     'name': function_name,
  39 |                     'code': function_code,
  40 |                     'file': str(file_path),
  41 |                     'start_line': start_line,
  42 |                     'end_line': end_line,
  43 |                     'full_file_content': code  # Store the full file content
  44 |                 })
  45 |         return functions
  46 |     except Exception as e:
  47 |         print(f"Error processing {file_path}: {e}")
  48 |         return []
  49 |
  50 | def embed_code(code_snippets):
  51 |     """Embed code using Ollama Nomic Embed Text."""
--------------------------------------------------------------------------------


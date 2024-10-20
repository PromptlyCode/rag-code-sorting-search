## python rag : use treesitter  the python code to search ，and then  embed  calc consin search list sort & embed_code use  ollama nomic-embed-text
import tree_sitter
from tree_sitter import Language, Parser
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import requests
import json

# Step 1: Set up Tree-sitter for Python
PY_LANGUAGE = Language('path/to/tree-sitter-python.so', 'python')
parser = Parser()
parser.set_language(PY_LANGUAGE)

def search_code(code, query):
    tree = parser.parse(bytes(code, "utf8"))
    root_node = tree.root_node
    
    results = []
    for node in root_node.children:
        if node.type == 'function_definition':
            function_name = node.child_by_field_name('name').text.decode('utf8')
            if query.lower() in function_name.lower():
                results.append((function_name, node.start_point, node.end_point))
    
    return results

# Step 2: Embed code snippets using Ollama Nomic Embed Text
def embed_code(code_snippets):
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
            embeddings.append([0] * 768)  # Default to zero vector on error
    return np.array(embeddings)

# Step 3: Cosine similarity search
def cosine_search(query_embedding, code_embeddings):
    similarities = cosine_similarity([query_embedding], code_embeddings)
    return similarities.flatten()

# Step 4: Main RAG function
def rag_search(code, query):
    # Search for relevant functions
    search_results = search_code(code, query)
    
    if not search_results:
        return "No matching functions found."
    
    # Extract function names and code snippets
    function_names = [result[0] for result in search_results]
    code_snippets = [code[result[1][0]:result[2][0]] for result in search_results]
    
    # Embed code snippets
    code_embeddings = embed_code(code_snippets)
    
    # Embed query
    query_embedding = embed_code([query])[0]  # Take the first (and only) embedding
    
    # Perform cosine similarity search
    similarities = cosine_search(query_embedding, code_embeddings)
    
    # Sort results by similarity
    sorted_results = sorted(zip(function_names, similarities), key=lambda x: x[1], reverse=True)
    
    return sorted_results

# Example usage
sample_code = """
def hello_world():
    print("Hello, World!")

def greet_user(name):
    print(f"Hello, {name}!")

def calculate_sum(a, b):
    return a + b
"""

query = "greet"
results = rag_search(sample_code, query)
print(results)


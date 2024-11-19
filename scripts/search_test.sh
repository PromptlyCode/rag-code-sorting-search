@ prunp rag_search_code.py search "search code"

Rank: 1
Score: 0.0020
Function: search_code
File: /Users/clojure/Desktop/1112AIlearn-interview/rag-code-sorting-search/rag_search_code.py
Code:
 Language, Parser
import nump
--------------------------------------------------------------------------------
...

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
 159 |
...
 160 |     except FileNotFoundError:
 161 |         return "Index not found. Please build the index first using the build command."
 162 |
 163 | def main():
 164 |     parser = argparse.ArgumentParser(description='Code Search Tool')
--------------------------------------------------------------------------------
...


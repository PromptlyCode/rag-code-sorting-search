import faiss
import pickle

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

def search_code(query, embed_code, top_k=5):
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

# RAG code sorting search

## RAG First Principles

* The essence of rag is knowledge organization, which is convenient for accurate search again. If there is not enough context, it should be completed in the rag knowledge organization process, such as using tree_sitter in the code to complete the problem of insufficient keywords for insufficient types.

## Init

* Setup python env
```sh
conda create -n rag-code-sorting-search python=3.11
conda activate rag-code-sorting-search
poetry install
```
* [Ollama](https://ollama.com/) run embed model
```sh
ollama run nomic-embed-text
```


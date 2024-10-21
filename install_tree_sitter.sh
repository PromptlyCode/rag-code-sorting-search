sudo apt update
sudo apt install build-essential git

sudo apt install tree-sitter-cli
git clone https://github.com/tree-sitter/tree-sitter-python.git
cd tree-sitter-python

gcc -c -I./src src/parser.c -fPIC -Os
gcc -shared -o python.so parser.o

mkdir -p ~/.tree-sitter
mv python.so ~/.tree-sitter/


curl https://ollama.ai/install.sh | sh
ollama pull nomic-embed-text
ollama serve


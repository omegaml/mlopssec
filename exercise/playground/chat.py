import sys
from .llm import ask_llm

if __name__ == '__main__':
    if len(sys.argv) == 1:
        prompt = input('prompt >')
    else:
        prompt = sys.argv[1]
    
    response = ask_llm([], prompt)
    print(f'assistant: {response}')
import argparse
from LLM import CodeGen
from prompt import userPrompt, systemPrompt, normalPrompt
from utils import parse_css, count_tokens
import time
from rich.console import Console

def run_normal():
    console = Console()
    model = CodeGen(model_name='gpt-4o', system=normalPrompt, temperature=0)
    
    with open('input.css', 'r') as f:
        css_code = f.read()

    user_input = input("Enter your refactoring changes: ")
    start_time = time.time()
    
    query = userPrompt.format(css_code=css_code, instructions=user_input)
    out = model(query)
    out_tokens = count_tokens(out)

    with open('output.css', 'w+') as f:
        f.write(out)

    console.print("\n✨ Done! File written to output.css", style="bold green")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print()
    print("-"*75)
    print(f"Total execution time: {elapsed_time:.2f} seconds")
    print(f"Output tokens: {out_tokens}")
    print("-"*75)

def run_accelerated():
    console = Console()
    model = CodeGen(model_name='gpt-4o', system=systemPrompt, temperature=0)

    with open('input.css', 'r') as f:
        css_code = f.read()

    user_input = input("Enter your refactoring changes: ")
    console.print("🚀 Running in accelerated mode...", style="bold green")
    start_time = time.time()

    with console.status("Generating...", spinner="balloon", speed=0.7):
        existing_code = parse_css(css_code)

        query = userPrompt.format(css_code=css_code, instructions=user_input, temperature=0.5)
        out = model(query)
        out_tokens = count_tokens(out)

        updated_code, blocks = parse_css(out, llm_output=True)

        # Update Algorithm
        edits = open('output.css', 'w+')

        while existing_code:
            existing_key, existing_value = existing_code.popleft()
            if existing_key in blocks:
                while updated_code:
                    updated_key, updated_value = updated_code.popleft()
                    if updated_value: 
                        edits.write(f"{existing_value}\n\n")
                    if updated_key == existing_key:
                        break
            else:
                edits.write(f"{existing_value}\n\n")

        while updated_code:
            updated_key, updated_value = updated_code.popleft()
            if updated_value: edits.write(f"{updated_value}\n\n")

        edits.close()

        end_time = time.time()
        elapsed_time = end_time - start_time

    console.print("✨ Done! File written to output.css", style="bold green")

    print()
    print("-"*75)
    print(f"Total execution time: {elapsed_time:.2f} seconds")
    print(f"Output tokens: {out_tokens}")
    print("-"*75)

def main():
    parser = argparse.ArgumentParser(description='CSS Refactoring Tool')
    parser.add_argument('-accelerate', action='store_true', help='Run in accelerated mode')
    args = parser.parse_args()

    if args.accelerate:
        run_accelerated()
    else:
        run_normal()

if __name__ == "__main__":
    main()
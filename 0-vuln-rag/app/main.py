import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types 

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def main():
    load_dotenv(PROJECT_ROOT.parent / ".env")

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL")

    if not api_key or not model: 
        raise SystemExit(
            "Set GEMINI_API_KEY and GEMINI_MODEL in your .env file."
        )

    question = input("Question: ").strip()

    if not question: 
        raise SystemExit("Please enter a question.")

    with genai.Client(api_key=api_key) as client: 
        response = client.models.generate_content(
            model = model, 
            contents = question, 
            config = types.GenerateContentConfig(
                system_instruction=(
                    "You are a learning assistant."
                    "Explain concepts clearly and concisely."
                    "If you do not know something, say so."
                ),
                temperature = 0.2, 
                max_output_tokens = 512,
            ),
        )
        
        print("\nAnswer:")
        print(response.text or "[No text returned]")
        
        usage = response.usage_metadata
        if usage is not None: 
            print("\nToken usage:")
            print(f"Input: {usage.prompt_token_count}")
            print(f"Output: {usage.candidates_token_count}")
            print(f"Total: {usage.total_token_count}")
            

if __name__ == "__main__":
    main()
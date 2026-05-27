"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

def pull_prompts_from_langsmith():
    check_env_vars(["LANGCHAIN_API_KEY"])

    print_section_header("Pulling prompts from LangSmith")

    prompt_ref = "leonanluppi/bug_to_user_story_v1"
    print(f"Pulling: {prompt_ref}")
    prompt = hub.pull(prompt_ref)

    system_prompt = ""
    user_prompt = ""
    for msg in getattr(prompt, "messages", []):
        role = getattr(msg, "role", None) or type(msg).__name__.lower()
        template = getattr(msg, "prompt", msg).template
        if "system" in role.lower():
            system_prompt = template
        elif "human" in role.lower() or "user" in role.lower():
            user_prompt = template

    prompt_data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
        }
    }

    output_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v1.yml"
    if save_yaml(prompt_data, str(output_path)):
        print(f"Prompt saved to: {output_path}")
    else:
        print("Failed to save prompt.")
        return 1

    return 0


def main():
    return pull_prompts_from_langsmith()


if __name__ == "__main__":
    sys.exit(main())

"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    username = os.getenv("USERNAME_LANGSMITH_HUB", "")
    if not username:
        print("❌ USERNAME_LANGSMITH_HUB não configurada no .env")
        return False

    full_name = f"{username}/{prompt_name}"

    system_prompt = prompt_data.get("system_prompt", "")
    user_prompt = prompt_data.get("user_prompt", "")
    description = prompt_data.get("description", "")
    tags = prompt_data.get("tags", [])
    techniques = prompt_data.get("techniques_applied", [])

    template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt),
    ])

    if techniques:
        description = f"{description}\n\nTécnicas aplicadas: {', '.join(techniques)}"

    try:
        client = Client()
        client.push_prompt(
            prompt_identifier=full_name,
            object=template,
            description=description,
            tags=tags,
            is_public=True,
        )
        print(f"   ✓ Publicado: {full_name}")
        return True
    except Exception as e:
        if "Nothing to commit" in str(e):
            print(f"   ✓ Sem alterações: {full_name}")
            return True
        print(f"   ❌ Erro ao publicar {full_name}: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    system_prompt = prompt_data.get("system_prompt", "").strip()
    if not system_prompt:
        errors.append("system_prompt está vazio ou ausente")

    if not prompt_data.get("user_prompt", "").strip():
        errors.append("user_prompt está vazio ou ausente")

    techniques = prompt_data.get("techniques_applied", [])
    if len(techniques) < 2:
        errors.append(f"techniques_applied requer pelo menos 2 técnicas, encontradas: {len(techniques)}")

    full_text = system_prompt + prompt_data.get("user_prompt", "")
    if "[TODO]" in full_text or "TODO" in full_text:
        errors.append("Prompt contém TODOs não resolvidos")

    return (len(errors) == 0, errors)


def main():
    print_section_header("Push de prompts otimizados para o LangSmith")

    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    yaml_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
    print(f"Carregando: {yaml_path}")
    data = load_yaml(str(yaml_path))

    if not data:
        print("❌ Não foi possível carregar o arquivo YAML.")
        return 1

    prompts_to_push = {
        "bug_to_user_story_v2": data.get("bug_to_user_story_v2"),
    }

    all_ok = True

    for prompt_name, prompt_data in prompts_to_push.items():
        if prompt_data is None:
            print(f"❌ Chave '{prompt_name}' não encontrada no YAML.")
            all_ok = False
            continue

        print(f"\nValidando: {prompt_name}")
        is_valid, errors = validate_prompt(prompt_data)

        if not is_valid:
            print("   ❌ Validação falhou:")
            for err in errors:
                print(f"      - {err}")
            all_ok = False
            continue

        print("   ✓ Validação OK")
        print(f"   Publicando no LangSmith Hub...")

        if not push_prompt_to_langsmith(prompt_name, prompt_data):
            all_ok = False

    if all_ok:
        print("\n✅ Todos os prompts publicados com sucesso.")
        username = os.getenv("USERNAME_LANGSMITH_HUB", "")
        print(f"   Acesse: https://smith.langchain.com/prompts/{username}")
        return 0
    else:
        print("\n❌ Alguns prompts falharam.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

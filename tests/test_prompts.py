"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def prompt_v2():
    """Carrega os dados do prompt bug_to_user_story_v2."""
    yaml_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
    data = load_prompts(str(yaml_path))
    return data["bug_to_user_story_v2"]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_v2):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_v2, "Campo 'system_prompt' ausente no YAML"
        system_prompt = prompt_v2["system_prompt"]
        assert system_prompt is not None, "system_prompt é None"
        assert system_prompt.strip(), "system_prompt está vazio"

    def test_prompt_has_role_definition(self, prompt_v2):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system_prompt = prompt_v2["system_prompt"]
        assert "Você é um" in system_prompt, (
            "system_prompt não define uma persona. "
            "Esperado: 'Você é um <role>'"
        )

    def test_prompt_mentions_format(self, prompt_v2):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_v2["system_prompt"]
        user_story_markers = ["Como um", "eu quero", "para que"]
        markdown_markers = ["##", "**", "```"]

        has_user_story_format = all(m in system_prompt for m in user_story_markers)
        has_markdown = any(m in system_prompt for m in markdown_markers)

        assert has_user_story_format or has_markdown, (
            "system_prompt não especifica formato User Story ('Como um / eu quero / para que') "
            "nem usa estrutura Markdown (##, **, ```)."
        )

    def test_prompt_has_few_shot_examples(self, prompt_v2):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_v2["system_prompt"]
        has_input = "Input:" in system_prompt
        has_output = "Output:" in system_prompt
        has_example_label = "Exemplo" in system_prompt

        assert has_example_label, (
            "system_prompt não contém marcador de exemplo ('Exemplo'). "
            "Adicione pelo menos um bloco de few-shot com exemplos rotulados."
        )
        assert has_input and has_output, (
            "system_prompt não contém pares de entrada/saída. "
            "Esperado: 'Input:' e 'Output:' nos exemplos few-shot."
        )

    def test_prompt_no_todos(self, prompt_v2):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        full_text = (
            prompt_v2.get("system_prompt", "")
            + prompt_v2.get("user_prompt", "")
            + prompt_v2.get("description", "")
        )
        assert "[TODO]" not in full_text, "Prompt contém '[TODO]' não resolvido"
        assert "TODO" not in full_text, "Prompt contém 'TODO' não resolvido"

    def test_minimum_techniques(self, prompt_v2):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_v2.get("techniques_applied", [])
        assert isinstance(techniques, list), (
            "Campo 'techniques_applied' deve ser uma lista"
        )
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requeridas em 'techniques_applied', "
            f"encontradas: {len(techniques)} ({techniques})"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

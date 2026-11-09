
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from src import agente


def resposta_tool(nome, argumentos, tool_id="tool_123"):
    """Simula uma resposta da Anthropic solicitando uma ferramenta."""
    return SimpleNamespace(
        content=[
            SimpleNamespace(
                type="tool_use",
                name=nome,
                input=argumentos,
                id=tool_id,
            )
        ]
    )


def resposta_texto(texto):
    """Simula uma resposta textual da Anthropic."""
    return SimpleNamespace(
        content=[
            SimpleNamespace(
                type="text",
                text=texto,
            )
        ]
    )


class TestExecutarFerramenta(unittest.TestCase):

    def test_ferramenta_desconhecida(self):
        """Deve rejeitar ferramentas não cadastradas."""
        with self.assertRaises(ValueError):
            agente.executar_ferramenta("inexistente", {})

    def test_argumentos_invalidos(self):
        """Deve rejeitar argumentos que não sejam dicionários."""
        with self.assertRaises(ValueError):
            agente.executar_ferramenta("status_acao", "inválido")

    def test_executar_ferramenta_com_sucesso(self):
        """Deve executar corretamente uma ferramenta cadastrada."""
        with patch.dict(
            agente.IMPLEMENTACOES,
            {"teste": lambda entrada: "sucesso"},
        ):
            resultado = agente.executar_ferramenta("teste", {})

        self.assertEqual(resultado, "sucesso")


class TestConversar(unittest.TestCase):

    def test_resposta_sem_ferramentas(self):
        """Deve retornar o texto quando não houver tool use."""
        client = Mock()
        client.messages.create.return_value = resposta_texto(
            "Olá! Sou seu agente financeiro."
        )

        resultado = agente.conversar(client, [])

        self.assertEqual(
            resultado,
            "Olá! Sou seu agente financeiro."
        )

        client.messages.create.assert_called_once()

    def test_execucao_de_ferramenta(self):
        """Deve executar uma ferramenta e retornar a resposta final."""
        client = Mock()

        client.messages.create.side_effect = [
            resposta_tool("teste", {"valor": 100}),
            resposta_texto("Ferramenta executada com sucesso."),
        ]

        mensagens = []

        with patch.dict(
            agente.IMPLEMENTACOES,
            {"teste": lambda entrada: "resultado correto"},
        ):
            resultado = agente.conversar(client, mensagens)

        self.assertEqual(
            resultado,
            "Ferramenta executada com sucesso."
        )

        self.assertEqual(client.messages.create.call_count, 2)

        self.assertEqual(mensagens[0]["role"], "assistant")
        self.assertEqual(mensagens[1]["role"], "user")

        resultado_tool = mensagens[1]["content"][0]

        self.assertEqual(resultado_tool["type"], "tool_result")
        self.assertEqual(resultado_tool["tool_use_id"], "tool_123")
        self.assertEqual(resultado_tool["content"], "resultado correto")


if __name__ == "__main__":
    unittest.main()

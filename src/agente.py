"""
Agente Financeiro com IA Generativa
------------------------------------
Um agente de linha de comando que entende pedidos em linguagem natural
e decide sozinho qual ferramenta usar: analisar uma ação, calcular um
saldo, remover transações duplicadas ou padronizar um nome.

Uso:
    export ANTHROPIC_API_KEY="sua_chave_aqui"
    python src/agente.py
"""

import os
import sys
import json

import anthropic

from ferramentas import (
    status_acao,
    calcular_saldo,
    remover_duplicatas,
    converter_maiusculas,
)

MODELO = "claude-sonnet-5"

# Descrição das ferramentas no formato que a API da Anthropic espera.
# É a partir daqui que o modelo decide QUAL função chamar e com quais
# argumentos, com base no que o usuário escreveu.
FERRAMENTAS = [
    {
        "name": "status_acao",
        "description": (
            "Compara o preço de abertura e fechamento de uma ação e diz "
            "se ela teve ALTA, BAIXA ou permaneceu ESTAVEL."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "abertura": {"type": "integer", "description": "Preço de abertura"},
                "fechamento": {"type": "integer", "description": "Preço de fechamento"},
            },
            "required": ["abertura", "fechamento"],
        },
    },
    {
        "name": "calcular_saldo",
        "description": (
            "Calcula o saldo final do dia a partir de uma lista de lançamentos "
            "financeiros no formato 'R 100.00,D 50.00' (R = receita, D = despesa)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "lancamentos": {
                    "type": "string",
                    "description": "Lançamentos separados por vírgula, ex: 'R 100.00,D 50.00'",
                }
            },
            "required": ["lancamentos"],
        },
    },
    {
        "name": "remover_duplicatas",
        "description": (
            "Remove identificadores de transações duplicados de uma lista, "
            "mantendo apenas a primeira ocorrência de cada um."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "identificadores": {
                    "type": "string",
                    "description": "Identificadores separados por espaço, ex: 'TX1 TX2 TX1'",
                }
            },
            "required": ["identificadores"],
        },
    },
    {
        "name": "converter_maiusculas",
        "description": "Converte um texto (como o nome de um destinatário) para maiúsculas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "texto": {"type": "string", "description": "Texto a ser convertido"}
            },
            "required": ["texto"],
        },
    },
]

# Liga o nome da ferramenta (que o modelo escolhe) à função Python real
IMPLEMENTACOES = {
    "status_acao": lambda i: status_acao(i["abertura"], i["fechamento"]),
    "calcular_saldo": lambda i: calcular_saldo(i["lancamentos"]),
    "remover_duplicatas": lambda i: remover_duplicatas(i["identificadores"]),
    "converter_maiusculas": lambda i: converter_maiusculas(i["texto"]),
}


def executar_ferramenta(nome: str, entrada: dict):
    if nome not in IMPLEMENTACOES:
        return f"Ferramenta desconhecida: {nome}"
    try:
        return IMPLEMENTACOES[nome](entrada)
    except Exception as erro:
        return f"Erro ao executar {nome}: {erro}"


def conversar(client: anthropic.Anthropic, mensagens: list) -> str:
    """Envia as mensagens ao modelo e resolve o loop de tool-use até
    obter uma resposta final em texto."""

    while True:
        resposta = client.messages.create(
            model=MODELO,
            max_tokens=1024,
            tools=FERRAMENTAS,
            messages=mensagens,
        )

        blocos_tool_use = [b for b in resposta.content if b.type == "tool_use"]

        if not blocos_tool_use:
            # Não há mais chamadas de ferramenta: essa é a resposta final
            texto = "".join(b.text for b in resposta.content if b.type == "text")
            return texto

        # Guarda a resposta do modelo (incluindo os tool_use) no histórico
        mensagens.append({"role": "assistant", "content": resposta.content})

        # Executa cada ferramenta pedida e devolve o resultado ao modelo
        resultados = []
        for bloco in blocos_tool_use:
            resultado = executar_ferramenta(bloco.name, bloco.input)
            resultados.append(
                {
                    "type": "tool_result",
                    "tool_use_id": bloco.id,
                    "content": str(resultado),
                }
            )

        mensagens.append({"role": "user", "content": resultados})


def main():
    chave = os.environ.get("ANTHROPIC_API_KEY")
    if not chave:
        print("Defina a variável de ambiente ANTHROPIC_API_KEY antes de rodar.")
        print('Exemplo: export ANTHROPIC_API_KEY="sua_chave_aqui"')
        sys.exit(1)

    client = anthropic.Anthropic(api_key=chave)
    mensagens = []

    print("Agente Financeiro pronto. Digite 'sair' para encerrar.\n")
    print("Exemplos do que você pode pedir:")
    print(' - "A ação abriu a 10 e fechou a 15, como ela se saiu?"')
    print(' - "Calcule o saldo de: R 100.00,D 50.00,R 20.00"')
    print(' - "Remova as transações repetidas: TX1 TX2 TX1 TX3"')
    print(' - "Deixe este nome em maiúsculas: joao silva"\n')

    while True:
        entrada = input("Você: ").strip()
        if entrada.lower() in ("sair", "exit", "quit"):
            print("Até mais!")
            break
        if not entrada:
            continue

        mensagens.append({"role": "user", "content": entrada})
        resposta = conversar(client, mensagens)
        mensagens.append({"role": "assistant", "content": resposta})
        print(f"Agente: {resposta}\n")


if __name__ == "__main__":
    main()

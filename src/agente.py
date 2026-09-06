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
    estatisticas_serie,
    gerar_grafico,
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
    {
        "name": "estatisticas_serie",
        "description": (
            "Calcula estatísticas descritivas (média, mediana, desvio padrão, "
            "mínimo e máximo) de uma série de números, como preços de uma ação "
            "ao longo de vários dias."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "valores": {
                    "type": "string",
                    "description": "Números separados por vírgula, ex: '32,34,31,36,40'",
                }
            },
            "required": ["valores"],
        },
    },
    {
        "name": "gerar_grafico",
        "description": (
            "Gera um gráfico (de linha ou de barra) a partir de uma série de "
            "números e salva como imagem PNG. Útil para visualizar a evolução "
            "de preços ou saldos ao longo do tempo."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "valores": {
                    "type": "string",
                    "description": "Números separados por vírgula, ex: '32,34,31,36,40'",
                },
                "tipo": {
                    "type": "string",
                    "enum": ["linha", "barra"],
                    "description": "Tipo de gráfico. Padrão: 'linha'.",
                },
                "titulo": {
                    "type": "string",
                    "description": "Título do gráfico.",
                },
            },
            "required": ["valores"],
        },
    },
]

# Liga o nome da ferramenta (que o modelo escolhe) à função Python real
IMPLEMENTACOES = {
    "status_acao": lambda i: status_acao(i["abertura"], i["fechamento"]),
    "calcular_saldo": lambda i: calcular_saldo(i["lancamentos"]),
    "remover_duplicatas": lambda i: remover_duplicatas(i["identificadores"]),
    "converter_maiusculas": lambda i: converter_maiusculas(i["texto"]),
    "estatisticas_serie": lambda i: estatisticas_serie(i["valores"]),
    "gerar_grafico": lambda i: gerar_grafico(
        i["valores"], i.get("tipo", "linha"), i.get("titulo", "Série de valores")
    ),
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
    print(' - "Deixe este nome em maiúsculas: joao silva"')
    print(' - "Quais as estatísticas desses preços: 32,34,31,36,40,38,42?"')
    print(' - "Gere um gráfico de linha com esses valores: 32,34,31,36,40,38,42"\n')

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

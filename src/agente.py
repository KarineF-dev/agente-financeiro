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

try:
    from .ferramentas import (
        status_acao,
        calcular_saldo,
        remover_duplicatas,
        converter_maiusculas,
        estatisticas_serie,
        gerar_grafico,
        inspecionar_csv,
        analisar_csv,
        gerar_grafico_csv,
    )
except ImportError:
    from ferramentas import (
        status_acao,
        calcular_saldo,
        remover_duplicatas,
        converter_maiusculas,
        estatisticas_serie,
        gerar_grafico,
        inspecionar_csv,
        analisar_csv,
        gerar_grafico_csv,
    )

MODELO = "claude-sonnet-5"

MAX_CICLOS_AGENTE = 8

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
            "números digitados diretamente na conversa e salva como imagem PNG. "
            "Use quando o usuário digitar os valores na mensagem, não quando "
            "houver um arquivo CSV envolvido."
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
    {
        "name": "inspecionar_csv",
        "description": (
            "Lê um arquivo CSV da pasta 'dados/' do projeto e retorna as "
            "colunas disponíveis, o número de linhas e uma amostra dos "
            "primeiros registros. Use isso primeiro, antes de analisar_csv "
            "ou gerar_grafico_csv, se você não souber os nomes das colunas."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "nome_arquivo": {
                    "type": "string",
                    "description": "Nome do arquivo CSV, ex: 'acoes_exemplo.csv'",
                }
            },
            "required": ["nome_arquivo"],
        },
    },
    {
        "name": "analisar_csv",
        "description": (
            "Lê um arquivo CSV da pasta 'dados/' e calcula estatísticas "
            "descritivas (média, mediana, desvio padrão, mínimo, máximo) de "
            "uma coluna numérica específica."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "nome_arquivo": {
                    "type": "string",
                    "description": "Nome do arquivo CSV, ex: 'acoes_exemplo.csv'",
                },
                "coluna": {
                    "type": "string",
                    "description": "Nome da coluna numérica a ser analisada, ex: 'fechamento'",
                },
            },
            "required": ["nome_arquivo", "coluna"],
        },
    },
    {
        "name": "gerar_grafico_csv",
        "description": (
            "Lê um arquivo CSV da pasta 'dados/' e gera um gráfico (linha ou "
            "barra) de uma coluna numérica em função de outra coluna (ex: "
            "preço de fechamento por data). Salva como PNG e retorna o caminho."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "nome_arquivo": {
                    "type": "string",
                    "description": "Nome do arquivo CSV, ex: 'acoes_exemplo.csv'",
                },
                "coluna_x": {
                    "type": "string",
                    "description": "Coluna do eixo X, geralmente uma data, ex: 'data'",
                },
                "coluna_y": {
                    "type": "string",
                    "description": "Coluna numérica do eixo Y, ex: 'fechamento'",
                },
                "tipo": {
                    "type": "string",
                    "enum": ["linha", "barra"],
                    "description": "Tipo de gráfico. Padrão: 'linha'.",
                },
                "titulo": {
                    "type": "string",
                    "description": "Título do gráfico. Opcional.",
                },
            },
            "required": ["nome_arquivo", "coluna_x", "coluna_y"],
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
    "inspecionar_csv": lambda i: inspecionar_csv(i["nome_arquivo"]),
    "analisar_csv": lambda i: analisar_csv(i["nome_arquivo"], i["coluna"]),
    "gerar_grafico_csv": lambda i: gerar_grafico_csv(
        i["nome_arquivo"], i["coluna_x"], i["coluna_y"],
        i.get("tipo", "linha"), i.get("titulo", ""),
    ),
}


def executar_ferramenta(nome: str, entrada: dict):
    """Executa uma ferramenta registrada no agente."""
    if nome not in IMPLEMENTACOES:
        raise ValueError(f"Ferramenta desconhecida: {nome}")

    if not isinstance(entrada, dict):
        raise ValueError("Os argumentos devem ser um dicionário.")

    return IMPLEMENTACOES[nome](entrada)


def conversar(client: anthropic.Anthropic, mensagens: list) -> str:
    """Executa o ciclo de tool use com limite e tratamento de erros."""

    for ciclo in range(MAX_CICLOS_AGENTE):
        resposta = client.messages.create(
            model=MODELO,
            max_tokens=1024,
            tools=FERRAMENTAS,
            messages=mensagens,
        )

        blocos_tool_use = [
            bloco for bloco in resposta.content
            if bloco.type == "tool_use"
        ]

        if not blocos_tool_use:
            return "".join(
                bloco.text
                for bloco in resposta.content
                if bloco.type == "text"
            )

        mensagens.append({
            "role": "assistant",
            "content": resposta.content,
        })

        resultados = []

        for bloco in blocos_tool_use:
            try:
                resultado = executar_ferramenta(
                    bloco.name,
                    bloco.input
                )

                conteudo = (
                    resultado
                    if isinstance(resultado, str)
                    else json.dumps(
                        resultado,
                        ensure_ascii=False,
                        default=str
                    )
                )

                resultados.append({
                    "type": "tool_result",
                    "tool_use_id": bloco.id,
                    "content": conteudo,
                })

            except Exception as erro:
                resultados.append({
                    "type": "tool_result",
                    "tool_use_id": bloco.id,
                    "content": (
                        f"Erro ao executar a ferramenta: "
                        f"{type(erro).__name__}: {erro}"
                    ),
                    "is_error": True,
                })

        mensagens.append({
            "role": "user",
            "content": resultados,
        })

    return (
        "Não consegui concluir a solicitação dentro do limite "
        "de ciclos de execução."
    )

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
    print(' - "O que tem no arquivo acoes_exemplo.csv?"')
    print(' - "Analise a coluna fechamento do acoes_exemplo.csv"')
    print(' - "Gere um gráfico de fechamento por data usando acoes_exemplo.csv"\n')

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

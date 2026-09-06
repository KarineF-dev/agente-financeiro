"""
Ferramentas do agente financeiro.

Cada função aqui é uma "ferramenta" que o agente de IA pode escolher
chamar, dependendo do que o usuário pedir em linguagem natural.
São as mesmas lógicas dos desafios resolvidos anteriormente,
organizadas como funções reutilizáveis, mais um par de ferramentas
de análise de dados (estatísticas e gráficos).
"""

import os
import statistics
import uuid

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # gera imagem sem precisar de tela/display
import matplotlib.pyplot as plt

PASTA_GRAFICOS = os.path.join(os.path.dirname(__file__), "..", "graficos")
PASTA_DADOS = os.path.join(os.path.dirname(__file__), "..", "dados")


def status_acao(abertura: int, fechamento: int) -> str:
    """
    Compara o preço de abertura e fechamento de uma ação e retorna
    "ALTA", "BAIXA" ou "ESTAVEL".
    """
    if fechamento > abertura:
        return "ALTA"
    elif fechamento < abertura:
        return "BAIXA"
    else:
        return "ESTAVEL"


def calcular_saldo(lancamentos: str) -> float:
    """
    Recebe uma string com lançamentos separados por vírgula, no formato
    "TIPO VALOR" (ex.: "R 100.00,D 50.00"), e retorna o saldo final:
    soma das receitas (R) menos soma das despesas (D).
    """
    saldo = 0.0
    for lancamento in lancamentos.split(","):
        tipo, valor = lancamento.strip().split(" ")
        valor = float(valor)
        if tipo == "R":
            saldo += valor
        elif tipo == "D":
            saldo -= valor
    return round(saldo, 2)


def remover_duplicatas(identificadores: str) -> str:
    """
    Recebe uma string com identificadores separados por espaço e retorna
    apenas a primeira ocorrência de cada um, na ordem original.
    """
    itens = identificadores.split(" ")
    vistos = []
    for item in itens:
        ja_apareceu = False
        for v in vistos:
            if v == item:
                ja_apareceu = True
                break
        if not ja_apareceu:
            vistos.append(item)
    return " ".join(vistos)


def converter_maiusculas(texto: str) -> str:
    """
    Converte todas as letras de uma string para maiúsculas, preservando
    números, espaços e demais caracteres.
    """
    return texto.upper()


def _converter_valores(valores: str) -> list:
    """Converte uma string 'v1,v2,v3' em uma lista de floats."""
    return [float(v.strip()) for v in valores.split(",") if v.strip() != ""]


def estatisticas_serie(valores: str) -> dict:
    """
    Recebe uma série de números separados por vírgula (ex: preços de
    fechamento dos últimos dias) e retorna estatísticas descritivas:
    média, mediana, desvio padrão, mínimo e máximo.
    """
    numeros = _converter_valores(valores)

    if not numeros:
        return {"erro": "Nenhum valor numérico foi encontrado na entrada."}

    resultado = {
        "quantidade": len(numeros),
        "media": round(statistics.mean(numeros), 2),
        "mediana": round(statistics.median(numeros), 2),
        "minimo": min(numeros),
        "maximo": max(numeros),
    }

    # desvio padrão exige pelo menos 2 valores
    if len(numeros) >= 2:
        resultado["desvio_padrao"] = round(statistics.stdev(numeros), 2)
    else:
        resultado["desvio_padrao"] = 0.0

    return resultado


def gerar_grafico(valores: str, tipo: str = "linha", titulo: str = "Série de valores") -> str:
    """
    Gera um gráfico (linha ou barra) a partir de uma série de números
    separados por vírgula e salva como imagem PNG. Retorna o caminho
    do arquivo gerado.
    """
    numeros = _converter_valores(valores)

    if not numeros:
        return "Erro: nenhum valor numérico foi encontrado na entrada."

    os.makedirs(PASTA_GRAFICOS, exist_ok=True)
    nome_arquivo = f"grafico_{uuid.uuid4().hex[:8]}.png"
    caminho = os.path.join(PASTA_GRAFICOS, nome_arquivo)

    eixo_x = list(range(1, len(numeros) + 1))

    plt.figure(figsize=(8, 4.5))
    if tipo == "barra":
        plt.bar(eixo_x, numeros, color="#4527a0")
    else:
        plt.plot(eixo_x, numeros, marker="o", color="#4527a0")

    plt.title(titulo)
    plt.xlabel("Período")
    plt.ylabel("Valor")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(caminho)
    plt.close()

    return caminho


def _resolver_caminho_csv(nome_arquivo: str) -> str:
    """
    Resolve o caminho de um CSV dentro da pasta 'dados/' do projeto.
    Aceita tanto o nome do arquivo ('acoes_exemplo.csv') quanto um
    caminho relativo já apontando para a pasta 'dados/'.
    """
    nome_arquivo = os.path.basename(nome_arquivo)  # evita sair da pasta dados/
    return os.path.join(PASTA_DADOS, nome_arquivo)


def inspecionar_csv(nome_arquivo: str) -> dict:
    """
    Lê um arquivo CSV da pasta 'dados/' e retorna um resumo: nomes das
    colunas, quantidade de linhas e uma amostra das 3 primeiras linhas.
    Útil para o agente descobrir o que existe no arquivo antes de
    analisar uma coluna específica.
    """
    caminho = _resolver_caminho_csv(nome_arquivo)

    if not os.path.exists(caminho):
        return {"erro": f"Arquivo '{nome_arquivo}' não encontrado na pasta dados/."}

    df = pd.read_csv(caminho)

    return {
        "colunas": list(df.columns),
        "linhas": len(df),
        "amostra": df.head(3).to_dict(orient="records"),
    }


def analisar_csv(nome_arquivo: str, coluna: str) -> dict:
    """
    Lê um arquivo CSV da pasta 'dados/' e retorna estatísticas
    descritivas (média, mediana, desvio padrão, mínimo, máximo) de uma
    coluna numérica específica.
    """
    caminho = _resolver_caminho_csv(nome_arquivo)

    if not os.path.exists(caminho):
        return {"erro": f"Arquivo '{nome_arquivo}' não encontrado na pasta dados/."}

    df = pd.read_csv(caminho)

    if coluna not in df.columns:
        return {"erro": f"Coluna '{coluna}' não existe. Colunas disponíveis: {list(df.columns)}"}

    serie = pd.to_numeric(df[coluna], errors="coerce").dropna()

    if serie.empty:
        return {"erro": f"A coluna '{coluna}' não contém valores numéricos."}

    return {
        "quantidade": int(serie.count()),
        "media": round(float(serie.mean()), 2),
        "mediana": round(float(serie.median()), 2),
        "desvio_padrao": round(float(serie.std()), 2) if serie.count() >= 2 else 0.0,
        "minimo": float(serie.min()),
        "maximo": float(serie.max()),
    }


def gerar_grafico_csv(nome_arquivo: str, coluna_x: str, coluna_y: str,
                       tipo: str = "linha", titulo: str = "") -> str:
    """
    Lê um arquivo CSV da pasta 'dados/' e gera um gráfico (linha ou
    barra) de uma coluna numérica (coluna_y) em função de outra coluna
    (coluna_x, geralmente uma data ou índice). Salva como PNG e retorna
    o caminho do arquivo gerado.
    """
    caminho = _resolver_caminho_csv(nome_arquivo)

    if not os.path.exists(caminho):
        return f"Erro: arquivo '{nome_arquivo}' não encontrado na pasta dados/."

    df = pd.read_csv(caminho)

    for coluna in (coluna_x, coluna_y):
        if coluna not in df.columns:
            return f"Erro: coluna '{coluna}' não existe. Colunas disponíveis: {list(df.columns)}"

    os.makedirs(PASTA_GRAFICOS, exist_ok=True)
    nome_saida = f"grafico_{uuid.uuid4().hex[:8]}.png"
    caminho_saida = os.path.join(PASTA_GRAFICOS, nome_saida)

    titulo_final = titulo or f"{coluna_y} por {coluna_x}"

    plt.figure(figsize=(8, 4.5))
    if tipo == "barra":
        plt.bar(df[coluna_x].astype(str), df[coluna_y], color="#4527a0")
    else:
        plt.plot(df[coluna_x].astype(str), df[coluna_y], marker="o", color="#4527a0")

    plt.title(titulo_final)
    plt.xlabel(coluna_x)
    plt.ylabel(coluna_y)
    plt.xticks(rotation=45, ha="right")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(caminho_saida)
    plt.close()

    return caminho_saida


"""
Ferramentas do agente financeiro.

Cada função aqui é uma ferramenta que o agente de IA pode escolher
chamar, dependendo do que o usuário pedir em linguagem natural.
"""

import os
import statistics
import uuid

import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


PASTA_GRAFICOS = os.path.join(os.path.dirname(__file__), "..", "graficos")
PASTA_DADOS = os.path.join(os.path.dirname(__file__), "..", "dados")


def status_acao(abertura: int, fechamento: int) -> str:
    """Compara abertura e fechamento de uma ação."""
    if fechamento > abertura:
        return "ALTA"
    elif fechamento < abertura:
        return "BAIXA"
    else:
        return "ESTAVEL"


def calcular_saldo(lancamentos: str) -> float:
    """Calcula o saldo de receitas e despesas."""
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
    """Remove duplicatas preservando a ordem original."""
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
    """Converte o texto para letras maiúsculas."""
    return texto.upper()


def _converter_valores(valores: str) -> list:
    """Converte uma string de números em uma lista de floats."""
    return [
        float(v.strip())
        for v in valores.split(",")
        if v.strip() != ""
    ]


def estatisticas_serie(valores: str) -> dict:
    """Calcula estatísticas descritivas de uma série numérica."""
    numeros = _converter_valores(valores)

    if not numeros:
        return {
            "erro": "Nenhum valor numérico foi encontrado na entrada."
        }

    resultado = {
        "quantidade": len(numeros),
        "media": round(statistics.mean(numeros), 2),
        "mediana": round(statistics.median(numeros), 2),
        "minimo": min(numeros),
        "maximo": max(numeros),
    }

    if len(numeros) >= 2:
        resultado["desvio_padrao"] = round(
            statistics.stdev(numeros), 2
        )
    else:
        resultado["desvio_padrao"] = 0.0

    return resultado


def _resolver_caminho_csv(nome_arquivo: str) -> str:
    """Resolve o caminho do arquivo dentro da pasta dados/."""
    nome_arquivo = os.path.basename(nome_arquivo)
    return os.path.join(PASTA_DADOS, nome_arquivo)


def inspecionar_csv(nome_arquivo: str) -> dict:
    """Inspeciona as colunas, quantidade de linhas e amostra de um CSV."""
    caminho = _resolver_caminho_csv(nome_arquivo)

    if not os.path.exists(caminho):
        return {
            "erro": f"Arquivo '{nome_arquivo}' não encontrado na pasta dados/."
        }

    df = pd.read_csv(caminho)

    return {
        "colunas": list(df.columns),
        "linhas": len(df),
        "amostra": df.head(3).to_dict(orient="records"),
    }


def analisar_csv(nome_arquivo: str, coluna: str) -> dict:
    """Calcula estatísticas de uma coluna numérica de um CSV."""
    caminho = _resolver_caminho_csv(nome_arquivo)

    if not os.path.exists(caminho):
        return {
            "erro": f"Arquivo '{nome_arquivo}' não encontrado na pasta dados/."
        }

    df = pd.read_csv(caminho)

    if coluna not in df.columns:
        return {
            "erro": (
                f"Coluna '{coluna}' não existe. "
                f"Colunas disponíveis: {list(df.columns)}"
            )
        }

    serie = pd.to_numeric(
        df[coluna],
        errors="coerce"
    ).dropna()

    if serie.empty:
        return {
            "erro": f"A coluna '{coluna}' não contém valores numéricos."
        }

    return {
        "quantidade": int(serie.count()),
        "media": round(float(serie.mean()), 2),
        "mediana": round(float(serie.median()), 2),
        "desvio_padrao": (
            round(float(serie.std()), 2)
            if len(serie) >= 2
            else 0.0
        ),
        "minimo": float(serie.min()),
        "maximo": float(serie.max()),
    }


def _estilizar_grafico(ax, titulo, eixo_x, eixo_y):
    """Aplica uma identidade visual profissional aos gráficos."""

    ax.set_facecolor("#FFFFFF")

    ax.set_title(
        titulo,
        loc="left",
        fontsize=15,
        fontweight="bold",
        color="#1E293B",
        pad=20,
    )

    ax.set_xlabel(
        eixo_x,
        fontsize=10,
        color="#64748B",
        labelpad=10,
    )

    ax.set_ylabel(
        eixo_y,
        fontsize=10,
        color="#64748B",
        labelpad=10,
    )

    ax.grid(
        axis="y",
        linestyle="--",
        linewidth=0.7,
        alpha=0.25,
        color="#94A3B8",
    )

    ax.set_axisbelow(True)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["left"].set_color("#E2E8F0")
    ax.spines["bottom"].set_color("#E2E8F0")

    ax.tick_params(
        axis="both",
        colors="#64748B",
        labelsize=9,
    )

    ax.margins(x=0.05, y=0.15)


def gerar_grafico(
    valores: str,
    tipo: str = "linha",
    titulo: str = "Série de valores"
) -> str:
    """Gera um gráfico profissional de linha ou barra."""

    numeros = _converter_valores(valores)

    if not numeros:
        return "Erro: nenhum valor numérico foi encontrado na entrada."

    os.makedirs(PASTA_GRAFICOS, exist_ok=True)

    nome_arquivo = f"grafico_{uuid.uuid4().hex[:8]}.png"
    caminho = os.path.join(PASTA_GRAFICOS, nome_arquivo)

    eixo_x = list(range(1, len(numeros) + 1))

    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    fig.patch.set_facecolor("#F8FAFC")

    _estilizar_grafico(
        ax,
        titulo,
        "Período",
        "Valor",
    )

    if tipo == "barra":
        barras = ax.bar(
            eixo_x,
            numeros,
            width=0.6,
            color="#635BDB",
            edgecolor="none",
            alpha=0.9,
        )

        if len(numeros) <= 15:
            for barra in barras:
                altura = barra.get_height()

                ax.annotate(
                    f"{altura:,.2f}",
                    (barra.get_x() + barra.get_width() / 2, altura),
                    xytext=(0, 6),
                    textcoords="offset points",
                    ha="center",
                    fontsize=8,
                    color="#475569",
                )

    else:
        ax.plot(
            eixo_x,
            numeros,
            color="#635BDB",
            linewidth=2.8,
            marker="o",
            markersize=6,
            markerfacecolor="#FFFFFF",
            markeredgecolor="#635BDB",
            markeredgewidth=2,
        )

        ax.annotate(
            f"{numeros[-1]:,.2f}",
            (eixo_x[-1], numeros[-1]),
            xytext=(8, 10),
            textcoords="offset points",
            fontsize=9,
            fontweight="bold",
            color="#635BDB",
        )

    fig.tight_layout(pad=2)

    fig.savefig(
        caminho,
        dpi=150,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )

    plt.close(fig)

    return caminho


def gerar_grafico_csv(
    nome_arquivo: str,
    coluna_x: str,
    coluna_y: str,
    tipo: str = "linha",
    titulo: str = ""
) -> str:
    """Gera um gráfico profissional a partir de um arquivo CSV."""

    caminho = _resolver_caminho_csv(nome_arquivo)

    if not os.path.exists(caminho):
        return f"Erro: arquivo '{nome_arquivo}' não encontrado na pasta dados/."

    df = pd.read_csv(caminho)

    for coluna in (coluna_x, coluna_y):
        if coluna not in df.columns:
            return (
                f"Erro: coluna '{coluna}' não existe. "
                f"Colunas disponíveis: {list(df.columns)}"
            )

    dados = df[[coluna_x, coluna_y]].copy()

    dados[coluna_y] = pd.to_numeric(
        dados[coluna_y],
        errors="coerce",
    )

    dados = dados.dropna(subset=[coluna_x, coluna_y])

    if dados.empty:
        return "Erro: não existem dados numéricos válidos para gerar o gráfico."

    os.makedirs(PASTA_GRAFICOS, exist_ok=True)

    nome_saida = f"grafico_{uuid.uuid4().hex[:8]}.png"
    caminho_saida = os.path.join(PASTA_GRAFICOS, nome_saida)

    titulo_final = titulo or f"{coluna_y} por {coluna_x}"

    labels = dados[coluna_x].astype(str).tolist()
    numeros = dados[coluna_y].tolist()

    posicoes = list(range(len(labels)))

    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=150)
    fig.patch.set_facecolor("#F8FAFC")

    _estilizar_grafico(
        ax,
        titulo_final,
        coluna_x,
        coluna_y,
    )

    if tipo == "barra":
        barras = ax.bar(
            posicoes,
            numeros,
            width=0.6,
            color="#635BDB",
            edgecolor="none",
            alpha=0.9,
        )

        if len(numeros) <= 15:
            for barra in barras:
                altura = barra.get_height()

                ax.annotate(
                    f"{altura:,.2f}",
                    (barra.get_x() + barra.get_width() / 2, altura),
                    xytext=(0, 6),
                    textcoords="offset points",
                    ha="center",
                    fontsize=8,
                    color="#475569",
                )

    else:
        ax.plot(
            posicoes,
            numeros,
            color="#635BDB",
            linewidth=2.8,
            marker="o",
            markersize=6,
            markerfacecolor="#FFFFFF",
            markeredgecolor="#635BDB",
            markeredgewidth=2,
        )

        ax.annotate(
            f"{numeros[-1]:,.2f}",
            (posicoes[-1], numeros[-1]),
            xytext=(8, 10),
            textcoords="offset points",
            fontsize=9,
            fontweight="bold",
            color="#635BDB",
        )

    ax.set_xticks(posicoes)
    ax.set_xticklabels(
        labels,
        rotation=35,
        ha="right",
    )

    fig.tight_layout(pad=2)

    fig.savefig(
        caminho_saida,
        dpi=150,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )

    plt.close(fig)

    return caminho_saida

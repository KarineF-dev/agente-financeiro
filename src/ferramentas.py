"""
Ferramentas do agente financeiro.

Cada função aqui é uma "ferramenta" que o agente de IA pode escolher
chamar, dependendo do que o usuário pedir em linguagem natural.
São as mesmas lógicas dos desafios resolvidos anteriormente,
organizadas como funções reutilizáveis.
"""


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

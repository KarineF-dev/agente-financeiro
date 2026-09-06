"""
Testes das ferramentas do agente. Rode com:
    python -m unittest discover tests
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ferramentas import (
    status_acao,
    calcular_saldo,
    remover_duplicatas,
    converter_maiusculas,
)


class TestStatusAcao(unittest.TestCase):
    def test_alta(self):
        self.assertEqual(status_acao(10, 15), "ALTA")

    def test_baixa(self):
        self.assertEqual(status_acao(20, 18), "BAIXA")

    def test_estavel(self):
        self.assertEqual(status_acao(30, 30), "ESTAVEL")
        self.assertEqual(status_acao(5, 5), "ESTAVEL")


class TestCalcularSaldo(unittest.TestCase):
    def test_misto(self):
        self.assertEqual(calcular_saldo("R 100.00,D 50.00,R 20.00"), 70.00)

    def test_so_receitas(self):
        self.assertEqual(calcular_saldo("R 10.00,R 25.50,R 14.50"), 50.00)

    def test_uma_receita(self):
        self.assertEqual(calcular_saldo("R 200.00"), 200.00)

    def test_so_despesas(self):
        self.assertEqual(calcular_saldo("D 100.00,D 50.00"), -150.00)


class TestRemoverDuplicatas(unittest.TestCase):
    def test_transacoes(self):
        self.assertEqual(
            remover_duplicatas("TX1001 TX1002 TX1001 TX1003"),
            "TX1001 TX1002 TX1003",
        )

    def test_ordem_preservada(self):
        self.assertEqual(
            remover_duplicatas("AB12 CD34 AB12 EF56 CD34"),
            "AB12 CD34 EF56",
        )

    def test_sem_duplicatas(self):
        self.assertEqual(remover_duplicatas("QW1 ER2 TY3"), "QW1 ER2 TY3")

    def test_varias_repeticoes(self):
        self.assertEqual(remover_duplicatas("AA BB AA AA BB CC"), "AA BB CC")


class TestConverterMaiusculas(unittest.TestCase):
    def test_nome_simples(self):
        self.assertEqual(converter_maiusculas("joao silva"), "JOAO SILVA")

    def test_com_numeros(self):
        self.assertEqual(converter_maiusculas("Maria123"), "MARIA123")

    def test_ja_minusculo(self):
        self.assertEqual(converter_maiusculas("ana paula"), "ANA PAULA")

    def test_ja_capitalizado(self):
        self.assertEqual(converter_maiusculas("Lucas"), "LUCAS")


if __name__ == "__main__":
    unittest.main()

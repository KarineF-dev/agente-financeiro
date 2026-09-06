# Agente Financeiro

Agente de IA generativa com ferramentas (tool use), construído com a
[API da Anthropic](https://docs.claude.com). Ele entende pedidos em
linguagem natural e decide sozinho qual ferramenta chamar:

- **status_acao** — diz se uma ação teve ALTA, BAIXA ou ficou ESTAVEL
- **calcular_saldo** — soma receitas e subtrai despesas de um extrato
- **remover_duplicatas** — limpa identificadores de transação repetidos
- **converter_maiusculas** — padroniza um nome para maiúsculas
- **estatisticas_serie** — calcula média, mediana, desvio padrão, mínimo e máximo de uma série de números
- **gerar_grafico** — gera um gráfico de linha ou barra (PNG) a partir de uma série de números digitados na conversa
- **inspecionar_csv** — lê um CSV da pasta `dados/` e mostra colunas, número de linhas e uma amostra
- **analisar_csv** — calcula estatísticas descritivas de uma coluna numérica de um CSV
- **gerar_grafico_csv** — gera um gráfico a partir de duas colunas de um CSV (ex: preço por data)

Cada ferramenta é uma função Python comum (em `src/ferramentas.py`); quem
decide **quando** e **com quais argumentos** chamar cada uma é o modelo,
com base no que você escreve.

## Estrutura do projeto

```
agente-financeiro/
├── src/
│   ├── agente.py        # loop principal do agente (chama a API da Anthropic)
│   └── ferramentas.py   # as funções que o agente pode executar
├── dados/
│   └── acoes_exemplo.csv  # CSV de exemplo para as ferramentas de análise de dados
├── tests/
│   └── test_ferramentas.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Como rodar localmente

1. Clone o repositório e entre na pasta:
   ```bash
   git clone https://github.com/SEU_USUARIO/agente-financeiro.git
   cd agente-financeiro
   ```

2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate      # no Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Pegue uma chave de API em [console.anthropic.com](https://console.anthropic.com)
   e defina a variável de ambiente:
   ```bash
   export ANTHROPIC_API_KEY="sua_chave_aqui"    # no Windows: set ANTHROPIC_API_KEY=sua_chave_aqui
   ```

4. Rode o agente:
   ```bash
   python src/agente.py
   ```

5. Converse com ele, por exemplo:
   ```
   Você: A ação abriu a 10 e fechou a 15, como ela se saiu?
   Agente: A ação teve ALTA...

   Você: Calcule o saldo de: R 100.00,D 50.00,R 20.00
   Agente: O saldo final é 70.00...

   Você: Quais as estatísticas desses preços: 32,34,31,36,40,38,42?
   Agente: Média de 36.14, mediana de 36.0, desvio padrão de 4.1...

   Você: Gere um gráfico de linha com esses valores: 32,34,31,36,40,38,42
   Agente: Gráfico salvo em graficos/grafico_xxxxxxxx.png

   Você: O que tem no arquivo acoes_exemplo.csv?
   Agente: O arquivo tem 10 linhas e as colunas: data, ticker, abertura, fechamento, volume...

   Você: Analise a coluna fechamento do acoes_exemplo.csv
   Agente: Média de 34.82, mediana de 34.65, desvio padrão de 1.98...

   Você: Gere um gráfico de fechamento por data usando acoes_exemplo.csv
   Agente: Gráfico salvo em graficos/grafico_xxxxxxxx.png
   ```

   Os gráficos gerados ficam na pasta `graficos/` (criada automaticamente
   e ignorada pelo Git). Para analisar seus próprios dados, basta colocar
   outro arquivo `.csv` dentro da pasta `dados/` e pedir para o agente
   inspecioná-lo primeiro.

## Rodando os testes

As ferramentas têm testes automatizados, sem precisar de chave de API:

```bash
python -m unittest discover tests -v
```

## Como publicar este projeto no GitHub

Se você recebeu este projeto como uma pasta/zip (sem repositório Git
ainda), os passos são:

1. Crie um repositório vazio no GitHub (sem README, sem .gitignore —
   já temos os nossos).
2. Na pasta do projeto, rode:
   ```bash
   git init
   git add .
   git commit -m "Primeira versão do agente financeiro"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/agente-financeiro.git
   git push -u origin main
   ```
3. **Importante:** nunca faça commit da sua chave de API. O `.gitignore`
   já ignora arquivos `.env`; se você criar um para guardar a chave,
   ele não sobe para o GitHub.

## Próximos passos possíveis

- Trocar a "conversa por linha de comando" por uma interface web (Flask/FastAPI)
- Adicionar uma ferramenta real de cotação de ações via API externa
- Guardar o histórico de conversas em um arquivo ou banco de dados

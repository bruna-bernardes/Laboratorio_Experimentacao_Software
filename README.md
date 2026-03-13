# Laboratório 01 — Características de Repositórios Populares

## 📚 Descrição

Este projeto realiza uma análise de **1000 repositórios populares do GitHub**, com o objetivo de identificar características comuns em projetos amplamente utilizados pela comunidade.

A análise investiga aspectos como maturidade dos projetos, atividade de desenvolvimento, contribuições externas e tecnologias utilizadas.

O trabalho foi desenvolvido como parte da disciplina de **Laboratório de Experimentação de Software**.

---

# 👥 Integrantes

* Bruna Barbosa Portilho Bernardes Campidelli
* Ana Luiza Santos Gomes
* Walter Roberto Rodrigues Louback

---

# 🔎 Questões de Pesquisa

O estudo busca responder às seguintes questões:

**RQ1** — Sistemas populares são maduros/antigos?
**RQ2** — Sistemas populares recebem muitas contribuições externas?
**RQ3** — Sistemas populares lançam releases com frequência?
**RQ4** — Sistemas populares são atualizados frequentemente?
**RQ5** — Sistemas populares são escritos nas linguagens mais populares?
**RQ6** — Sistemas populares possuem muitas issues fechadas?

### ⭐ Bônus

**RQ7** — Sistemas escritos em linguagens mais populares recebem mais contribuição externa, lançam mais releases e são atualizados com mais frequência?

Essa análise foi realizada agrupando os resultados das métricas por linguagem de programação.

---

# 📊 Metodologia

Os dados foram coletados utilizando a **API GraphQL do GitHub**.

Consulta utilizada:

```
stars:>0 sort:stars-desc
```

Foram coletados **1000 repositórios**, utilizando requisições paginadas.

As informações coletadas incluem:

* data de criação do repositório
* data da última atualização
* linguagem principal
* número de pull requests aceitas
* número de releases
* número total de issues
* número de issues fechadas

---

# 📂 Estrutura do Projeto

```
lab_01
 ├─ Codigo
 │   ├─ coletar_100.py
 │   ├─ coletar_1000.py
 │   ├─ analise.py
 │   └─ graficos.py
 │
 ├─ Relatorios
 │   ├─ Dados
 │   │   ├─ repos_100.json
 │   │   ├─ repos_1000.json
 │   │   └─ repos_1000.csv
 │
 │   ├─ grafico_linguagens.png
 │   ├─ grafico_idade.png
 │   ├─ tabela_mediana.csv
 │   ├─ rq7_linguagens.csv
 │   └─ relatorio_final.md
```

---

# ⚙️ Tecnologias Utilizadas

* Python
* Pandas
* Matplotlib
* GitHub GraphQL API

---

# 📈 Resultados

A análise dos repositórios populares mostrou que esses projetos geralmente:

* possuem **maior maturidade**
* recebem **grande volume de contribuições externas**
* possuem **lançamentos frequentes**
* são **atualizados constantemente**
* utilizam **linguagens amplamente adotadas**
* apresentam **alta taxa de resolução de issues**

Além disso, a análise adicional **RQ7** mostrou que projetos escritos em determinadas linguagens apresentam maior volume de contribuições e atividade de desenvolvimento.

---

# 🔗 API Utilizada

GitHub GraphQL API:

https://docs.github.com/en/graphql

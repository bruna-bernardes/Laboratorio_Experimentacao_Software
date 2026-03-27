# Lab 01 — Características de Repositórios Populares

## Integrantes

* Ana Luiza Santos Gomes
* Bruna Barbosa Portilho Bernardes Campidelli
* Walter Roberto Rodrigues Louback

---

# 1. Introdução

O GitHub é uma das principais plataformas de hospedagem e colaboração em projetos de software. Repositórios populares geralmente apresentam características relacionadas à maturidade do projeto, atividade de desenvolvimento e participação da comunidade.

Este trabalho analisa **1000 repositórios populares do GitHub**, com o objetivo de identificar padrões relacionados ao desenvolvimento e manutenção desses projetos.

---

# 2. Metodologia

## Coleta de dados

Os dados foram coletados utilizando a **API GraphQL do GitHub**.

Consulta utilizada:

```
stars:>0 sort:stars-desc
```

Foram coletados **1000 repositórios**, utilizando requisições paginadas de 100 repositórios por vez.

Os dados coletados incluem:

* data de criação
* data da última atualização
* linguagem principal
* número de Pull Requests aceitas
* número de releases
* número total de issues
* número de issues fechadas

Os dados foram armazenados em **JSON** e posteriormente convertidos para **CSV** para análise.

---

# 3. Resultados

## RQ1 — Sistemas populares são maduros/antigos?

**Métrica:** idade do repositório.

Idade mediana encontrada:

**8.34 anos**

**Conclusão**

Projetos populares tendem a ser sistemas **maduros**, com vários anos de desenvolvimento.

---

## RQ2 — Sistemas populares recebem muitas contribuições externas?

**Métrica:** Pull Requests aceitas.

Mediana encontrada:

**746 Pull Requests**

**Conclusão**

Projetos populares recebem **grande volume de contribuições externas**, indicando forte participação da comunidade.

---

## RQ3 — Sistemas populares lançam releases com frequência?

**Métrica:** número de releases.

Mediana encontrada:

**36 releases**

**Conclusão**

Projetos populares passam por diversas versões e apresentam **evolução contínua**.

---

## RQ4 — Sistemas populares são atualizados com frequência?

**Métrica:** dias desde a última atualização.

Mediana encontrada:

**2 dias**

**Conclusão**

Projetos populares apresentam **manutenção ativa e atualizações frequentes**.

---

## RQ5 — Sistemas populares são escritos nas linguagens mais populares?

Top linguagens encontradas:

| Linguagem  | Quantidade |
| ---------- | ---------- |
| Python     | 203        |
| TypeScript | 162        |
| JavaScript | 112        |
| Go         | 76         |
| Rust       | 55         |
| C++        | 46         |
| Java       | 46         |

Essas linguagens estão entre as mais utilizadas atualmente na indústria de software.

---

## RQ6 — Sistemas populares possuem muitas issues fechadas?

**Métrica:** proporção de issues fechadas.

Mediana encontrada:

**0.88 (88%)**

Isso indica que a maioria das issues abertas nesses projetos é resolvida.

---

# 4. Visualizações

Para facilitar a interpretação dos resultados, foram criadas visualizações dos dados coletados.

## Linguagens mais utilizadas

![Figura 1 - Linguagens mais utilizadas](grafico_linguagens.png)

**Figura 1:** Distribuição das linguagens de programação mais utilizadas entre os repositórios analisados.

## Distribuição da idade dos repositórios

![Figura 2 - Idade dos repositórios](grafico_idade.png)

**Figura 2:** Distribuição da idade dos repositórios populares analisados.

---

# 5. RQ7 (Bônus) — Análise por linguagem

Foi realizada uma análise adicional agrupando os resultados das RQs 02, 03 e 04 por linguagem de programação.

Foram analisadas:

* Pull Requests aceitas
* número de releases
* dias desde última atualização

Tabela de comparação:

| Linguagem  | PRs aceitas | Releases | Dias desde update |
| ---------- | ----------- | -------- | ----------------- |
| LLVM       | 76334       | 150      | 0                 |
| Julia      | 26914       | 196      | 0                 |
| V          | 13091       | 303      | 0                 |
| Zig        | 7207        | 21       | 0                 |
| PHP        | 5814        | 603      | 0                 |
| C#         | 5186        | 102      | 0                 |
| Ruby       | 4771        | 14       | 0.5               |
| Clojure    | 4355        | 110      | 0                 |
| Lua        | 3384        | 72       | 2                 |
| TypeScript | 2527        | 152      | 0                 |

**Conclusão**

Linguagens amplamente utilizadas apresentam maior atividade de desenvolvimento e contribuições da comunidade.

---

# 6. Discussão

Os resultados mostram que repositórios populares do GitHub apresentam:

* maior maturidade
* grande volume de contribuições externas
* manutenção frequente
* diversas releases
* alta taxa de resolução de issues

Esses fatores indicam projetos bem mantidos e com comunidades ativas.

---

# 7. Conclusão

Este estudo analisou **1000 repositórios populares do GitHub** e identificou características comuns entre esses projetos.

Os resultados indicam que projetos populares:

* possuem histórico de desenvolvimento mais longo
* recebem contribuições frequentes da comunidade
* são atualizados constantemente
* utilizam linguagens amplamente adotadas

Essas características refletem boas práticas de desenvolvimento e forte participação da comunidade.

---

# Ferramentas Utilizadas

* Python
* Pandas
* Matplotlib
* GitHub GraphQL API

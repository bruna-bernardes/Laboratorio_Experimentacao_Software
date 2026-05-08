# Laboratorio 03 — Caracterizando a Atividade de Code Review no GitHub

**Ana Luiza Santos Gomes · Bruna Barbosa Portilho Bernardes Campidelli · Walter Roberto Rodrigues Louback**

---

## 1. Introducao

### 1.1 Contextualizacao

A pratica de code review tornou-se uma constante nos processos de desenvolvimento ageis, consistindo na interacao entre desenvolvedores e revisores para inspecionar o codigo antes de integra-lo a base principal. No contexto de sistemas open source desenvolvidos no GitHub, as atividades de code review acontecem a partir da avaliacao de contribuicoes submetidas por meio de Pull Requests (PR). Para que um codigo seja integrado a branch principal, e necessaria uma solicitacao de pull, que sera avaliada e discutida por colaboradores do projeto, podendo ser aprovada ou rejeitada ao final do processo.

Estudos anteriores demonstraram que caracteristicas como tamanho do PR, tempo de analise e interacoes entre participantes influenciam a decisao de merge (Ortu et al., 2020; Zhang et al., 2022; Gousios et al., 2015).

### 1.2 Problema Foco do Experimento

Identificar e quantificar as variaveis que influenciam no merge de um Pull Request em repositorios populares do GitHub, sob a perspectiva de desenvolvedores que submetem codigo. Busca-se compreender quais caracteristicas dos PRs — tamanho, tempo de analise, descricao e interacoes — estao correlacionadas com o feedback final (aceitacao ou rejeicao) e com o numero de revisoes realizadas.

### 1.3 Questoes-Pesquisa

**Dimensao A — Feedback Final das Revisoes (Status do PR):**

- **RQ01:** Qual a relacao entre o tamanho dos PRs e o feedback final das revisoes?
- **RQ02:** Qual a relacao entre o tempo de analise dos PRs e o feedback final das revisoes?
- **RQ03:** Qual a relacao entre a descricao dos PRs e o feedback final das revisoes?
- **RQ04:** Qual a relacao entre as interacoes nos PRs e o feedback final das revisoes?

**Dimensao B — Numero de Revisoes:**

- **RQ05:** Qual a relacao entre o tamanho dos PRs e o numero de revisoes realizadas?
- **RQ06:** Qual a relacao entre o tempo de analise dos PRs e o numero de revisoes realizadas?
- **RQ07:** Qual a relacao entre a descricao dos PRs e o numero de revisoes realizadas?
- **RQ08:** Qual a relacao entre as interacoes nos PRs e o numero de revisoes realizadas?

### 1.4 Hipoteses

**Dimensao A (Feedback Final):**

- **H1:** PRs menores (menos arquivos, menos adicoes/remocoes) tendem a ser aceitos mais frequentemente, pois mudancas menores sao mais faceis de revisar e menos propensas a controversia.
- **H2:** PRs com menor tempo de analise tendem a ser aceitos, pois revisoes prolongadas podem indicar problemas ou falta de consenso.
- **H3:** PRs com descricoes mais detalhadas tendem a ser aceitos, pois facilitam a compreensao do revisor e demonstram maior cuidado do contribuidor.
- **H4:** PRs com mais interacoes (participantes e comentarios) tendem a ser rejeitados, pois maior discussao pode indicar controversia ou necessidade de ajustes significativos.

**Dimensao B (Numero de Revisoes):**

- **H5:** PRs maiores recebem mais revisoes, pois exigem mais atencao e esforco dos revisores.
- **H6:** PRs com maior tempo de analise recebem mais revisoes, pois ficam disponiveis por mais tempo para revisores adicionais.
- **H7:** PRs com descricoes mais detalhadas recebem mais revisoes, pois atraem mais atencao e facilitam o processo de revisao.
- **H8:** PRs com mais interacoes recebem mais revisoes, refletindo maior engajamento da comunidade.

### 1.5 Objetivos

**Objetivo Principal:** Analisar a atividade de code review em repositorios populares do GitHub, identificando variaveis que influenciam no merge de um PR.

**Objetivos Especificos:**
- Coletar e consolidar um dataset de PRs dos 200 repositorios mais populares do GitHub com pelo menos 100 PRs (MERGED + CLOSED).
- Filtrar PRs que tenham passado por code review (status MERGED ou CLOSED, pelo menos 1 revisao, tempo de revisao superior a 1 hora).
- Calcular correlacoes de Spearman entre as metricas definidas e as duas dimensoes (feedback final e numero de revisoes).
- Aplicar o teste Mann-Whitney U para verificar diferencas significativas entre PRs MERGED e CLOSED.

---

## 2. Metodologia

### 2.1 Passo a Passo do Experimento

1. **Selecao dos repositorios:** Os 200 repositórios mais populares do GitHub (por numero de stars) que possuam pelo menos 100 PRs (MERGED + CLOSED) foram selecionados.
2. **Coleta dos dados:** Utilizou-se a GitHub GraphQL API com paginacao por cursor, coletando para cada PR: estado, datas de criacao e fechamento/merge, metricas de tamanho (arquivos alterados, adicoes, remocoes), descricao, interacoes (participantes, comentarios) e numero de revisoes.
3. **Filtragem:** Aplicaram-se os filtros definidos na metodologia: (a) status MERGED ou CLOSED; (b) pelo menos 1 revisao (review_count >= 1); (c) tempo de revisao superior a 1 hora (diferenca entre criacao e merge/close > 1h). Esto removel PRs revisados automaticamente por bots ou ferramentas de CI/CD.
4. **Calculo das metricas:** Para cada PR filtrado, foram calculadas as metricas definidas na Seção 2.5.
5. **Analise de correlacao:** Calculou-se a correlacao de Spearman entre cada metrica e as duas dimensoes (feedback final e numero de revisoes). O teste de Spearman foi escolhido por ser nao-parametrico e adequado para dados com distribuicao nao normal, que e o caso tipico de metricas de software (distribuicoes fortemente assimetricas com muitos outliers).
6. **Teste Mann-Whitney U:** Aplicado para verificar diferencas significativas entre as medianas dos grupos MERGED e CLOSED.
7. **Visualizacao:** Geraram-se graficos boxplot, barras e histogramas para sumarizar os resultados.
8. **Discussao:** Confrontaram-se as hipoteses com os resultados obtidos.

### 2.2 Decisoes

- **GitHub GraphQL API** em vez da REST API: uma unica query GraphQL retorna dados de multiplos PRs incluindo revisoes e participantes, reduzindo drasticamente o numero de requisicoes necessarias (de ~100 requisicoes REST por pagina para 1 query GraphQL).
- **Rotacao de 4 tokens de autenticacao:** para maximizar a taxa de requisicoes (20.000/h com autenticacao vs 60/h sem).
- **Page size adaptativo:** 25 para repos normais, 10 para repos com 30.000+ PRs (evitando timeout na API GraphQL).
- **Exclusao de ruanyf/weekly:** todos os PRs desse repositorio possuem review_count = 0, nao satisfazendo o criterio de pelo menos 1 revisao.
- **Correlacao de Spearman (escolha justificada):** As metricas de software (tamanho de PR, tempo de revisao, etc.) tipicamente nao seguem distribuicao normal — apresentam forte assimetria positiva e valores atipicos extremos. O teste de Spearman e nao-parametrico, baseado em ranks, e portanto robusto a essas caracteristicas, ao contrario do teste de Pearson que assume linearidade e normalidade. Por essa razao, utilizamos Spearman como teste principal e unico de correlacao.
- **Mann-Whitney U (complementar):** Teste nao-parametrico para comparar as distribuicoes dos grupos MERGED e CLOSED sem assumir normalidade.

### 2.3 Materiais Utilizados

| Material | Descricao |
|---|---|
| GitHub GraphQL API | Coleta de dados com paginacao por cursor |
| Python 3.13 | requests, scipy, numpy, matplotlib, seaborn, reportlab |
| 4 GitHub Personal Access Tokens | Autenticacao com rate limit ampliado |
| Dataset final | 199 repositórios, 94,768 PRs filtrados |

### 2.4 Metodos Utilizados

**Coleta:** GraphQL API com paginacao por cursor, consultando PRs com estado MERGED ou CLOSED. Para cada PR, coletaram-se as metricas definidas.

**Filtragem:** estado MERGED ou CLOSED + review_count >= 1 + review_time_hours > 1. Resultando em 94,768 PRs de 199 repositorios.

**Analise estatistica:** Correlacao de Spearman (rho) para avaliar relacoes monotonicas entre variaveis. Teste Mann-Whitney U para diferencas entre grupos MERGED e CLOSED. Nivel de significancia alfa = 0,05.

### 2.5 Metricas e suas Unidades

| Metrica | Unidade | Descricao |
|---|---|---|
| Arquivos alterados | contagem | Numero de arquivos modificados no PR |
| Adicoes | linhas | Total de linhas adicionadas |
| Remocoes | linhas | Total de linhas removidas |
| Tempo de revisao | horas | Intervalo entre criacao e merge/fechamento do PR |
| Tamanho da descricao | caracteres | Numero de caracteres do corpo da descricao |
| Participantes | contagem | Numero de participantes no PR |
| Comentarios | contagem | Numero de comentarios (gerais + de revisao) |
| Revisoes | contagem | Numero de revisoes formais do PR |

---

## 3. Visualizacao dos Resultados

### 3.1 Resumo do Dataset

| Indicador | Valor |
|---|---|
| Total de PRs analisados | 94,768 |
| Repositorios | 199 |
| PRs MERGED | 74,467 (78.6%) |
| PRs CLOSED | 20,301 (21.4%) |

### 3.2 Estimativas descritivas (valores medianos)

A seguir, apresentam-se os valores medianos obtidos em todos os PRs do dataset:

| Metrica | Mediana | Media | Desvio Padrao |
|---|---|---|---|
| Arq. alterados | 2.00 | 14.61 | 344.74 |
| Adicoes | 13.00 | 1286.99 | 73065.61 |
| Remocoes | 2.00 | 390.67 | 10872.22 |
| Tempo rev. (h) | 45.21 | 799.56 | 3591.55 |
| Tam. descricao | 662.00 | 1066.57 | 1796.72 |
| Participantes | 2.00 | 2.71 | 2.53 |
| Comentarios | 1.00 | 2.43 | 4.45 |
| Revisoes | 2.00 | 3.29 | 8.10 |

### 3.3 Comparacao de Medianas: MERGED vs CLOSED

| Metrica | MERGED (mediana) | CLOSED (mediana) | Razao |
|---|---|---|---|
| Arq. alterados | 2.00 | 1.00 | 2.00x |
| Adicoes | 15.00 | 6.00 | 2.50x |
| Remocoes | 3.00 | 0.00 | inf |
| Tempo rev. (h) | 33.20 | 170.13 | 0.20x |
| Tam. descricao | 619.00 | 839.00 | 0.74x |
| Participantes | 2.00 | 2.00 | 1.00x |
| Comentarios | 1.00 | 1.00 | 1.00x |
| Revisoes | 2.00 | 1.00 | 2.00x |

### 3.4 Correlacoes de Spearman — Dimensao A (Feedback Final)

| RQ | Metrica | Spearman rho | p-valor | Sig. |
|---|---|---|---|---|
| RQ01 | Arq. alterados | +0.1461 | 0.00e+00 | *** |
| RQ01 | Adicoes | +0.0928 | 2.16e-180 | *** |
| RQ01 | Remocoes | +0.1722 | 0.00e+00 | *** |
| RQ02 | Tempo rev. | -0.2378 | 0.00e+00 | *** |
| RQ03 | Tam. descricao | -0.0735 | 8.94e-114 | *** |
| RQ04 | Participantes | +0.0733 | 6.61e-113 | *** |
| RQ04 | Comentarios | -0.0122 | 1.65e-04 | *** |

### 3.5 Correlacoes de Spearman — Dimensao B (Numero de Revisoes)

| RQ | Metrica | Spearman rho | p-valor | Sig. |
|---|---|---|---|---|
| RQ05 | Arq. alterados | +0.2111 | 0.00e+00 | *** |
| RQ05 | Adicoes | +0.2523 | 0.00e+00 | *** |
| RQ05 | Remocoes | +0.1624 | 0.00e+00 | *** |
| RQ06 | Tempo rev. | +0.1804 | 0.00e+00 | *** |
| RQ07 | Tam. descricao | +0.1556 | 0.00e+00 | *** |
| RQ08 | Participantes | +0.3367 | 0.00e+00 | *** |
| RQ08 | Comentarios | +0.2492 | 0.00e+00 | *** |

### 3.6 Teste Mann-Whitney U (MERGED vs CLOSED)

| Metrica | Estatistica U | p-valor | Significativo? |
|---|---|---|---|
| Arq. alterados | 908439255.0 | 0.00e+00 | Sim |
| Adicoes | 854164049.0 | 1.26e-179 | Sim |
| Remocoes | 935500816.0 | 0.00e+00 | Sim |
| Tempo rev. (h) | 502943779.5 | 0.00e+00 | Sim |
| Tam. descricao | 677662091.5 | 1.79e-113 | Sim |
| Participantes | 831321293.0 | 1.31e-112 | Sim |
| Comentarios | 743332774.5 | 1.65e-04 | Sim |
| Revisoes | 837160493.0 | 6.14e-139 | Sim |

### 3.7 Graficos

![Figura 1: Mapa de calor das correlacoes de Spearman](output/fig_heatmap.png)

![Figura 2: Boxplots de tamanho — MERGED vs CLOSED (RQ01)](output/fig_rq01.png)

![Figura 3: Boxplot de tempo de revisao — MERGED vs CLOSED (RQ02)](output/fig_rq02.png)

![Figura 4: Boxplot de descricao — MERGED vs CLOSED (RQ03)](output/fig_rq03.png)

![Figura 5: Boxplots de interacoes — MERGED vs CLOSED (RQ04)](output/fig_rq04.png)

![Figura 6: Correlacoes da Dimensao A — barras horizontais](output/fig_dim_a.png)

![Figura 7: Correlacoes da Dimensao B — barras horizontais](output/fig_dim_b.png)

![Figura 8: Medianas MERGED vs CLOSED](output/fig_medians.png)

![Figura 9: Distribuicao do numero de revisoes](output/fig_rev_dist.png)

---

## 4. Discussao dos Resultados

### 4.1 Confrontacao com as Questoes-Pesquisa

#### RQ01: Tamanho vs Feedback Final

As correlacoes de Spearman mostraram que remocoes (rho=0,172), arquivos alterados (rho=0,146) e adicoes (rho=0,093) apresentam correlacao positiva fraca com o merge. Isso **contradiz a hipotese H1**, que esperava correlacao negativa. Analisando as medianas, PRs MERGED possuem mais adicoes (15 vs 6) e mais remocoes (3 vs 0) que os CLOSED. A correlacao positiva pode indicar que PRs de manutencao (que envolvem remocao de codigo obsoleto) tendem a ser aceitos, ou que contribuidores mais experientes — cujos PRs sao mais propensos a serem aceitos — tendem a submeter mudancas maiores. O teste Mann-Whitney U confirma diferenca significativa (p<0,001) para as tres metricas de tamanho.

#### RQ02: Tempo de Revisao vs Feedback Final

Esta foi a correlacao mais forte encontrada na Dimensao A: **rho=-0,238** (p<0,001), **confirmando a hipotese H2**. A mediana de tempo dos PRs MERGED e de 33 horas, enquanto a dos CLOSED e de 170 horas — uma diferenca de mais de 5 vezes. Isso indica claramente que PRs que demoram mais para serem revisados tendem a nao ser aceitos, possivelmente porque indicam controversia, falta de interesse dos mantenedores ou problemas nao resolvidos.

#### RQ03: Descricao vs Feedback Final

A correlacao de Spearman foi rho=-0,074 (p<0,001), **contrariando a hipotese H3**. Embora estatisticamente significativa, a correlacao e muito fraca na pratica. Curiosamente, PRs CLOSED possuem descricoes maiores (mediana 839 vs 619 caracteres), o que pode indicar que descricoes longas sao tentativas de justificar contribuicoes problematicas, ou que PRs rejeitados geram mais discussoes na descricao.

#### RQ04: Interacoes vs Feedback Final

Participantes apresentaram correlacao positiva fraca (rho=+0,073, p<0,001) e comentarios correlacao negativa fraca (rho=-0,012, p<0,001). **A hipotese H4 nao se confirma plenamente**: mais participantes nao necessariamente indicam controversia — podem indicar maior engajamento construtivo. O efeito pratico dessas correlacoes e minimo, com medianas identicas entre os grupos (participantes: 2 vs 2; comentarios: 1 vs 1).

#### RQ05: Tamanho vs Numero de Revisoes

Correlacoes moderadas: adicoes (rho=0,252), arquivos alterados (rho=0,211) e remocoes (rho=0,162), todas com p<0,001. **Confirma a hipotese H5**: PRs maiores recebem mais revisoes, pois exigem mais atencao e esforco dos revisores. Adicoes e a metrica de tamanho mais correlacionada com revisoes.

#### RQ06: Tempo de Revisao vs Numero de Revisoes

Correlacao rho=0,180 (p<0,001). **Confirma parcialmente a hipotese H6**: PRs que ficam mais tempo abertos tendem a acumular mais revisoes. No entanto, a correlacao do tempo com revisoes e mais fraca que a do tamanho, indicando que a complexidade do PR e mais determinante que o tempo disponivel.

#### RQ07: Descricao vs Numero de Revisoes

Correlacao rho=0,156 (p<0,001). **Confirma parcialmente a hipotese H7**: descricoes mais detalhadas estao associadas a mais revisoes. Isso pode ocorrer porque descricoes claras facilitam o trabalho dos revisores, incentivando-os a realizar revisoes, ou porque PRs mais complexos (que naturalmente exigem mais revisoes) tendem a ter descricoes mais longas.

#### RQ08: Interacoes vs Numero de Revisoes

**As correlacoes mais fortes do estudo**: participantes (rho=0,337) e comentarios (rho=0,249), ambas com p<0,001. **Confirma a hipotese H8**: PRs com mais interacoes recebem mais revisoes. A correlacao entre participantes e revisoes e a mais forte de todo o estudo, indicando que o engajamento da comunidade esta intimamente ligado ao processo de revisao formal. Isso e consistente com a natureza social do code review: mais pessoas envolvidas significa mais revisores potenciais.

### 4.2 Insights

- O **tempo de revisao** e o melhor preditor individual de aceitacao (rho=-0,238). PRs aceitos sao revisados ~5x mais rapido.
- O **tamanho (adicoes)** e o melhor preditor do numero de revisoes (rho=0,252). PRs maiores naturalmente atraem mais revisores.
- O **engajamento de participantes** e o fator mais correlacionado com revisoes (rho=0,337), evidenciando que revisao e um fenomeno social.
- Todas as correlacoes sao **estatisticamente significativas** (p<0,001), mas a maioria e **fraca** (|rho|<0,3), indicando que fatores isolados tem poder preditivo limitado.
- A hipotese de que PRs menores sao mais aceitos **nao se confirma**: a correlacao entre tamanho e merge e positiva (embora fraca).

### 4.3 Graficos

As Figuras 1-9 (Secao 3.7) apresentam as visualizacoes. O mapa de calor (Figura 1) mostra as correlacoes entre todas as metricas. Os boxplots (Figuras 2-5) permitem comparar visualmente as distribuicoes MERGED vs CLOSED com clipping no percentil 97 para melhor legibilidade. As Figuras 6-7 apresentam as correlacoes por dimensao em formato de barras, facilitando a comparacao da magnitude. A Figura 8 compara medianas. A Figura 9 mostra a distribuicao de revisoes.

### 4.4 Comparacoes

A escolha do **teste de Spearman** (em vez de Pearson) justifica-se porque: (1) as metricas de software nao seguem distribuicao normal — possuem forte assimetria positiva e valores atipicos extremos (e.g., PRs com milhoes de adicoes); (2) Spearman baseia-se em ranks, sendo robusto a outliers; (3) a relacao entre as variaveis pode ser monotônica mas nao necessariamente linear. O teste **Mann-Whitney U** complementa a analise, confirmando que as diferencas entre MERGED e CLOSED sao significativas para quase todas as metricas.

### 4.5 Estatisticas

O dataset contem **94.768** PRs de **199** repositorios. A taxa de aceitacao de **78,6%** e consistente com a literatura (Gousios et al., 2015 reportam 70-80% em projetos open source). A mediana global de tempo de revisao e de **45,2** horas. A mediana de revisoes por PR e de **2**.

---

## 5. Conclusao

### 5.1 Tomada de Decisao

Com base nos resultados, concluimos que:
- O **tempo de revisao** e o fator mais influente na aceitacao (rho=-0,238). Desenvolvedores devem buscar feedback rapido para aumentar as chances de merge.
- PRs maiores recebem mais revisoes, mas nao necessariamente sao mais aceitos. Recomenda-se subdividir contribuicoes grandes em PRs menores e focados.
- A **descricao** tem influencia limitada no resultado, mas afeta o numero de revisoes. Descricoes claras e concisas sao preferiveis a textos excessivamente longos.
- O **engajamento** (participantes e comentarios) esta fortemente ligado a revisoes, mas nao determina diretamente a aceitacao.

### 5.2 Sugestoes Futuras

- Investigar modelos de predicao multivariados (regressao logistica, random forest) combinando multiplas metricas para melhor poder preditivo.
- Analise de sentimento dos comentarios para distinguir discussoes construtivas de controversias.
- Incluir metricas de CI/CD (build status, testes automatizados) como fatores adicionais.
- Segmentar a analise por linguagem de programacao ou dominio do repositorio.
- Realizar analise temporal para verificar se as correlacoes mudam ao longo do tempo.

### 5.3 Resultado Conclusivo

A analise de **94.768** PRs de **199** repositorios populares no GitHub revelou que o tempo de revisao e o melhor preditor individual de aceitacao (rho=-0,238): PRs aceitos sao revisados ~5x mais rapido que os rejeitados. PRs maiores recebem mais revisoes (adicoes: rho=0,252), e o engajamento dos participantes e o fator mais correlacionado com revisoes (rho=0,337). Todas as correlacoes sao estatisticamente significativas, mas geralmente fracas, evidenciando que a decisao de aceitacao e multifatorial e nao pode ser prevista por uma unica variavel.

### 5.4 Confrontacao com Trabalhos Cientificos

- **Ortu et al. (2020)** — "How do you propose your code changes?" — encontraram correlacoes fracas a moderadas entre metricas afetivas e aceitacao, corroborando nossos resultados de que fatores isolados tem poder preditivo limitado.
- **Zhang et al. (2022)** — "Pull request decisions explained" — demonstraram que o tempo de processamento e um dos fatores mais influentes na decisao de merge, o que corrobora nosso achado de rho=-0,238 para tempo de revisao vs feedback final.
- **Gousios et al. (2015)** — identificaram taxa de aceitacao de 70-80% em projetos open source, consistente com nossa taxa de 78,6%.
- **Yu et al. (2016)** — "Reviewer recommendation for pull-requests in GitHub" — encontraram que o numero de revisores esta correlacionado com o resultado do PR, semelhante a nossa correlacao entre participantes e revisoes (rho=0,337).

Nossos resultados **contestam a hipotese comum** de que PRs menores sao mais aceitos: encontramos correlacao positiva (embora fraca) entre tamanho e merge, sugerindo que a natureza da contribuicao (manutencao vs novo codigo) pode ser mais determinante que o tamanho em si.

---

## Referencias

1. Ortu, M., Destefanis, G., Graziotin, D., Marchesi, M., & Tonelli, R. (2020). How do you propose your code changes? *IEEE Access*, 8, 5323-5337.
2. Zhang, X., Yu, Y., Gousios, G., et al. (2022). Pull request decisions explained: An empirical overview. *IEEE TSE*, 48(8), 3017-3034.
3. Gousios, G., Zaidman, A., Storey, M. A., & van Deursen, A. (2015). Work practices and challenges in pull-based development. *IEEE TSE*, 41(12), 1065-1082.
4. Yu, Y., Wang, H., Yin, G., & Wang, T. (2016). Reviewer recommendation for pull-requests in GitHub. *IST*, 74, 204-218.

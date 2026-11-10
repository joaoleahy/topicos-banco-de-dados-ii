# Roteiro: NorBERTo: A ModernBERT Model Trained for Portuguese with 331B Tokens Corpus

Apresentação de 10 minutos[cite: 40]. João Victor: slides 1 a 4 (3min20); Lucas Rapozo: 5 a 7 (3min40); Antoniel Magalhães: 8 a 10 (3min)[cite: 40]. A referência final é para consulta[cite: 40]. A numeração abaixo conta a capa; o rodapé do tema conta apenas os nove slides de conteúdo[cite: 40].

Os tempos são metas para ensaio, incluindo transições[cite: 40]. As falas desenvolvem os argumentos dos slides; use as âncoras para explicar sem ler[cite: 40]. As notas de aprofundamento ao final ficam fora dos 10 minutos[cite: 40].

| Slide | Intervalo | Responsável | Tema |
|---|---|---|---|
| 1 | 0:00–0:20 | João Victor | Abertura |
| 2 | 0:20–1:15 | João Victor | Motivação e Right-Sized AI |
| 3 | 1:15–2:20 | João Victor | O Corpus Aurora-PT (331B) |
| 4 | 2:20–3:20 | João Victor | Curadoria e Qualidade Lexical |
| 5 | 3:20–4:25 | Lucas Rapozo | Arquitetura ModernBERT |
| 6 | 4:25–5:50 | Lucas Rapozo | Treinamento em 3 Fases |
| 7 | 5:50–7:00 | Lucas Rapozo | Resultados no ASSIN 2 |
| 8 | 7:00–7:55 | Antoniel Magalhães | Resultados no PLUE |
| 9 | 7:55–9:00 | Antoniel Magalhães | Classificação e Redes Sociais |
| 10 | 9:00–10:00 | Antoniel Magalhães | Conclusão e Limites |
| 11 | Consulta | Equipe | Referência |

## 1. Abertura
Somos João Victor, Lucas Rapozo e Antoniel Magalhães[cite: 40]. Vamos apresentar o artigo *NorBERTo: A ModernBERT Model Trained for Portuguese with 331 Billion Tokens Corpus*, de Enzo Silva e colaboradores do Itaú Unibanco e do ICTi, publicado no PROPOR 2026, aqui em Salvador[cite: 51].

## 2. Motivação: LLMs generativos versus Encoders dedicados
Nos últimos anos, os grandes modelos generativos baseados em *decoder* dominaram as atenções pela capacidade de resolver tarefas via *prompting*[cite: 51, 53]. Porém, em ambientes reais de produção, eles trazem problemas críticos: alto custo financeiro e computacional, latência elevada, riscos de governança em dados sensíveis e alucinações[cite: 51, 53].

Em tarefas discriminativas — como classificação, busca semântica, ranqueamento e recuperação para RAG — modelos menores baseados apenas em *encoder*, como a família BERT, continuam empatando ou superando LLMs com uma fração mínima do custo[cite: 51, 53]. Os autores chamam essa visão de *Right-Sized AI*: usar um modelo do tamanho certo para a tarefa certa[cite: 53, 58].

O problema é que o ecossistema de *encoders* em português parou no tempo em dois aspectos[cite: 52]. Primeiro, tamanho de dados: o clássico BERTimbau foi treinado em apenas 2,68 bilhões de tokens do corpus brWaC[cite: 52]. Segundo, arquitetura: faltavam modelos nacionais com atenção eficiente e janela de contexto longa, como o recente ModernBERT[cite: 52].

Âncoras: custo/latência dos LLMs -> Right-Sized AI -> defasagem de dados (2,68B) e arquitetura no português.

## 3. Contribuição 1: O corpus monolíngue Aurora-PT
Para resolver o gargalo de dados, a primeira grande entrega do artigo é o **Aurora-PT**, atualmente o maior corpus monolíngue aberto para o português[cite: 51, 54].

A tabela mostra o salto de escala histórica[cite: 53, 54]. Enquanto o Carolina tem 11 gigabytes e o brWaC tem 25 gigabytes, iniciativas recentes para modelos generativos como o Aroeira e o GigaVerbo chegaram a 100 e 780 gigabytes[cite: 54]. O Aurora-PT atinge **873 gigabytes** distribuídos em **275 milhões de documentos**[cite: 54].

Diferente de projetos que extraem dados brutos diretamente do Common Crawl do zero, os autores agregaram nove bases já existentes: FineWeb v2 — que teve a maior taxa de retenção, mantendo 90,8% dos textos —, mC4, HPLT 2.0, MOSCAR, Wikipédia, Aroeira, Blogset-br, Aya e CC100[cite: 54]. Ao final da limpeza, o corpus soma **331 bilhões de tokens** quando medido pelo tokenizador do GPT-2, ou **226 bilhões de tokens** usando o tokenizador próprio treinado para o NorBERTo[cite: 51, 54].

Âncoras: evolução 25 GB para 873 GB -> 9 fontes combinadas -> 331B tokens (GPT-2) vs. 226B (próprio).

## 4. Curadoria de dados e avaliação intrínseca do Aurora-PT
Para garantir que tamanho não signifique lixo, o texto passou por uma esteira rigorosa na biblioteca DataTrove, inspirada no FineWeb v1[cite: 54]. Primeiro, aplicaram identificação de idioma com o GlotLID exigindo confiança mínima de 0,799 para português[cite: 54]. Depois, fizeram desduplicação via MinHash com 112 hashes em 14 *buckets*[cite: 54]. Por fim, aplicaram os filtros heurísticos do C4 e do FineWeb, descartando linhas com menos de três palavras, chaves de código, avisos de *cookies* ou *Javascript* e documentos sem pontuação adequada[cite: 54].

Os autores avaliaram a qualidade linguística do corpus resultante[cite: 55]. Na diversidade lexical, tanto o *Type-Token Ratio* mediano de 0,567 quanto a métrica probabilística HD-D ficaram estáveis no centro das distribuições dos demais corpora, mostrando que o tamanho massivo não inflou artificialmente o ruído[cite: 55]. A proporção de palavras de conteúdo (0,465) e de *stopwords* (0,350) também seguiu o padrão natural da língua[cite: 56].

Além disso, o Aurora-PT obteve a menor perplexidade no modelo mGPT: 20.438, menos da metade do GigaVerbo[cite: 56]. Os próprios autores fazem uma ressalva importante aqui: como o mGPT é pré-treinado na web, parte dos documentos pode ter sido vista por ele, o que exige cautela ao interpretar a perplexidade isoladamente[cite: 57]. Passo a palavra ao Lucas para detalhar o modelo NorBERTo.

Âncoras: GlotLID + MinHash + filtros C4/FineWeb -> estabilidade lexical (TTR/HD-D) -> menor perplexidade com ressalva de contaminação -> Lucas.

## 5. Contribuição 2: Arquitetura do NorBERTo (ModernBERT)
Com o corpus pronto, os autores treinaram o **NorBERTo**, adaptando a arquitetura do ModernBERT para o português em duas versões: **base**, com cerca de 150 milhões de parâmetros e 22 camadas, e **large**, com 395 milhões de parâmetros e 28 camadas[cite: 54, 55]. Ambas compartilham um vocabulário próprio de 50.368 tokens aprendido sobre o Aurora-PT[cite: 54, 55].

O que torna essa arquitetura moderna em relação ao BERT tradicional de 2018?[cite: 51, 53] Primeiro, a janela de contexto salta de 512 para **8.192 tokens**, permitindo processar documentos inteiros sem truncamento[cite: 53, 54]. Isso é viabilizado pelo uso de *Rotary Positional Embeddings* (RoPE) e por um padrão de atenção alternada: apenas a primeira camada e uma a cada três camadas calculam atenção global sobre todos os tokens; as demais usam atenção local restrita a uma janela deslizante de 128 tokens, economizando memória e processamento[cite: 54, 55].

Além disso, o modelo utiliza camadas *feed-forward* com ativação GeGLU, projeções lineares sem viés (*bias-free*), e técnicas de *sequence packing* e *unpadding* aceleradas por FlashAttention v2, evitando desperdiçar cálculo em tokens vazios de preenchimento[cite: 54, 55].

Âncoras: versões 150M e 395M -> salto para 8.192 tokens -> RoPE + atenção alternada (global a cada 3 vs. local 128) -> GeGLU e unpadding.

## 6. Treinamento em três fases para extensão de contexto
O pré-treinamento utilizou o objetivo de *Masked Language Modeling* (MLM) mascarando **30% dos tokens** — o dobro dos 15% clássicos do BERT — sobre os 226 bilhões de tokens do Aurora-PT[cite: 55].

Para alcançar a janela de 8.192 tokens com eficiência, o treinamento foi dividido em três fases[cite: 55, 56]. Na Fase 1, 85% dos tokens (195 bilhões) são processados com contexto máximo de 1.024 e *batch size* elevado[cite: 55, 56]. Na Fase 2, de extensão de contexto, 12,5% dos tokens (29 bilhões) expandem a janela para 8.192 tokens com taxa de aprendizado constante menor[cite: 55, 56]. Na Fase 3, os 2,5% finais (6 bilhões de tokens) mantêm a janela de 8.192 aplicando decaimento *1-sqrt* na taxa de aprendizado[cite: 55, 56].

Como textos longos são mais raros, todos os documentos com mais de 1.024 tokens foram reservados exclusivamente para as fases 2 e 3[cite: 55]. Um detalhe técnico interessante é que os pesos do NorBERTo-large foram inicializados via *tiling* a partir dos pesos do modelo base[cite: 56]. Todo o treino durou cerca de 3 dias para uma época em 8 GPUs NVIDIA H100[cite: 55].

Âncoras: MLM 30% -> Fase 1 (195B em 1024) -> Fase 2 e 3 (29B + 6B em 8192) -> reserva de textos longos -> 3 dias em 8 H100.

## 7. Evidência 1: Inferência e Similaridade no ASSIN 2
Passando aos resultados experimentais, a primeira avaliação utiliza o benchmark **ASSIN 2**, composto por cerca de 10 mil pares de sentenças em português, divididos em duas tarefas: inferência textual (*Entailment*, medida por F1) e similaridade semântica (medida pela correlação de Pearson de 0 a 5)[cite: 57].

Na tarefa de inferência textual, o NorBERTo-large atinge o melhor resultado entre todos os modelos avaliados, com **90,38% de F1** na variante de classificação de sequência e **90,33%** como *cross-encoder*, superando o BERTimbau-large (88,91%), o Albertina-base (87,40%) e o multilíngue mmBERT (89,63%)[cite: 57, 58].

Porém, na tarefa de similaridade semântica, ocorre o oposto: o BERTimbau-large lidera com correlação de **0,852**, enquanto a melhor versão do NorBERTo alcança **0,766**[cite: 57, 58]. Os autores explicam essa diferença pela estratégia de inicialização: enquanto o NorBERTo foi treinado totalmente do zero (*from scratch*), o BERTimbau continuou o pré-treinamento a partir de um checkpoint já treinado em inglês, herdando alinhamentos semânticos finos daquele modelo base[cite: 57]. O Antoniel agora mostrará os resultados no PLUE e nas demais tarefas.

Âncoras: ASSIN 2 -> vitória em Entailment (90,4% F1) -> queda em Similaridade (0,766 vs. 0,852) -> treino do zero vs. checkpoint herdado do inglês -> Antoniel.

## 8. Evidência 2: Estado da Arte no Benchmark PLUE
A segunda avaliação utiliza o **PLUE**, versão traduzida do benchmark GLUE para o português, focando em três tarefas: detecção de paráfrases (MRPC), reconhecimento de inferência textual (RTE) e resolução de correferência e inferência (WNLI)[cite: 57].

Aqui, o **NorBERTo-large** estabelece o novo estado da arte nas três frentes[cite: 57, 58]. No MRPC, ele atinge **91,91%**, abrindo 3,2 pontos percentuais de vantagem sobre o BERTimbau-large (88,73%)[cite: 57, 58]. No RTE, alcança **76,89%** contra 75,45% do BERTimbau-large; e no WNLI chega a **57,74%**, também 1,4 ponto acima dos concorrentes[cite: 57, 58].

Mais impressionante ainda é o desempenho de eficiência do **NorBERTo-base**: com apenas 150 milhões de parâmetros, ele consegue superar o BERTimbau-large, que tem 340 milhões de parâmetros, tanto na detecção de paráfrases (89,26% contra 88,73%) quanto no WNLI (57,74% contra 56,34%)[cite: 58].

Âncoras: PLUE (MRPC, RTE, WNLI) -> liderança do Large nas 3 tarefas (+3,2 pts no MRPC) -> Base de 150M supera BERTimbau-large de 340M.

## 9. Evidência 3: Tarefas de Classificação e Redes Sociais
No Apêndice A, os autores realizam uma otimização sistemática de hiperparâmetros com o framework Optuna em quatro conjuntos brasileiros de classificação: análise de sentimento no TweetSent-BR, detecção binária de ódio no Hate-BR, discurso de ódio multiclasse no TuPy-E e detecção de notícias falsas no FakeRecogna 2.0[cite: 61].

Os resultados mostram que modelos maiores tendem a levar vantagem, mas o NorBERTo-large se mantém extremamente competitivo contra arquiteturas multilíngues gigantes[cite: 61]. Ele praticamente empata com o líder XLM-RoBERTa-large no FakeRecogna 2.0 (**98,3% contra 98,4%**) e no Hate-BR (**92,1% contra 93,0%**), superando diversas outras variantes monolíngues e multilíngues[cite: 61].

Por outro lado, o XLM-RoBERTa-large lidera no TweetSent-BR (79,5%) e o BERTimbau vence no TuPy-E (90,8%)[cite: 61]. Isso reforça a conclusão dos autores de que nenhum modelo único vence universalmente em todos os cenários, defendendo uma visão de "caixa de ferramentas" onde o NorBERTo entra como uma peça moderna e eficiente[cite: 58].

Âncoras: HPO com Optuna -> empate técnico em Fake News (98,3%) e Hate-BR (92,1%) -> liderança dividida em tweets -> abordagem de caixa de ferramentas.

## 10. Conclusão e limites
Para concluir, o artigo entrega dois recursos abertos de grande valor para o PLN em português: o corpus Aurora-PT, com 331 bilhões de tokens limpos e diversos, e o encoder NorBERTo, que atualiza a arquitetura BERT nacional para suportar até 8.192 tokens com alta eficiência computacional[cite: 51, 54, 58].

Como análise crítica e limites apontados no próprio artigo, destacamos três pontos[cite: 57, 58, 59]. Primeiro, a escala de exposição no pré-treino: embora 226 bilhões de tokens seja um recorde para encoders em português, o ModernBERT original em inglês foi treinado na casa dos **trilhões de tokens**[cite: 58, 59]. Essa diferença de exposição, somada ao treino do zero sem checkpoint prévio, ajuda a explicar a desvantagem em similaridade semântica fina no ASSIN 2[cite: 57, 59]. Segundo, os autores sugerem que aprendizado contrastivo futuro pode corrigir essa lacuna de similaridade[cite: 58]. E terceiro, apesar de o modelo suportar 8.192 tokens, os benchmarks avaliados no artigo (como ASSIN 2, PLUE e tweets) são compostos por textos curtos, deixando a validação prática em documentos longos e pipelines de RAG para trabalhos futuros[cite: 57, 58].

Âncoras: entregas abertas (Aurora-PT + NorBERTo) -> 226B vs. trilhões do ModernBERT original -> lacuna em similaridade pede aprendizado contrastivo -> falta avaliar benchmarks de contexto longo.

## Preparação para perguntas, fora do tempo principal
- **Por que o corpus tem 331 bilhões de tokens no título, mas o modelo treinou com 226 bilhões?** A contagem de tokens depende diretamente do tokenizador utilizado[cite: 54]. Quando o Aurora-PT é medido com o tokenizador padrão do GPT-2 (usado como régua comum de comparação na literatura), ele possui ~330–331 bilhões de tokens[cite: 51, 54]. Porém, como os autores treinaram um tokenizador específico para o português (com vocabulário de 50.368 tokens), as palavras do português são menos fragmentadas, comprimindo o mesmo texto para 226 bilhões de tokens[cite: 54, 55].
- **Como funciona a atenção alternada do ModernBERT / NorBERTo?** Calcular atenção completa ($O(n^2)$) em 8.192 tokens em todas as camadas seria muito caro[cite: 54]. Por isso, o modelo usa atenção global completa apenas na camada 1 e a cada 3 camadas; todas as camadas intermediárias calculam atenção local apenas dentro de uma janela deslizante de 128 tokens, combinando alcance global com velocidade local[cite: 54, 55].
- **O que é RoPE theta ($\theta$) diferente para atenção global e local?** O *Rotary Positional Embedding* usa uma frequência base $\theta$ para codificar posições relativas[cite: 54, 55]. Na atenção local (janela curta de 128 tokens), o NorBERTo usa $\theta = 10.000$, enquanto nas camadas de atenção global (que precisam enxergar até 8.192 tokens) usa $\theta = 160.000$, permitindo extrapolar distâncias longas[cite: 55].
- **O que significa inicializar o modelo Large via *tiling* do Base?** Em vez de inicializar os 395 milhões de parâmetros do NorBERTo-large do zero absoluto, os autores usam a técnica de *tiling* (ladrilhamento/expansão dos pesos já aprendidos ou estruturados no modelo Base) para preencher as matrizes maiores do Large, acelerando a convergência no pré-treino[cite: 56].
- **Por que o filtro do CC100 reteve apenas 1,15% dos documentos enquanto o FineWeb v2 reteve 90,83%?** Porque o FineWeb v2 já havia passado por uma esteira moderna de limpeza e desduplicação similar à adotada pelos autores, enquanto o CC100 bruto continha enorme volume de linhas curtas, duplicatas ou ruído que reprovaram nas heurísticas do C4/FineWeb e no MinHash[cite: 54].

## Conferência das fontes
- Slide 2: seções 1, 2.1 e 2.2 (motivação, limites de LLMs, brWaC 2,68B e *right-sized AI*)[cite: 51, 52, 53].
- Slide 3: seções 2.3 e 3.1; Tabela 1 (comparativo de corpora em GB e nº de documentos) e Tabela 2 (retenção das 9 fontes)[cite: 53, 54].
- Slide 4: seções 3.1 e 4.1; Figuras 1 e 2 (TTR 0,567, HD-D, sofisticação) e Tabelas 5 e 6 (densidade lexical 0,465, *stopwords* 0,350 e perplexidade mGPT 20.437,97)[cite: 54, 55, 56, 57].
- Slide 5: seção 3.2 e Tabela 3 (parâmetros Base 150M e Large 395M, vocabulário 50.368, janela local 128, RoPE)[cite: 54, 55].
- Slide 6: seção 3.2 e Tabela 4 (três fases de treino: 195B, 29B e 6B; hiperparâmetros e 8 GPUs H100 por ~3 dias)[cite: 55, 56].
- Slide 7: seção 4.2.1 e Tabela 7 (ASSIN 2: Entailment 0,9038 / 0,9033 e Similaridade 0,766 vs. 0,852 do BERTimbau-large)[cite: 57, 58].
- Slide 8: seção 4.2.2 e Tabela 8 (PLUE: MRPC 0,9191, RTE 0,7689 e WNLI 0,5774)[cite: 57, 58].
- Slide 9: seção 5 e Apêndice A, Tabela 9 (HPO com Optuna em TweetSent-BR, Hate-BR, TuPy-E e FakeRecogna 2.0)[cite: 58, 61].
- Slide 10: seções 4.2.1, 5 e seção *Limitations* (226B tokens vs. trilhões do ModernBERT original)[cite: 57, 58, 59].

Referência: Silva, E. S. N. et al. *NorBERTo: A ModernBERT Model Trained for Portuguese with 331 Billion Tokens Corpus*. PROPOR 2026, Salvador, Brasil, 2026[cite: 51].
# Roteiro de apresentação — 10 minutos

Artigo: Paiola et al. (2025), *The Bode Family of Large Language Models: Investigating the Frontiers of LLMs in Brazilian Portuguese*. DOI: https://doi.org/10.5753/jbcs.2025.5812.

A divisão abaixo é uma sugestão. Os intervalos incluem as transições. O tempo real depende do ensaio; use o texto como guia de fala, sem ler as tabelas célula por célula.

| Slide físico | Intervalo | Responsável | Assunto |
|---|---|---|---|
| 1 | 0:00–0:20 | João Victor | Abertura |
| 2 | 0:20–1:15 | João Victor | Problema e objetivo |
| 3 | 1:15–2:20 | João Victor | Família Bode |
| 4 | 2:20–3:20 | João Victor | Dados e ajuste |
| 5 | 3:20–4:25 | Lucas Rapozo | Avaliação |
| 6 | 4:25–5:50 | Lucas Rapozo | Ganhos |
| 7 | 5:50–7:00 | Lucas Rapozo | Quedas |
| 8 | 7:00–7:55 | Antoniel Magalhães | Exemplo cultural |
| 9 | 7:55–9:00 | Antoniel Magalhães | Limitações |
| 10 | 9:00–10:00 | Antoniel Magalhães | Síntese |
| 11 | Consulta | Equipe | Referência |

## 1 — Abertura

“Somos João Victor, Lucas Rapozo e Antoniel Magalhães. Vamos apresentar uma síntese do artigo de Paiola e colaboradores, publicado em 2025, sobre a família Bode: modelos de linguagem adaptados ao português brasileiro.”

## 2 — Problema e objetivo

“Um modelo de linguagem pode produzir frases em português e, ainda assim, interpretar mal uma expressão, uma ironia ou uma referência cultural. O artigo parte desse problema: boa parte dos recursos usados no treinamento desses modelos se concentra em inglês. Os autores investigam o ajuste fino com instruções em português, aproveitando modelos que já existem. Ajuste fino é uma etapa adicional de treinamento para adaptar o comportamento do modelo. A pergunta que orienta nossa síntese é: quando essa adaptação realmente melhora o desempenho? Veremos que a resposta varia conforme o modelo e a tarefa.”

## 3 — Família Bode

“Bode não é um único modelo treinado do zero. É uma família de adaptações de bases como LLaMA, Gemma, Phi, Mistral e InternLM, entre outras. O artigo cataloga 35 variantes. Esse número inclui formas diferentes de disponibilizar alguns modelos, como adaptadores incorporados aos pesos e arquivos em outros formatos. Portanto, não devemos interpretar as 35 variantes como 35 arquiteturas independentes. O trabalho reúne alternativas de portes diferentes e compara seus resultados em tarefas de português. A contribuição é tanto a disponibilização dos modelos quanto a possibilidade de observar como diferentes escolhas de adaptação se comportam. Mais adiante, vamos comparar cada variante com sua própria base.”

## 4 — Dados e ajuste

“Os dados principais são o Alpaca traduzido, com 52 mil exemplos de instruções, e o UltraAlpaca, que reúne diferentes conjuntos, incluindo conversas, código e matemática. O artigo combina recursos traduzidos e amostras já disponíveis em português. Há três formas principais de ajuste. No ajuste completo, todos os pesos podem ser atualizados. No LoRA, a base fica congelada e o treinamento se concentra em adaptadores menores. No QLoRA, a base também usa uma representação quantizada, que reduz a memória necessária. Essas estratégias tornam a adaptação mais acessível, mas isso não significa que todas produzam o mesmo resultado. Lucas vai mostrar como os autores fizeram a avaliação.”

## 5 — Avaliação

“A avaliação usa nove tarefas do Open PT-LLM Leaderboard. Elas cobrem questões de provas, relações de sentido entre textos, ofensividade, discurso de ódio e sentimento. Não é necessário decorar os nomes: o importante é perceber que os testes medem capacidades diferentes. Os modelos recebem alguns exemplos no prompt, em quantidades definidas para cada tarefa. Isso é diferente do ajuste fino dos pesos. As provas usam acurácia; várias tarefas de classificação usam F1 macro; a similaridade textual usa correlação de Pearson. Os autores apresentam uma média desses resultados para resumir o desempenho, mas essa média combina métricas distintas. A comparação principal é sempre entre a versão adaptada e a base correspondente.”

## 6 — Ganhos

“Selecionamos quatro pares da tabela do artigo para mostrar ganhos de tamanhos diferentes. No Gemma-7B-it, a pontuação passa de 49,61 para 60,60: um aumento de 10,99 pontos no escore agregado. Phi-Bode também melhora em relação ao Phi-2. No Mistral, a configuração que combina QLoRA com UltraAlpaca ganha 4,22 pontos. Já ChatBode-20B chega a 71,68, a maior média entre os Bode apresentados. O ganho sobre sua base, porém, é de apenas 1,09 ponto. Isso mostra uma distinção importante: ter a maior pontuação final não significa ter obtido a maior melhora com a adaptação. Esses números são pontos de uma média de métricas, não uma porcentagem única de acertos, nem um ganho percentual relativo.”

## 7 — Quedas

“Os resultados negativos impedem concluir que ajustar para português sempre ajuda. O LLaMA-3.1-8B-Instruct perde 1,46 ponto com o ajuste completo. O Phi-3-mini perde 5,72. No Gemma-2B com QLoRA e UltraAlpaca, a queda chega a 12,88 pontos. Esses exemplos são configurações específicas; não provam que QLoRA seja sempre ruim ou que um modelo pequeno seja sempre inadequado. Os autores discutem hipóteses como sobreajuste e perda de conhecimento adquirido anteriormente. O estudo não isola uma causa única para todas as quedas. O resultado prático é que precisamos avaliar a combinação de base, dados e método, considerando também a tarefa. Antoniel vai mostrar um exemplo de interpretação e as limitações dessa evidência.”

## 8 — Exemplo cultural

“O artigo analisa a expressão ‘vergonha alheia’. No exemplo apresentado, a base InternLM2 atribui sentimento neutro, enquanto ChatBode identifica o sentimento negativo ligado ao constrangimento. Esse caso ajuda a visualizar o tipo de interpretação que pode melhorar com a adaptação. O significado depende do uso da expressão, não apenas de palavras isoladas. Entretanto, trata-se de um exemplo selecionado pelos autores. Ele ilustra uma diferença entre modelos, mas não permite afirmar que o ChatBode compreende qualquer ironia, variedade regional ou contexto cultural brasileiro.”

## 9 — Limitações

“Destacamos quatro limites. Primeiro, a média geral combina métricas que não são diretamente equivalentes e pode esconder uma queda em determinada tarefa. Segundo, os autores informam que não preservaram todos os registros de treinamento; por isso, apresentam hiperparâmetros representativos, o que limita a reprodução exata de todas as variantes. Terceiro, traduzir dados de origem inglesa pode preservar vieses e deixar escapar referências culturais locais. Por fim, a avaliação cultural adicional usa somente sete questões selecionadas do ENEM. Esse recorte é pequeno para sustentar conclusões amplas sobre domínio cultural. Assim, nossa leitura distingue os resultados medidos das interpretações mais gerais sobre o que os modelos aprenderam.”

## 10 — Síntese

“A contribuição do artigo é reunir modelos adaptados ao português e comparar alternativas em diferentes tarefas. O estudo mostra ganhos relevantes, mas também quedas expressivas. Portanto, o ajuste fino é uma possibilidade de melhoria que precisa ser verificada. Nossa síntese é que a escolha deve considerar a tarefa de interesse e a comparação com a base, em vez de depender apenas da média do ranking. Uma direção futura apontada pelos autores é ampliar os dados de instrução produzidos originalmente em português, reduzindo a dependência de traduções. A família Bode oferece recursos e resultados úteis para investigar essas escolhas, mas não estabelece uma receita universal. Obrigado.”

## Cuidados para perguntas

- **Os 35 modelos aparecem na tabela principal?** A Tabela 1 cataloga 35 variantes; a Tabela 2 apresenta um recorte de comparações. Não confundir catálogo e número de experimentos independentes.
- **É a melhor família para português?** O artigo não sustenta superioridade universal. A própria Tabela 3 contém modelos externos com médias maiores. Os slides retratam os resultados de 2025, não um ranking atual.
- **O que significa “B”?** Bilhões de parâmetros, uma medida de porte do modelo. Não equivale diretamente à qualidade.
- **Fine-tuning e few-shot são iguais?** Não. O primeiro atualiza pesos ou adaptadores por treinamento; o segundo coloca exemplos no prompt durante a avaliação.
- **Reduziu alucinações?** Essa discussão cita trabalhos anteriores; os nove benchmarks apresentados não devem ser tratados como uma medição direta e geral de alucinação.

## Notas de fidelidade ao artigo

As diferenças nos slides 6 e 7 foram calculadas a partir da coluna Average da Tabela 2. Evitamos a média global de ganhos narrada na seção 7.2 para priorizar pares diretamente verificáveis. A discussão da seção 7.5.1 contém inconsistências com a Tabela 4, inclusive na contagem de pares que empatam ou melhoram; por isso, não reproduzimos o percentual de 67%. Isso não altera os resultados usados nos slides.

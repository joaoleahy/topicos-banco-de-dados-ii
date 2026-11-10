# Roteiro: From Tokens to Words: On the Inner Lexicon of LLMs

Apresentação de 10 minutos. João Victor: slides 1 a 4 (3min20); Lucas Rapozo: 5 a 7 (3min40); Antoniel Magalhães: 8 a 10 (3min). A referência final é para consulta. A numeração abaixo conta a capa; o rodapé do tema conta apenas os nove slides de conteúdo.

Os tempos são metas para ensaio, incluindo transições. As falas desenvolvem os argumentos dos slides; use as âncoras para explicar sem ler. As notas de aprofundamento ao final ficam fora dos 10 minutos.

| Slide | Intervalo | Responsável | Tema |
|---|---|---|---|
| 1 | 0:00–0:20 | João Victor | Abertura |
| 2 | 0:20–1:15 | João Victor | Problema |
| 3 | 1:15–2:20 | João Victor | Léxico interno |
| 4 | 2:20–3:20 | João Victor | Mecanismo proposto |
| 5 | 3:20–4:25 | Lucas Rapozo | Palavras e não palavras |
| 6 | 4:25–5:50 | Lucas Rapozo | Recuperação da palavra |
| 7 | 5:50–7:00 | Lucas Rapozo | Intervenção nas FFNs |
| 8 | 7:00–7:55 | Antoniel Magalhães | Expansão do vocabulário |
| 9 | 7:55–9:00 | Antoniel Magalhães | Resultados práticos |
| 10 | 9:00–10:00 | Antoniel Magalhães | Conclusão e limites |
| 11 | Consulta | Equipe | Referência |

## 1. Abertura

“Somos João Victor, Lucas Rapozo e Antoniel Magalhães. Vamos apresentar o artigo From Tokens to Words: On the Inner Lexicon of LLMs, de Kaplan e colaboradores, publicado na ICLR 2025. Ele investiga como modelos de linguagem reconstroem palavras a partir de tokens.”

## 2. Problema e pergunta de pesquisa

“Quando lemos cats, enxergamos uma palavra. Mas o modelo pode receber partes separadas. Nesse exemplo, os pesquisadores dividem artificialmente cats em ca e ts. A questão é o que acontece com esses pedaços depois que entram no modelo.

O tokenizador define quais unidades têm uma entrada própria no vocabulário. Se uma palavra não tem um token único, ela ainda pode ser escrita como uma sequência de tokens. Isso não significa que o modelo desconheça a palavra.

Então, os autores perguntam: durante os cálculos, esses fragmentos se transformam numa representação da palavra inteira? Se isso acontece, em qual posição e em quais camadas conseguimos observar essa informação?”

Âncoras: cats → fragmentos → vocabulário não é todo o conhecimento → onde a palavra emerge.

## 3. Hipótese do léxico interno

“O artigo distingue o vocabulário do tokenizador de um possível léxico interno. O primeiro é uma lista explícita de unidades. O segundo é uma hipótese sobre representações que o modelo constrói nos seus cálculos.

Não estamos falando de um dicionário escondido com uma linha para cada palavra. Os autores descrevem um léxico distribuído: diferentes vetores e camadas podem participar da representação.

A hipótese é que a informação da palavra inteira se concentre no último token. Isso faz sentido porque, nesses modelos, essa posição pode acessar os fragmentos que vieram antes. Mas essa possibilidade, sozinha, não comprova que o processo acontece. É justamente isso que os experimentos vão testar.

O estudo inclui quatro modelos. Para acompanhar os números apresentados aqui, nosso foco será o Llama2-7B.”

Âncoras: lista explícita versus representação → não é dicionário literal → último token → testar a hipótese.

## 4. Mecanismo proposto

“Esta figura do artigo deve ser lida de baixo para cima, à esquerda. A palavra unhappiness chega dividida em três tokens. Primeiro, a atenção permite que a última posição reúna informação dos fragmentos anteriores.

Depois, as redes feedforward, ou FFNs, contribuem para transformar essa informação numa representação da palavra. Elas são componentes das camadas que processam os vetores e acrescentam atualizações ao estado interno.

À direita aparece uma forma de testar a hipótese: os pesquisadores retiram um vetor interno e o inserem em outro contexto. Se o modelo consegue repetir a palavra completa, temos evidência de que aquela representação carrega sua identidade.

A figura resume o mecanismo proposto. Lucas vai apresentar os experimentos que sustentam essa interpretação.”

Âncoras: apontar base da figura → atenção agrega → FFN refina → vetor em outro contexto → Lucas.

## 5. Palavras versus não palavras

“A primeira pergunta experimental é se os estados internos diferenciam palavras reais de combinações sem sentido. Os pesquisadores usam 10 mil palavras em inglês e constroem um grupo de não palavras embaralhando tokens, preservando características de posição, como fragmentos que costumam aparecer no final.

Um classificador auxiliar tenta separar os grupos olhando para os vetores do modelo. Usando o último token, ele chega a 89% de acurácia na camada 13. Esse número é do classificador, não uma nota geral do Llama.

No controle com o penúltimo token, para palavras de pelo menos três tokens, o resultado chega a 61%. Isso favorece a hipótese de que completar a palavra importa. Mas distinguir os grupos ainda não demonstra que podemos recuperar qual palavra está representada.”

Âncoras: grupos controlados → classificador externo → 89% → controle → falta identificar a palavra.

## 6. Recuperação da palavra inteira

“Por isso, o próximo passo testa a identidade da palavra. Há dois casos. Quando a palavra originalmente tinha um token e foi dividida artificialmente, existe um vetor de referência. Os pesquisadores comparam o estado interno com os vetores de entrada, usando uma adaptação do logit lens. Em 93,2% das palavras, a identidade correta aparece em pelo menos uma camada.

O segundo caso é mais interessante: palavras que já eram representadas por vários tokens. Elas não possuem um vetor único no vocabulário para usar como referência. Então entra o Patchscopes: o vetor do último token é colocado em outro prompt, e o modelo tenta repetir a palavra.

Nesse teste, 77,4% são recuperadas em alguma camada. Isso não quer dizer que uma única camada acerte 77,4%: o número reúne sucessos ao longo das camadas. Os 22,6% restantes não foram recuperados pelo procedimento. Essa falha pode refletir limites da representação ou da ferramenta usada para examiná-la.”

Âncoras: existe referência? → logit lens → sem referência, Patchscopes → acumulado entre camadas → cautela com falhas.

## 7. Intervenção nas FFNs

“Até aqui, observamos o que conseguimos ler dos vetores. Para investigar se as FFNs participam efetivamente do processo, os autores fazem uma intervenção chamada ablação: removem certas contribuições durante o cálculo.

Eles usam palavras com sufixos, divididas artificialmente, como eating em eat e ing. Removem atualizações FFN associadas à palavra completa, presentes em aproximadamente 5% das camadas. A recuperação cai de 85% para 18%.

O controle é importante: retirar a mesma quantidade de atualizações aleatórias tem pouco ou nenhum efeito nesse teste. Portanto, o resultado não se explica apenas por retirar qualquer parte do processamento.

Essa intervenção reforça o papel específico dessas atualizações na reconstrução, dentro do experimento. Antoniel vai mostrar como os autores transformam esse achado numa aplicação.”

Âncoras: observar versus intervir → ablação dirigida → 85 para 18 → controle aleatório → aplicação.

## 8. Expansão do vocabulário

“Se o modelo já produz uma representação da palavra inteira, podemos aproveitá-la para criar um token novo. O método procura a primeira camada em que a palavra é recuperada. Depois, aprende projeções para transformar esse estado interno em novas entradas nas matrizes de entrada e saída.

Há ainda uma etapa curta que treina matrizes adicionais para refinar essas representações. Os demais parâmetros ficam congelados.

Essa é uma ressalva importante ao termo sem fine-tuning usado no artigo: os pesos centrais não são reajustados, mas há treinamento auxiliar e novas entradas no vocabulário. A proposta aproveita capacidades já presentes no modelo para representar certas palavras com menos tokens.”

Âncoras: recuperar vetor → projetar para entrada e saída → refinar → núcleo congelado não é zero treinamento.

## 9. Resultados práticos

“A tabela mostra dois tipos de resultado. Nas colunas centrais, a acurácia de previsão de tokens permanece próxima à original, embora haja pequenas quedas nos três conjuntos. No WikiText, por exemplo, passa de 52,2 para 51,9%.

Na última coluna, vemos a economia de tokens ao codificar os textos. Ela varia de 10,5% no WikiText a 14,5% no conjunto em árabe. O PubMed mostra a aplicação num domínio especializado, com vocabulário biomédico.

Essas medidas não devem ser confundidas: menos tokens não significa automaticamente a mesma porcentagem de redução no tempo de execução. O resultado demonstrado aqui é a redução da sequência, com acurácia próxima da original. O ganho real de latência depende também da implementação e do custo de processar o vocabulário ampliado.”

Âncoras: qualidade próxima, pequenas quedas → sequência menor → domínio e idioma → tokens não são milissegundos.

## 10. Conclusão e limites

“O artigo reúne evidências de que modelos reconstroem representações de palavras no último token, principalmente nas camadas iniciais e intermediárias. A atenção agrega informações dos fragmentos, e as FFNs contribuem para formar a representação completa.

A aplicação mostra que podemos aproveitar esses vetores para ampliar o vocabulário e reduzir a quantidade de tokens. Mas recuperar a identidade de uma palavra não comprova que o modelo compreenda todos os seus sentidos ou usos. Da mesma forma, uma falha na recuperação não demonstra que ele desconheça a palavra.

A expansão foi avaliada no Llama2-7B, em três conjuntos. A contribuição é ligar uma investigação do funcionamento interno a uma possibilidade de eficiência, deixando a generalização e os ganhos de tempo para avaliações adicionais.”

Âncoras: evidências convergentes → aplicação → identidade não é compreensão completa → alcance dos testes.

## Preparação para perguntas, fora do tempo principal

- **Token é uma palavra?** Pode ser uma palavra, parte dela ou outra unidade textual. A divisão depende do tokenizador.
- **Fora do vocabulário significa nunca vista?** Não. Aqui significa que a palavra não tem uma entrada como token único; ela pode ter aparecido no treinamento como sequência de tokens.
- **Estado interno e peso são a mesma coisa?** Não. Pesos são parâmetros aprendidos; estados internos são vetores calculados para a entrada atual. O artigo extrai estados, não uma “linha de palavra” diretamente dos pesos.
- **O que é residual stream?** É o estado que percorre as camadas e recebe contribuições dos componentes, como atenção e FFN.
- **O que é Patchscopes?** Uma técnica que insere um estado interno em outro contexto para que o próprio modelo verbalize a informação nele representada. Neste trabalho, a tarefa é recuperar a palavra.
- **Por que o último token?** Pela atenção causal, ele tem acesso aos fragmentos anteriores. A concentração da informação nessa posição é testada empiricamente, não assumida como garantida.
- **Acurácia de 89% prova compreensão?** Não. Mede a separação de palavras e não palavras por um classificador auxiliar naquele conjunto.
- **93,2% e 77,4% são diretamente comparáveis?** Referem-se a experimentos e procedimentos diferentes. Ambos são sucessos em pelo menos uma camada, não a uma camada fixa.
- **Por que não usar perplexidade na expansão?** A mudança de vocabulário altera as unidades de predição, comprometendo a comparação direta. Os autores usam acurácia top-1 em nível de token.
- **“Sem fine-tuning” é literalmente sem treinamento?** Não nesta implementação. A seção 6 aprende mapas lineares e treina matrizes de refinamento, mantendo os demais parâmetros congelados. Novas entradas são adicionadas às matrizes de entrada e saída.
- **É um dicionário humano dentro da rede?** Não. O léxico é uma interpretação de representações distribuídas; a analogia não estabelece equivalência cognitiva com humanos.
- **O desempenho melhorou?** Na métrica geral selecionada da Tabela 1, há pequenas quedas. A conclusão segura é desempenho próximo do original com menos tokens, não melhoria universal.
- **Há um limite adicional no desenho experimental?** A escolha das palavras para expansão usa frequência no conjunto de teste (seção 6). Isso torna o recorte específico ao conjunto avaliado e deve ser considerado antes de generalizar para texto inteiramente novo.

## Conferência das fontes

- Slides 2–4: seções 1, 2, 4 e 5; Figura 1.
- Slide 5: seção 3, Figura 2. 89% é o pico da sonda k-NN no último token; 61% é o controle descrito para o penúltimo.
- Slide 6: seções 4.1 e 4.2, incluindo as notas 8 e 9. 93,2% corresponde à divisão artificial, não aos erros de digitação. 77,4% é a recuperação acumulada das palavras originalmente multitoken; 22,6% é o complemento.
- Slide 7: seção 5.1. 85% → 18% é a ablação de palavras com sufixos, não a experiência separada sobre capitais de países.
- Slide 8: seção 6, Figura 6.
- Slide 9: Tabela 1, linha geral (All words), valores multiplicados por 100; Apêndice H, Tabela 5, redução de tokens na codificação.
- Slide 10: conclusão das evidências e leitura crítica da equipe.

Referência: Kaplan, G.; Oren, M.; Reif, Y.; Schwartz, R. From Tokens to Words: On the Inner Lexicon of LLMs. ICLR 2025. PDF fornecido, arXiv:2410.05864v4, 3 de março de 2025. https://arxiv.org/abs/2410.05864v4

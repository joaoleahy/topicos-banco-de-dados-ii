# Roteiro: Distributed Representations of Sentences and Documents (Doc2Vec)

Apresentação de 10 minutos[cite: 40]. João Victor: slides 1 a 4 (3min20); Lucas Rapozo: 5 a 7 (3min40); Antoniel Magalhães: 8 a 10 (3min)[cite: 40]. A referência final é para consulta[cite: 40]. A numeração abaixo conta a capa; o rodapé do tema conta apenas os nove slides de conteúdo[cite: 40].

Os tempos são metas para ensaio, incluindo transições[cite: 40]. As falas desenvolvem os argumentos dos slides; use as âncoras para explicar sem ler[cite: 40]. As notas de aprofundamento ao final ficam fora dos 10 minutos[cite: 40].

| Slide | Intervalo | Responsável | Tema |
|---|---|---|---|
| 1 | 0:00–0:20 | João Victor | Abertura |
| 2 | 0:20–1:15 | João Victor | Problema do Bag-of-Words |
| 3 | 1:15–2:20 | João Victor | Proposta Paragraph Vector |
| 4 | 2:20–3:20 | João Victor | Arquitetura PV-DM |
| 5 | 3:20–4:25 | Lucas Rapozo | PV-DBOW e Inferência |
| 6 | 4:25–5:50 | Lucas Rapozo | Sentimento em Sentenças (SST) |
| 7 | 5:50–7:00 | Lucas Rapozo | Sentimento em Documentos (IMDB) |
| 8 | 7:00–7:55 | Antoniel Magalhães | Recuperação de Informação |
| 9 | 7:55–9:00 | Antoniel Magalhães | Ablações e custo de inferência |
| 10 | 9:00–10:00 | Antoniel Magalhães | Conclusão e limites |
| 11 | Consulta | Equipe | Referência |

## 1. Abertura
Somos João Victor, Lucas Rapozo e Antoniel Magalhães[cite: 40]. Vamos apresentar o artigo *Distributed Representations of Sentences and Documents*, de Quoc Le e Tomas Mikolov, publicado na ICML de 2014, que introduziu o método Paragraph Vector, amplamente conhecido como Doc2Vec[cite: 42].

## 2. O problema: representar textos em tamanho fixo
Muitos algoritmos clássicos de aprendizado de máquina, como regressão logística, SVMs ou K-means, exigem que a entrada seja um vetor de características de tamanho fixo[cite: 42]. Na época do artigo, a solução padrão para textos era o *Bag-of-Words* ou *Bag-of-N-grams*[cite: 42].

O problema é que o *Bag-of-Words* sofre de duas falhas estruturais graves[cite: 42]. Primeiro, ele descarta completamente a ordem das palavras: duas frases com sentidos opostos têm exatamente a mesma representação se usarem os mesmos vocábulos[cite: 42]. Usar n-gramas tenta preservar a ordem curta, mas explode a dimensionalidade e gera alta esparsidade[cite: 42]. Segundo, ele ignora a semântica: como cada palavra é uma dimensão ortogonal independente, a distância entre *powerful* e *strong* é exatamente igual à distância entre *powerful* e *Paris*[cite: 42].

Tentativas anteriores de tirar a média dos vetores de palavras continuavam perdendo a ordem, enquanto redes neurais recursivas dependiam de árvores de *parsing* sintático, o que impedia seu uso em documentos com várias frases[cite: 43, 46].

Âncoras: entrada fixa -> perda de ordem -> powerful/strong/Paris -> limite de sentença única.

## 3. Proposta: Paragraph Vector (Doc2Vec)
Para superar essas limitações, Le e Mikolov propõem o *Paragraph Vector*: um framework não supervisionado que aprende representações vetoriais densas e contínuas para textos de qualquer comprimento, desde frases curtas até documentos inteiros[cite: 42, 43].

A intuição vem diretamente do sucesso do Word2Vec[cite: 43, 44]. Nos modelos de vetores de palavras, embora os vetores sejam inicializados de forma aleatória, eles acabam capturando propriedades semânticas como efeito indireto de tentar prever a próxima palavra em uma janela de contexto[cite: 44].

Os autores aplicam o mesmo princípio ao documento: cada parágrafo é mapeado para um vetor único, representado por uma coluna em uma matriz $D$, enquanto cada palavra do vocabulário é mapeada para uma coluna em uma matriz $W$[cite: 44]. A diferença fundamental é que a matriz de palavras $W$ é compartilhada por todo o corpus, mas os vetores em $D$ são exclusivos de cada documento[cite: 42, 44]. O treinamento ocorre via descida de gradiente estocástica e *backpropagation*, utilizando *hierarchical softmax* com árvore binária de Huffman para acelerar o acesso às palavras frequentes[cite: 43, 44].

Âncoras: tamanho variável -> inspiração no Word2Vec -> matriz D exclusiva vs. matriz W compartilhada -> árvore de Huffman.

## 4. Arquitetura 1: Memória Distribuída (PV-DM)
A primeira arquitetura proposta é chamada de *Distributed Memory*, ou PV-DM[cite: 44]. Nela, amostramos uma janela deslizante de tamanho fixo dentro do parágrafo — por exemplo, três palavras como *the*, *cat*, *sat* — e concatenamos ou tiramos a média desses vetores junto com o vetor do parágrafo $D$ para prever a quarta palavra, *on*[cite: 43, 44].

Por que o nome Memória Distribuída? Porque o token do parágrafo funciona como uma palavra virtual adicional que atua como memória: ele guarda o tópico geral do documento ou a informação contextual que está faltando naquela janela curta de palavras[cite: 44].

Como o mesmo vetor $D$ participa da predição em todas as janelas amostradas daquele parágrafo, ele é forçado a sintetizar o tema global do texto[cite: 44]. Se tivermos $N$ parágrafos de dimensão $p$ e $M$ palavras de dimensão $q$, o modelo terá $N \times p + M \times q$ parâmetros antes do softmax, mas como cada passo atualiza apenas um documento e poucas palavras, o treino é esparso e eficiente[cite: 44]. Agora o Lucas vai explicar a segunda arquitetura e como o modelo lida com textos inéditos.

Âncoras: janela deslizante -> D como memória do tópico -> compartilhado dentro do parágrafo -> atualizações esparsas -> Lucas.

## 5. Arquitetura 2 (PV-DBOW) e Etapa de Inferência
Além do PV-DM, os autores propõem uma segunda variante mais simples chamada *Distributed Bag of Words*, ou PV-DBOW[cite: 45]. Nela, ignoramos as palavras de contexto na entrada e forçamos o modelo a prever palavras sorteadas aleatoriamente de uma janela do texto usando exclusivamente o vetor do parágrafo $D$[cite: 45].

Essa abordagem é análoga ao modelo *Skip-gram* do Word2Vec[cite: 45]. A vantagem é conceitual e de memória: não precisamos armazenar a matriz de palavras $W$, apenas os pesos do softmax[cite: 45]. Na prática, o artigo descobre que concatenar um vetor de 400 dimensões do PV-DM com outro de 400 dimensões do PV-DBOW gera representações mais consistentes em diferentes tarefas[cite: 45, 46, 47].

Mas como obtemos o vetor de um documento novo, que não estava no treinamento? Entra a **etapa de inferência**[cite: 44]. Congelamos a matriz de palavras $W$ e os pesos do classificador softmax, adicionamos uma nova coluna na matriz $D$ para o texto de teste e rodamos a descida de gradiente apenas sobre esse novo vetor até convergir[cite: 42, 44]. Depois, entregamos esse vetor pronto para um classificador padrão, como regressão logística[cite: 44].

Âncoras: PV-DBOW sem contexto de entrada -> análogo ao Skip-gram -> inferência congela W e otimiza novo D -> concatenação 400d + 400d.

## 6. Evidência 1: Análise de Sentimento em Sentenças (SST)
O primeiro experimento avalia o método no *Stanford Sentiment Treebank*, com 11.855 frases do site Rotten Tomatoes e mais de 239 mil subfrases rotuladas com auxílio do Stanford Parser[cite: 45]. Os autores treinam os vetores com janela ótima de tamanho 8 e alimentam uma regressão logística em duas tarefas: classificação binária e classificação fina em 5 níveis de sentimento[cite: 46].

A tabela mostra que modelos *Bag-of-Words* e até a média simples de vetores de palavras têm taxas de erro altas, próximas de 20% no binário e 67,3% em 5 classes, porque perdem a ordem das palavras e falham em capturar fenômenos de composição e sarcasmo[cite: 46].

Já as redes neurais recursivas de Socher, como a RNTN, usam árvores sintáticas explícitas para compor o significado e baixam o erro binário para 14,6%[cite: 46]. Mesmo sem exigir nenhum *parser* sintático, o Paragraph Vector supera todas as baselines, reduzindo o erro para 12,2% no binário e 51,3% nas 5 classes — uma queda absoluta de 2,4 pontos, equivalente a 16% de melhoria relativa sobre o estado da arte anterior[cite: 43, 46].

Âncoras: Rotten Tomatoes -> falha da média simples -> superar RNTN sem parsing -> 12,2% binário e 51,3% fino.

## 7. Evidência 2: Documentos de Múltiplas Sentenças (IMDB)
O segundo experimento destaca a principal vantagem prática do método: ir além de uma única frase[cite: 46]. Redes dependentes de *parsing*, como a RNTN, não têm uma forma clara de combinar árvores sintáticas de várias sentenças ao mesmo tempo[cite: 46].

Os autores testam a base do IMDB, que contém 100 mil críticas de filmes longas, com várias frases cada: 25 mil de treino, 25 mil de teste e 50 mil documentos sem rótulo[cite: 46, 47]. A fase não supervisionada aprende os vetores nos 75 mil textos de treino usando janela de 10 palavras, e uma rede neural rasa com 50 unidades ocultas classifica os 25 mil rotulados[cite: 47].

Em documentos longos, o *Bag-of-Words* tradicional funciona bem e é difícil de bater, ficando em 12,20%, enquanto o modelo NBSVM com bigramas chegava a 8,78%[cite: 47]. O Paragraph Vector é o único a romper com folga a barreira dos 10%, atingindo 7,42% de taxa de erro — redução absoluta de 1,36 ponto, ou 15% de melhoria relativa sobre o melhor resultado anterior[cite: 47]. Agora o Antoniel apresenta o teste em recuperação de informação e as análises de ablação.

Âncoras: limite de múltiplas frases -> uso de 50k textos sem rótulo -> barreira dos 10% -> 7,42% contra 8,78% do NBSVM -> Antoniel.

## 8. Evidência 3: Recuperação de Informação em Trincas
A terceira avaliação testa se os vetores preservam semântica para busca de documentos[cite: 47]. Os autores constroem uma base com os 10 primeiros trechos — ou *snippets* — retornados por um buscador para 1 milhão de consultas populares[cite: 47].

Para cada consulta, eles montam uma trinca de parágrafos: dois são resultados reais da mesma busca e o terceiro é sorteado aleatoriamente de outra busca qualquer[cite: 47]. O objetivo é que a distância vetorial entre os dois parágrafos da mesma consulta seja menor do que a distância para o texto intruso[cite: 47, 48]. Quando isso não acontece, contabiliza-se um erro[cite: 48].

Como vemos na tabela, tirar a média dos vetores de palavras erra em 10,25% das trincas, pior até que o *Bag-of-Words* com TF-IDF, que tem 8,10% de erro[cite: 48]. Mesmo aprendendo uma matriz de pesos supervisionada sobre bigramas, o erro fica em 5,67%[cite: 48]. O Paragraph Vector cai para 3,82%, representando uma redução relativa de 32% nos erros de ranqueamento[cite: 48].

Âncoras: trincas de busca -> dois da mesma query vs. um intruso -> média de vetores perde para TF-IDF -> 3,82% (32% de redução).

## 9. Ablações e escolhas de projeto no IMDB
Na seção 3.4, os autores investigam o que realmente faz o modelo funcionar usando o IMDB como referência[cite: 48].

Primeiro, comparam as duas arquiteturas isoladas: o PV-DM sozinho, usando concatenação na camada oculta, já alcança 7,63% de erro, muito perto do estado da arte[cite: 48]. Porém, se trocarmos a concatenação pela soma ou média dos vetores no PV-DM, o erro sobe para 8,06%[cite: 48]. Os autores atribuem essa perda justamente ao fato de a soma descartar a ordem das palavras dentro da janela[cite: 48]. E quando combinamos PV-DM concatenado com PV-DBOW, chegamos ao melhor resultado de 7,42%[cite: 48].

Segundo, testam a sensibilidade ao hiperparâmetro de janela: valores entre 5 e 12 palavras são boas escolhas gerais e fazem a taxa de erro variar em no máximo 0,7 ponto percentual[cite: 48]. Por fim, medem o custo computacional do passo de inferência: calcular os vetores dos 25 mil textos de teste do IMDB levou cerca de 30 minutos em uma máquina de 16 núcleos, mostrando que o processo tem custo relevante, mas pode ser paralelizado[cite: 48].

Âncoras: PV-DM 7,63% -> concatenação vs. soma (8,06%) -> janela entre 5 e 12 -> 30 minutos para 25 mil testes.

## 10. Conclusão e limites
Em conclusão, o Paragraph Vector resolve as duas principais fraquezas do *Bag-of-Words*: ele herda as distâncias semânticas contínuas do Word2Vec e preserva a ordem local das palavras sem explodir a dimensionalidade e sem exigir árvores sintáticas[cite: 42, 45]. Além disso, por ser não supervisionado na criação dos vetores, aproveita dados não rotulados para melhorar classificadores posteriores[cite: 45, 49].

Como leitura crítica da equipe, destacamos três limites importantes do método[cite: 44, 48]. O primeiro é o custo de inferência em produção: enquanto redes modernas geram representações em uma única passagem direta (*forward pass*), o Doc2Vec exige rodar descida de gradiente iterativa para cada novo documento recebido[cite: 44, 48]. O segundo é que a ordem só é preservada estritamente dentro da janela deslizante quando se usa concatenação[cite: 45, 48]. E o terceiro é o crescimento linear da matriz $D$ durante o treino, que adiciona uma coluna de parâmetros para cada documento do corpus[cite: 44].

Âncoras: síntese das vantagens -> inferência iterativa por gradiente -> ordem restrita à janela -> crescimento linear da matriz D.

## Preparação para perguntas, fora do tempo principal
- **Por que o nome popular é Doc2Vec se o artigo chama de Paragraph Vector?** O artigo usa o termo *Paragraph Vector* para enfatizar que o método serve para pedaços de texto de tamanho variável, de uma frase a um documento inteiro[cite: 42]. A comunidade e bibliotecas como o *Gensim* popularizaram o nome *Doc2Vec* em analogia direta ao *Word2Vec* de Mikolov[cite: 43].
- **Como o modelo lida com textos muito curtos, menores que a janela?** Se o parágrafo tiver menos palavras do que o tamanho da janela (por exemplo, menos de 9 palavras nos experimentos de sentimento), os autores fazem *pre-padding* preenchendo as posições iniciais com um símbolo especial `NULL`[cite: 46, 47]. Além disso, sinais de pontuação como `,.!?` são tratados como palavras normais[cite: 46, 47].
- **Qual a diferença exata entre concatenar e tirar a média no PV-DM?** Na concatenação, cada posição da janela tem seus próprios pesos na matriz $U$ do classificador softmax, preservando a ordem exata em que as palavras apareceram na janela[cite: 43, 48]. Na soma ou média, as posições são colapsadas antes da multiplicação por $U$, perdendo a ordem imediata dentro da janela (o que elevou o erro no IMDB de 7,63% para 8,06%)[cite: 48].
- **Por que a etapa de inferência no teste pode ser paralelizada?** Porque durante o teste a matriz de palavras $W$ e os pesos do softmax $U, b$ ficam totalmente congelados[cite: 44]. Assim, a otimização por gradiente do vetor $D_{novo}$ de um documento de teste não interfere nos parâmetros nem nos vetores de outros documentos de teste, permitindo processar milhares de textos simultaneamente em múltiplos núcleos de CPU[cite: 44, 48].
- **O modelo usa árvores sintáticas na base do Stanford Sentiment Treebank?** Não para construir o vetor[cite: 46]. O dataset SST já vinha dividido em 239.232 subfrases geradas pelo Stanford Parser pelos autores originais da base (Socher et al.)[cite: 45]. Le e Mikolov apenas trataram cada subfrase rotulada do treino como uma frase independente para treinar o modelo, mas na avaliação final classificaram as frases completas sem precisar rodar nenhum *parser*[cite: 46].

## Conferência das fontes
- Slides 2–4: seções 1, 2.1 e 2.2; Equação 1 e Figuras 1 e 2[cite: 42, 43, 44].
- Slide 5: seções 2.2 e 2.3; Figura 3[cite: 44, 45].
- Slide 6: seção 3.1 e Tabela 1 (taxas de erro no SST binário e *fine-grained*)[cite: 45, 46].
- Slide 7: seção 3.2 e Tabela 2 (taxas de erro no IMDB)[cite: 46, 47].
- Slide 8: seção 3.3 e Tabela 3 (erro nas trincas de busca com TF-IDF)[cite: 47, 48].
- Slide 9: seção 3.4 (ablações de PV-DM 7,63%, soma 8,06%, combinação 7,42% e tempo de 30 min em 16 cores)[cite: 48].
- Slide 10: seções 2.2, 3.4 e 5[cite: 44, 48, 49].

Referência: Le, Q.; Mikolov, T. *Distributed Representations of Sentences and Documents*. ICML 2014, JMLR: W&CP volume 32, 2014[cite: 42].
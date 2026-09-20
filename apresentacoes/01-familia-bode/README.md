# Síntese da família Bode

Apresentação em português para 10 minutos. Equipe: João Victor, Lucas Rapozo e Antoniel Magalhães.

- `main.tex`: slides editáveis em LaTeX/Beamer.
- `main.pdf`: apresentação compilada.
- `roteiro.md`: guia de fala, tempos e divisão sugerida entre os integrantes.
- `beamerthemeDCC.sty` e `imgs/dcc.png`: cópias preservadas do template DCC/UFBA, provenientes da pasta `slides-template` do projeto `luisfelipesena/ufba-latex`. Os arquivos necessários estão incluídos nesta pasta.

São 10 slides de apresentação, incluindo a capa, e 1 slide de referência para consulta. O tema original não conta a capa; por isso a numeração visível do conteúdo vai de 1 a 9. A referência não acrescenta tempo ao roteiro. A data da apresentação e a disciplina não foram inventadas.

## Compilação

Dentro desta pasta, com uma distribuição TeX instalada:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Ou com Tectonic:

```sh
tectonic main.tex
```

No Overleaf, envie esta pasta inteira e defina `main.tex` como documento principal.

## Fonte

Paiola et al. (2025). *The Bode Family of Large Language Models: Investigating the Frontiers of LLMs in Brazilian Portuguese*. Journal of the Brazilian Computer Society, 31(1). https://doi.org/10.5753/jbcs.2025.5812

A apresentação usa o PDF fornecido pelo usuário. Resultados e comparações correspondem ao artigo, sem atualização de rankings externos. As fontes de cada recorte aparecem no rodapé do respectivo slide.

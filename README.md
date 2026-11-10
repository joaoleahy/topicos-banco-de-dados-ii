# Tópicos em Banco de Dados II

Apresentações da equipe:

- João Victor
- Lucas Rapozo
- Antoniel Magalhães

## Apresentações

| Nº | Tema | Material |
|---|---|---|
| 01 | Família Bode: modelos de linguagem para o português brasileiro | [Pasta](apresentacoes/01-familia-bode/) · [PDF](apresentacoes/01-familia-bode/main.pdf) · [Roteiro](apresentacoes/01-familia-bode/roteiro.md) |
| 02 | From Tokens to Words: On the Inner Lexicon of LLMs | [Pasta](apresentacoes/teorica-2-tokens-to-words/) · [PDF](apresentacoes/teorica-2-tokens-to-words/main.pdf) · [Roteiro](apresentacoes/teorica-2-tokens-to-words/roteiro.md) |
| 03 | Distributed Representations of Sentences and Documents (Doc2Vec) | [Pasta](apresentacoes/teorica-3-doc2vec/) · [PDF](apresentacoes/teorica-3-doc2vec/main.pdf) · [Roteiro](apresentacoes/teorica-3-doc2vec/roteiro.md) |
| 04 | NorBERTo: A ModernBERT Model Trained for Portuguese with 331B Tokens Corpus | [Pasta](apresentacoes/teorica-4-norberto/) · [PDF](apresentacoes/teorica-4-norberto/main.pdf) · [Roteiro](apresentacoes/teorica-4-norberto/roteiro.md) |

## Organização

Cada apresentação possui uma pasta independente em `apresentacoes/`, com identificação da apresentação e nome do tema, como `01-familia-bode/`, `teorica-2-tokens-to-words/`, `teorica-3-doc2vec/` e `teorica-4-norberto/`. A pasta contém o código LaTeX, o tema Beamer, as imagens necessárias, o PDF compilado e o roteiro quando disponível.

## Compilação

Entre na pasta da apresentação e use uma das opções:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

```sh
tectonic main.tex
```

Para usar o Overleaf, envie o conteúdo da pasta da apresentação e selecione `main.tex` como documento principal.

Os PDFs finais são versionados para permitir a consulta sem compilar o LaTeX. Arquivos temporários de compilação são ignorados.

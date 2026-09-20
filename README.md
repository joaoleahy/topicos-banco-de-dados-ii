# Tópicos em Banco de Dados II

Apresentações da equipe:

- João Victor
- Lucas Rapozo
- Antoniel Magalhães

## Apresentações

| Nº | Tema | Material |
|---|---|---|
| 01 | Família Bode: modelos de linguagem para o português brasileiro | [Pasta](apresentacoes/01-familia-bode/) · [PDF](apresentacoes/01-familia-bode/main.pdf) · [Roteiro](apresentacoes/01-familia-bode/roteiro.md) |

## Organização

Cada apresentação possui uma pasta independente em `apresentacoes/`, com prefixo numérico e nome do tema, por exemplo `02-nome-do-tema/`. A pasta contém o código LaTeX, o tema Beamer, as imagens necessárias, o PDF compilado e o roteiro quando disponível.

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

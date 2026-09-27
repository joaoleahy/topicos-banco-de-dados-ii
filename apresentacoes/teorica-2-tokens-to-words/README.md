# Teórica 2 — From Tokens to Words: On the Inner Lexicon of LLMs

Síntese do artigo de Guy Kaplan, Matanel Oren, Yuval Reif e Roy Schwartz, publicado na ICLR 2025. Base: PDF fornecido, arXiv:2410.05864v4 (3 de março de 2025).

Equipe: João Victor, Lucas Rapozo e Antoniel Magalhães.

- [main.pdf](main.pdf): slides compilados, com título original em inglês e conteúdo em português.
- [main.tex](main.tex): fonte LaTeX/Beamer.
- [roteiro.md](roteiro.md): falas para 10 minutos, divisão entre integrantes, âncoras e preparação para perguntas.
- `beamerthemeDCC.sty` e `imgs/dcc.png`: tema e símbolo preservados da primeira apresentação.
- `imgs/figura-1-artigo.pdf`: recorte vetorial da Figura 1 do artigo, com atribuição no slide 4. Autoria da figura: Kaplan et al.

São 10 slides para a fala, incluindo a capa, e um slide de referência para consulta. A numeração do tema exclui a capa. Os tempos do roteiro precisam de confirmação por ensaio.

## Compilação

Nesta pasta, execute `tectonic main.tex` ou `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`. Para usar o Overleaf, envie todos os arquivos desta pasta e selecione `main.tex` como principal.

## Fonte

[Artigo, versão utilizada](https://arxiv.org/abs/2410.05864v4) · [Código dos autores](https://github.com/schwartz-lab-NLP/Tokens2Words)

A apresentação diferencia resultados medidos de interpretações: “sem fine-tuning” mantém o núcleo congelado, mas inclui treinamento auxiliar; redução de tokens não é uma medição direta de latência.

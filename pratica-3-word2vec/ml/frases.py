"""Etapa 2 — Transformar cada artigo em frases de palavras, a entrada do Word2Vec.

O Word2Vec aprende com a janela de vizinhos de cada palavra. Se o artigo fosse
uma lista única, a janela juntaria o fim de uma frase com o começo da próxima.
Por isso:

1. corta o artigo em frases nos tokens de fim de frase (`.`, `!`, `?`, `;`);
2. em cada frase, fica só com as palavras (token com pelo menos uma letra),
   em minúsculas — pontuação e números não têm vetor;
3. descarta frase com menos de 2 palavras (não há vizinho para prever).
"""

from __future__ import annotations

FIM_DE_FRASE = {".", "!", "?", ";"}
MIN_PALAVRAS = 2


def eh_palavra(token: str) -> bool:
    return any(c.isalpha() for c in token)


def dividir_em_frases(tokens: list[str]) -> list[list[str]]:
    frases, atual = [], []
    for token in tokens:
        if token in FIM_DE_FRASE:
            frases.append(atual)
            atual = []
        else:
            atual.append(token)
    return frases + [atual]


def so_palavras(frase: list[str]) -> list[str]:
    return [t.lower() for t in frase if eh_palavra(t)]


def preparar(artigos: list[dict]) -> list[list[str]]:
    frases = []
    for artigo in artigos:
        for frase in dividir_em_frases(artigo["artigo_tokenizado_pontuado"]):
            palavras = so_palavras(frase)
            if len(palavras) >= MIN_PALAVRAS:
                frases.append(palavras)
    return frases

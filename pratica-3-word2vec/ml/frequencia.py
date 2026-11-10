"""Etapa 3 — Substantivo e verbo mais frequentes, pela classe gramatical da PRÁTICA 1.

`pos_tagger` guarda "CLASSE_palavra" (ex.: "NOUN_dados", "VERB_pode"). A
contagem é pela forma da palavra em minúsculas, a mesma unidade que o
Word2Vec usa para criar os vetores ("construção" e "construções" são
palavras diferentes).
"""

from __future__ import annotations

from collections import Counter


def por_classe(artigos: list[dict], classe: str) -> Counter:
    contagem: Counter = Counter()
    for artigo in artigos:
        for marcado in artigo["pos_tagger"]:
            tag, palavra = marcado.split("_", 1)
            if tag == classe:
                contagem[palavra.lower()] += 1
    return contagem


def mais_frequente(artigos: list[dict], classe: str) -> str:
    return por_classe(artigos, classe).most_common(1)[0][0]

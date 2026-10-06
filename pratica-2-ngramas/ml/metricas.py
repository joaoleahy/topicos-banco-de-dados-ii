"""Métricas para comparar os textos gerados.

- repetidos: fração de k-gramas do texto que já tinham aparecido antes nele
- distintos: fração de k-gramas únicos (distinct-k)
- copia: maior trecho do texto gerado que existe idêntico no corpus
"""

from __future__ import annotations

from ml.ngrama import kgramas
from ml.tokenizar import eh_palavra


def repetidos(tokens: list[str], k: int = 3) -> float:
    gs = kgramas(tokens, k)
    return 1 - len(set(gs)) / len(gs) if gs else 0.0


def copia(tokens: list[str], corpus: list[list[str]], max_k: int = 40) -> int:
    maior = 0
    for k in range(2, max_k + 1):
        do_corpus = {g for doc in corpus for g in kgramas(doc, k)}
        if not any(g in do_corpus for g in kgramas(tokens, k)):
            break
        maior = k
    return maior


def resumo(tokens: list[str], corpus: list[list[str]]) -> dict[str, str]:
    return {
        "palavras": str(sum(map(eh_palavra, tokens))),
        "pontos finais": str(tokens.count(".")),
        "trigramas repetidos": f"{repetidos(tokens, 3):.0%}",
        "maior trecho copiado do corpus": f"{copia(tokens, corpus)} tokens",
    }

"""Etapa 3 — Bigrama: contar pares e gerar o próximo token.

Contagem: para cada token `a`, quantas vezes cada `b` veio logo depois.
Isso é uma linha da matriz termo x termo, guardada como dicionário
(só as células diferentes de zero).

    P(b | a) = C(a, b) / C(a, *)

Geração: parte de um token inicial e sorteia o próximo proporcional a P(b | a),
até atingir o limite de palavras (pontuação não conta como palavra).
"""

from __future__ import annotations

import random
from collections import Counter, defaultdict

from ml.tokenizar import eh_palavra


def contar(documentos: list[list[str]]) -> dict[str, Counter]:
    # Cada documento é contado separado: o último token de um artigo
    # não forma par com o primeiro do próximo.
    pares: dict[str, Counter] = defaultdict(Counter)
    for tokens in documentos:
        for a, b in zip(tokens, tokens[1:]):
            pares[a][b] += 1
    return dict(pares)


def proximas(pares: dict[str, Counter], a: str, k: int = 10) -> list[tuple[str, int, float]]:
    linha = pares.get(a, Counter())
    total = sum(linha.values())
    return [(b, c, c / total) for b, c in linha.most_common(k)]


def gerar(pares: dict[str, Counter], inicio: str, max_palavras: int = 150, seed: int = 0) -> list[str]:
    rng = random.Random(seed)
    saida = [inicio]
    palavras = int(eh_palavra(inicio))
    while palavras < max_palavras:
        linha = pares.get(saida[-1])
        if not linha:
            break
        proximo = rng.choices(list(linha), weights=list(linha.values()))[0]
        saida.append(proximo)
        palavras += eh_palavra(proximo)
    return saida


def juntar(tokens: list[str]) -> str:
    texto = " ".join(tokens)
    for p in ".,;:!?)]":
        texto = texto.replace(f" {p}", p)
    for p in "([":
        texto = texto.replace(f"{p} ", p)
    return texto

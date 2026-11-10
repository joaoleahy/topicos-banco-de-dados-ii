"""Etapa — n-gramas genéricos (unigrama, bigrama, trigrama).

Tabela de um modelo de ordem n: contexto (as n-1 palavras anteriores) -> Counter
do próximo token. Cada contexto é uma linha da matriz termo x termo.

    unigrama: contexto ()          P(w)
    bigrama:  contexto (a,)        P(w | a)
    trigrama: contexto (a, b)      P(w | a, b)

Geração: o contexto são os últimos n-1 tokens gerados. Se o contexto ainda é
curto (início do texto) ou nunca foi visto, recua para a ordem menor (backoff).

Controle de repetição (`bloquear=k`): um candidato que formaria um k-grama já
presente no texto gerado é descartado. Se todos os candidatos do contexto
forem descartados, recua para a ordem menor.
"""

from __future__ import annotations

import random
from collections import Counter, defaultdict

Tabela = dict[tuple[str, ...], Counter]


def eh_palavra(token: str) -> bool:
    return token[0].isalnum()


def juntar(tokens: list[str]) -> str:
    texto = " ".join(tokens)
    for p in ".,;:!?)]":
        texto = texto.replace(f" {p}", p)
    for p in "([":
        texto = texto.replace(f"{p} ", p)
    return texto


def contar(documentos: list[list[str]], n: int) -> Tabela:
    tabela: dict[tuple[str, ...], Counter] = defaultdict(Counter)
    for tokens in documentos:
        for i in range(n - 1, len(tokens)):
            tabela[tuple(tokens[i - n + 1 : i])][tokens[i]] += 1
    return dict(tabela)


def modelos(documentos: list[list[str]], n: int) -> dict[int, Tabela]:
    """Todas as ordens até n: o trigrama precisa do bigrama e do unigrama para o backoff."""
    return {k: contar(documentos, k) for k in range(1, n + 1)}


def probabilidade(tabela: Tabela, contexto: tuple[str, ...], w: str) -> float:
    linha = tabela.get(contexto)
    return linha[w] / sum(linha.values()) if linha else 0.0


def kgramas(tokens: list[str], k: int) -> list[tuple[str, ...]]:
    return [tuple(tokens[i : i + k]) for i in range(len(tokens) - k + 1)]


def candidatos(
    tabelas: dict[int, Tabela],
    n: int,
    saida: list[str],
    proibido=lambda w: False,
    backoff: bool = True,
) -> Counter:
    ordem = min(n, len(saida) + 1)  # início do texto: ainda não há n-1 tokens de contexto
    for k in range(ordem, 0 if backoff else ordem - 1, -1):
        linha = tabelas[k].get(tuple(saida[len(saida) - k + 1 :]) if k > 1 else (), Counter())
        linha = Counter({w: c for w, c in linha.items() if not proibido(w)})
        if linha:
            return linha
    return tabelas[1][()] if backoff else Counter()  # tudo bloqueado até no unigrama: aceita repetir


def gerar(
    tabelas: dict[int, Tabela],
    n: int,
    inicio: list[str],
    max_palavras: int = 150,
    seed: int = 0,
    gulosa: bool = False,
    bloquear: int = 0,
    backoff: bool = True,
    limite_tokens: int | None = None,
) -> list[str]:
    rng = random.Random(seed)
    saida = list(inicio)
    palavras = sum(map(eh_palavra, saida))
    vistos = set(kgramas(saida, bloquear)) if bloquear else set()

    def proibido(w: str) -> bool:
        return bool(bloquear) and tuple(saida[len(saida) - bloquear + 1 :] + [w]) in vistos

    # a gulosa pode travar repetindo pontuação, que não conta como palavra
    limite = limite_tokens or 3 * max_palavras
    while palavras < max_palavras and len(saida) < limite:
        linha = candidatos(tabelas, n, saida, proibido, backoff)
        if not linha:  # sem backoff: contexto sem candidato encerra o texto
            break
        if gulosa:
            proximo = linha.most_common(1)[0][0]
        else:
            proximo = rng.choices(list(linha), weights=list(linha.values()))[0]
        saida.append(proximo)
        palavras += eh_palavra(proximo)
        if bloquear and len(saida) >= bloquear:
            vistos.add(tuple(saida[-bloquear:]))
    return saida

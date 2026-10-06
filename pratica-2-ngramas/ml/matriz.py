"""Etapa — Matriz termo x termo reduzida (top 10) e heatmap.

Linhas = contextos, colunas = próximos tokens, célula = P(coluna | linha)
calculada sobre a linha inteira (vocabulário completo), não só sobre o recorte.
"""

from __future__ import annotations

from collections import Counter

from ml.ngrama import Tabela, probabilidade
from ml.tokenizar import eh_palavra


def top_palavras(documentos: list[list[str]], k: int = 10) -> list[str]:
    c = Counter(t for doc in documentos for t in doc if eh_palavra(t))
    return [w for w, _ in c.most_common(k)]


def top_contextos(tabela: Tabela, k: int = 10) -> list[tuple[str, ...]]:
    totais = Counter({ctx: sum(l.values()) for ctx, l in tabela.items() if all(map(eh_palavra, ctx))})
    return [ctx for ctx, _ in totais.most_common(k)]


def top_sucessores(tabela: Tabela, contextos: list[tuple[str, ...]], k: int = 10) -> list[str]:
    c: Counter = Counter()
    for ctx in contextos:
        c.update({w: n for w, n in tabela[ctx].items() if eh_palavra(w)})
    return [w for w, _ in c.most_common(k)]


def submatriz(tabela: Tabela, contextos: list[tuple[str, ...]], colunas: list[str]) -> list[list[float]]:
    return [[probabilidade(tabela, ctx, w) for w in colunas] for ctx in contextos]


def heatmap(ax, M: list[list[float]], linhas: list[str], colunas: list[str], titulo: str) -> None:
    im = ax.imshow(M, cmap="YlOrRd")
    ax.set_xticks(range(len(colunas)), colunas, rotation=45, ha="right")
    ax.set_yticks(range(len(linhas)), linhas)
    ax.set_xlabel("próximo token")
    ax.set_title(titulo)
    topo = max(max(r) for r in M) or 1
    for i, row in enumerate(M):
        for j, p in enumerate(row):
            ax.text(j, i, f"{p:.2f}", ha="center", va="center", fontsize=7, color="white" if p > topo / 2 else "black")
    ax.figure.colorbar(im, ax=ax, fraction=0.046)

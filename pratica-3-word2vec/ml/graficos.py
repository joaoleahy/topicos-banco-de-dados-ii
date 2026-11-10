"""Etapa 7 — Ver os vetores: heatmap de similaridade e plano 2D.

Heatmap: a mesma matriz de cosseno entre as palavras, com a cor no lugar do
número (mais claro = mais similar).

Conta no plano: "verbos - verbo + substantivo" como movimento. A seta de
`verbo` até `verbos` é o que a conta extrai (singular -> plural); essa seta,
saindo de `substantivo`, leva ao vetor resultado.

Plano 2D: cada vetor tem 100 dimensões; o PCA acha as duas direções em que os
vetores escolhidos mais variam e projeta cada palavra nelas. Palavras próximas
no plano tendem a ser próximas no modelo, mas a projeção perde informação: o
título do gráfico diz quanto da variância o plano guarda.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from gensim.models import KeyedVectors

from ml import vetores


def matriz_similaridade(kv: KeyedVectors, palavras: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        [[kv.similarity(a, b) for b in palavras] for a in palavras], index=palavras, columns=palavras
    )


def heatmap(kv: KeyedVectors, palavras: list[str], titulo: str = "Similaridade de cosseno", ax=None):
    sim = matriz_similaridade(kv, palavras)
    n = len(palavras)
    if ax is None:
        _, ax = plt.subplots(figsize=(max(4.5, 0.55 * n + 2), max(4, 0.55 * n + 1.5)))
    # A diagonal é sempre 1: fica cinza, fora da escala, para a cor mostrar as diferenças entre as palavras.
    diagonal = np.eye(n, dtype=bool)
    fora = sim.values[~diagonal]
    cores = plt.get_cmap("viridis").copy()
    cores.set_bad("lightgray")
    imagem = ax.imshow(np.where(diagonal, np.nan, sim.values), cmap=cores, vmin=min(0.0, fora.min()), vmax=fora.max())
    ax.set_xticks(range(n), palavras, rotation=45, ha="right")
    ax.set_yticks(range(n), palavras)
    if n <= 12:
        meio = (imagem.norm.vmin + imagem.norm.vmax) / 2
        for i in range(n):
            for j in range(n):
                valor = sim.values[i, j]
                ax.text(j, i, f"{valor:.2f}", ha="center", va="center", fontsize=9,
                        color="black" if i == j or valor > meio else "white")
    ax.set_title(titulo)
    ax.figure.colorbar(imagem, ax=ax, fraction=0.046, pad=0.04)
    ax.figure.tight_layout()
    return ax


def com_vizinhos(kv: KeyedVectors, alvos: list[str], k: int = 8) -> dict[str, str]:
    """Cada alvo e seus k vizinhos -> {palavra: alvo do grupo}. Uma palavra fica no primeiro grupo em que aparece."""
    grupo: dict[str, str] = {alvo: alvo for alvo in alvos if alvo in kv}
    for alvo in list(grupo):
        for vizinho, _ in kv.most_similar(alvo, topn=k):
            grupo.setdefault(vizinho, alvo)
    return grupo


def projetar_2d(kv: KeyedVectors, palavras: list[str]) -> tuple[np.ndarray, float]:
    """PCA dos vetores normalizados (comprimento 1, como no cosseno). Devolve as coordenadas e a variância guardada."""
    x = np.array([kv.get_vector(p, norm=True) for p in palavras])
    x = x - x.mean(axis=0)
    u, s, _ = np.linalg.svd(x, full_matrices=False)
    variancia = float((s[:2] ** 2).sum() / (s**2).sum())
    return u[:, :2] * s[:2], variancia


def plano_2d(kv: KeyedVectors, alvos: list[str], k: int = 8, titulo: str = "Vetores no plano", ax=None):
    """Os alvos (marcador grande, negrito) e os k vizinhos de cada um, na cor do alvo."""
    grupo = com_vizinhos(kv, alvos, k)
    palavras = list(grupo)
    xy, variancia = projetar_2d(kv, palavras)
    if ax is None:
        _, ax = plt.subplots(figsize=(9, 6.5))
    cores = {alvo: f"C{i}" for i, alvo in enumerate(a for a in alvos if a in kv)}
    for (x, y), palavra in zip(xy, palavras):
        alvo = grupo[palavra]
        eh_alvo = palavra == alvo
        ax.scatter(x, y, s=140 if eh_alvo else 30, color=cores[alvo], edgecolor="black" if eh_alvo else "none",
                   zorder=3 if eh_alvo else 2, label=alvo if eh_alvo else None)
        ax.annotate(palavra, (x, y), xytext=(5, 5), textcoords="offset points",
                    fontsize=11 if eh_alvo else 8, fontweight="bold" if eh_alvo else "normal")
    ax.axhline(0, lw=0.5, color="gray")
    ax.axvline(0, lw=0.5, color="gray")
    ax.set_xlabel("componente 1")
    ax.set_ylabel("componente 2")
    ax.set_title(f"{titulo} — PCA 2D guarda {variancia:.0%} da variância")
    ax.legend(title="alvo e vizinhos", fontsize=8)
    ax.figure.tight_layout()
    return ax


def conta_2d(kv: KeyedVectors, expressao: str, k: int = 5, titulo: str = "", ax=None):
    """A conta "a - b + c" como movimento: a seta b -> a, saindo de c, leva ao resultado."""
    positivos, negativos = vetores.ler_expressao(expressao)
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 5.5))
    faltam = vetores.fora_do_vocabulario(kv, expressao)
    if faltam or len(positivos) != 2 or len(negativos) != 1:
        ax.text(0.5, 0.5, "fora do vocabulário: " + ", ".join(faltam) if faltam else "a conta precisa ser a - b + c",
                ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()
        return ax
    a, c = positivos
    b = negativos[0]
    vizinhos = [w for w, _ in vetores.resolver(kv, expressao, k)]
    # O cosseno compara só a direção: o resultado entra com comprimento 1, como as palavras.
    # Por isso a seta c -> resultado sai quase igual à seta b -> a, não idêntica.
    resultado = vetores.calcular(kv, expressao)
    pontos = np.array(
        [kv.get_vector(w, norm=True) for w in (a, b, c)]
        + [resultado / np.linalg.norm(resultado)]
        + [kv.get_vector(w, norm=True) for w in vizinhos]
    )
    centrado = pontos - pontos.mean(axis=0)
    u, s, _ = np.linalg.svd(centrado, full_matrices=False)
    xy = u[:, :2] * s[:2]
    variancia = float((s[:2] ** 2).sum() / (s**2).sum())
    pa, pb, pc, resultado = xy[:4]

    def seta(de, ate, cor, rotulo):
        ax.annotate("", xy=ate, xytext=de, arrowprops=dict(arrowstyle="->", color=cor, lw=2, shrinkA=6, shrinkB=6))
        ax.annotate(rotulo, (de + ate) / 2, xytext=(6, 6), textcoords="offset points", fontsize=8, color=cor)

    seta(pb, pa, "C0", f"{a} − {b}")
    seta(pc, resultado, "C1", f"+ ({a} − {b})")
    for ponto, palavra in zip((pa, pb, pc), (a, b, c)):
        ax.scatter(*ponto, s=110, color="C0", edgecolor="black", zorder=3)
        ax.annotate(palavra, ponto, xytext=(7, -12), textcoords="offset points", fontsize=11, fontweight="bold")
    ax.scatter(*resultado, s=200, marker="*", color="C1", edgecolor="black", zorder=4)
    ax.annotate("resultado", resultado, xytext=(7, -12), textcoords="offset points", fontsize=10, color="C1", fontweight="bold")
    for i, (ponto, palavra) in enumerate(zip(xy[4:], vizinhos)):
        ax.scatter(*ponto, s=40 if i else 90, color="C2", zorder=2)
        ax.annotate(f"{i + 1}. {palavra}", ponto, xytext=(6, 5), textcoords="offset points",
                    fontsize=9, fontweight="bold" if i == 0 else "normal", color="C2")
    ax.margins(0.18)
    ax.set_xlabel("componente 1")
    ax.set_ylabel("componente 2")
    ax.set_title(f"{titulo + ': ' if titulo else ''}{expressao}\nPCA 2D guarda {variancia:.0%} da variância", fontsize=10)
    ax.figure.tight_layout()
    return ax


def conta_2d_modelos(modelos: dict[str, KeyedVectors], expressao: str, k: int = 5):
    """A mesma conta em cada modelo, lado a lado."""
    fig, eixos = plt.subplots(1, len(modelos), figsize=(7 * len(modelos), 5.5), squeeze=False)
    for ax, (nome, kv) in zip(eixos[0], modelos.items()):
        conta_2d(kv, expressao, k, titulo=nome, ax=ax)
    return fig

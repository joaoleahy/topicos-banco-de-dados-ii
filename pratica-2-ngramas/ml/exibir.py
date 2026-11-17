"""Exibição lado a lado dos textos gerados (HTML no notebook)."""

from __future__ import annotations

from html import escape

from ml import metricas, ngrama

NOMES = metricas.NOMES_ORDEM


def lado_a_lado(colunas: dict[str, tuple[str, dict[str, str]]]) -> str:
    nomes = list(colunas)
    metricas_nomes = list(next(iter(colunas.values()))[1])
    cab = "".join(f"<th style='text-align:left'>{escape(n)}</th>" for n in nomes)
    textos = "".join(
        f"<td style='vertical-align:top;text-align:left;width:{100 // len(nomes)}%'>{escape(t)}</td>"
        for t, _ in colunas.values()
    )
    linhas = "".join(
        f"<tr><th style='text-align:left'>{escape(m)}</th>"
        + "".join(f"<td style='text-align:left'>{escape(colunas[n][1][m])}</td>" for n in nomes)
        + "</tr>"
        for m in metricas_nomes
    )
    return (
        f"<table><tr><th></th>{cab}</tr><tr><th style='text-align:left'>texto</th>{textos}</tr>"
        f"{linhas}</table>"
    )


def comparar_modelos(
    tabelas: dict[int, ngrama.Tabela],
    docs: list[list[str]],
    inicio: list[str],
    max_palavras: int = 150,
    seed: int = 42,
    exibir: bool = True,
    **kw,
) -> dict[str, list[str]]:
    textos = {
        NOMES[n]: ngrama.gerar(tabelas, n, list(inicio), max_palavras=max_palavras, seed=seed, **kw)
        for n in NOMES
    }
    if exibir:
        from IPython.display import HTML, display

        display(HTML(lado_a_lado({k: (ngrama.juntar(t), metricas.resumo(t, docs)) for k, t in textos.items()})))
    return textos

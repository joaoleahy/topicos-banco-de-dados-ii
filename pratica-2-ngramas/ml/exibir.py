"""Exibição lado a lado dos textos gerados (HTML no notebook)."""

from __future__ import annotations

from html import escape


def lado_a_lado(colunas: dict[str, tuple[str, dict[str, str]]]) -> str:
    nomes = list(colunas)
    metricas = list(next(iter(colunas.values()))[1])
    cab = "".join(f"<th style='text-align:left'>{escape(n)}</th>" for n in nomes)
    textos = "".join(
        f"<td style='vertical-align:top;text-align:left;width:{100 // len(nomes)}%'>{escape(t)}</td>"
        for t, _ in colunas.values()
    )
    linhas = "".join(
        f"<tr><th style='text-align:left'>{escape(m)}</th>"
        + "".join(f"<td style='text-align:left'>{escape(colunas[n][1][m])}</td>" for n in nomes)
        + "</tr>"
        for m in metricas
    )
    return (
        f"<table><tr><th></th>{cab}</tr><tr><th style='text-align:left'>texto</th>{textos}</tr>"
        f"{linhas}</table>"
    )

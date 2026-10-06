"""Etapa — Limpar o Markdown herdado da extração de PDF.

Descarta a linha inteira (não só o caractere):

- heading (`## 3.1. Criação dos catálogos`): não é frase, e o número traz um `.`
  que viraria fim de frase falso;
- tabela (`|sofreu [sofrer] <fmc> V PS 3S|`): células soltas e saída de
  etiquetador, não é texto corrido.
"""

from __future__ import annotations

MARCADORES = ("#", "|")


def eh_markdown(linha: str) -> bool:
    return linha.lstrip().startswith(MARCADORES)


def remover_markdown(texto: str) -> str:
    return "\n".join(l for l in texto.split("\n") if not eh_markdown(l))

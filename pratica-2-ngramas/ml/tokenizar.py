"""Etapa 2 — Tokenizar mantendo a pontuação.

O `artigo_tokenizado` da PRÁTICA 1 não tem pontuação (era o certo para contar
palavras). Para gerar texto, o ponto final é informação: é ele que diz ao
modelo onde a frase acaba.

Regra: minúsculas; palavra = sequência de letras/dígitos (com hífen ou
apóstrofo no meio); qualquer outro caractere visível vira um token sozinho.
"""

from __future__ import annotations

import re

TOKEN = re.compile(r"\w+(?:[-']\w+)*|[^\w\s]")


def tokenizar(texto: str) -> list[str]:
    return TOKEN.findall(texto.lower())


def eh_palavra(token: str) -> bool:
    return token[0].isalnum()

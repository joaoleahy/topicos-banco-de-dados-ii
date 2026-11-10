"""Etapa 6 — Consultas sobre os vetores: similaridade e aritmética.

Similaridade de cosseno: compara a direção de dois vetores (1 = mesma direção,
0 = sem relação). `similares` devolve as palavras do vocabulário com maior
cosseno em relação à palavra consultada.

Aritmética: "rei - homem + mulher" soma os vetores normalizados (comprimento 1)
de `rei` e `mulher` e subtrai o de `homem`. O resultado é um vetor novo, que
não é de nenhuma palavra; a resposta é a palavra mais próxima dele, fora as
palavras da própria conta (senão a resposta quase sempre seria `rei`).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from gensim.models import KeyedVectors


def similares(kv: KeyedVectors, palavra: str, k: int = 10) -> list[tuple[str, float]]:
    if palavra not in kv:
        return []
    return kv.most_similar(palavra, topn=k)


def tabela_similares(modelos: dict[str, KeyedVectors], palavra: str, k: int = 10) -> pd.DataFrame:
    """Uma coluna por modelo: "palavra (cosseno)" em ordem de similaridade."""
    colunas = {}
    for nome, kv in modelos.items():
        vizinhos = similares(kv, palavra, k)
        colunas[nome] = [f"{w} ({s:.2f})" for w, s in vizinhos] or ["fora do vocabulário"]
    return pd.DataFrame({nome: pd.Series(c) for nome, c in colunas.items()}).fillna("")


def ler_expressao(expressao: str) -> tuple[list[str], list[str]]:
    """ "rei - homem + mulher" -> (["rei", "mulher"], ["homem"]). Sinais separados por espaço."""
    positivos, negativos, sinal = [], [], "+"
    for parte in expressao.split():
        if parte in ("+", "-"):
            sinal = parte
            continue
        (negativos if sinal == "-" else positivos).append(parte)
        sinal = "+"
    return positivos, negativos


def fora_do_vocabulario(kv: KeyedVectors, expressao: str) -> list[str]:
    positivos, negativos = ler_expressao(expressao)
    return [w for w in positivos + negativos if w not in kv]


def calcular(kv: KeyedVectors, expressao: str) -> np.ndarray:
    """O vetor resultado da conta, com cada termo normalizado (como o gensim faz)."""
    positivos, negativos = ler_expressao(expressao)
    resultado = np.zeros(kv.vector_size, dtype=np.float32)
    for w in positivos:
        resultado += kv.get_vector(w, norm=True)
    for w in negativos:
        resultado -= kv.get_vector(w, norm=True)
    return resultado


def resolver(kv: KeyedVectors, expressao: str, k: int = 5) -> list[tuple[str, float]]:
    """Palavras mais próximas do vetor resultado, sem as palavras da conta."""
    positivos, negativos = ler_expressao(expressao)
    return kv.most_similar(positive=positivos, negative=negativos, topn=k)


def tabela_analogias(modelos: dict[str, KeyedVectors], expressoes: list[str], k: int = 3) -> pd.DataFrame:
    linhas = []
    for expressao in expressoes:
        linha = {"conta": expressao}
        for nome, kv in modelos.items():
            faltam = fora_do_vocabulario(kv, expressao)
            if faltam:
                linha[nome] = "fora do vocabulário: " + ", ".join(faltam)
            else:
                linha[nome] = ", ".join(f"{w} ({s:.2f})" for w, s in resolver(kv, expressao, k))
        linhas.append(linha)
    return pd.DataFrame(linhas).set_index("conta")

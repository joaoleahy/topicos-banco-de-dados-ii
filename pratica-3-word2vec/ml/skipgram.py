"""Etapa 4 — Treinar o Word2Vec com o algoritmo skip-gram (gensim, `sg=1`).

Skip-gram: para cada palavra da frase, o modelo tenta prever as palavras
vizinhas dentro da janela. Os pesos aprendidos nessa tarefa viram o vetor da
palavra; palavras com vizinhos parecidos terminam com vetores parecidos.

Reprodutibilidade: `workers=1` e `seed` fixa não bastam. O gensim sorteia o
vetor inicial de cada palavra com `hash(palavra)`, e o `hash` do Python muda a
cada execução. `hash_estavel` troca isso por um hash fixo (MD5).
"""

from __future__ import annotations

import hashlib

from gensim.models import Word2Vec


def hash_estavel(texto: str) -> int:
    return int(hashlib.md5(texto.encode("utf-8")).hexdigest()[:8], 16)


def treinar(
    frases: list[list[str]],
    *,
    dimensoes: int,
    janela: int,
    frequencia_minima: int,
    epocas: int,
    exemplos_negativos: int = 5,
    seed: int = 42,
) -> Word2Vec:
    return Word2Vec(
        sentences=frases,
        sg=1,  # skip-gram (0 seria CBOW)
        vector_size=dimensoes,
        window=janela,
        min_count=frequencia_minima,
        epochs=epocas,
        negative=exemplos_negativos,
        seed=seed,
        workers=1,
        hashfxn=hash_estavel,
    )

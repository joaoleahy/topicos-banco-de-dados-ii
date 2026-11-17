"""Etapa 5 — Modelos de embeddings pré-treinados (100 dimensões).

- Português (`pt`): `nilc-nlp/word2vec-skip-gram-100d` (NILC, ~1,39 bilhão de tokens,
  publicado no próprio STIL 2017 como `article_15`).
- Inglês (`en`): `glove-wiki-gigaword-100` (Wikipedia 2014 + Gigaword 5, 400 mil palavras,
  100 dimensões, via `gensim.downloader`).

Os downloads ficam no cache local (Hugging Face / gensim-data), fora do repositório.
"""

from __future__ import annotations

import gensim.downloader as api
from gensim.models import KeyedVectors
from huggingface_hub import hf_hub_download
from huggingface_hub.utils import logging as hf_logging
from safetensors.numpy import load_file

REPO_PT = "nilc-nlp/word2vec-skip-gram-100d"
REPO = REPO_PT
MODELO_EN = "glove-wiki-gigaword-100"

hf_logging.set_verbosity_error()  # o repositório é público: sem aviso de "sem HF_TOKEN"


def baixar(repo: str = REPO_PT) -> tuple[str, str]:
    return hf_hub_download(repo, "vocab.txt"), hf_hub_download(repo, "embeddings.safetensors")


def carregar_pt(repo: str = REPO_PT) -> KeyedVectors:
    caminho_vocab, caminho_vetores = baixar(repo)
    with open(caminho_vocab, encoding="utf-8") as f:
        vocab = [linha.rstrip("\n") for linha in f]
    vetores = load_file(caminho_vetores)["embeddings"]
    assert len(vocab) == len(vetores), "vocab.txt e embeddings.safetensors desalinhados"

    kv = KeyedVectors(vector_size=vetores.shape[1])
    kv.add_vectors(vocab, vetores)
    return kv


def carregar_en(modelo: str = MODELO_EN) -> KeyedVectors:
    return api.load(modelo)


def carregar(idioma: str = "pt", repo: str | None = None) -> KeyedVectors:
    if idioma == "en":
        return carregar_en(repo or MODELO_EN)
    return carregar_pt(repo or REPO_PT)

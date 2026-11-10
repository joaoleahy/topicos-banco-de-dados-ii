"""Etapa 5 — Word2Vec pré-treinado do NILC (skip-gram, 100 dimensões).

Treinado em ~1,39 bilhão de tokens de português (Wikipedia, notícias, legendas,
literatura...). É o modelo do artigo "Portuguese Word Embeddings: Evaluating on
Word Analogies and Natural Language Tasks" (Hartmann et al.), publicado no
próprio STIL 2017 — está no nosso corpus como `article_15`.

O Hugging Face guarda dois arquivos alinhados linha a linha:
- `vocab.txt`: uma palavra por linha;
- `embeddings.safetensors`: a matriz [palavras x 100].

O download (~380 MB) fica no cache do Hugging Face, fora do repositório.
"""

from __future__ import annotations

from gensim.models import KeyedVectors
from huggingface_hub import hf_hub_download
from huggingface_hub.utils import logging as hf_logging
from safetensors.numpy import load_file

REPO = "nilc-nlp/word2vec-skip-gram-100d"

hf_logging.set_verbosity_error()  # o repositório é público: sem aviso de "sem HF_TOKEN"


def baixar(repo: str = REPO) -> tuple[str, str]:
    return hf_hub_download(repo, "vocab.txt"), hf_hub_download(repo, "embeddings.safetensors")


def carregar(repo: str = REPO) -> KeyedVectors:
    caminho_vocab, caminho_vetores = baixar(repo)
    with open(caminho_vocab, encoding="utf-8") as f:
        vocab = [linha.rstrip("\n") for linha in f]
    vetores = load_file(caminho_vetores)["embeddings"]
    assert len(vocab) == len(vetores), "vocab.txt e embeddings.safetensors desalinhados"

    kv = KeyedVectors(vector_size=vetores.shape[1])
    kv.add_vectors(vocab, vetores)
    return kv

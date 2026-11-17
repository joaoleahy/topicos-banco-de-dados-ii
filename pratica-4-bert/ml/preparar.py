"""Divisão por artigo e blocos de tokens para MLM."""
import random
from math import ceil

def separar(artigos, fracao_validacao=0.2, seed=42):
    if len(artigos) < 2 or not 0 < fracao_validacao < 1:
        raise ValueError("A divisão exige ao menos dois artigos e fração entre 0 e 1.")
    if len({a['id'] for a in artigos}) != len(artigos):
        raise ValueError("Identificadores de artigos duplicados.")
    ordenados = sorted(artigos, key=lambda a: a['id'])
    random.Random(seed).shuffle(ordenados)
    n = min(len(artigos) - 1, ceil(len(artigos) * fracao_validacao))
    return ordenados[n:], ordenados[:n]


def tokenizar_artigos(artigos, tokenizer):
    """Converte cada texto em IDs, preservando a identificação do artigo."""
    return [
        {'artigo_id': artigo['id'], 'input_ids': tokenizer(
            artigo['artigo_completo'], add_special_tokens=False,
            truncation=False, verbose=False)['input_ids']}
        for artigo in artigos
    ]


def criar_blocos(artigos_tokenizados, tokenizer, tamanho):
    """Divide cada artigo; adiciona tokens especiais e padding sem perder o final."""
    if not 3 <= tamanho <= tokenizer.model_max_length:
        raise ValueError("Tamanho de bloco fora dos limites do tokenizador.")
    capacidade = tamanho - tokenizer.num_special_tokens_to_add(pair=False)
    resultado = []
    for artigo in artigos_tokenizados:
        ids = artigo['input_ids']
        for inicio in range(0, len(ids), capacidade):
            exemplo = tokenizer.prepare_for_model(
                ids[inicio:inicio + capacidade],
                padding='max_length', max_length=tamanho, truncation=False)
            exemplo['special_tokens_mask'] = tokenizer.get_special_tokens_mask(
                exemplo['input_ids'], already_has_special_tokens=True)
            resultado.append({'artigo_id': artigo['artigo_id'], **exemplo})
    return resultado

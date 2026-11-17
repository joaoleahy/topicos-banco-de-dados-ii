"""Representações de palavras completas, alinhadas ao texto por offsets."""
import csv
import json
import re
from bisect import bisect_right
from collections import Counter
from pathlib import Path

import torch

PALAVRA = re.compile(r"[^\W\d_]+(?:[-’'][^\W\d_]+)*", re.UNICODE)


def preparar_contextos(artigos, tokenizer, tamanho):
    """Blocos sem cortar palavras; mantém pontuação no contexto, fora dos alvos."""
    if not tokenizer.is_fast:
        raise ValueError('O alinhamento exige um tokenizador fast.')
    if not 3 <= tamanho <= tokenizer.model_max_length:
        raise ValueError('Tamanho de contexto inválido.')
    capacidade = tamanho - tokenizer.num_special_tokens_to_add(pair=False)
    contextos = []
    for artigo in artigos:
        texto = artigo['artigo_completo']
        palavras = list(PALAVRA.finditer(texto))
        inicios = [m.start() for m in palavras]
        codificado = tokenizer(texto, add_special_tokens=False, return_offsets_mapping=True,
                               truncation=False, verbose=False)
        ids = codificado['input_ids']
        alinhamento = []
        for inicio, fim in codificado['offset_mapping']:
            indice = bisect_right(inicios, inicio) - 1
            alinhamento.append(indice if indice >= 0 and fim <= palavras[indice].end()
                               and fim > inicio else None)
        inicio = 0
        while inicio < len(ids):
            fim = min(inicio + capacidade, len(ids))
            # Se o limite atravessar uma palavra, ela inteira passa ao próximo bloco.
            while fim < len(ids) and fim > inicio and alinhamento[fim] is not None and alinhamento[fim] == alinhamento[fim - 1]:
                fim -= 1
            if fim == inicio:
                raise ValueError(f"Palavra maior que o contexto em {artigo['id']}.")
            entrada = tokenizer.prepare_for_model(ids[inicio:fim], padding='max_length',
                                                  max_length=tamanho, truncation=False)
            grupos = {}
            for posicao in range(inicio, fim):
                indice = alinhamento[posicao]
                if indice is not None:
                    grupos.setdefault(indice, []).append(posicao - inicio + 1)  # [CLS]
            ocorrencias = []
            for indice, posicoes in grupos.items():
                if any(entrada['input_ids'][p] == tokenizer.unk_token_id for p in posicoes):
                    continue
                palavra = palavras[indice]
                ocorrencias.append({'palavra': palavra.group().lower(), 'posicoes': posicoes,
                                    'inicio': palavra.start(), 'fim': palavra.end()})
            contextos.append({'artigo_id': artigo['id'], 'entrada': dict(entrada),
                              'ocorrencias': ocorrencias})
            inicio = fim
    return contextos


def extrair_ocorrencias(encoder, contextos, dispositivo, tamanho_lote):
    """Média dos subtokens da última camada; uma representação por ocorrência."""
    encoder.eval()
    with torch.inference_mode():
        for inicio in range(0, len(contextos), tamanho_lote):
            lote = contextos[inicio:inicio + tamanho_lote]
            entradas = {k: torch.tensor([c['entrada'][k] for c in lote], device=dispositivo)
                        for k in lote[0]['entrada']}
            estados = encoder(**entradas).last_hidden_state.cpu()
            for contexto, matriz in zip(lote, estados):
                for ocorrencia in contexto['ocorrencias']:
                    yield {**ocorrencia, 'artigo_id': contexto['artigo_id'],
                           'vetor': matriz[ocorrencia['posicoes']].mean(dim=0).clone()}


def acumular_ocorrencias(ocorrencias):
    """Soma em fluxo: não mantém todos os vetores de ocorrências na memória."""
    somas, contagens = {}, Counter()
    for ocorrencia in ocorrencias:
        palavra, vetor = ocorrencia['palavra'], ocorrencia['vetor']
        if palavra not in somas:
            somas[palavra] = torch.zeros_like(vetor)
        somas[palavra] += vetor
        contagens[palavra] += 1
    return somas, contagens


def calcular_medias(somas, contagens):
    return {palavra: soma / contagens[palavra] for palavra, soma in somas.items()}


def selecionar_candidatos(contagens, frequencia_minima, tamanho_minimo):
    return sorted(p for p, n in contagens.items() if n >= frequencia_minima and len(p) >= tamanho_minimo)


def normalizar_vetores(vetores):
    normalizados = {}
    for palavra, vetor in vetores.items():
        norma = vetor.norm()
        if not torch.isfinite(vetor).all() or norma <= 0:
            raise ValueError(f'Vetor inválido: {palavra}')
        normalizados[palavra] = vetor / norma
    return normalizados


def buscar_similares(palavra, normalizados, candidatos, quantidade):
    if palavra not in normalizados:
        raise KeyError(f'Palavra sem ocorrências válidas: {palavra}')
    candidatos = [p for p in candidatos if p != palavra]
    if not candidatos:
        return []
    matriz = torch.stack([normalizados[p] for p in candidatos])
    scores = matriz @ normalizados[palavra]
    ranking = sorted(zip(candidatos, scores.tolist()), key=lambda par: (-par[1], par[0]))
    return ranking[:quantidade]


def salvar_vetores(vetores, contagens, destino):
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    torch.save({'vetores': vetores, 'contagens': dict(contagens)}, destino)


def exportar_alvos(alvos, vetores, contagens, rankings, destino):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    dados = {item: {'palavra': palavra, 'ocorrencias': contagens[palavra],
                    'vetor': vetores[palavra].tolist(), 'similares': rankings[palavra]}
             for item, palavra in alvos.items()}
    (destino / 'palavras-alvo.json').write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding='utf-8')
    with (destino / 'similares.csv').open('w', encoding='utf-8', newline='') as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(['alvo', 'posicao', 'termo', 'cosseno'])
        for palavra, ranking in rankings.items():
            for posicao, (termo, score) in enumerate(ranking, 1):
                writer.writerow([palavra, posicao, termo, score])

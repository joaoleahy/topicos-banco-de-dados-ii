"""Operações de MLM; o notebook coordena preparação, épocas e seleção do modelo."""
import json
import random
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from transformers import AutoModelForMaskedLM, DataCollatorForLanguageModeling


def fixar_semente(seed):
    random.seed(seed)
    torch.manual_seed(seed)


def escolher_dispositivo():
    if torch.cuda.is_available():
        return 'cuda'
    if torch.backends.mps.is_available():
        return 'mps'
    return 'cpu'


def criar_mascarador(tokenizer, probabilidade):
    """Seleciona alvos MLM; aplica a regra 80% máscara, 10% aleatório, 10% original."""
    return DataCollatorForLanguageModeling(tokenizer, mlm_probability=probabilidade)


def criar_lotes(blocos, mascarador, tamanho_lote, embaralhar, seed):
    """Aplica novas máscaras a cada passagem pelos lotes."""
    exemplos = [{k: v for k, v in b.items() if k != 'artigo_id'} for b in blocos]
    return DataLoader(exemplos, batch_size=tamanho_lote, shuffle=embaralhar,
                      collate_fn=mascarador,
                      generator=torch.Generator().manual_seed(seed) if embaralhar else None)


def fixar_mascaras(lotes):
    """Materializa os lotes uma vez, mantendo os mesmos alvos nas avaliações."""
    return list(lotes)


def carregar_modelo(nome, device):
    return AutoModelForMaskedLM.from_pretrained(nome).to(device)


def criar_otimizador(modelo, taxa_aprendizado, weight_decay):
    return torch.optim.AdamW(modelo.parameters(), lr=taxa_aprendizado,
                            weight_decay=weight_decay)


def avaliar(modelo, lotes, device):
    modelo.eval()
    soma, total = 0.0, 0
    with torch.no_grad():
        for lote in lotes:
            n = int((lote['labels'] != -100).sum())
            if not n:
                continue
            perda = modelo(**{k: v.to(device) for k, v in lote.items()}).loss
            soma += perda.item() * n
            total += n
    if not total:
        raise ValueError('Nenhum token selecionado na validação.')
    return soma / total



def treinar_epoca(modelo, lotes, otimizador, device, limite_gradiente):
    """Atualiza os pesos e retorna a perda média por token-alvo da época."""
    modelo.train()
    soma, total = 0.0, 0
    for passo, lote in enumerate(lotes, 1):
        n = int((lote['labels'] != -100).sum())
        if not n:
            continue
        otimizador.zero_grad(set_to_none=True)
        perda = modelo(**{k: v.to(device) for k, v in lote.items()}).loss
        if not torch.isfinite(perda):
            raise RuntimeError('Perda não finita no treinamento.')
        perda.backward()
        torch.nn.utils.clip_grad_norm_(modelo.parameters(), limite_gradiente)
        otimizador.step()
        soma += perda.item() * n
        total += n
        if passo % 20 == 0:
            print(f'Lote {passo}/{len(lotes)}', flush=True)
    if not total:
        raise ValueError('Nenhum token selecionado no treino.')
    return soma / total


def salvar_modelo(modelo, tokenizer, destino):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    modelo.save_pretrained(destino)
    tokenizer.save_pretrained(destino)


def salvar_resultado(resultado, destino):
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding='utf-8')

# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "spacy>=3.8,<3.9",
#   "langdetect",
#   "pt-core-news-sm @ https://github.com/explosion/spacy-models/releases/download/pt_core_news_sm-3.8.0/pt_core_news_sm-3.8.0-py3-none-any.whl",
#   "en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl",
# ]
# ///
"""Etapa 5 — Processar.

Para cada artigo: detecta o idioma (langdetect no titulo+resumo), tokeniza,
marca POS e gera lemas com spaCy (modelo pt ou en), e preenche os campos
artigo_tokenizado / pos_tagger / lema do JSON.

- Tokenizacao exclui espacos e pontuacao; stopwords ficam (regra da tarefa).
- pos_tagger no formato "TAG_token" (ex.: "NOUN_casa").
- artigo_tokenizado/pos_tagger/lema tem o mesmo tamanho e ordem.

Uso:
    uv run ml/processar.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import spacy
from langdetect import DetectorFactory, detect

DetectorFactory.seed = 0  # resultado estavel

ROOT = Path(__file__).resolve().parent.parent
JSON_DIR = ROOT / "corpus" / "json"
META_FILE = ROOT / "corpus" / "data" / "artigos.json"

MODELOS = {"pt": "pt_core_news_sm", "en": "en_core_web_sm"}


def detectar_idioma(texto: str) -> str:
    """Idioma do artigo a partir do corpo (o resumo do SOL pode estar em outra lingua)."""
    try:
        lang = detect(texto)
    except Exception:  # noqa: BLE001
        return "pt"
    return "en" if lang.startswith("en") else "pt"


def processar(nlp, texto: str) -> tuple[list[str], list[str], list[str]]:
    doc = nlp(texto)
    tokens, pos, lemas = [], [], []
    for t in doc:
        if t.is_space or t.is_punct:
            continue
        tokens.append(t.text)
        pos.append(f"{t.pos_}_{t.text}")
        lemas.append(t.lemma_)
    return tokens, pos, lemas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    metas = json.loads(META_FILE.read_text())
    por_ordem = {f"article_{r['ordem']:02d}": r for r in metas}

    nlp = {lang: spacy.load(modelo) for lang, modelo in MODELOS.items()}

    for n, arq in enumerate(sorted(JSON_DIR.glob("article_*.json")), 1):
        dados = json.loads(arq.read_text())
        idioma = detectar_idioma(dados["artigo_completo"])
        dados["idioma"] = idioma
        por_ordem[arq.stem]["idioma"] = idioma
        if dados["artigo_tokenizado"] and not args.force:
            print(f"[{n}] {arq.stem} ja processado", file=sys.stderr)
            continue
        tokens, pos, lemas = processar(nlp[idioma], dados["artigo_completo"])
        dados["artigo_tokenizado"], dados["pos_tagger"], dados["lema"] = tokens, pos, lemas
        arq.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n")
        print(f"[{n}] {arq.stem} ({idioma}): {len(tokens)} tokens", file=sys.stderr)

    META_FILE.write_text(json.dumps(metas, ensure_ascii=False, indent=2) + "\n")
    from collections import Counter

    print("idioma:", dict(Counter(d["idioma"] for d in por_ordem.values())), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

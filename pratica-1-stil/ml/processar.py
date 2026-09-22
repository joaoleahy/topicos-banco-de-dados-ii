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

Para cada artigo: detecta o idioma (langdetect no corpo), tokeniza, marca POS
e gera lemas com spaCy (modelo pt ou en), preenche artigo_tokenizado /
pos_tagger / lema, e extrai keywords do titulo+resumo (o SOL/PDF nao trazem).

- Tokenizacao exclui espacos e pontuacao; stopwords ficam (regra da tarefa).
- pos_tagger no formato "TAG_token" (ex.: "NOUN_casa").
- artigo_tokenizado/pos_tagger/lema tem o mesmo tamanho e ordem.
- keywords: sintagmas nominais do titulo (prioridade) e do resumo.

Uso:
    uv run ml/processar.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

import spacy
from langdetect import DetectorFactory, detect

DetectorFactory.seed = 0  # resultado estavel

ROOT = Path(__file__).resolve().parent.parent
JSON_DIR = ROOT / "corpus" / "json"
META_FILE = ROOT / "corpus" / "data" / "artigos.json"

MODELOS = {"pt": "pt_core_news_sm", "en": "en_core_web_sm"}
N_KEYWORDS = 6
_POS_KW = {"ADJ", "NOUN", "PROPN"}
_LIGA = {"de", "da", "do", "dos", "das", "of"}
_GENERICOS = {
    "abordagem",
    "an approach",
    "artigo",
    "case",
    "case study",
    "este artigo",
    "este trabalho",
    "estudo",
    "ferramenta",
    "method",
    "método",
    "objective",
    "objetivo",
    "paper",
    "pesquisa",
    "proposta",
    "research",
    "resultado",
    "resultados",
    "results",
    "the objective",
    "this paper",
    "this work",
    "tool",
    "trabalho",
    "work",
}


def detectar_idioma(texto: str) -> str:
    """Idioma do artigo a partir do corpo (o resumo do SOL pode estar em outra lingua)."""
    try:
        lang = detect(texto)
    except Exception:  # noqa: BLE001
        return "pt"
    return "en" if lang.startswith("en") else "pt"


def _lingua(texto: str) -> str:
    return detectar_idioma(texto) if texto.strip() else "pt"


def _frases_nominais(doc) -> list[str]:
    """Sintagmas NOM/ADJ ligados só por de/da/do/of — evita engolir o título inteiro."""
    toks = [t for t in doc if not t.is_space]
    frases: list[str] = []
    i = 0
    while i < len(toks):
        t = toks[i]
        if t.pos_ in _POS_KW and not t.like_num:
            start = i
            i += 1
            while i < len(toks) and (i - start) < 5:
                cur = toks[i]
                if cur.pos_ in _POS_KW and not cur.like_num:
                    i += 1
                    continue
                if (
                    cur.pos_ == "ADP"
                    and cur.text.lower() in _LIGA
                    and i + 1 < len(toks)
                    and toks[i + 1].pos_ in _POS_KW
                ):
                    i += 2
                    continue
                break
            partes = [x.text for x in toks[start:i] if x.pos_ != "DET"]
            frase = re.sub(r"\s+", " ", " ".join(partes)).strip(" .;,:")
            if len(frase) >= 3:
                frases.append(frase)
        else:
            i += 1
    return frases


def extrair_keywords(nlp: dict, titulo: str, resumo: str, k: int = N_KEYWORDS) -> list[str]:
    """Keywords do título (prioridade) + resumo. O SOL/PDF não trazem o campo."""
    do_titulo = _frases_nominais(nlp[_lingua(titulo)](titulo))
    do_resumo = _frases_nominais(nlp[_lingua(resumo)](resumo)) if resumo else []
    tit_low = {f.lower() for f in do_titulo}
    palavras_titulo = {p for f in do_titulo for p in f.lower().split() if len(p) >= 4}

    def ok(frase: str) -> bool:
        low = frase.lower()
        n = len(low.split())
        if low in _GENERICOS or n > 5:
            return False
        if any(x in low.split() for x in ("this", "that", "este", "esta", "esse", "essa", "seus", "suas")):
            return False
        return True

    freq = Counter(f.lower() for f in do_titulo + do_resumo if ok(f))
    scored: list[tuple[float, int, str]] = []
    seen: set[str] = set()
    for frase in do_titulo + do_resumo:
        if not ok(frase):
            continue
        key = frase.lower()
        if key in seen:
            continue
        n = len(frase.split())
        overlap = len({w for w in key.split() if len(w) >= 4} & palavras_titulo)
        score = freq[key] + (5 if key in tit_low else 0) + min(n, 3) + overlap
        if n == 1 and key not in tit_low:
            score -= 2
        scored.append((score, n, frase))
        seen.add(key)

    scored.sort(key=lambda x: (-x[0], -x[1], x[2].lower()))
    escolhidas: list[str] = []
    for _, _, frase in scored:
        low = frase.lower()
        if any(low != e.lower() and (low in e.lower() or e.lower() in low) for e in escolhidas):
            continue
        escolhidas.append(frase)
        if len(escolhidas) >= k:
            break
    return escolhidas


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


def run(force: bool = False) -> int:
    metas = json.loads(META_FILE.read_text())
    por_ordem = {f"article_{r['ordem']:02d}": r for r in metas}
    arquivos = [(p, json.loads(p.read_text())) for p in sorted(JSON_DIR.glob("article_*.json"))]

    falta_tokens = force or any(not d["artigo_tokenizado"] for _, d in arquivos)
    falta_kw = force or any(not d.get("keywords") for _, d in arquivos)
    if not falta_tokens and not falta_kw:
        print("todos os artigos ja processados", file=sys.stderr)
        return 0

    nlp = {lang: spacy.load(modelo) for lang, modelo in MODELOS.items()}

    for n, (arq, dados) in enumerate(arquivos, 1):
        idioma = detectar_idioma(dados["artigo_completo"])
        dados["idioma"] = idioma
        por_ordem[arq.stem]["idioma"] = idioma
        mudou = False

        if not dados["artigo_tokenizado"] or force:
            tokens, pos, lemas = processar(nlp[idioma], dados["artigo_completo"])
            dados["artigo_tokenizado"], dados["pos_tagger"], dados["lema"] = tokens, pos, lemas
            mudou = True
        if not dados.get("keywords") or force:
            dados["keywords"] = extrair_keywords(nlp, dados["titulo"], dados["resumo"])
            mudou = True

        if mudou:
            arq.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n")
        print(
            f"[{n}] {arq.stem} ({idioma}): {len(dados['artigo_tokenizado'])} tokens, "
            f"kw={dados['keywords']}",
            file=sys.stderr,
        )

    META_FILE.write_text(json.dumps(metas, ensure_ascii=False, indent=2) + "\n")
    print("idioma:", dict(Counter(d["idioma"] for d in por_ordem.values())), file=sys.stderr)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    return run(force=args.force)


if __name__ == "__main__":
    raise SystemExit(main())

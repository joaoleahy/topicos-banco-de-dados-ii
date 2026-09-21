# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "spacy>=3.8,<3.9",
#   "wordcloud",
#   "matplotlib",
#   "pt-core-news-sm @ https://github.com/explosion/spacy-models/releases/download/pt_core_news_sm-3.8.0/pt_core_news_sm-3.8.0-py3-none-any.whl",
#   "en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl",
# ]
# ///
"""Etapa 6 — Contar.

Junta os JSONs e monta as estatisticas do corpus pedidas na tarefa:

- quantidade de tokens e de types
- quantidade de sentencas (spaCy)
- quantidade por classe gramatical
- quantidade de lemas (unicos)
- Top 10 palavras (excluindo adjetivos e preposicoes)
- Top 10 substantivos / Top 10 verbos

Regra da tarefa: NAO remover stopwords. A versao "sem stopwords" tambem e
calculada, so pra comparar no notebook.

As nuvens de palavras (pt/en x com/sem stopwords) sao montadas no notebook,
usando as funcoes `carregar`, `frequencias` e `nuvem` deste modulo.

Saida: corpus/estatisticas.json
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from spacy.lang.en.stop_words import STOP_WORDS as STOP_EN  # noqa: E402
from spacy.lang.pt.stop_words import STOP_WORDS as STOP_PT  # noqa: E402
from wordcloud import WordCloud  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
JSON_DIR = ROOT / "corpus" / "json"
SAIDA = ROOT / "corpus" / "estatisticas.json"

STOPWORDS = set(STOP_PT) | set(STOP_EN)
EXCLUIR_TOP = {"ADJ", "ADP"}  # a tarefa pede excluir adjetivos e preposicoes


def carregar() -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted(JSON_DIR.glob("article_*.json"))]


def tags(artigo: dict) -> list[str]:
    return [p.split("_", 1)[0] for p in artigo["pos_tagger"]]


def frequencias(
    artigos: list[dict], idioma: str | None = None, sem_stopwords: bool = False
) -> Counter:
    """Frequencia das palavras (fora adjetivos e preposicoes) para a nuvem."""
    freq: Counter = Counter()
    for a in artigos:
        if idioma and a["idioma"] != idioma:
            continue
        for tok, tag in zip(a["artigo_tokenizado"], tags(a)):
            baixo = tok.lower()
            if tag in EXCLUIR_TOP:
                continue
            if sem_stopwords and baixo in STOPWORDS:
                continue
            freq[baixo] += 1
    return freq


def nuvem(freq: Counter, destino: Path, titulo: str) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    wc = WordCloud(
        width=1600, height=900, background_color="white", colormap="viridis",
        max_words=150, collocations=False,
    ).generate_from_frequencies(freq)
    plt.figure(figsize=(16, 9))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.title(titulo)
    plt.tight_layout()
    plt.savefig(destino, dpi=110)
    plt.close()


def top10(contador: Counter) -> list[list]:
    return [[palavra, n] for palavra, n in contador.most_common(10)]


def run(force: bool = False) -> int:
    if SAIDA.exists() and not force:
        print(f"ja existia: {SAIDA.relative_to(ROOT)}", file=sys.stderr)
        return 0

    artigos = carregar()
    print(f"artigos: {len(artigos)}", file=sys.stderr)

    tokens: list[str] = []
    all_tags: list[str] = []
    lemas: list[str] = []
    for a in artigos:
        tokens += a["artigo_tokenizado"]
        all_tags += tags(a)
        lemas += a["lema"]

    import spacy

    modelos = {"pt": spacy.load("pt_core_news_sm"), "en": spacy.load("en_core_web_sm")}
    sentencas = sum(
        len(list(modelos[a["idioma"]](a["artigo_completo"]).sents)) for a in artigos
    )

    palavras, palavras_sem_stop = Counter(), Counter()
    substantivos, verbos = Counter(), Counter()
    for tok, tag in zip(tokens, all_tags):
        baixo = tok.lower()
        if tag not in EXCLUIR_TOP:
            palavras[baixo] += 1
            if baixo not in STOPWORDS:
                palavras_sem_stop[baixo] += 1
        if tag == "NOUN":
            substantivos[baixo] += 1
        elif tag == "VERB":
            verbos[baixo] += 1

    stats = {
        "corpus": {
            "artigos": len(artigos),
            "tokens": len(tokens),
            "types": len({t.lower() for t in tokens}),
            "sentencas": sentencas,
            "lemas_unicos": len({l.lower() for l in lemas}),
        },
        "pos": dict(Counter(all_tags).most_common()),
        "com_stopwords": {
            "top10_palavras": top10(palavras),
            "top10_substantivos": top10(substantivos),
            "top10_verbos": top10(verbos),
        },
        "sem_stopwords": {
            "top10_palavras": top10(palavras_sem_stop),
            "top10_substantivos": top10(substantivos),
            "top10_verbos": top10(verbos),
        },
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n")

    c = stats["corpus"]
    print(f"tokens={c['tokens']} types={c['types']} sentencas={c['sentencas']} lemas={c['lemas_unicos']}")
    print("saida:", SAIDA.relative_to(ROOT))
    return 0


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())

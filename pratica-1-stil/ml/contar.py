# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "spacy>=3.8,<3.9",
#   "wordcloud",
#   "matplotlib",
#   "pt-core-news-lg @ https://github.com/explosion/spacy-models/releases/download/pt_core_news_lg-3.8.0/pt_core_news_lg-3.8.0-py3-none-any.whl",
#   "en-core-web-lg @ https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl",
# ]
# ///
"""Etapa 6 — Contar.

Junta os JSONs e monta as estatisticas do corpus pedidas na tarefa:

- quantidade de tokens e de types
- quantidade de sentencas (spaCy large)
- quantidade por classe gramatical (geral, português e inglês)
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

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: E402
except ImportError:
    plt = None

try:
    from spacy.lang.en.stop_words import STOP_WORDS as STOP_EN  # noqa: E402
    from spacy.lang.pt.stop_words import STOP_WORDS as STOP_PT  # noqa: E402
except ImportError:
    STOP_EN = frozenset()
    STOP_PT = frozenset()

try:
    from wordcloud import WordCloud  # noqa: E402
except ImportError:
    WordCloud = None

ROOT = Path(__file__).resolve().parent.parent
JSON_DIR = ROOT / "corpus" / "json"
SAIDA = ROOT / "corpus" / "estatisticas.json"

STOPWORDS = set(STOP_PT) | set(STOP_EN)
EXCLUIR_TOP = {"ADJ", "ADP", "PUNCT", "SYM", "SPACE", "NUM"}  # exclui adjetivos, preposicoes e nao-palavras

MAPA_POS = {
    "NOUN": "Substantivo",
    "ADP": "Preposição",
    "VERB": "Verbo",
    "DET": "Determinante / Artigo",
    "PROPN": "Substantivo Próprio",
    "ADJ": "Adjetivo",
    "NUM": "Numeral",
    "PRON": "Pronome",
    "CCONJ": "Conjunção Coordenativa",
    "ADV": "Advérbio",
    "AUX": "Verbo Auxiliar",
    "SCONJ": "Conjunção Subordinativa",
    "PART": "Partícula",
    "X": "Outros / Estrangeirismo",
    "PUNCT": "Pontuação",
    "INTJ": "Interjeição",
    "SYM": "Símbolo",
}


def carregar() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(JSON_DIR.glob("article_*.json"))]


def tags(artigo: dict) -> list[str]:
    return [p.split("_", 1)[0] for p in artigo["pos_tagger"]]


def _stopwords_do_idioma(idioma: str | None) -> set[str]:
    if idioma == "pt":
        return set(STOP_PT)
    if idioma == "en":
        return set(STOP_EN)
    return set(STOPWORDS)


def frequencias(
    artigos: list[dict], idioma: str | None = None, sem_stopwords: bool = False
) -> Counter:
    """Frequencia das palavras (fora adjetivos e preposicoes) para a nuvem."""
    stops = _stopwords_do_idioma(idioma)
    freq: Counter = Counter()
    for a in artigos:
        if idioma and a["idioma"] != idioma:
            continue
        for tok, tag in zip(a["artigo_tokenizado"], tags(a)):
            baixo = tok.lower()
            if tag in EXCLUIR_TOP or not any(c.isalpha() for c in baixo):
                continue
            if sem_stopwords and baixo in stops:
                continue
            freq[baixo] += 1
    return freq


def nuvem(freq: Counter, destino: Path, titulo: str) -> None:
    if WordCloud is None or plt is None:
        raise ImportError("wordcloud e matplotlib são necessários para gerar a nuvem de palavras.")
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


def _calcular_bloco(
    artigos_bloco: list[dict],
    stopwords_bloco: set[str],
    sentencas: int | None = None,
) -> dict:
    tokens: list[str] = []
    all_tags: list[str] = []
    lemas: list[str] = []
    for a in artigos_bloco:
        if "artigo_tokenizado" in a and a["artigo_tokenizado"]:
            tokens += a["artigo_tokenizado"]
        else:
            tokens += [p.split("_", 1)[1] for p in a["pos_tagger"]]
        all_tags += tags(a)
        if "lema" in a and a["lema"]:
            lemas += a["lema"]

    palavras, palavras_sem_stop = Counter(), Counter()
    substantivos, verbos = Counter(), Counter()
    for tok, tag in zip(tokens, all_tags):
        baixo = tok.lower()
        if not any(c.isalpha() for c in baixo):
            continue
        if tag not in EXCLUIR_TOP:
            palavras[baixo] += 1
            if stopwords_bloco and baixo not in stopwords_bloco:
                palavras_sem_stop[baixo] += 1
        if tag == "NOUN":
            substantivos[baixo] += 1
        elif tag == "VERB":
            verbos[baixo] += 1

    corpus_info: dict[str, int] = {
        "artigos": len(artigos_bloco),
        "tokens": len(tokens),
        "types": len({t.lower() for t in tokens}),
    }
    if sentencas is not None:
        corpus_info["sentencas"] = sentencas
    if lemas:
        corpus_info["lemas_unicos"] = len({l.lower() for l in lemas})

    return {
        "corpus": corpus_info,
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


def imprimir_tabela_pos(pos: dict[str, int], qtd_artigos: int, titulo: str) -> None:
    print(f"\n--- {titulo} ---")
    for classe, quantidade in pos.items():
        media = quantidade / qtd_artigos if qtd_artigos else 0.0
        nome_pt = MAPA_POS.get(classe, classe)
        print(f"{nome_pt:<25} | Total: {quantidade:<6} | Média por artigo: {media:.2f}")
    total_tokens = sum(pos.values())
    media_total = total_tokens / qtd_artigos if qtd_artigos else 0.0
    print(f"Total de tokens (soma das classes): {total_tokens} | Média por artigo: {media_total:.2f}")


def imprimir_relatorio(stats: dict) -> None:
    print(stats["corpus"])

    print("\nTop 10 palavras (regra):   ", stats["com_stopwords"]["top10_palavras"])
    print("Top 10 substantivos:       ", stats["com_stopwords"]["top10_substantivos"])
    print("Top 10 verbos:             ", stats["com_stopwords"]["top10_verbos"])
    sem_stop = stats.get("sem_stopwords", {}).get("top10_palavras")
    if sem_stop:
        print("\nTop 10 palavras (sem stop):", sem_stop)

    por_idioma = stats.get("por_idioma", {})
    nomes = {"pt": "Português", "en": "Inglês"}
    for idioma in ("pt", "en"):
        sub = por_idioma.get(idioma)
        if not sub:
            continue
        qtd = sub["corpus"]["artigos"]
        print(f"\n--- {nomes[idioma]} ({qtd} artigos) ---")
        print("Resumo:", sub["corpus"])
        print("Top 10 palavras (regra):   ", sub["com_stopwords"]["top10_palavras"])
        print("Top 10 substantivos:       ", sub["com_stopwords"]["top10_substantivos"])
        print("Top 10 verbos:             ", sub["com_stopwords"]["top10_verbos"])
        sub_sem = sub.get("sem_stopwords", {}).get("top10_palavras")
        if sub_sem:
            print("Top 10 palavras (sem stop):", sub_sem)

    qtd_geral = stats["corpus"]["artigos"]
    imprimir_tabela_pos(
        stats["pos"],
        qtd_geral,
        f"Quantidade por Classe Gramatical (POS) — Geral ({qtd_geral} artigos)",
    )

    for idioma in ("pt", "en"):
        sub = por_idioma.get(idioma)
        if not sub:
            continue
        qtd_sub = sub["corpus"]["artigos"]
        imprimir_tabela_pos(
            sub["pos"],
            qtd_sub,
            f"Quantidade por Classe Gramatical (POS) — {nomes[idioma]} ({qtd_sub} artigos)",
        )


def run(force: bool = False) -> int:
    if SAIDA.exists() and not force:
        print(f"ja existia: {SAIDA.relative_to(ROOT)}", file=sys.stderr)
        return 0

    artigos = carregar()
    print(f"artigos: {len(artigos)}", file=sys.stderr)

    import spacy

    modelos = {"pt": spacy.load("pt_core_news_lg"), "en": spacy.load("en_core_web_lg")}
    sentencas_por_artigo = [
        len(list(modelos[a["idioma"]](a["artigo_completo"]).sents)) for a in artigos
    ]

    geral = _calcular_bloco(artigos, STOPWORDS, sentencas=sum(sentencas_por_artigo))
    por_idioma: dict[str, dict] = {}
    for idioma in ("pt", "en"):
        pares = [(a, s) for a, s in zip(artigos, sentencas_por_artigo) if a["idioma"] == idioma]
        if pares:
            sub_artigos, sub_sents = zip(*pares)
            por_idioma[idioma] = _calcular_bloco(
                list(sub_artigos),
                _stopwords_do_idioma(idioma),
                sentencas=sum(sub_sents),
            )

    stats = {**geral, "por_idioma": por_idioma}
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    c = stats["corpus"]
    print(f"tokens={c['tokens']} types={c['types']} sentencas={c['sentencas']} lemas={c['lemas_unicos']}")
    print("saida:", SAIDA.relative_to(ROOT))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    return run(force=args.force)


if __name__ == "__main__":
    raise SystemExit(main())

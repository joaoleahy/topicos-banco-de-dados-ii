# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Etapa 3 — Limpar.

Tira o ruido da extracao, mas PRESERVA os headings (#, ##) porque a Etapa 4
usa as secoes pra achar abstract / corpo / referencias.

Regras:
  1. conserta mojibake dos acentos (ex.: "Formac¸˜ao" -> "Formacao" com acento)
  2. remove zero-width, NBSP, tags HTML (<u>, <sup>, ...) e enfase do markdown (*)
  3. remove o cabecalho repetido ("Proceedings of Symposium...") e o running head
     (linha igual ao titulo do artigo) — sem tocar nos headings
  4. normaliza espacos em branco

Saida: corpus/text/limpo/article_01.md ... article_NN.md

Uso:
    uv run ml/limpar.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_DIR = ROOT / "corpus" / "text"
LIMPO_DIR = ROOT / "corpus" / "text" / "limpo"
META_FILE = ROOT / "corpus" / "data" / "artigos.json"

# acento (marcador) -> letras acentuadas correspondentes
_ACENTOS = {
    "´": "áéíóú",  # agudo
    "ˆ": "âêîôû",  # circunflexo
    "˜": "ãõ",  # til
    "¨": "äëïöü",  # trema
    "`": "àèìòù",  # grave
}

# sequencias que o mapa generico nao cobre (letra sem acento + marcador)
_CASOS = {"´ı": "í", "´I": "Í", "ˆı": "î", "ˆI": "Î", "c¸": "ç", "C¸": "Ç"}


def _acentos_map() -> dict[str, str]:
    m = dict(_CASOS)
    for marcador, letras in _ACENTOS.items():
        for letra in letras:
            base = unicodedata.normalize("NFD", letra)[0]
            m[marcador + base] = letra
            m[marcador + base.upper()] = letra.upper()
    return m


_MOJIBAKE = _acentos_map()


def conserta_acentos(txt: str) -> str:
    for ruim, bom in sorted(_MOJIBAKE.items(), key=lambda kv: -len(kv[0])):
        txt = txt.replace(ruim, bom)
    txt = txt.replace("çao", "ção")  # til perdido: "Computac¸ao" -> "Computação"
    return re.sub(r"[´ˆ˜¨`¸]", "", txt)  # marcadores soltos


def esqueleto(s: str) -> str:
    """So letras/numeros minusculos, sem acento — pra comparar titulos."""
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", s).lower())


def limpar(txt: str, titulo: str) -> str:
    txt = conserta_acentos(txt)
    txt = txt.replace("\ufffd", " ")  # sobra sem conserto: vira espaco
    txt = re.sub(r"[\u200b\u200c\u200d\ufeff\u20dd]", "", txt)  # zero-width: some
    txt = txt.replace("\u00a0", " ")  # NBSP vira espaco normal
    txt = re.sub(r"</?(?:u|sup|sub|br|b|i|em|strong)\s*/?>", "", txt)
    txt = txt.replace("*", "")  # enfase do markdown; headings (#) ficam
    txt = re.sub(r"(?<![A-Za-z0-9])_|_(?![A-Za-z0-9])", "", txt)  # _enfase_; preserva a_b

    alvo = esqueleto(titulo)
    linhas = []
    for linha in txt.splitlines():
        if linha.lstrip().startswith("#"):  # heading = estrutura, preserva
            linhas.append(re.sub(r"[ \t]+", " ", linha).rstrip())
            continue
        s = esqueleto(linha)
        if s.startswith("proceedingsofsymposium") or (s and s == alvo):
            continue  # cabecalho/rodape repetido
        if not s:
            continue
        linhas.append(re.sub(r"[ \t]+", " ", linha).strip())

    return re.sub(r"\n{2,}", "\n\n", "\n".join(linhas)).strip() + "\n"


def run(force: bool = False) -> int:
    LIMPO_DIR.mkdir(parents=True, exist_ok=True)
    titulos = {f"article_{r['ordem']:02d}": r["titulo"] for r in json.loads(META_FILE.read_text())}

    for n, arq in enumerate(sorted(TEXT_DIR.glob("article_*.md")), 1):
        destino = LIMPO_DIR / arq.name
        if destino.exists() and not force:
            print(f"[{n}] {arq.name} ja existia", file=sys.stderr)
            continue
        limpo = limpar(arq.read_text(), titulos[arq.stem])
        destino.write_text(limpo)
        print(f"[{n}] {arq.name} -> limpo/{arq.name} ({len(limpo)} chars)", file=sys.stderr)

    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="re-limpar existentes")
    args = ap.parse_args()
    return run(force=args.force)


if __name__ == "__main__":
    raise SystemExit(main())

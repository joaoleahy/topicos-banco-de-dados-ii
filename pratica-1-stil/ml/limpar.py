# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Etapa 3 — Limpar.

Tira o ruido da extracao, mas PRESERVA os headings (#, ##) porque a Etapa 4
usa as secoes pra achar abstract / corpo / referencias.

Regras:
  1. conserta mojibake dos acentos (ex.: "Formac¸˜ao" -> "Formacao" com acento),
     inclusive marcador separado por espaco ("opini ˜ ao") ou depois da vogal ("e´ o")
     e junta a hifenizacao de quebra de linha ("inte- resse")
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
from collections import Counter
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

_MARCADORES = "´ˆ˜¨`"
_SUFIXO_C = {"ao": "ão", "oes": "ões", "oe": "õe"}
# marcador depois da vogal ("e´ o" -> "é o"): reaproveita o mapa marcador+vogal
_DEPOIS = {k[1] + k[0]: v for k, v in _MOJIBAKE.items() if len(k) == 2 and k[0] in _MARCADORES}
_GRAVE_ERRADO = str.maketrans("èìòùÈÌÒÙ", "éíóúÉÍÓÚ")  # pt só tem grave no "à"


def sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c))


def montar_lexico(textos: list[str]) -> dict[str, str]:
    """Forma sem acento -> forma acentuada mais frequente no corpus ("analise" -> "análise")."""
    contagem = Counter(w.lower() for t in textos for w in re.findall(r"\w{2,}", conserta_acentos(t)))
    lexico: dict[str, str] = {}
    for w, _ in contagem.most_common():
        if sem_acento(w) != w:  # só formas acentuadas: a versão sem acento é justamente o ruído
            lexico.setdefault(sem_acento(w), w)
    return lexico


def _junta_marcador(m: re.Match, lexico: dict[str, str]) -> str:
    esq, marcador, dir_ = m[1], m[2], m[3]
    candidato = esq + _MOJIBAKE.get(marcador + dir_[0], dir_[0]) + dir_[1:]
    candidato = re.sub(r"[áâà]o(s?)$", r"ão\1", candidato)
    forma = lexico.get(sem_acento(candidato))
    if forma:
        return esq[0] + forma[1:] if esq[0].isupper() else forma
    if dir_ == "e":
        return f"{esq} é"  # "geralmente ´ e" -> "geralmente é"
    return f"{esq} {dir_}"


def conserta_acentos(txt: str, lexico: dict[str, str] | None = None) -> str:
    # "classificac¸ ˜ ao", "Computac¸ ´ ao": no sufixo -ção/-ções o til é certo,
    # qualquer que seja o marcador (a fonte do PDF troca)
    txt = re.sub(
        rf"([cC])¸[ \t]*[{_MARCADORES}]?[ \t]*(ao|oes|oe)\b",
        lambda m: ("ç" if m[1] == "c" else "Ç") + _SUFIXO_C[m[2]],
        txt,
    )
    # "An ´ alise", "Matem ˆ aticas": marcador com espaço dos dois lados. Só junta se a
    # palavra resultante existe acentuada no próprio corpus; senão ("geologico ´ deve-se")
    # o marcador é solto entre duas palavras e elas ficam separadas
    if lexico:
        txt = re.sub(
            rf"(\w+)[ \t]+([{_MARCADORES}])[ \t]+(\w+)",
            lambda m: _junta_marcador(m, lexico),
            txt,
        )
    # "subdivisao˜", "e´ o": marcador deslocado para depois da vogal
    txt = txt.replace("ao˜", "ão")
    txt = re.sub(
        rf"([aeiouAEIOU])([{_MARCADORES}])(?=\s|$)",
        lambda m: _DEPOIS.get(m[1] + m[2], m[1]),
        txt,
    )

    for ruim, bom in sorted(_MOJIBAKE.items(), key=lambda kv: -len(kv[0])):
        txt = txt.replace(ruim, bom)
    txt = txt.replace("çao", "ção")  # til perdido: "Computac¸ao" -> "Computação"
    txt = re.sub(r"[áâà]o(s?)\b", r"ão\1", txt)  # "n ´ ao" -> "náo" -> "não"
    txt = txt.translate(_GRAVE_ERRADO)  # "Geol ` ogicas" -> "Geològicas" -> "Geológicas"
    return re.sub(r"[´ˆ˜¨`¸]", "", txt)  # marcadores soltos


def junta_hifenizacao(txt: str) -> str:
    """Quebra de linha do PDF: "inte- resse" -> "interesse". Preserva "pré- e pós-"."""
    return re.sub(r"(?<=[a-zà-úç])-(?:[ \t]+|[ \t]*\n[ \t]*)(?!(?:e|ou)\b)(?=[a-zà-úç])", "", txt)


def esqueleto(s: str) -> str:
    """So letras/numeros minusculos, sem acento — pra comparar titulos."""
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", s).lower())


def limpar(txt: str, titulo: str, lexico: dict[str, str] | None = None) -> str:
    txt = conserta_acentos(txt, lexico)
    txt = txt.replace("\ufffd", " ")  # sobra sem conserto: vira espaco
    txt = re.sub(r"[\u200b\u200c\u200d\ufeff\u20dd]", "", txt)  # zero-width: some
    txt = txt.replace("\u00a0", " ")  # NBSP vira espaco normal
    txt = re.sub(r"</?(?:u|sup|sub|br|b|i|em|strong)\s*/?>", "", txt)
    txt = txt.replace("*", "")  # enfase do markdown; headings (#) ficam
    txt = re.sub(r"(?<![A-Za-z0-9])_|_(?![A-Za-z0-9])", "", txt)  # _enfase_; preserva a_b
    txt = junta_hifenizacao(txt)  # depois da enfase: "embed-* *dings"

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
    arquivos = sorted(TEXT_DIR.glob("article_*.md"))
    lexico = montar_lexico([a.read_text() for a in arquivos])

    for n, arq in enumerate(arquivos, 1):
        destino = LIMPO_DIR / arq.name
        if destino.exists() and not force:
            print(f"[{n}] {arq.name} ja existia", file=sys.stderr)
            continue
        limpo = limpar(arq.read_text(), titulos[arq.stem], lexico)
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

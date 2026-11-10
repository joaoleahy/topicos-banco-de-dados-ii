# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Etapa 3 — Limpar.

Tira o ruido da extracao, preservando toda a acentuacao original das palavras
e os headings (#, ##), porque a Etapa 4 usa as secoes pra achar abstract /
corpo / referencias.

Regras:
  1. conserta mojibake dos acentos (ex.: "Formac¸˜ao" -> "Formação"),
     inclusive marcador separado por espaco ("opini ˜ ao", "dist ˆ ancia",
     "m ´ etricas", "log ´ ıstica") ou depois da vogal ("e´ o"),
     marcador duplicado ("Log ˜ ´ıstica") ou cortado pela linha ("Partic¸ ˜\\nao"),
     e junta a hifenizacao de quebra de linha ("inte- resse"), mantendo o hifen
     de palavra composta ("pre- processamento" -> "pre-processamento")
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

# Palavras curtas autonomas que nao devem ser coladas a palavra seguinte
# quando houver um marcador de acento solto entre elas (ex.: "de ˜ agrupamento")
_PALAVRAS_SOLTAS = {
    "a", "o", "e", "de", "da", "do", "das", "dos", "em", "na", "no", "nas", "nos",
    "por", "para", "com", "sem", "sob", "que", "se", "ou", "um", "uma", "uns", "umas",
    "os", "as", "ao", "aos", "pelo", "pela", "pelos", "pelas",
    "este", "estes", "esta", "estas", "esse", "esses", "essa", "essas",
    "deste", "destes", "desta", "destas", "desse", "desses", "dessa", "dessas",
}


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
_SEPARADOR = r"(?:[ \t]+|[ \t]*\n[ \t]*)"  # espaco que pode atravessar uma quebra de linha
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
        if sem_acento(w) != w:  # só formas acentuadas
            lexico.setdefault(sem_acento(w), w)
    return lexico


def _tira_marcador_sobrando(m: re.Match) -> str:
    """ "Log ˜ ´ıstica" -> "Log ´ ıstica" (palavra partida); "um ´ ´ındice" -> "um ´ındice" (duas palavras)."""
    esq, marcador = m[1], m[2]
    return f"{esq} {marcador}" if esq.lower() in _PALAVRAS_SOLTAS else f"{esq} {marcador} "


def _cola_se_conhecida(m: re.Match, lexico: dict[str, str]) -> str:
    """ "n ´umero" -> "número", se o léxico conhece; "os ´ındices" são duas palavras e ficam."""
    esq, marcador, dir_ = m[1], m[2], m[3]
    letra = _MOJIBAKE.get(marcador + dir_[0])
    if not letra or esq.lower() in _PALAVRAS_SOLTAS:
        return m[0]
    candidato = re.sub(r"[áâà]o(s?)$", r"ão\1", esq + letra + dir_[1:])
    forma = lexico.get(sem_acento(candidato))
    if not forma:
        return m[0]
    return esq[0] + forma[1:] if esq[0].isupper() else forma


def _junta_marcador(m: re.Match, lexico: dict[str, str] | None = None) -> str:
    esq, marcador, dir_ = m[1], m[2], m[3]

    # Caso especial: verbo "é" separado ("geralmente ´ e" -> "geralmente é"),
    # exceto quando as partes formam uma palavra conhecida ("pr ´ e" -> "pré")
    conhecida = lexico and esq.lower() not in _PALAVRAS_SOLTAS and sem_acento(esq + dir_) in lexico
    if dir_ == "e" and marcador == "´" and not conhecida:
        return f"{esq} é"

    letra_acentuada = _MOJIBAKE.get(marcador + dir_[0])
    if not letra_acentuada:
        # Marcador antes de consoante ("geologico ´ deve-se"): marcador solto
        return f"{esq} {dir_}"

    candidato = esq + letra_acentuada + dir_[1:]
    candidato = re.sub(r"[áâà]o(s?)$", r"ão\1", candidato)

    # 1. Se existir no léxico do corpus, usa a grafia canônica acentuada
    if lexico:
        forma = lexico.get(sem_acento(candidato))
        if forma:
            return esq[0] + forma[1:] if esq[0].isupper() else forma

    # 2. Se a parte esquerda for preposição/artigo solto e não estava no léxico
    # (ex.: "de ˜ agrupamento"), não cola
    if esq.lower() in _PALAVRAS_SOLTAS and sem_acento(candidato) not in {"nao", "sao", "vao", "dao", "tao", "mao", "maos", "pao", "paes", "cao", "caes"}:
        return f"{esq} {dir_}"

    # 3. Se o marcador for til (~), só cola em terminações nasais válidas (-ão, -ões, -ã, etc.)
    if marcador == "˜" and not re.match(r"^(?:[aáâà]o|oes|oe|ae|a)s?$", dir_, flags=re.IGNORECASE):
        return f"{esq} {dir_}"

    # 4. Caso geral ("dist ˆ ancia" -> "distância", "m ´ etricas" -> "métricas", "log ´ ıstica" -> "logística"):
    # preserva a palavra unida e acentuada!
    return candidato


def conserta_acentos(txt: str, lexico: dict[str, str] | None = None) -> str:
    txt = re.sub(r"\*[ \t]+\*", " ", txt)  # ênfase vazia no meio da palavra: "adic¸ ˜* *oes"
    # "Log ˜ ´ıstica": o primeiro marcador sobrou de outra posição
    txt = re.sub(rf"(\w+)[ \t]+[{_MARCADORES}][ \t]+([{_MARCADORES}])(?=\w)", _tira_marcador_sobrando, txt)
    # "classificac¸ ˜ ao", "Computac¸ ´ ao", "explorac¸ ´ ˜ao": no sufixo -ção/-ções o til é certo
    txt = re.sub(
        rf"([cC])¸\s*(?:[{_MARCADORES}]\s*)*(ao|oes|oe)\b",
        lambda m: ("ç" if m[1] == "c" else "Ç") + _SUFIXO_C[m[2]],
        txt,
    )
    # "An ´ alise", "dist ˆ ancia", "m ´ etricas": marcador com espaço dos dois lados
    txt = re.sub(
        rf"(\w+)[ \t]+([{_MARCADORES}]){_SEPARADOR}(\w+)",
        lambda m: _junta_marcador(m, lexico),
        txt,
    )
    if lexico:
        txt = re.sub(rf"(\w+)[ \t]+([{_MARCADORES}])(\w+)", lambda m: _cola_se_conhecida(m, lexico), txt)
    # "subdivisao˜", "e´ o": marcador deslocado para depois da vogal
    txt = txt.replace("ao˜", "ão").replace("ão˜", "ão")
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
    return re.sub(r"[´ˆ˜¨`¸]", "", txt)  # remove apenas marcadores órfãos


_QUEBRA_HIFEN = re.compile(rf"(\w*[a-zà-úç])-{_SEPARADOR}(?!(?:e|ou|and|or)\b)([a-zà-úç]\w*)")
_PALAVRA = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)*")


def montar_vocabulario(textos: list[str]) -> set[str]:
    """Palavras e compostos com hífen, sem contar os pedaços partidos em fim de linha."""
    vocab: set[str] = set()
    for t in textos:
        for w in _PALAVRA.findall(_QUEBRA_HIFEN.sub(" ", t)):
            w = sem_acento(w)
            vocab.add(w)
            vocab.update(w.split("-"))
    return vocab


def _resolve_quebra(m: re.Match, vocab: set[str]) -> str:
    a, b = m[1], m[2]
    if sem_acento(f"{a}-{b}") in vocab:  # "pre- processamento": o corpus usa com hífen
        return f"{a}-{b}"
    if sem_acento(a + b) in vocab:  # "inte- resse": o corpus usa colado
        return a + b
    # "define- se", "sintático- semânticos": dois termos completos (prefixo curto não conta)
    if len(a) >= 4 and b not in ("mente", "ing") and sem_acento(a) in vocab and sem_acento(b) in vocab:
        return f"{a}-{b}"
    return a + b


def junta_hifenizacao(txt: str, vocab: set[str] | None = None) -> str:
    """Quebra de linha do PDF: junta a sílaba ou mantém o composto. Preserva "pré- e pós-"."""
    return _QUEBRA_HIFEN.sub(lambda m: _resolve_quebra(m, vocab or set()), txt)


def esqueleto(s: str) -> str:
    """So letras/numeros minusculos, sem acento —usado apenas para comparar cabeçalhos repetidos."""
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", s).lower())


def normalizar(txt: str, lexico: dict[str, str] | None = None) -> str:
    """Tudo o que precisa acontecer antes de resolver a hifenização."""
    txt = conserta_acentos(txt, lexico)
    txt = txt.replace("\ufffd", " ")  # sobra sem conserto: vira espaco
    txt = re.sub(r"[\u200b\u200c\u200d\ufeff\u20dd]", "", txt)  # zero-width: some
    txt = txt.replace("\u00a0", " ")  # NBSP vira espaco normal
    txt = re.sub(r"</?(?:u|sup|sub|br|b|i|em|strong)\s*/?>", "", txt)
    txt = txt.replace("*", "")  # enfase do markdown; headings (#) ficam
    return re.sub(r"(?<![A-Za-z0-9])_|_(?![A-Za-z0-9])", "", txt)  # _enfase_; preserva a_b


def limpar(
    txt: str,
    titulo: str,
    lexico: dict[str, str] | None = None,
    vocab: set[str] | None = None,
) -> str:
    txt = junta_hifenizacao(normalizar(txt, lexico), vocab)  # depois da enfase: "embed-* *dings"

    alvo = esqueleto(titulo)
    linhas = []
    for linha in txt.splitlines():
        if linha.lstrip().startswith("#"):  # heading = estrutura, preserva para a Etapa 4
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
    textos = [a.read_text() for a in arquivos]
    lexico = montar_lexico(textos)
    vocab = montar_vocabulario([normalizar(t, lexico) for t in textos])

    for n, arq in enumerate(arquivos, 1):
        destino = LIMPO_DIR / arq.name
        if destino.exists() and not force:
            print(f"[{n}] {arq.name} ja existia", file=sys.stderr)
            continue
        limpo = limpar(arq.read_text(), titulos[arq.stem], lexico, vocab)
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

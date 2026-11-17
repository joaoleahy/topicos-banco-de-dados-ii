"""Etapa — n-gramas genéricos (unigrama, bigrama, trigrama).

Tabela de um modelo de ordem n: contexto (as n-1 palavras anteriores) -> Counter
do próximo token. Cada contexto é uma linha da matriz termo x termo.

    unigrama: contexto ()          P(w)
    bigrama:  contexto (a,)        P(w | a)
    trigrama: contexto (a, b)      P(w | a, b)

Geração: o contexto são os últimos n-1 tokens gerados. Se o contexto ainda é
curto (início do texto) ou nunca foi visto, recua para a ordem menor (backoff).

Controle de repetição (`bloquear=k`): um candidato que formaria um k-grama já
presente no texto gerado é descartado. Se todos os candidatos do contexto
forem descartados, recua para a ordem menor.
"""

from __future__ import annotations

import random
import re
from collections import Counter, defaultdict

Tabela = dict[tuple[str, ...], Counter]

_SUFIXOS_APOSTROFO = ("’s", "'s", "n’t", "n't", "’ve", "'ve", "’re", "'re", "’ll", "'ll", "’m", "'m", "’d", "'d")
_NAO_POSSESSIVO = {
    "and", "used", "with", "of", "in", "for", "to", "from", "by", "on", "at",
    "as", "is", "are", "was", "were", "that", "which", "or", "the", "a", "an",
}
_ASPAS_SOLTAS = {"’", "‘", "“", "”", '"', "'"}

# Correções explícitas de tokens cifrados por deslocamento de fonte no article_30
_CORRECOES_A30: dict[str, list[str]] = {
    "3Tags": ["ptags"],
    "7KH": ["the"],
    "7KHme": ["theme"],
    "7RSLF": ["topic"],
    "DOtKRXJh": ["although"],
    "DUrive": ["arrive"],
    "DW": ["at"],
    "EDVHd": ["based"],
    "EHFDXVe": ["because"],
    "EUHaks": ["breaks"],
    "EXVLQHVs": ["business"],
    "FDU": ["car"],
    "FDVH": ["case"],
    "FOimbs": ["climbs"],
    "FafiFD": ["faça"],
    "DHLVH": ["daisy"],
    "GH": ["de"],
    "GHSHQGHQFe": ["dependence"],
    "GHVFULSWLRn": ["description"],
    "GHgUHe": ["degree"],
    "GHtailed": ["detailed"],
    "GLDFKURQLF": ["diachronic"],
    "GLQDWH": ["subordinate"],
    "GLrty": ["dirty"],
    "GRHV": ["does"],
    "GRQ": ["don"],
    "IRU": ["for"],
    "IUeTXHnt": ["frequent"],
    "KH": ["he"],
    "KHUH": ["here"],
    "KRPe": ["home"],
    "LGHQWLILFDWLRn": ["identification"],
    "LOORFXWLRQof": ["illocution", "of"],
    "LQGHSHQGHnt": ["independent"],
    "LQVXERUGLQDWLon": ["insubordination"],
    "LQWeUQDl": ["internal"],
    "LQWeUSUeWDEOH": ["interpretable"],
    "MiVV": ["miss"],
    "ODEHl": ["label"],
    "OLGLWy": ["validity"],
    "OLNH": ["like"],
    "OLQJXLVWic": ["linguistic"],
    "PDLQ": ["main"],
    "PDWHULDl": ["material"],
    "PRVW": ["most"],
    "QRQ": ["non"],
    "RI": ["of"],
    "RQHs": ["ones"],
    "RUJanizaWLon": ["organization"],
    "SDUDOlHO": ["parallel"],
    "SHUVSHcWLYH": ["perspective"],
    "SKHQRPHQRQof": ["phenomenon", "of"],
    "SODFe": ["place"],
    "SRVVLble": ["possible"],
    "SSHech": ["speech"],
    "SUHYLRXV": ["previous"],
    "SURIHVVRU": ["professor"],
    "SURVRGLF": ["prosodic"],
    "SURVRGLFaOOy": ["prosodically"],
    "UHIHrs": ["refers"],
    "UHVSHcWLYHly": ["respectively"],
    "VH": ["se"],
    "VHPL": ["semi"],
    "VHe": ["see"],
    "VHgPHQWDWLon": ["segmentation"],
    "VHgment": ["segment"],
    "VRXUFe": ["source"],
    "VSHech": ["speech"],
    "VWrHHt": ["street"],
    "VXFh": ["such"],
    "WHUm": ["term"],
    "WKLs": ["this"],
    "WKe": ["the"],
    "XQLWs": ["units"],
    "XVHs": ["uses"],
    "XWWeUDQFe": ["utterance"],
    "XWWeUDQFes": ["utterances"],
    "YDlue": ["value"],
    "ZH": ["we"],
    "ZHOO": ["well"],
    "ZKLFh": ["which"],
    "aGMDFent": ["adjacent"],
    "aGYHUELDl": ["adverbial"],
    "aQDlyVLV": ["analysis"],
    "aSSURDch": ["approach"],
    "becDXVe": ["because"],
    "cODXVH": ["clause"],
    "cRQFOXVLYH": ["conclusive"],
    "cRQFept": ["concept"],
    "cRQVLGHr": ["consider"],
    "cRQVWUXFWLon": ["construction"],
    "cRQWH[t": ["context"],
    "cRQYHyed": ["conveyed"],
    "cRUUecWLQJ": ["correcting"],
    "caVH": ["case"],
    "caVHs": ["cases"],
    "caXVDl": ["causal"],
    "caXVH": ["cause"],
    "carULQKo": ["carrinho"],
    "eQYiRXs": ["envious"],
    "expiriQJ": ["expiring"],
    "fDPily": ["family"],
    "fHHl": ["feel"],
    "fROORZLQJ": ["following"],
    "fRRW": ["foot"],
    "fiQH": ["fine"],
    "frRP": ["from"],
    "gHW": ["get"],
    "geVWL": ["gesture"],
    "grDQGSD": ["grandpa"],
    "haSSLHU": ["happier"],
    "iQWHUHVtiQJ": ["interesting"],
    "iQYited": ["invited"],
    "immHGLDWHOy": ["immediately"],
    "kQRZ": ["know"],
    "lHW": ["let"],
    "lRQJ": ["long"],
    "lRRN": ["look"],
    "mDNiQJ": ["making"],
    "mDQLfDFtXUiQJ": ["manufacturing"],
    "mHWHU": ["meter"],
    "mRWKHU": ["mother"],
    "ofREYLRXVQH": ["of", "obviousness"],
    "partnHU": ["partner"],
    "perceiYHd": ["perceived"],
    "plDFe": ["place"],
    "pragPDWLFDOOy": ["pragmatically"],
    "rHJXODU": ["regular"],
    "sWDQd": ["stand"],
    "scKRRO": ["school"],
    "spHDkHUs": ["speakers"],
    "tKDW": ["that"],
    "tKHP": ["them"],
    "tKLQN": ["think"],
    "tKLQNiQJ": ["thinking"],
    "tKLs": ["this"],
    "teUPLQDl": ["terminal"],
    "tiYHr": ["tiver"],
    "twHQWy": ["twenty"],
    "vHUy": ["very"],
    "wDQW": ["want"],
    "wDV": ["was"],
    "wHQW": ["went"],
    "wKLch": ["which"],
    "xSUHVVLon": ["expression"],
    "yHDh": ["yeah"],
    "yRXQJ": ["young"],
}
_CORRECOES_EN = {
    "so1stl": "1st",
    "so2ndl": "2nd",
    "so3rdl": "3rd",
    "qfequal": "equal",
    "1angola": "angola",
}
_RE_SECAO = re.compile(r"^\d+\.([a-z][a-z\-]*)$")
_RE_URL = re.compile(r"(?:https?://|www\.|github\.com/|nilc\.icmc\.usp\.br/|\]\()", re.IGNORECASE)
_RE_PROSODIA = re.compile(r"^(/+=?(?:[a-z]+)?=?|/1\]?=.*|bpubdl\d+|bfam\w+\d+)$", re.IGNORECASE)


def eh_palavra(token: str) -> bool:
    return token[0].isalnum()


def juntar(tokens: list[str]) -> str:
    texto = " ".join(tokens)
    for p in ".,;:!?)]":
        texto = texto.replace(f" {p}", p)
    for p in "([":
        texto = texto.replace(f"{p} ", p)
    for suf in _SUFIXOS_APOSTROFO:
        texto = texto.replace(f" {suf}", suf)
    return texto


def _decodificar_token_en(token: str) -> list[str]:
    return _CORRECOES_A30.get(token, [token])


def _limpar_tokens_en(tokens: list[str]) -> list[str]:
    brutos: list[str] = []
    for t in tokens:
        brutos.extend(_decodificar_token_en(t))

    limpos: list[str] = []
    pular_ate_fecha = False
    i = 0
    while i < len(brutos):
        tok = brutos[i]
        low = tok.lower()

        if pular_ate_fecha:
            if ")" in low or "]" in low:
                pular_ate_fecha = False
            i += 1
            continue

        if _RE_URL.search(low):
            if "(" in low and ")" not in low:
                pular_ate_fecha = True
            i += 1
            continue

        if low in _ASPAS_SOLTAS or low in {"=", "<", ">", "⌊hc/2⌋", "ϕ", "[", "]"}:
            i += 1
            continue

        if _RE_PROSODIA.match(low):
            i += 1
            continue

        if low in _CORRECOES_EN:
            low = _CORRECOES_EN[low]

        m_sec = _RE_SECAO.match(low)
        if m_sec:
            low = m_sec.group(1)

        if low.startswith("-") and len(low) > 1 and low[1:].isalpha():
            low = low[1:]

        if low in _SUFIXOS_APOSTROFO:
            if limpos and limpos[-1][-1].isalnum() and not (
                low in ("’s", "'s") and limpos[-1] in _NAO_POSSESSIVO
            ):
                limpos[-1] = limpos[-1] + low.replace("’", "'")
            i += 1
            continue

        if (
            low == "-"
            and limpos
            and i + 1 < len(brutos)
            and limpos[-1].isalpha()
            and brutos[i + 1].isalpha()
            and not _RE_URL.search(brutos[i + 1])
        ):
            prox = _decodificar_token_en(brutos[i + 1])[0].lower()
            limpos[-1] = f"{limpos[-1]}-{prox}"
            i += 2
            continue

        if low in {".", ",", ";", ":"} and limpos and limpos[-1] in {".", ",", ";", ":", "(", "["}:
            if low == "." and limpos[-1] not in {"(", "["}:
                limpos[-1] = "."
            i += 1
            continue

        limpos.append(low.replace("’", "'"))
        i += 1

    return limpos


def preparar_docs(artigos: list[dict], idioma: str) -> list[list[str]]:
    """Prepara os tokens por idioma preservando integralmente o comportamento em português."""
    if idioma == "en":
        return [_limpar_tokens_en(a["artigo_tokenizado_pontuado"]) for a in artigos]
    return [[t.lower() for t in a["artigo_tokenizado_pontuado"]] for a in artigos]


def contar(documentos: list[list[str]], n: int) -> Tabela:
    tabela: dict[tuple[str, ...], Counter] = defaultdict(Counter)
    for tokens in documentos:
        for i in range(n - 1, len(tokens)):
            tabela[tuple(tokens[i - n + 1 : i])][tokens[i]] += 1
    return dict(tabela)


def modelos(documentos: list[list[str]], n: int) -> dict[int, Tabela]:
    """Todas as ordens até n: o trigrama precisa do bigrama e do unigrama para o backoff."""
    return {k: contar(documentos, k) for k in range(1, n + 1)}


def probabilidade(tabela: Tabela, contexto: tuple[str, ...], w: str) -> float:
    linha = tabela.get(contexto)
    return linha[w] / sum(linha.values()) if linha else 0.0


def kgramas(tokens: list[str], k: int) -> list[tuple[str, ...]]:
    return [tuple(tokens[i : i + k]) for i in range(len(tokens) - k + 1)]


def candidatos(
    tabelas: dict[int, Tabela],
    n: int,
    saida: list[str],
    proibido=lambda w: False,
    backoff: bool = True,
) -> Counter:
    ordem = min(n, len(saida) + 1)  # início do texto: ainda não há n-1 tokens de contexto
    for k in range(ordem, 0 if backoff else ordem - 1, -1):
        linha = tabelas[k].get(tuple(saida[len(saida) - k + 1 :]) if k > 1 else (), Counter())
        linha = Counter({w: c for w, c in linha.items() if not proibido(w)})
        if linha:
            return linha
    return tabelas[1][()] if backoff else Counter()  # tudo bloqueado até no unigrama: aceita repetir


def gerar(
    tabelas: dict[int, Tabela],
    n: int,
    inicio: list[str],
    max_palavras: int = 150,
    seed: int = 0,
    gulosa: bool = False,
    bloquear: int = 0,
    backoff: bool = True,
    limite_tokens: int | None = None,
) -> list[str]:
    rng = random.Random(seed)
    saida = list(inicio)
    palavras = sum(map(eh_palavra, saida))
    vistos = set(kgramas(saida, bloquear)) if bloquear else set()

    def proibido(w: str) -> bool:
        return bool(bloquear) and tuple(saida[len(saida) - bloquear + 1 :] + [w]) in vistos

    # a gulosa pode travar repetindo pontuação, que não conta como palavra
    limite = limite_tokens or 3 * max_palavras
    while palavras < max_palavras and len(saida) < limite:
        linha = candidatos(tabelas, n, saida, proibido, backoff)
        if not linha:  # sem backoff: contexto sem candidato encerra o texto
            break
        if gulosa:
            proximo = linha.most_common(1)[0][0]
        else:
            proximo = rng.choices(list(linha), weights=list(linha.values()))[0]
        saida.append(proximo)
        palavras += eh_palavra(proximo)
        if bloquear and len(saida) >= bloquear:
            vistos.add(tuple(saida[-bloquear:]))
    return saida

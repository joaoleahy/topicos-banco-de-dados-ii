# /// script
# requires-python = ">=3.11"
# dependencies = ["requests", "beautifulsoup4"]
# ///
"""Etapa 1 — Baixar.

Pega a issue do STIL 2017 no SOL/SBC, extrai os metadados de cada artigo
(titulo, autores+afiliacao, data, resumo, urls) e baixa os PDFs.

Os arquivos saem numerados na ordem dos anais: files/article_01.pdf ... article_NN.pdf.
O `artigo_id` do SOL fica guardado no JSON pra rastrear a origem.

Uso:
    uv run ml/baixar.py            # baixa o que falta
    uv run ml/baixar.py --force    # re-baixa tudo
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ISSUE_URL = "https://sol.sbc.org.br/index.php/stil/issue/view/262"
BASE = "https://sol.sbc.org.br/index.php/stil"

ROOT = Path(__file__).resolve().parent.parent
FILES_DIR = ROOT / "corpus" / "files"
DATA_DIR = ROOT / "corpus" / "data"
META_FILE = DATA_DIR / "artigos.json"

HEADERS = {"User-Agent": "stil-2017-corpus/0.1 (trabalho de disciplina)"}
DELAY = 0.7  # educacao com o servidor do SBC


def get(url: str) -> requests.Response:
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    return r


def article_ids(html: str) -> list[str]:
    ids = re.findall(r"article/view/(\d+)", html)
    seen: dict[str, None] = {}
    for i in ids:
        seen.setdefault(i, None)
    return list(seen)


def meta(soup: BeautifulSoup, name: str) -> list[str]:
    return [m.get("content", "").strip() for m in soup.find_all("meta", attrs={"name": name})]


def abstract(soup: BeautifulSoup) -> str:
    div = soup.select_one("div.abstract")
    if not div:
        return ""
    text = div.get_text(" ", strip=True)
    return re.sub(r"^(Resumo|Abstract)\s*", "", text).strip()


def first_page(soup: BeautifulSoup) -> int:
    valor = (meta(soup, "citation_firstpage") or [""])[0]
    return int(valor) if valor.isdigit() else 9999


def parse_article(artigo_id: str) -> dict:
    url = f"{BASE}/article/view/{artigo_id}"
    soup = BeautifulSoup(get(url).text, "html.parser")

    autores = []
    nomes, afiliacoes = meta(soup, "citation_author"), meta(soup, "citation_author_institution")
    for i, nome in enumerate(nomes):
        autores.append(
            {"nome": nome, "afiliacao": afiliacoes[i] if i < len(afiliacoes) else ""}
        )

    pdf_url = (meta(soup, "citation_pdf_url") or [""])[0]
    data = (meta(soup, "citation_date") or [""])[0]
    primeira = (meta(soup, "citation_firstpage") or [""])[0]
    ultima = (meta(soup, "citation_lastpage") or [""])[0]

    return {
        "artigo_id": artigo_id,
        "_primeira_pagina": first_page(soup),
        "titulo": (meta(soup, "citation_title") or [""])[0].strip(),
        "idioma": (meta(soup, "DC.Language") or meta(soup, "citation_language") or ["pt"])[0] or "pt",
        "informacoes_url": url,
        "pdf_url": pdf_url,
        "autores": autores,
        "data_publicacao": data,
        "paginas": f"{primeira}-{ultima}".strip("-"),
        "resumo": abstract(soup),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="re-baixar PDFs existentes")
    args = ap.parse_args()

    FILES_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    ids = article_ids(get(ISSUE_URL).text)
    print(f"artigos encontrados: {len(ids)}", file=sys.stderr)

    # 1) metadados de todos
    registros = []
    for n, artigo_id in enumerate(ids, 1):
        print(f"[{n}/{len(ids)}] metadata {artigo_id}", file=sys.stderr)
        try:
            registros.append(parse_article(artigo_id))
        except Exception as e:  # noqa: BLE001
            print(f"  erro nos metadados: {e}", file=sys.stderr)
        time.sleep(DELAY)

    # 2) ordena como nos anais e numera 01..N
    registros.sort(key=lambda r: (r["_primeira_pagina"], r["artigo_id"]))
    for i, reg in enumerate(registros, 1):
        reg["ordem"] = i
        reg["storage_key"] = f"corpus/files/article_{i:02d}.pdf"

    # 3) baixa os PDFs numerados
    for reg in registros:
        destino = ROOT / reg["storage_key"]
        reg.pop("_primeira_pagina", None)
        if destino.exists() and destino.stat().st_size > 0 and not args.force:
            print(f"  {reg['storage_key']} ja existia", file=sys.stderr)
            continue
        if not reg["pdf_url"]:
            print(f"  {reg['storage_key']} SEM pdf_url", file=sys.stderr)
            continue
        try:
            destino.write_bytes(get(reg["pdf_url"]).content)
            print(f"  {reg['storage_key']} baixado", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            print(f"  erro no pdf: {e}", file=sys.stderr)
        time.sleep(DELAY)

    META_FILE.write_text(json.dumps(registros, ensure_ascii=False, indent=2) + "\n")
    print(f"\n{len(registros)} artigos -> {META_FILE.relative_to(ROOT)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

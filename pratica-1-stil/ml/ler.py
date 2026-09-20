# /// script
# requires-python = ">=3.11"
# dependencies = ["firecrawl-anydoc", "pymupdf4llm"]
# ///
"""Etapa 2 — Ler.

Converte cada PDF em Markdown. O principal é o anydoc; quando ele recusa a
pagina pedindo OCR (falso positivo em alguns PDFs que tem camada de texto),
cai no pymupdf4llm local.

Saida: corpus/text/article_01.md ... corpus/text/article_NN.md

Uso:
    uv run ml/ler.py            # converte o que falta
    uv run ml/ler.py --force    # re-converte tudo
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import anydoc
import pymupdf4llm

ROOT = Path(__file__).resolve().parent.parent
FILES_DIR = ROOT / "corpus" / "files"
TEXT_DIR = ROOT / "corpus" / "text"


def converter(pdf: Path) -> tuple[str, str]:
    """Devolve (markdown, metodo)."""
    try:
        return anydoc.to_markdown(str(pdf)), "anydoc"
    except anydoc.NeedsOcrError:
        return pymupdf4llm.to_markdown(str(pdf)), "pymupdf4llm"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="re-converter existentes")
    args = ap.parse_args()

    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(FILES_DIR.glob("article_*.pdf"))
    print(f"pdfs: {len(pdfs)}", file=sys.stderr)

    metodos = {"anydoc": 0, "pymupdf4llm": 0}
    for n, pdf in enumerate(pdfs, 1):
        destino = TEXT_DIR / f"{pdf.stem}.md"
        if destino.exists() and destino.stat().st_size > 0 and not args.force:
            print(f"[{n}/{len(pdfs)}] {pdf.stem} ja existia", file=sys.stderr)
            continue
        try:
            md, metodo = converter(pdf)
        except Exception as e:  # noqa: BLE001
            print(f"[{n}/{len(pdfs)}] {pdf.stem} ERRO: {type(e).__name__}: {e}", file=sys.stderr)
            continue
        destino.write_text(md)
        metodos[metodo] += 1
        print(f"[{n}/{len(pdfs)}] {pdf.stem} -> {destino.name} ({metodo}, {len(md)} chars)", file=sys.stderr)

    print(f"\nanydoc: {metodos['anydoc']}  fallback: {metodos['pymupdf4llm']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

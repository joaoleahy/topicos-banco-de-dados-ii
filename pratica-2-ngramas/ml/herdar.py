"""Etapa 1 — Herdar o corpus da PRÁTICA 1.

O `pratica-1-stil/corpus/` não vai pro git (é regenerado a partir dos PDFs).
Aqui guardamos só o que a PRÁTICA 2 usa, em snapshots pequenos e versionados:

    corpus/stil2017-v1.jsonl   limpeza original da PRÁTICA 1 (congelado)
    corpus/stil2017.jsonl      depois de melhorar `pratica-1-stil/ml/limpar.py`
                               (acento separado por espaço, hifenização)

Campos: id, titulo, idioma, artigo_completo, artigo_tokenizado.

Se o snapshot já existir (ex.: no Colab, depois do git clone), não faz nada.

Uso:
    python ml/herdar.py [--force]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORIGEM = ROOT.parent / "pratica-1-stil" / "corpus" / "json"
SNAPSHOTS = {
    "v1": ROOT / "corpus" / "stil2017-v1.jsonl",
    "v2": ROOT / "corpus" / "stil2017.jsonl",
}
SNAPSHOT = SNAPSHOTS["v2"]
CAMPOS = ("titulo", "idioma", "artigo_completo", "artigo_tokenizado")


def run(force: bool = False) -> Path:
    if SNAPSHOT.exists() and not force:
        return SNAPSHOT
    arquivos = sorted(ORIGEM.glob("article_*.json"))
    if not arquivos:
        raise FileNotFoundError(f"snapshot ausente e PRÁTICA 1 não encontrada em {ORIGEM}")
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    with SNAPSHOT.open("w") as f:
        for p in arquivos:
            d = json.loads(p.read_text())
            linha = {"id": p.stem, **{c: d[c] for c in CAMPOS}}
            f.write(json.dumps(linha, ensure_ascii=False) + "\n")
    return SNAPSHOT


def carregar(idioma: str | None = None, versao: str = "v2") -> list[dict]:
    artigos = [json.loads(l) for l in SNAPSHOTS[versao].read_text().splitlines()]
    if idioma:
        artigos = [a for a in artigos if a["idioma"] == idioma]
    return artigos


if __name__ == "__main__":
    print(run(force="--force" in sys.argv))

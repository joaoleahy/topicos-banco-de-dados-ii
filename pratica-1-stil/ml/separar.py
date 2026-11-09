# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Etapa 4 — Separar.

Le o markdown limpo de cada artigo e monta o JSON do template do professor,
separando resumo / corpo / referencias. Nao processa nada de NLP ainda
(artigo_tokenizado, pos_tagger, lema ficam vazios para a Etapa 5).

Regras da tarefa:
- Referencias (tanto a secao final quanto as citacoes inline nos paragrafos)
  e autores NAO sao processados no corpo.
- Remove headings (#) e linhas de tabela markdown (|) do corpo final.
- Preserva a chave `orcid` em cada autor conforme o template.

Saida: corpus/json/article_01.json ... article_NN.json

Uso:
    uv run ml/separar.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIMPO_DIR = ROOT / "corpus" / "text" / "limpo"
JSON_DIR = ROOT / "corpus" / "json"
META_FILE = ROOT / "corpus" / "data" / "artigos.json"

# "Referências", "## 7. Referências", "References Bibliográficas"...
_REF_HEADING = re.compile(
    r"(?i)^(?:#+\s*)?(?:\d+[.)]?\s*)?(refer[êe]ncias?|references|refer[êe]ncias bibliogr[áa]ficas)\s*$"
)
# "References" no meio da linha, seguido de entrada de referencia "Banks, A. (2015)"
_REF_INLINE = re.compile(r"(?i)\b(refer[êe]ncias?|references)\b")
_ENTRADA_REF = re.compile(r"\s+[A-ZÀ-Ý][\w’'.-]+(?:\s+[A-ZÀ-Ý][\w’'.-]+)*,\s+[A-ZÀ-Ý]\.")
_SECTION = re.compile(r"^#+\s*\d")
_ABS = re.compile(r"(?i)^\W*(resumo|abstract)\b")
_KEYWORDS = re.compile(r"(?i)^\W*(palavras[- ]chave|keywords)\s*[:.]\s*(.+)$")
_MARCADORES_MD = ("#", "|")


def achar_referencias(linhas: list[str]) -> tuple[int, int | None, int | None] | None:
    """Devolve (linha, corte_do_corpo, inicio_das_refs)."""
    for i, ln in enumerate(linhas):
        if _REF_HEADING.match(ln.strip()):
            return i, None, None
    for i, ln in enumerate(linhas):
        for m in _REF_INLINE.finditer(ln):
            if _ENTRADA_REF.match(ln[m.end() : m.end() + 80]):
                return i, m.start(), m.end()
    return None


def inicio_corpo(linhas: list[str]) -> int:
    """Primeira secao numerada depois do resumo; sem secao, logo apos o resumo."""
    ultimo_resumo = max((i for i, ln in enumerate(linhas) if _ABS.match(ln.strip())), default=-1)
    for i, ln in enumerate(linhas):
        if i > ultimo_resumo and _SECTION.match(ln):
            return i
    return ultimo_resumo + 1


def _tidy(s: str) -> str:
    """Tira zero-width e normaliza espacos em texto vindo do SOL."""
    s = re.sub(r"[\u200b\u200c\u200d\ufeff\u20dd\u00a0]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def palavras_chave(linhas: list[str]) -> list[str]:
    for ln in linhas:
        m = _KEYWORDS.match(ln.strip())
        if m:
            return [p.strip(" .;") for p in re.split(r"[;,]", m.group(2)) if p.strip(" .;")]
    return []


def remover_citacoes_inline(texto: str) -> str:
    """Remove citacoes bibliograficas ao longo dos paragrafos."""
    # 1. Citacoes narrativas do tipo "Segundo Barbosa et al. (2016)" ou "Silva e Souza [2015]"
    texto = re.sub(
        r"\b[A-ZÀ-Ý][a-zà-úçA-ZÀ-Ý'-]+(?:\s+(?:e|and|&)\s+[A-ZÀ-Ý][a-zà-úçA-ZÀ-Ý'-]+|\s+et\s+al\.?)+\s*(?:\(\s*(?:19|20)\d{2}[a-z]?(?:\s*[,;:]\s*[^)]*)?\)|\[\s*(?:19|20)\d{2}[a-z]?(?:\s*[,;:]\s*[^\]]*)?\])",
        " ",
        texto,
    )
    # 2. Citacoes narrativas simples "Autor (2016)" ou "Autor [2016]"
    texto = re.sub(
        r"\b[A-ZÀ-Ý][a-zà-úçA-ZÀ-Ý'-]+\s+(?:\(\s*(?:19|20)\d{2}[a-z]?(?:\s*[,;:]\s*p\.?\s*\d+)?\s*\)|\[\s*(?:19|20)\d{2}[a-z]?\s*\])",
        " ",
        texto,
    )
    # 3. Citacoes entre colchetes ou parenteses contendo anos: [Barbosa et al. 2016], (Gomaa and Conrath, 1997; Kay, 1999)
    texto = re.sub(r"\[[^\[\]]*\b(?:19|20)\d{2}[a-z]?\b[^\[\]]*\]", " ", texto)
    texto = re.sub(r"\([^()]*\b(?:19|20)\d{2}[a-z]?\b[^()]*\)", " ", texto)
    # 4. Citacoes numericas entre colchetes estilo IEEE: [1], [1, 2], [1-4]
    texto = re.sub(r"\[\s*\d+(?:\s*[,;–-]\s*\d+)*\s*\]", " ", texto)
    # 5. Qualquer "et al." residual que tenha sobrado sem ano
    texto = re.sub(r"\bet\s+al\.?", " ", texto, flags=re.IGNORECASE)
    # Limpa espacos antes de pontuacao e espacos duplos
    texto = re.sub(r"\s+([.,;:!?])", r"\1", texto)
    return re.sub(r"[ \t]{2,}", " ", texto).strip()


def limpar_corpo_markdown(linhas: list[str]) -> list[str]:
    """Descarta linhas de heading (#) e tabela (|) e limpa citacoes inline."""
    limpas = []
    for ln in linhas:
        s = ln.strip()
        if not s or s.startswith(_MARCADORES_MD):
            continue
        s = remover_citacoes_inline(s)
        if s:
            limpas.append(s)
    return limpas


def separar(md: str, meta: dict) -> dict:
    linhas = [ln for ln in md.splitlines() if ln.strip()]
    ref = achar_referencias(linhas)

    if ref:
        i_ref, corta_corpo, abre_ref = ref
        if corta_corpo is None:  # heading sozinho: linha fica de fora
            corpo_linhas = linhas[inicio_corpo(linhas) : i_ref]
            ref_linhas = linhas[i_ref + 1 :]
        else:  # "...trabalho. References Banks, A. ..."
            corpo_linhas = linhas[inicio_corpo(linhas) : i_ref] + [linhas[i_ref][:corta_corpo].rstrip()]
            ref_linhas = [linhas[i_ref][abre_ref:].strip()] + linhas[i_ref + 1 :]
    else:
        corpo_linhas = linhas[inicio_corpo(linhas) :]
        ref_linhas = []

    corpo_limpo = limpar_corpo_markdown(corpo_linhas)
    corpo = "\n".join(corpo_limpo).strip()
    referencias = [x.strip() for x in ref_linhas if x.strip() and not x.strip().startswith("#")]
    resumo = _tidy(meta["resumo"])
    artigo_completo = corpo if corpo else remover_citacoes_inline(resumo)

    return {
        "titulo": _tidy(meta["titulo"]),
        "informacoes_url": meta["informacoes_url"],
        "idioma": meta["idioma"],
        "storage_key": meta["storage_key"],
        "autores": [
            {
                "nome": _tidy(a["nome"]),
                "afiliacao": _tidy(a.get("afiliacao", "")),
                "orcid": _tidy(a.get("orcid", "")),
            }
            for a in meta["autores"]
        ],
        "data_publicacao": meta["data_publicacao"],
        "resumo": resumo,
        "keywords": palavras_chave(linhas),
        "referencias": referencias,
        "artigo_completo": artigo_completo,
        "artigo_tokenizado": [],
        "pos_tagger": [],
        "lema": [],
    }


def run(force: bool = False) -> int:
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    metas = {f"article_{r['ordem']:02d}": r for r in json.loads(META_FILE.read_text())}

    for n, arq in enumerate(sorted(LIMPO_DIR.glob("article_*.md")), 1):
        destino = JSON_DIR / f"{arq.stem}.json"
        if destino.exists() and not force:
            print(f"[{n}] {arq.name} ja existia", file=sys.stderr)
            continue
        dados = separar(arq.read_text(), metas[arq.stem])
        destino.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n")
        print(
            f"[{n}] {arq.name}: corpo={len(dados['artigo_completo'])} chars, "
            f"refs={len(dados['referencias'])}, kw={len(dados['keywords'])}",
            file=sys.stderr,
        )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    return run(force=args.force)


if __name__ == "__main__":
    raise SystemExit(main())

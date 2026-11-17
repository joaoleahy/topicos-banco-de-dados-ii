"""Snapshot em português, preservando o texto para o tokenizador do BERT."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORIGEM = ROOT.parent / "pratica-1-stil" / "corpus" / "json"
SNAPSHOT = ROOT / "corpus" / "stil2017-pt.jsonl"


def gerar_snapshot() -> Path:
    """Reutiliza o snapshot versionado; na primeira execução, importa a Prática 1."""
    if SNAPSHOT.exists():
        return SNAPSHOT
    arquivos = sorted(ORIGEM.glob("article_*.json"))
    if not arquivos:
        raise FileNotFoundError(f"Corpus da Prática 1 ausente: {ORIGEM}")
    artigos = []
    for arquivo in arquivos:
        artigo = json.loads(arquivo.read_text(encoding="utf-8"))
        if artigo["idioma"] == "pt":
            artigos.append({
                "id": arquivo.stem,
                **{campo: artigo[campo] for campo in
                   ("titulo", "idioma", "artigo_completo", "pos_tagger")},
            })
    if not artigos or any(not a["artigo_completo"].strip() for a in artigos):
        raise ValueError("Corpus em português vazio ou com artigo sem texto.")
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(
        "".join(json.dumps(a, ensure_ascii=False) + "\n" for a in artigos),
        encoding="utf-8",
    )
    return SNAPSHOT


def carregar() -> list[dict]:
    return [json.loads(linha) for linha in
            gerar_snapshot().read_text(encoding="utf-8").splitlines() if linha.strip()]


def frequencias(artigos: list[dict], classe: str) -> Counter:
    """Conta formas em minúsculas; VERB exclui AUX, como na Prática 3."""
    contagem = Counter()
    for artigo in artigos:
        for marcado in artigo["pos_tagger"]:
            tag, palavra = marcado.split("_", 1)
            if tag == classe:
                contagem[palavra.lower()] += 1
    return contagem


def palavras_alvo(artigos: list[dict]) -> dict[str, str]:
    return {
        "a) palavra indicada": "modelos",
        "b) palavra indicada": "linguagem",
        "c) substantivo mais frequente": frequencias(artigos, "NOUN").most_common(1)[0][0],
        "d) verbo mais frequente": frequencias(artigos, "VERB").most_common(1)[0][0],
    }


if __name__ == "__main__":
    artigos = carregar()
    print(f"Corpus: {len(artigos)} artigos em português")
    for item, palavra in palavras_alvo(artigos).items():
        print(f"{item}: {palavra}")

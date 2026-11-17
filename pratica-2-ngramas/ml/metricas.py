"""Métricas para comparar os textos gerados.

- repetidos: fração de k-gramas do texto que já tinham aparecido antes nele
- distintos: fração de k-gramas únicos (distinct-k)
- copia: maior trecho do texto gerado que existe idêntico no corpus
"""

from __future__ import annotations

from ml.ngrama import Tabela, eh_palavra, gerar, juntar, kgramas

NOMES_ORDEM = {1: "unigrama", 2: "bigrama", 3: "trigrama"}


def repetidos(tokens: list[str], k: int = 3) -> float:
    gs = kgramas(tokens, k)
    return 1 - len(set(gs)) / len(gs) if gs else 0.0


def copia(tokens: list[str], corpus: list[list[str]], max_k: int = 40) -> int:
    maior = 0
    for k in range(2, max_k + 1):
        do_corpus = {g for doc in corpus for g in kgramas(doc, k)}
        if not any(g in do_corpus for g in kgramas(tokens, k)):
            break
        maior = k
    return maior


def resumo(tokens: list[str], corpus: list[list[str]]) -> dict[str, str]:
    return {
        "tokens": str(len(tokens)),
        "palavras": str(sum(map(eh_palavra, tokens))),
        "pontos finais": str(tokens.count(".")),
        "trigramas repetidos": f"{repetidos(tokens, 3):.0%}",
        "maior trecho copiado do corpus": f"{copia(tokens, corpus)} tokens",
    }


def imprimir_esparsidade(tabelas: dict[int, Tabela]) -> None:
    V = len(tabelas[1][()])
    print(f"{'':<10}{'contextos':>12}{'células > 0':>14}{'células possíveis':>22}{'preenchido':>12}")
    for n, nome in NOMES_ORDEM.items():
        cheias = sum(len(l) for l in tabelas[n].values())
        possiveis = V**n
        print(f"{nome:<10}{len(tabelas[n]):>12,}{cheias:>14,}{possiveis:>22,}{cheias / possiveis:>12.5%}")


def diagnosticar_backoff(
    tabelas: dict[int, Tabela],
    inicio: list[str],
    inicio_backoff: list[str],
    max_palavras: int = 150,
) -> None:
    def palavras(tokens: list[str]) -> int:
        return sum(map(eh_palavra, tokens))

    sem = gerar(tabelas, 3, inicio_backoff, max_palavras, gulosa=True, bloquear=3, backoff=False)
    com = gerar(tabelas, 3, inicio_backoff, max_palavras, gulosa=True, bloquear=3)
    print("trigrama, gulosa + bloqueio, início:", inicio_backoff)
    print(f"  sem backoff: {palavras(sem):>3} palavras | termina em: ... {juntar(sem[-10:])}")
    print(f"  com backoff: {palavras(com):>3} palavras")

    seeds = range(200)
    param = sum(palavras(gerar(tabelas, 3, inicio, max_palavras, seed=s, bloquear=3, backoff=False)) < max_palavras for s in seeds)
    print(f"\ntrigrama, amostragem + bloqueio, sem backoff: {param} de {len(seeds)} seeds param antes de {max_palavras} palavras")


def imprimir_evolucao(evolucao: dict[str, dict[str, list[str]]]) -> None:
    print(f"{'':<28}" + "".join(f"{NOMES_ORDEM[n]:>14}" for n in NOMES_ORDEM))
    for passo, textos in evolucao.items():
        celulas = [f"{repetidos(textos[NOMES_ORDEM[n]]):.0%} ({len(textos[NOMES_ORDEM[n]])})" for n in NOMES_ORDEM]
        print(f"{passo:<28}" + "".join(f"{x:>14}" for x in celulas))

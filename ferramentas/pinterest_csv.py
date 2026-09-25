"""Gera o CSV de "Criar Pins em massa" do Pinterest a partir da fila aprovada.

Uso:
    python ferramentas/pinterest_csv.py --lote 2026-10-03   -> Pins aprovados e no futuro desse lote
    python ferramentas/pinterest_csv.py                     -> idem, se só um lote tiver Pins no futuro
    python ferramentas/pinterest_csv.py --ensaio ...        -> inclui lotes não aprovados (para revisar)
    ... --fila <pasta>                                      -> usa outra pasta de fila

O arquivo sai em saida/pinterest-lote-<lote>.csv.

Um CSV é sempre de um lote só. O lote anterior já foi enviado ao Pinterest e ainda tem Pins
no futuro durante a semana; misturar os dois criaria esses Pins em dobro. Por isso, se mais de
um lote tiver Pins no futuro, o gerador se recusa até alguém dizer qual lote quer.

Formato: o que a ajuda oficial do Pinterest pede. Colunas Title (até 100 caracteres),
Media URL (endereço público da imagem), Pinterest board, Thumbnail (vazio para imagem),
Description (até 500), Link, Publish date e Keywords. A data de publicação vai em UTC:
tempo.para_utc_pinterest faz a conversão. Um Pin às 22:30 de Brasília sai com a data do
dia seguinte, e isso está certo.
"""
import csv
import json
import pathlib
import sys
from datetime import timedelta  # só para a MARGEM; tempo de verdade vem de tempo.py

import fila
import tempo

RAIZ = pathlib.Path(__file__).resolve().parent.parent
COLUNAS = ["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link", "Publish date", "Keywords"]
LIMITE_LINHAS = 200
# O Pinterest leva "cerca de duas horas" para criar os Pins depois do upload (mensagem da
# própria tela, 25/09/2026). Pin marcado para antes disso pode não ficar pronto a tempo.
MARGEM = timedelta(hours=3)


def url_publica(base: str, caminho: str) -> str:
    return caminho if caminho.startswith("http") else f"{base.rstrip('/')}/{caminho.lstrip('/')}"


def linha(post: fila.Post, pin: dict, base: str) -> dict:
    titulo, descricao = pin["titulo_pin"], pin["descricao"]
    if len(titulo) > 100:
        raise ValueError(f"{post.id}: título com {len(titulo)} caracteres (o Pinterest aceita 100)")
    if len(descricao) > 500:
        raise ValueError(f"{post.id}: descrição com {len(descricao)} caracteres (o Pinterest aceita 500)")
    return {
        "Title": titulo,
        "Media URL": url_publica(base, f"img/pins/{pin['id']}.jpg"),
        "Pinterest board": pin["pasta"],
        "Thumbnail": "",
        "Description": descricao,
        "Link": url_publica(base, post.dados["link"]),
        "Publish date": tempo.para_utc_pinterest(post.momento),
        "Keywords": pin.get("palavras_chave", ""),
    }


def nome_do_lote(lote: str) -> str:
    """'2026-10-03' ou '2026-10-03.json' -> '2026-10-03.json', o nome do arquivo em conteudo/fila."""
    return lote if lote.endswith(".json") else f"{lote}.json"


def escolher(posts: list, agora, lote: str | None = None, ensaio: bool = False):
    """Pins aprovados, no futuro e de um lote só. Devolve (vão no CSV, ficam fora pela MARGEM).
    Função pura, sem arquivo nem rede."""
    candidatos = [p for p in posts if p.canal == "pinterest" and (p.aprovado or ensaio) and p.momento > agora]
    lotes = sorted({p.lote for p in candidatos})
    if lote is None:
        if len(lotes) > 1:
            raise SystemExit(f"Há Pins no futuro em {len(lotes)} lotes ({', '.join(lotes)}). Um CSV leva um lote só, "
                             "senão o lote já enviado sai em dobro. Escolha com --lote.")
    else:
        lote = nome_do_lote(lote)
        if lote not in lotes:
            raise SystemExit(f"O lote {lote} não tem Pin aprovado no futuro. Lotes com Pins a enviar: {', '.join(lotes) or 'nenhum'}.")
        candidatos = [p for p in candidatos if p.lote == lote]
    escolhidos = [p for p in candidatos if tempo.diferenca(p.momento, agora) >= MARGEM]
    return escolhidos, [p for p in candidatos if p not in escolhidos]


def gerar(ensaio: bool = False, pasta: pathlib.Path = fila.PASTA_FILA, lote: str | None = None) -> pathlib.Path | None:
    base = json.loads((RAIZ / "conteudo" / "site.json").read_text(encoding="utf-8"))["base_url"]
    pins = fila.pins_por_id()
    agora = tempo.agora()
    escolhidos, fora = escolher(fila.carregar(pasta), agora, lote, ensaio)
    for p in fora:
        print(f"  FORA: {p.id} é para {tempo.texto_local(p.momento)}, a menos de {MARGEM} do upload; o Pinterest pode não criar a tempo")
    if not escolhidos:
        print("Nenhum Pin aprovado e no futuro. Nada a gerar.")
        return None
    if len(escolhidos) > LIMITE_LINHAS:
        raise SystemExit(f"{len(escolhidos)} Pins: o Pinterest aceita {LIMITE_LINHAS} por arquivo.")
    nome = escolhidos[0].lote.removesuffix(".json")
    destino = RAIZ / "saida" / f"pinterest-lote-{nome}{'-ensaio' if ensaio else ''}.csv"
    destino.parent.mkdir(exist_ok=True)
    with destino.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUNAS)
        escritor.writeheader()
        for p in escolhidos:
            escritor.writerow(linha(p, pins[p.dados["pin"]], base))
            print(f"  {tempo.texto_local(p.momento)} (Brasília) -> {tempo.para_utc_pinterest(p.momento)} UTC  {p.id}")
    print(f"{len(escolhidos)} Pins em {destino.relative_to(RAIZ)}")
    return destino


if __name__ == "__main__":
    argv = sys.argv[1:]
    pasta = pathlib.Path(argv[argv.index("--fila") + 1]) if "--fila" in argv else fila.PASTA_FILA
    lote = argv[argv.index("--lote") + 1] if "--lote" in argv else None
    gerar(ensaio="--ensaio" in argv, pasta=pasta, lote=lote)

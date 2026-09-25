"""Gera o CSV de "Criar Pins em massa" do Pinterest a partir da fila aprovada.

Uso:
    python ferramentas/pinterest_csv.py              -> só lotes aprovados, Pins ainda no futuro
    python ferramentas/pinterest_csv.py --ensaio     -> inclui lotes não aprovados (para revisar)
    python ferramentas/pinterest_csv.py --ensaio --fila <pasta>   -> usa outra pasta de fila

O arquivo sai em saida/pinterest-AAAA-MM-DD.csv (a data é a de hoje em Brasília).

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


def gerar(ensaio: bool = False, pasta: pathlib.Path = fila.PASTA_FILA) -> pathlib.Path | None:
    base = json.loads((RAIZ / "conteudo" / "site.json").read_text(encoding="utf-8"))["base_url"]
    pins = fila.pins_por_id()
    agora = tempo.agora()
    candidatos = [p for p in fila.carregar(pasta) if p.canal == "pinterest" and (p.aprovado or ensaio) and p.momento > agora]
    escolhidos = [p for p in candidatos if tempo.diferenca(p.momento, agora) >= MARGEM]
    for p in candidatos:
        if p not in escolhidos:
            print(f"  FORA: {p.id} é para {tempo.texto_local(p.momento)}, a menos de {MARGEM} do upload; o Pinterest pode não criar a tempo")
    if not escolhidos:
        print("Nenhum Pin aprovado e no futuro. Nada a gerar.")
        return None
    if len(escolhidos) > LIMITE_LINHAS:
        raise SystemExit(f"{len(escolhidos)} Pins: o Pinterest aceita {LIMITE_LINHAS} por arquivo.")
    destino = RAIZ / "saida" / f"pinterest-{tempo.hoje()}{'-ensaio' if ensaio else ''}.csv"
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
    gerar(ensaio="--ensaio" in argv, pasta=pasta)

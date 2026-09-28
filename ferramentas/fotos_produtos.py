"""Baixa a foto de cada produto de conteudo/produtos.json para site/img/produtos/.

Uso:
    python ferramentas/fotos_produtos.py            (só as que faltam)
    python ferramentas/fotos_produtos.py --todas    (baixa de novo todas)

A foto vem do endereço de imagem que a própria Shopee entrega no painel de afiliado
(campo shopee.imagem). O site guarda uma cópia em vez de apontar para a Shopee: se a loja
trocar ou apagar a foto, a página continua de pé. Sai quadrada, 800 x 800, com fundo branco,
sem cortar nada da foto original.
"""
import io
import json
import pathlib
import sys
import urllib.request

from PIL import Image

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "site" / "img" / "produtos"
LADO = 800
CDN = "https://down-ws-br.img.susercontent.com/"


def baixar(imagem: str) -> Image.Image:
    pedido = urllib.request.Request(CDN + imagem, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(pedido, timeout=30) as resposta:
        return Image.open(io.BytesIO(resposta.read())).convert("RGB")


def quadrada(foto: Image.Image) -> Image.Image:
    foto.thumbnail((LADO, LADO))
    fundo = Image.new("RGB", (LADO, LADO), "white")
    fundo.paste(foto, ((LADO - foto.width) // 2, (LADO - foto.height) // 2))
    return fundo


def main(argv: list[str]) -> None:
    produtos = json.loads((RAIZ / "conteudo" / "produtos.json").read_text(encoding="utf-8"))
    DESTINO.mkdir(parents=True, exist_ok=True)
    for p in produtos:
        arquivo = RAIZ / "site" / p["foto"]
        if arquivo.exists() and "--todas" not in argv:
            continue
        quadrada(baixar(p["shopee"]["imagem"])).save(arquivo, "JPEG", quality=88, optimize=True, progressive=True)
        print(f"ok  {arquivo.relative_to(RAIZ)}  {arquivo.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main(sys.argv[1:])

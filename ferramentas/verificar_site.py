"""Confere o site gerado antes de publicar: todo link e imagem interna tem que existir.

Uso:
    python ferramentas/verificar_site.py        (sai com código 1 se achar problema)
"""
import pathlib
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

SITE = pathlib.Path(__file__).resolve().parent.parent / "site"


class Coletor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for campo in ("href", "src"):
            if a.get(campo):
                self.refs.append((tag, a[campo]))


def alvo_existe(pagina: pathlib.Path, ref: str) -> bool:
    partes = urlsplit(ref)
    if partes.scheme or ref.startswith(("mailto:", "#", "//")):
        return True
    caminho = (pagina.parent / unquote(partes.path)).resolve()
    if partes.path.endswith("/") or caminho.is_dir():
        caminho = caminho / "index.html"
    return caminho.exists()


def main():
    problemas = []
    paginas = sorted(SITE.rglob("*.html"))
    for pagina in paginas:
        texto = pagina.read_text(encoding="utf-8")
        coletor = Coletor()
        coletor.feed(texto)
        for tag, ref in coletor.refs:
            if not alvo_existe(pagina, ref):
                problemas.append(f"{pagina.relative_to(SITE)}: <{tag}> aponta para '{ref}', que não existe")
        if "${" in texto:
            problemas.append(f"{pagina.relative_to(SITE)}: sobrou um campo de modelo sem preencher")
        if not re.search(r"<title>[^<]+</title>", texto):
            problemas.append(f"{pagina.relative_to(SITE)}: sem <title>")
    for linha in problemas:
        print("ERRO", linha)
    print(f"{len(paginas)} páginas conferidas, {len(problemas)} problema(s)")
    sys.exit(1 if problemas else 0)


if __name__ == "__main__":
    main()

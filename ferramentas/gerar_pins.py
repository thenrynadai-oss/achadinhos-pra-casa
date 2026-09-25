"""Gera as imagens dos Pins (1000 x 1500) a partir de um arquivo de conteúdo.

Uso:
    python ferramentas/gerar_pins.py                      (todos os Pins de conteudo/pins.json)
    python ferramentas/gerar_pins.py despensa-5-passos    (só os ids indicados)

Cada Pin é um modelo HTML de pins/modelos/ preenchido com os dados do JSON e
fotografado pelo Edge em modo headless. O resultado sai em JPG em site/img/pins/, que é
de onde o CSV do Pinterest e a API do Facebook vão buscá-lo depois de publicado. JPG e não
PNG: o PNG de um Pin com foto passa de 900 KB, e a home carrega vários.
"""
import html
import json
import os
import pathlib
import string
import subprocess
import sys

from PIL import Image

RAIZ = pathlib.Path(__file__).resolve().parent.parent
MODELOS = RAIZ / "pins" / "modelos"
BUILD = RAIZ / "pins" / "_build"
SAIDA = RAIZ / "site" / "img" / "pins"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PERFIL = pathlib.Path(os.environ["TEMP"]) / "edge-headless-claude"
LARGURA, ALTURA = 1000, 1500


def tamanho_do_titulo(titulo: str) -> int:
    """Quanto mais longo o título, menor a fonte, para caber em até três linhas."""
    n = len(titulo)
    if n <= 26:
        return 108
    if n <= 40:
        return 94
    if n <= 56:
        return 82
    return 72


def foto_url(foto_id: str) -> str:
    return f"https://images.unsplash.com/{foto_id}?auto=format&fit=crop&w=1000&h=900&q=80"


def preencher(pin: dict) -> str:
    modelo = string.Template((MODELOS / f"{pin['modelo']}.html").read_text(encoding="utf-8"))
    campos = {chave: html.escape(str(valor)) for chave, valor in pin.items() if isinstance(valor, str)}
    campos["tam_titulo"] = str(tamanho_do_titulo(pin["titulo"]))
    campos["classe_numero"] = "" if pin.get("numero") else "sem-numero"
    campos.setdefault("numero", "")
    if pin.get("foto"):
        campos["foto_url"] = foto_url(pin["foto"])
    # substitute (e não safe_substitute): campo faltando no JSON quebra aqui, não vira Pin com buraco
    return modelo.substitute(campos)


def fotografar(pagina: pathlib.Path, destino: pathlib.Path) -> None:
    subprocess.run(
        [
            EDGE,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            f"--user-data-dir={PERFIL}",
            f"--window-size={LARGURA},{ALTURA}",
            "--virtual-time-budget=15000",
            f"--screenshot={destino}",
            pagina.as_uri(),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main() -> None:
    pins = json.loads((RAIZ / "conteudo" / "pins.json").read_text(encoding="utf-8"))
    so_estes = set(sys.argv[1:])
    BUILD.mkdir(parents=True, exist_ok=True)
    SAIDA.mkdir(parents=True, exist_ok=True)

    for pin in pins:
        if so_estes and pin["id"] not in so_estes:
            continue
        pagina = BUILD / f"{pin['id']}.html"
        pagina.write_text(preencher(pin), encoding="utf-8")
        bruto = BUILD / f"{pin['id']}.png"
        fotografar(pagina, bruto)
        destino = SAIDA / f"{pin['id']}.jpg"
        with Image.open(bruto) as im:
            if im.size != (LARGURA, ALTURA):
                sys.exit(f"{pin['id']}: o Pin saiu com {im.size[0]}x{im.size[1]}, e não {LARGURA}x{ALTURA}.")
            im.convert("RGB").save(destino, "JPEG", quality=86, optimize=True, progressive=True)
        (SAIDA / f"{pin['id']}.png").unlink(missing_ok=True)
        print(f"ok  {destino.relative_to(RAIZ)}  {LARGURA}x{ALTURA}  {destino.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()

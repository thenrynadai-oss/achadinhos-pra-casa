"""Lê e valida a fila de publicações (conteudo/fila/*.json).

Cada arquivo é um lote semanal:

    {
      "semana": "2026-09-28",
      "aprovado_em": null,          <- só vira data quando o Henrique aprova o lote no chat
      "posts": [
        {"id": "...", "canal": "pinterest", "data": "2026-09-29", "hora": "09:15",
         "pin": "<id em conteudo/pins.json>", "link": "dicas/slug/"},
        {"id": "...", "canal": "telegram", "data": "2026-09-29", "hora": "19:30",
         "imagem": "img/pins/x.jpg", "texto": "...", "botao": {"rotulo": "...", "link": "..."}}
      ]
    }

Datas e horas são de Brasília. Lote sem aprovado_em nunca é publicado.
"""
import json
import pathlib
import re
from dataclasses import dataclass, field
from datetime import datetime

import tempo

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PASTA_FILA = RAIZ / "conteudo" / "fila"
CANAIS = {"pinterest", "telegram", "facebook"}


@dataclass
class Post:
    id: str
    canal: str
    momento: datetime
    dados: dict = field(repr=False)
    lote: str = ""
    aprovado: bool = False


class FilaInvalida(Exception):
    pass


def carregar_json(caminho: pathlib.Path):
    return json.loads(caminho.read_text(encoding="utf-8"))


def pins_por_id() -> dict:
    return {p["id"]: p for p in carregar_json(RAIZ / "conteudo" / "pins.json")}


def validar_post(p: dict, pins: dict) -> list[str]:
    erros = []
    pid = p.get("id", "?")
    if p.get("canal") not in CANAIS:
        erros.append(f"{pid}: canal '{p.get('canal')}' desconhecido")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(p.get("data", ""))):
        erros.append(f"{pid}: data deve ser AAAA-MM-DD")
    if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", str(p.get("hora", ""))):
        erros.append(f"{pid}: hora deve ser HH:MM (24h)")
    if p.get("canal") == "pinterest":
        if p.get("pin") not in pins:
            erros.append(f"{pid}: pin '{p.get('pin')}' não existe em conteudo/pins.json")
        if not p.get("link"):
            erros.append(f"{pid}: Pin sem link de destino")
    if p.get("canal") in ("telegram", "facebook"):
        if not p.get("texto"):
            erros.append(f"{pid}: post sem texto")
    imagem = p.get("imagem")
    if imagem and not (RAIZ / "site" / imagem).exists():
        erros.append(f"{pid}: imagem '{imagem}' não existe em site/")
    return erros


def carregar(pasta: pathlib.Path = PASTA_FILA) -> list[Post]:
    """Todos os posts de todos os lotes, validados e em ordem de horário."""
    pins = pins_por_id()
    posts, erros, vistos = [], [], set()
    for arquivo in sorted(pasta.glob("*.json")):
        lote = carregar_json(arquivo)
        aprovado = bool(lote.get("aprovado_em"))
        for p in lote.get("posts", []):
            erros += [f"{arquivo.name}: {e}" for e in validar_post(p, pins)]
            if p.get("id") in vistos:
                erros.append(f"{arquivo.name}: id '{p.get('id')}' repetido")
            vistos.add(p.get("id"))
            if not erros:
                posts.append(Post(p["id"], p["canal"], tempo.instante(p["data"], p["hora"]), p,
                                  lote=arquivo.name, aprovado=aprovado))
    if erros:
        raise FilaInvalida("\n".join(erros))
    return sorted(posts, key=lambda post: post.momento)

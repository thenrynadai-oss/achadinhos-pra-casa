"""Publica no canal do Telegram os posts aprovados cuja hora já chegou.

Roda no GitHub Actions a cada 15 minutos (.github/workflows/telegram.yml), mas funciona
igual no PC:

    python ferramentas/telegram_publicar.py                    -> publica o que venceu
    python ferramentas/telegram_publicar.py --ensaio           -> só mostra o que publicaria
    python ferramentas/telegram_publicar.py --ensaio --agora 2026-09-29T19:31
                                                              -> finge que é essa hora (Brasília)
    ... --fila <pasta>                                         -> usa outra pasta de fila
    python ferramentas/telegram_publicar.py --verificar        -> confere token e canal, sem publicar

Precisa de TELEGRAM_TOKEN (do @BotFather) e TELEGRAM_CANAL (@nome ou -100...) no
ambiente. Sem token, ele avisa e sai sem erro, para o agendamento não falhar enquanto o
canal não existe.

Regras:
- só publica post de lote aprovado (aprovado_em preenchido);
- nunca publica o mesmo post duas vezes: o que saiu fica registrado em
  conteudo/publicados/telegram.json;
- post atrasado mais que JANELA (por exemplo, o Actions ficou parado) não sai de surpresa
  horas depois: fica marcado como perdido e aparece no resumo.
"""
import html
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta  # timedelta só para a JANELA; tempo de verdade vem de tempo.py

import fila
import tempo

RAIZ = pathlib.Path(__file__).resolve().parent.parent
REGISTRO = RAIZ / "conteudo" / "publicados" / "telegram.json"
JANELA = timedelta(hours=3)
LIMITE_LEGENDA = 1024  # limite do Telegram para legenda de foto


def escolher(posts: list, publicados: dict, agora: datetime, janela: timedelta = JANELA):
    """Separa o que publicar agora e o que perdeu a hora. Função pura, sem rede."""
    publicar, perdidos = [], []
    for p in posts:
        if p.canal != "telegram" or not p.aprovado or p.id in publicados:
            continue
        if p.momento > agora:
            continue
        (perdidos if agora - p.momento > janela else publicar).append(p)
    return publicar, perdidos


def url_publica(base: str, caminho: str) -> str:
    return caminho if caminho.startswith("http") else f"{base.rstrip('/')}/{caminho.lstrip('/')}"


def montar_envio(post, base: str, canal: str) -> tuple[str, dict]:
    """Devolve o método da API e os campos. A legenda é HTML escapado."""
    d = post.dados
    texto = html.escape(d["texto"])
    if len(texto) > LIMITE_LEGENDA:
        raise ValueError(f"{post.id}: texto com {len(texto)} caracteres; a legenda do Telegram aceita {LIMITE_LEGENDA}")
    campos = {"chat_id": canal, "parse_mode": "HTML"}
    if d.get("botao"):
        teclado = {"inline_keyboard": [[{"text": d["botao"]["rotulo"], "url": url_publica(base, d["botao"]["link"])}]]}
        campos["reply_markup"] = json.dumps(teclado, ensure_ascii=False)
    if d.get("imagem"):
        campos.update(photo=url_publica(base, d["imagem"]), caption=texto)
        return "sendPhoto", campos
    campos["text"] = texto
    return "sendMessage", campos


def chamar_api(token: str, metodo: str, campos: dict) -> dict:
    corpo = urllib.parse.urlencode(campos).encode()
    pedido = urllib.request.Request(f"https://api.telegram.org/bot{token}/{metodo}", data=corpo)
    try:
        with urllib.request.urlopen(pedido, timeout=30) as resposta:
            return json.loads(resposta.read())
    except urllib.error.HTTPError as erro:
        # o corpo da resposta explica o motivo; o token nunca aparece na mensagem
        return json.loads(erro.read() or b"{}") or {"ok": False, "description": f"HTTP {erro.code}"}


def verificar(token: str, canal: str) -> int:
    """Confere token, canal e permissão do bot sem publicar nada. Não imprime o token."""
    eu = chamar_api(token, "getMe", {})
    if not eu.get("ok"):
        print(f"ERRO: o Telegram recusou o token ({eu.get('description', 'sem descrição')}).")
        return 1
    bot = eu["result"]
    print(f"ok  token aceito: bot @{bot['username']}")
    if not canal:
        print("ERRO: falta o segredo TELEGRAM_CANAL (o @ do canal).")
        return 1
    chat = chamar_api(token, "getChat", {"chat_id": canal})
    if not chat.get("ok"):
        print(f"ERRO: canal '{canal}' não encontrado ({chat.get('description', 'sem descrição')}).")
        return 1
    print(f"ok  canal encontrado: {chat['result'].get('title')} ({chat['result'].get('type')})")
    membro = chamar_api(token, "getChatMember", {"chat_id": canal, "user_id": bot["id"]}).get("result", {})
    if membro.get("status") != "administrator" or not membro.get("can_post_messages"):
        print(f"ERRO: o bot está no canal como '{membro.get('status', 'fora do canal')}', sem permissão de publicar.")
        return 1
    print("ok  o bot é administrador e pode publicar. Tudo pronto.")
    return 0


def ler_registro() -> dict:
    return json.loads(REGISTRO.read_text(encoding="utf-8")) if REGISTRO.exists() else {}


def gravar_registro(registro: dict) -> None:
    REGISTRO.parent.mkdir(parents=True, exist_ok=True)
    REGISTRO.write_text(json.dumps(registro, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    if "--verificar" in argv:
        token, canal = os.environ.get("TELEGRAM_TOKEN", ""), os.environ.get("TELEGRAM_CANAL", "")
        if not token:
            print("ERRO: falta o segredo TELEGRAM_TOKEN.")
            return 1
        return verificar(token, canal)  # testa o token mesmo sem canal: é assim que se descobre o @ do bot

    ensaio = "--ensaio" in argv
    agora = tempo.agora()
    if "--agora" in argv:
        agora = tempo.de_texto(argv[argv.index("--agora") + 1])

    base = json.loads((RAIZ / "conteudo" / "site.json").read_text(encoding="utf-8"))["base_url"]
    registro = ler_registro()
    pasta = pathlib.Path(argv[argv.index("--fila") + 1]) if "--fila" in argv else fila.PASTA_FILA
    publicar, perdidos = escolher(fila.carregar(pasta), registro, agora)
    print(f"Agora em Brasília: {tempo.texto_local(agora)} | a publicar: {len(publicar)} | perdidos: {len(perdidos)}")

    token, canal = os.environ.get("TELEGRAM_TOKEN", ""), os.environ.get("TELEGRAM_CANAL", "")
    if not ensaio and not (token and canal):
        # sem canal configurado não publica nem marca nada como perdido: nada foi tentado
        print("Sem TELEGRAM_TOKEN/TELEGRAM_CANAL configurados: nada foi publicado.")
        return 0

    falhas = 0
    for p in publicar:
        metodo, campos = montar_envio(p, base, canal or "@canal-de-ensaio")
        if ensaio:
            print(f"  [ensaio] {metodo} {p.id} marcado para {tempo.texto_local(p.momento)}")
            continue
        resposta = chamar_api(token, metodo, campos)
        if resposta.get("ok"):
            registro[p.id] = {"publicado_em": tempo.utc_iso(tempo.agora()),
                              "mensagem": resposta["result"]["message_id"]}
            print(f"  publicado {p.id}")
        else:
            falhas += 1
            print(f"  FALHOU {p.id}: {resposta.get('description', 'sem descrição')}")
    for p in perdidos:
        print(f"  PERDIDO {p.id}: era para {tempo.texto_local(p.momento)}, passou da janela de {JANELA}")
        if not ensaio:
            registro[p.id] = {"perdido": True, "era_para": tempo.utc_iso(p.momento)}

    if not ensaio:
        gravar_registro(registro)
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

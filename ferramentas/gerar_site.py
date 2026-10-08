"""Gera o site estático em site/ a partir de conteudo/*.json e web/.

Uso:
    python ferramentas/gerar_site.py

O que é gerado aqui (HTML, CSS, sitemap) é sobrescrito a cada execução. As imagens em
site/img/ vêm de gerar_pins.py e não são tocadas.

Datas: o conteúdo guarda a data de publicação como data de calendário (AAAA-MM-DD), já no
dia de Brasília. O site só formata essa data; não converte instante nenhum, então não
depende de fuso. Quem converte instante é ferramentas/tempo.py.
"""
import html
import json
import pathlib
import shutil
import string
from urllib.parse import quote

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CONTEUDO = RAIZ / "conteudo"
WEB = RAIZ / "web"
SITE = RAIZ / "site"

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]
LOJAS = {"shopee": "Ver na Shopee", "mercadolivre": "Ver no Mercado Livre", "amazon": "Ver na Amazon"}

e = html.escape


def carregar(nome):
    return json.loads((CONTEUDO / nome).read_text(encoding="utf-8"))


def data_por_extenso(iso_data: str) -> str:
    ano, mes, dia = (int(p) for p in iso_data.split("-"))
    return f"{dia} de {MESES[mes - 1]} de {ano}"


class Gerador:
    def __init__(self):
        self.cfg = carregar("site.json")
        self.dicas = sorted(carregar("dicas.json"), key=lambda d: d["publicada_em"], reverse=True)
        self.produtos = carregar("produtos.json")
        self.base = string.Template((WEB / "base.html").read_text(encoding="utf-8"))
        self.url_base = self.cfg["base_url"].rstrip("/")
        self.canal_telegram = self.cfg.get("telegram", "")
        datas = [d["publicada_em"] for d in self.dicas] + [p["adicionado_em"] for p in self.produtos]
        # o ano do rodapé sai do conteúdo, não do relógio da máquina
        self.ano = max(datas)[:4] if datas else "2026"
        self.urls_sitemap = []

    def url(self, caminho: str) -> str:
        return f"{self.url_base}/{caminho}"

    def pagina(self, caminho, titulo, descricao, conteudo, og_tipo="website", meta_extra="", lastmod=None):
        """caminho: '' para a home, 'dicas/slug/' para as internas, ou um arquivo como '404.html'."""
        profundidade = caminho.count("/")
        raiz = "../" * profundidade
        extras = [meta_extra] if meta_extra else []
        if self.cfg.get("pinterest_verificacao"):
            extras.append(f'<meta name="p:domain_verify" content="{e(self.cfg["pinterest_verificacao"])}">')
        menu_achadinhos = f'<a href="{raiz}#achadinhos">Achadinhos</a>' if self.produtos else ""
        menu_telegram = f'<a href="{raiz}telegram/">Telegram</a>' if self.canal_telegram else ""
        # a faixa aparece em toda página, menos na do próprio canal e no 404
        convite = self.convite_telegram() if caminho not in ("telegram/", "404.html") else ""
        doc = self.base.substitute(
            titulo_pagina=e(titulo if caminho == "" else f"{titulo} · {self.cfg['nome']}"),
            titulo=e(titulo),
            descricao=e(descricao),
            url=e(self.url(caminho)),
            nome_site=e(self.cfg["nome"]),
            og_tipo=og_tipo,
            meta_extra="\n".join(extras),
            raiz=raiz,
            menu_achadinhos=menu_achadinhos,
            menu_telegram=menu_telegram,
            conteudo=conteudo,
            convite_telegram=convite,
            ano=self.ano,
        )
        destino = SITE / (caminho + "index.html" if caminho == "" or caminho.endswith("/") else caminho)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(doc, encoding="utf-8")
        if caminho != "404.html":
            self.urls_sitemap.append((self.url(caminho), lastmod))

    # ---------- blocos ----------
    ICONE_TELEGRAM = ('<svg class="icone-tg" width="44" height="44" viewBox="0 0 48 48" aria-hidden="true">'
                      '<circle cx="24" cy="24" r="24" fill="#2aa1da"/>'
                      '<path d="M11 23.4 34.6 14c1.1-.4 2 .3 1.7 1.9l-4 18.9c-.3 1.3-1.1 1.7-2.2 1l-6-4.4-2.9 2.8'
                      'c-.3.3-.6.6-1.2.6l.4-6.1 11.1-10c.5-.4-.1-.7-.7-.3l-13.7 8.6-5.9-1.8c-1.3-.4-1.3-1.3.3-1.8z" fill="#fff"/></svg>')

    def link_telegram(self) -> str:
        return f"https://t.me/{self.canal_telegram}"

    def convite_telegram(self) -> str:
        if not self.canal_telegram:
            return ""
        return (f'<section class="convite-telegram" aria-label="Canal no Telegram"><div class="largura convite-linha">'
                f'{self.ICONE_TELEGRAM}<div class="convite-texto"><b>Achadinhos todo dia no Telegram</b>'
                f'<span>Dois achados por dia, com foto e link. É grátis e você sai quando quiser.</span></div>'
                f'<a class="botao botao-tg" href="{e(self.link_telegram())}" target="_blank" rel="noopener">Entrar no canal</a>'
                f'</div></section>')

    def card_dica(self, d, raiz=""):
        return (
            f'<article class="card"><img src="{raiz}{e(d["imagem"])}" alt="" loading="lazy" width="1000" height="1500">'
            f'<div class="card-texto">'
            f'<h3><a href="{raiz}dicas/{e(d["slug"])}/">{e(d["titulo"])}</a></h3></div></article>'
        )

    @staticmethod
    def src(foto: str, raiz: str) -> str:
        """A foto do produto mora no site (img/produtos/); endereço absoluto também vale."""
        return foto if foto.startswith("http") else raiz + foto

    def botoes_loja(self, p):
        return "".join(
            f'<a class="botao" href="{e(p["links"][loja])}" target="_blank" rel="sponsored noopener">{rotulo}</a> '
            for loja, rotulo in LOJAS.items() if p["links"].get(loja)
        )

    def card_produto(self, p, raiz=""):
        return (
            f'<article class="card produto"><img src="{e(self.src(p["foto"], raiz))}" alt="" loading="lazy">'
            f'<div class="card-texto"><span class="chip">{e(p["categoria"])}</span>'
            f'<h3><a href="{raiz}achadinhos/{e(p["slug"])}/">{e(p["nome"])}</a></h3></div></article>'
        )

    def achadinhos_da_dica(self, d, raiz):
        """Bloco no fim da dica com os produtos que resolvem o mesmo problema."""
        produtos = [p for p in self.produtos if p.get("dica") == d["slug"]]
        if not produtos:
            return ""
        itens = "".join(
            f'<div class="achadinho"><img src="{e(self.src(p["foto"], raiz))}" alt="{e(p["nome"])}" loading="lazy">'
            f'<div><h3><a href="{raiz}achadinhos/{e(p["slug"])}/">{e(p["nome"])}</a></h3>'
            f'<p>{e(p["por_que"])}</p>{self.botoes_loja(p)}</div></div>'
            for p in produtos
        )
        return (f'<section class="achadinhos-da-dica"><h2>Achadinho que ajuda nessa dica</h2>{itens}'
                f'<p class="meta">Link de afiliado: a loja nos paga uma pequena comissão se você comprar, sem mudar o seu preço.</p>'
                f'</section>')

    # ---------- páginas ----------
    def home(self):
        blocos = [
            '<section class="capa largura"><h1>Achadinhos pra deixar a casa organizada</h1>'
            '<p>Dicas de organização e produtos baratos que resolvem problema de verdade na casa e na cozinha, escolhidos um a um.</p></section>'
        ]
        if self.produtos:
            blocos.append('<section class="secao largura" id="achadinhos"><h2>Achadinhos</h2><div class="grade">'
                          + "".join(self.card_produto(p) for p in self.produtos) + "</div></section>")
        blocos.append('<section class="secao largura" id="dicas"><h2>Dicas</h2><div class="grade">'
                      + "".join(self.card_dica(d) for d in self.dicas) + "</div></section>")
        self.pagina("", self.cfg["nome"], self.cfg["descricao"], "\n".join(blocos),
                    lastmod=self.dicas[0]["publicada_em"] if self.dicas else None)

    def dica(self, d):
        caminho = f"dicas/{d['slug']}/"
        raiz = "../../"
        img_abs = self.url(d["imagem"])
        salvar = ("https://www.pinterest.com/pin/create/button/?url=" + quote(self.url(caminho), safe="")
                  + "&media=" + quote(img_abs, safe="") + "&description=" + quote(d["titulo"], safe=""))
        passos = "".join(f"<li><b>{e(t)}</b><span>{e(x)}</span></li>" for t, x in d["itens"])
        corpo = (
            f'<div class="largura"><p class="migalha"><a href="{raiz}">Início</a> › <a href="{raiz}#dicas">Dicas</a></p>'
            f'<article class="artigo"><div class="pin"><img src="{raiz}{e(d["imagem"])}" alt="{e(d["titulo"])}" width="1000" height="1500"></div>'
            f'<div><span class="chip">{e(d["categoria"])}</span><h1>{e(d["titulo"])}</h1>'
            f'<p class="meta">Publicado em {data_por_extenso(d["publicada_em"])}</p>'
            f'<p class="resumo">{e(d["resumo"])}</p><ol class="passos">{passos}</ol>'
            f'<a class="botao" href="{e(salvar)}" target="_blank" rel="noopener">Salvar no Pinterest</a>'
            f"{self.achadinhos_da_dica(d, raiz)}"
            f"</div></article></div>"
        )
        meta = (f'<meta property="og:image" content="{e(img_abs)}">\n'
                f'<meta property="article:published_time" content="{e(d["publicada_em"])}">')
        self.pagina(caminho, d["titulo"], d["resumo"], corpo, og_tipo="article", meta_extra=meta,
                    lastmod=d["publicada_em"])

    def aviso_amazon(self, p):
        # o Contrato de Associados da Amazon exige este aviso onde houver link dela
        if not p["links"].get("amazon"):
            return ""
        return ('<p class="meta">Na Amazon, o link leva a um modelo equivalente, de outro vendedor. '
                'Como Associado da Amazon, recebo por compras qualificadas.</p>')

    def produto(self, p):
        caminho = f"achadinhos/{p['slug']}/"
        raiz = "../../"
        dica = next((d for d in self.dicas if d["slug"] == p.get("dica")), None)
        ligacao = (f'<p class="meta">Combina com a dica <a href="{raiz}dicas/{e(dica["slug"])}/">{e(dica["titulo"])}</a>.</p>'
                   if dica else "")
        corpo = (
            f'<div class="largura"><p class="migalha"><a href="{raiz}">Início</a> › <a href="{raiz}#achadinhos">Achadinhos</a></p>'
            f'<article class="artigo"><div class="pin produto"><img src="{e(self.src(p["foto"], raiz))}" alt="{e(p["nome"])}"></div>'
            f'<div><span class="chip">{e(p["categoria"])}</span><h1>{e(p["nome"])}</h1>'
            f'<p class="resumo">{e(p["por_que"])}</p>{self.botoes_loja(p)}'
            f'<p class="meta">Link de afiliado: a loja nos paga uma pequena comissão se você comprar, sem mudar o seu preço. '
            f'O preço e a disponibilidade são os da loja no momento da compra.</p>{self.aviso_amazon(p)}{ligacao}'
            f"</div></article></div>"
        )
        foto_abs = p["foto"] if p["foto"].startswith("http") else self.url(p["foto"])
        self.pagina(caminho, p["nome"], p["por_que"], corpo, og_tipo="product",
                    meta_extra=f'<meta property="og:image" content="{e(foto_abs)}">', lastmod=p["adicionado_em"])

    def textos(self):
        sobre = (
            '<div class="largura texto"><h1>Sobre</h1>'
            "<p>O Achadinhos pra Casa junta dicas de organização e produtos baratos que resolvem problemas "
            "reais da casa e da cozinha: a gaveta que não fecha, a despensa que vira bagunça, a bancada sem espaço.</p>"
            "<h2>Como os achadinhos são escolhidos</h2>"
            "<p>Um a um. Antes de indicar um produto, olhamos a nota e os comentários de quem já comprou, o preço "
            "e se ele faz mesmo o que promete. Não recebemos produtos de lojas para falar bem deles.</p>"
            "<h2>Como o site se mantém</h2>"
            "<p>Alguns links são de afiliado: se você comprar por eles, a loja nos paga uma pequena comissão. "
            "O preço para você é o mesmo. Como Associado da Amazon, recebo por compras qualificadas.</p></div>"
        )
        self.pagina("sobre/", "Sobre", "Quem somos e como os achadinhos são escolhidos.", sobre)
        privacidade = (
            '<div class="largura texto"><h1>Privacidade</h1>'
            "<p>Este site não usa cookies, não tem formulário e não coleta dados pessoais.</p>"
            "<p>As fontes de texto vêm do Google Fonts, e o site é hospedado no GitHub Pages. Esses serviços "
            "podem registrar dados técnicos do acesso, como o endereço IP, conforme as políticas de privacidade deles.</p>"
            "<p>Ao clicar num link de loja, você sai deste site e passa a valer a política de privacidade da loja.</p></div>"
        )
        self.pagina("privacidade/", "Privacidade", "Como este site trata os seus dados.", privacidade)

    def pagina_telegram(self):
        """Página de entrada do canal: é para cá que aponta o Pin de convite (link do nosso domínio,
        não t.me, para o Pinterest ver um site verificado)."""
        if not self.canal_telegram:
            return
        raiz = "../"
        vitrine = "".join(self.card_produto(p, raiz) for p in self.produtos[:4])
        corpo = (
            f'<div class="largura"><section class="capa-tg">{self.ICONE_TELEGRAM}'
            f'<h1>Achadinhos pra Casa no Telegram</h1>'
            f'<p>Todo dia, dois achadinhos pra casa e cozinha: a foto, o que ele resolve e o link da loja. '
            f'Nada de textão, nada de corrente.</p>'
            f'<a class="botao botao-tg" href="{e(self.link_telegram())}" target="_blank" rel="noopener">Entrar no canal</a>'
            f'<p class="meta">É um canal: só a gente posta, ninguém vê o seu número e você sai quando quiser. '
            f'Os links são de afiliado: a loja nos paga uma pequena comissão se você comprar, e o seu preço não muda.</p>'
            f'</section>'
            + (f'<section class="secao"><h2>O tipo de achadinho que aparece lá</h2><div class="grade">{vitrine}</div></section>'
               if vitrine else "")
            + '</div>'
        )
        self.pagina("telegram/", "No Telegram", "Dois achadinhos por dia pra casa e cozinha, com foto e link, no canal do Telegram.",
                    corpo)

    def erro_404(self):
        # o 404 é servido em qualquer caminho, então os links dele são absolutos
        corpo = (f'<div class="largura texto"><h1>Página não encontrada</h1>'
                 f'<p>Esse endereço não existe mais. <a href="{e(self.url(""))}">Volte para o início</a>.</p></div>')
        destino_raiz = self.url("")
        doc_antigo = self.base.template
        self.base = string.Template(doc_antigo.replace("${raiz}", destino_raiz))
        self.pagina("404.html", "Página não encontrada", self.cfg["descricao"], corpo)
        self.base = string.Template(doc_antigo)

    def extras(self):
        shutil.copy(WEB / "estilo.css", SITE / "estilo.css")
        shutil.copy(WEB / "favicon.svg", SITE / "favicon.svg")
        linhas = ['<?xml version="1.0" encoding="UTF-8"?>',
                  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        for url, lastmod in self.urls_sitemap:
            linhas.append(f"  <url><loc>{e(url)}</loc>" + (f"<lastmod>{lastmod}</lastmod>" if lastmod else "") + "</url>")
        linhas.append("</urlset>")
        (SITE / "sitemap.xml").write_text("\n".join(linhas) + "\n", encoding="utf-8")
        (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {self.url('sitemap.xml')}\n", encoding="utf-8")
        (SITE / ".nojekyll").write_text("", encoding="utf-8")

    def limpar_paginas_orfas(self):
        """Apaga páginas de dica/produto que saíram do conteúdo, para o site não servir página morta."""
        vivos = {"dicas": {d["slug"] for d in self.dicas}, "achadinhos": {p["slug"] for p in self.produtos}}
        for pasta, slugs in vivos.items():
            base = SITE / pasta
            if base.exists():
                for sub in base.iterdir():
                    if sub.is_dir() and sub.name not in slugs:
                        shutil.rmtree(sub)

    def gerar(self):
        SITE.mkdir(exist_ok=True)
        self.limpar_paginas_orfas()
        self.home()
        for d in self.dicas:
            self.dica(d)
        for p in self.produtos:
            self.produto(p)
        self.textos()
        self.pagina_telegram()
        self.erro_404()
        self.extras()
        print(f"site gerado: {len(self.urls_sitemap)} páginas ({len(self.dicas)} dicas, {len(self.produtos)} produtos)")


if __name__ == "__main__":
    Gerador().gerar()

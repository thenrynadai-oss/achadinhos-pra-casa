"""Testes das ferramentas. Sem rede, sem token, sem dependência além do Python.

    python ferramentas/testes.py        (sai com código 1 se algum falhar)
"""
import json
import pathlib
import re
import sys
import tempfile
import traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import fila  # noqa: E402
import pinterest_csv  # noqa: E402
import telegram_publicar as tg  # noqa: E402
import tempo  # noqa: E402

PASTA = pathlib.Path(__file__).resolve().parent
TESTES = []


def teste(f):
    TESTES.append(f)
    return f


# ---------------- tempo ----------------
@teste
def brasilia_vira_utc_somando_tres_horas():
    assert tempo.para_utc_pinterest(tempo.instante("2026-09-29", "09:15")) == "2026-09-29T12:15:00"


@teste
def perto_da_meia_noite_a_data_em_utc_e_o_dia_seguinte():
    # a armadilha: 22:30 em Brasília já é 01:30 do dia 30 em UTC
    assert tempo.para_utc_pinterest(tempo.instante("2026-09-29", "22:30")) == "2026-09-30T01:30:00"


@teste
def o_dia_anda_no_calendario_e_nao_somando_24_horas():
    # Atenção: subtrair dois horários do MESMO fuso em Python compara o relógio de parede e
    # sempre dá 24h. O que importa para publicar é o instante em UTC de cada um.
    # Em 2018 o horário de verão começou em 4/11: as mesmas 9h viram 12h e depois 11h em UTC.
    assert tempo.utc_iso(tempo.instante("2018-11-03", "09:00")) == "2018-11-03T12:00:00Z"
    assert tempo.utc_iso(tempo.instante("2018-11-04", "09:00")) == "2018-11-04T11:00:00Z"
    # e acabou em 17/02/2019: de 11h volta para 12h em UTC
    assert tempo.utc_iso(tempo.instante("2019-02-16", "09:00")) == "2019-02-16T11:00:00Z"
    assert tempo.utc_iso(tempo.instante("2019-02-17", "09:00")) == "2019-02-17T12:00:00Z"


@teste
def diferenca_entre_instantes_respeita_o_horario_de_verao():
    from datetime import timedelta
    # das 9h de 03/11/2018 às 9h de 04/11/2018 passaram 23 horas reais (começou o horário de verão)
    assert tempo.diferenca(tempo.instante("2018-11-04", "09:00"), tempo.instante("2018-11-03", "09:00")) == timedelta(hours=23)
    assert tempo.diferenca(tempo.instante("2026-09-29", "22:30"), tempo.instante("2026-09-29", "19:30")) == timedelta(hours=3)


def pin_na_fila(pid, data, hora, lote, aprovado=True):
    return fila.Post(pid, "pinterest", tempo.instante(data, hora), dict(PIN_OK, id=pid), lote=lote, aprovado=aprovado)


@teste
def csv_deixa_de_fora_pin_em_cima_da_hora():
    from datetime import timedelta
    assert pinterest_csv.MARGEM >= timedelta(hours=2)  # o Pinterest leva ~2h para criar os Pins
    agora = tempo.instante("2026-10-03", "10:00")
    vao, fora = pinterest_csv.escolher([pin_na_fila("cedo", "2026-10-03", "12:15", "s.json"),
                                        pin_na_fila("tarde", "2026-10-03", "20:30", "s.json")], agora)
    assert [p.id for p in vao] == ["tarde"] and [p.id for p in fora] == ["cedo"]


@teste
def csv_nunca_mistura_lotes():
    # o lote 1 já foi enviado e ainda tem Pins no futuro: sem --lote, gerar o CSV duplicaria esses Pins
    agora = tempo.instante("2026-09-28", "09:00")
    posts = [pin_na_fila("s1-a", "2026-09-30", "12:15", "2026-09-26.json"),
             pin_na_fila("s2-a", "2026-10-03", "12:15", "2026-10-03.json"),
             pin_na_fila("s2-rascunho", "2026-10-04", "12:15", "2026-10-03.json", aprovado=False)]
    try:
        pinterest_csv.escolher(posts, agora)
    except SystemExit as erro:
        assert "--lote" in str(erro)
    else:
        raise AssertionError("gerou CSV misturando dois lotes")
    vao, _ = pinterest_csv.escolher(posts, agora, lote="2026-10-03")
    assert [p.id for p in vao] == ["s2-a"]
    # com um lote só no futuro, não precisa escolher
    vao, _ = pinterest_csv.escolher(posts, tempo.instante("2026-10-01", "09:00"))
    assert [p.id for p in vao] == ["s2-a"]


@teste
def dias_seguidos_viram_mes_e_ano():
    assert tempo.dias_seguidos("2026-12-30", 3) == ["2026-12-30", "2026-12-31", "2027-01-01"]


@teste
def instante_sem_fuso_e_recusado():
    from datetime import datetime
    try:
        tempo.em_brasilia(datetime(2026, 9, 29, 9, 0))
    except ValueError:
        return
    raise AssertionError("aceitou um horário sem fuso")


@teste
def hoje_e_uma_data_de_calendario():
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", tempo.hoje())


@teste
def nenhuma_ferramenta_usa_offset_fixo_nem_soma_24h():
    proibidos = {
        r"86_?400": "soma de um dia em segundos/ms",
        r"timedelta\(\s*hours\s*=\s*-\s*3": "offset fixo de -3h",
        r"timezone\(\s*timedelta": "fuso fixo montado à mão",
        r"[+-]03:?00\b": "offset -03:00 escrito à mão",
        r"UTC\s*-\s*3": "UTC-3 escrito à mão",
        r"utcnow\(": "utcnow devolve horário sem fuso",
        r"datetime\.now\(\s*\)": "now() sem fuso",
    }
    achados = []
    for arquivo in sorted(PASTA.glob("*.py")):
        if arquivo.name == "testes.py":
            continue
        texto = arquivo.read_text(encoding="utf-8")
        for padrao, motivo in proibidos.items():
            if re.search(padrao, texto):
                achados.append(f"{arquivo.name}: {motivo}")
        if arquivo.name != "tempo.py" and re.search(r"ZoneInfo\(|astimezone\(", texto):
            achados.append(f"{arquivo.name}: conversão de fuso fora de tempo.py")
    assert not achados, "\n".join(achados)


# ---------------- fila ----------------
def fila_temporaria(lotes: dict) -> pathlib.Path:
    pasta = pathlib.Path(tempfile.mkdtemp())
    for nome, conteudo in lotes.items():
        (pasta / nome).write_text(json.dumps(conteudo, ensure_ascii=False), encoding="utf-8")
    return pasta


PIN_OK = {"id": "p1", "canal": "pinterest", "data": "2026-09-29", "hora": "09:15",
          "pin": "despensa-5-passos", "link": "dicas/despensa-5-passos/"}


@teste
def lote_sem_aprovacao_carrega_como_nao_aprovado():
    posts = fila.carregar(fila_temporaria({"s.json": {"aprovado_em": None, "posts": [PIN_OK]}}))
    assert len(posts) == 1 and posts[0].aprovado is False


@teste
def hora_invalida_e_id_repetido_barram_a_fila():
    ruim = dict(PIN_OK, id="p2", hora="25:00")
    try:
        fila.carregar(fila_temporaria({"s.json": {"aprovado_em": "2026-09-26", "posts": [PIN_OK, PIN_OK, ruim]}}))
    except fila.FilaInvalida as erro:
        assert "repetido" in str(erro) and "HH:MM" in str(erro)
        return
    raise AssertionError("aceitou fila inválida")


@teste
def pin_inexistente_e_imagem_inexistente_barram_a_fila():
    ruim = dict(PIN_OK, pin="nao-existe", imagem="img/pins/nao-existe.jpg")
    try:
        fila.carregar(fila_temporaria({"s.json": {"posts": [ruim]}}))
    except fila.FilaInvalida as erro:
        assert "não existe em conteudo/pins.json" in str(erro) and "não existe em site/" in str(erro)
        return
    raise AssertionError("aceitou Pin inexistente")


# ---------------- CSV do Pinterest ----------------
@teste
def linha_do_csv_sai_em_utc_com_endereco_publico():
    post = fila.carregar(fila_temporaria({"s.json": {"aprovado_em": "x", "posts": [dict(PIN_OK, hora="22:30")]}}))[0]
    linha = pinterest_csv.linha(post, fila.pins_por_id()["despensa-5-passos"], "https://exemplo.github.io/site")
    assert linha["Publish date"] == "2026-09-30T01:30:00"
    assert linha["Media URL"] == "https://exemplo.github.io/site/img/pins/despensa-5-passos.jpg"
    assert linha["Link"] == "https://exemplo.github.io/site/dicas/despensa-5-passos/"
    assert linha["Pinterest board"] == "Despensa e potes" and linha["Thumbnail"] == ""


# ---------------- robô do Telegram ----------------
def post_tg(pid, hora, aprovado=True, **extra):
    dados = {"id": pid, "canal": "telegram", "data": "2026-09-29", "hora": hora, "texto": "Oi", **extra}
    return fila.Post(pid, "telegram", tempo.instante("2026-09-29", hora), dados, aprovado=aprovado)


@teste
def telegram_publica_so_o_que_venceu_aprovado_e_ainda_nao_saiu():
    agora = tempo.instante("2026-09-29", "19:40")
    posts = [
        post_tg("venceu", "19:30"),
        post_tg("futuro", "20:00"),
        post_tg("atrasado-demais", "14:00"),
        post_tg("nao-aprovado", "19:00", aprovado=False),
        post_tg("ja-saiu", "18:00"),
    ]
    publicar, perdidos = tg.escolher(posts, {"ja-saiu": {"mensagem": 1}}, agora)
    assert [p.id for p in publicar] == ["venceu"]
    assert [p.id for p in perdidos] == ["atrasado-demais"]


@teste
def telegram_escapa_html_e_usa_enderecos_publicos():
    post = post_tg("x", "10:00", texto="Potes <baratos> & bons", imagem="img/pins/despensa-5-passos.jpg",
                   botao={"rotulo": "Ver a dica", "link": "dicas/despensa-5-passos/"})
    metodo, campos = tg.montar_envio(post, "https://exemplo.github.io/site", "@canal")
    assert metodo == "sendPhoto"
    assert campos["caption"] == "Potes &lt;baratos&gt; &amp; bons"
    assert campos["photo"] == "https://exemplo.github.io/site/img/pins/despensa-5-passos.jpg"
    assert "https://exemplo.github.io/site/dicas/despensa-5-passos/" in campos["reply_markup"]


def main():
    falhas = 0
    for t in TESTES:
        try:
            t()
            print(f"ok     {t.__name__}")
        except Exception:
            falhas += 1
            print(f"FALHOU {t.__name__}")
            traceback.print_exc()
    print(f"{len(TESTES) - falhas}/{len(TESTES)} testes passaram")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()

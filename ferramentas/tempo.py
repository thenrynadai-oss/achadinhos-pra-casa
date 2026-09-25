"""O único lugar do projeto que decide dia e hora.

Toda data de publicação é escrita em horário de Brasília (dia + hora de parede) e vira
instante aqui. Ninguém mais soma horas, converte fuso ou formata data por conta própria:
quem precisa de tempo importa daqui. O teste em testes.py quebra se offset fixo ou soma
de 24h aparecer em outro arquivo.
"""
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

FUSO = ZoneInfo("America/Sao_Paulo")


def instante(data: str, hora: str) -> datetime:
    """'2026-09-29' + '19:30' em Brasília -> datetime com fuso."""
    h, m = (int(p) for p in hora.split(":"))
    return datetime.combine(date.fromisoformat(data), time(h, m), tzinfo=FUSO)


def agora() -> datetime:
    return datetime.now(tz=FUSO)


def hoje() -> str:
    """A data de hoje no calendário de Brasília (AAAA-MM-DD)."""
    return agora().date().isoformat()


def em_brasilia(momento: datetime) -> datetime:
    if momento.tzinfo is None:
        raise ValueError("instante sem fuso: não dá para saber que horas são em Brasília")
    return momento.astimezone(FUSO)


def para_utc_pinterest(momento: datetime) -> str:
    """O CSV do Pinterest lê a data de publicação em UTC, no formato AAAA-MM-DDTHH:MM:SS."""
    return em_brasilia(momento).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def utc_iso(momento: datetime) -> str:
    """Carimbo para registro: '2026-09-29T22:30:00Z'."""
    return para_utc_pinterest(momento) + "Z"


def de_texto(data_e_hora: str) -> datetime:
    """'2026-09-29T19:31' (relógio de Brasília) -> instante. Para simular horário em ensaio."""
    data, hora = data_e_hora.split("T")
    return instante(data, hora[:5])


def texto_local(momento: datetime) -> str:
    """'29/09 às 19:30', sempre no relógio de Brasília."""
    return em_brasilia(momento).strftime("%d/%m às %H:%M")


def dias_seguidos(inicio: str, quantidade: int) -> list[str]:
    """Dias de calendário a partir de `inicio`. Anda no calendário, nunca somando 24 horas a um instante."""
    primeiro = date.fromisoformat(inicio)
    return [(primeiro + timedelta(days=i)).isoformat() for i in range(quantidade)]

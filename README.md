# Achadinhos pra Casa

Dicas de organização e achadinhos baratos para casa e cozinha. Este repositório tem o site
(publicado no GitHub Pages) e as ferramentas que geram as imagens e as publicações.

## Como gerar

```bash
python ferramentas/gerar_pins.py             # imagens dos Pins (JPG) -> site/img/pins/
python ferramentas/gerar_site.py             # páginas -> site/
python ferramentas/verificar_site.py         # confere links e imagens
python ferramentas/testes.py                 # fuso, fila, CSV e robô
python ferramentas/pinterest_csv.py          # CSV de "Criar Pins em massa" -> saida/
python ferramentas/telegram_publicar.py --ensaio   # mostra o que o robô publicaria agora
```

Todo horário da fila é de Brasília, e só `ferramentas/tempo.py` converte fuso.

As imagens dos Pins são fotografadas pelo Edge em modo headless, por isso rodam no
Windows. O site e a verificação rodam em qualquer lugar.

## Estrutura

| Pasta | O que tem |
|---|---|
| `conteudo/` | Dicas, produtos e configuração do site, em JSON: a fonte de tudo |
| `pins/modelos/` | Modelos HTML dos Pins (1000 x 1500) |
| `web/` | Modelo base das páginas, CSS e favicon |
| `ferramentas/` | Geradores e verificador |
| `site/` | Resultado gerado, que é o que vai para o ar |

O plano do projeto está em [PLANO.md](PLANO.md).

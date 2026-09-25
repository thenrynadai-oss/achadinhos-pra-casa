# Achadinhos pra Casa — plano

Renda extra de afiliado em três camadas: Pinterest, Facebook e Telegram. Recomeço do zero
em 2026-09-25, porque as contas antigas foram abandonadas (não suspensas).

## O ciclo semanal

1. **Eu produzo a semana:** escolho os produtos, faço as imagens (`ferramentas/gerar_pins.py`),
   escrevo textos e links e monto a fila com data e hora de cada post.
2. **O Henrique aprova no chat:** um "aprovado" para o lote inteiro, uns 10 minutos por
   semana. Nada vai para o ar sem isso.
3. **A publicação acontece sozinha, só por canais oficiais:**

| Camada | Canal oficial | Quem publica |
|---|---|---|
| Pinterest | "Criar Pins em massa": um CSV com até 200 Pins já agendados | Um upload por semana. Chega a 100% se a API tiver acesso Standard |
| Facebook | API oficial da Meta, com post agendado até 30 dias à frente | Um script agenda a semana e o Facebook publica sozinho |
| Telegram | Bot API | GitHub Actions posta a fila aprovada, mesmo com o PC desligado |

## Decisões e o porquê

| Decisão | Por quê |
|---|---|
| **Nada de automação clicando no navegador** | O Pinterest pega extensão que imita clique humano e suspende a conta. A conta antiga travou no 14º Pin. Só canal oficial. |
| **Link para o nosso site, não marcação Shopee dentro do Pin** | A marcação só existe clicando na tela, e o Pinterest trata encurtador (s.shopee) como spam. O site também hospeda as imagens, e tanto o CSV quanto a API precisam de imagem em endereço público. |
| Facebook e Telegram com link de afiliado direto | Aí link encurtado não é problema. A faixa de produto da Shopee no Facebook é opcional; a comissão vem do link. |
| Shopee primeiro; Mercado Livre depois; Amazon só com tráfego | A Amazon fecha a conta sem 3 vendas em 180 dias. |
| Nicho: organização e cozinha | O público do Pinterest procura ideia para a casa; item de casa barato vende por impulso. |
| Primeira semana só com Pins de dica, sem produto | Aquecer a conta enquanto a Shopee aprova o cadastro. |
| Horários sempre em `America/Sao_Paulo`, calculados por uma função só | O dia da postagem é regra, não formatação. |
| Repositório público `thenrynadai-oss/achadinhos-pra-casa` | Site (Pages) e robô (Actions) de graça. Chave de acesso fica nos segredos do GitHub, nunca no código. |

## Parte do Henrique — uma vez só

1. [ ] Conta **Pinterest Business**: nome "Achadinhos pra Casa", usuário `achadinhospracasa`
   (livre em 2026-09-25).
2. [ ] **Shopee Afiliados** em https://affiliate.shopee.com.br (CPF, PIS/NIS e conta para
   receber). No canal, o perfil do Pinterest.
3. [ ] **Página no Facebook** "Achadinhos pra Casa" e um **app de desenvolvedor da Meta**
   (modo desenvolvimento, permissões `pages_manage_posts`, `pages_read_engagement`,
   `pages_show_list`). Guia passo a passo quando chegar a hora.
4. [ ] **Bot do Telegram** pelo @BotFather, mais um **canal** com o bot como administrador.
5. [ ] Colar as chaves no `.env` local, que o `.gitignore` já exclui. Nas Actions, elas
   entram como segredos do repositório.

## Estado

- 2026-09-25: repositório criado (vazio). Autor dos commits configurado só neste repo
  como `thenrynadai-oss`. Gerador de Pins pronto, com os 3 primeiros Pins de aquecimento em
  `site/img/pins/`. Nada publicado ainda.

## Estrutura

```
conteudo/          fila de conteúdo (JSON): o que vai ao ar e quando
pins/modelos/      modelos HTML dos Pins (1000 x 1500)
ferramentas/       geradores e publicadores
site/              vitrine pública (GitHub Pages) e imagens
```

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
4. [ ] **Telegram:**
   - no Telegram, fale com o @BotFather, mande `/newbot` e crie o bot "Achadinhos pra Casa";
     ele devolve um **token**;
   - crie um **canal público** (o endereço, por exemplo `@achadinhospracasa`, é você quem
     escolhe se estiver livre);
   - adicione o bot como **administrador** do canal, com permissão de publicar;
   - no PowerShell, rode os dois comandos abaixo. O primeiro pede o token e você cola; eu
     nunca digito chave:
     ```
     gh secret set TELEGRAM_TOKEN -R thenrynadai-oss/achadinhos-pra-casa
     gh secret set TELEGRAM_CANAL -R thenrynadai-oss/achadinhos-pra-casa --body "@nome-do-canal"
     ```
5. [ ] Chaves do Facebook, quando chegar a hora: segredos do repositório, do mesmo jeito.

## Operação

- **Fila:** `conteudo/fila/AAAA-MM-DD.json`, um lote por semana (o formato está em
  `ferramentas/fila.py`). O lote nasce com `aprovado_em: null`. Só depois do "aprovado" no
  chat eu preencho a data, e só aí ele pode ser publicado.
- **Pinterest:** `python ferramentas/pinterest_csv.py` gera `saida/pinterest-<data>.csv`.
  Ele é enviado pelo menu "Criar Pins em massa" do Pinterest Business: um upload por
  semana. A data vai em UTC, e a conversão já está feita e testada. Pin marcado para menos
  de 3 horas depois da geração fica de fora do CSV (aparece como FORA), porque o Pinterest
  leva cerca de 2 horas para criar os Pins depois do upload.
- **Telegram:** o workflow `telegram.yml` roda a cada 15 minutos no GitHub. Ele publica o
  que venceu e registra em `conteudo/publicados/telegram.json` com um commit do robô, para
  nunca repetir post. Post atrasado mais de 3 horas não sai: fica marcado como perdido.
- **Antes de qualquer push meu:** `git fetch` e `git pull --rebase`, porque o robô também
  faz commit na `main`. Nunca `--force`.
- **Atenção:** o GitHub desliga agendamento de repositório público depois de 60 dias sem
  atividade. Os commits do robô contam como atividade.
- **Testes:** `python ferramentas/testes.py` roda 15 testes: fuso (inclusive horário de
  verão, virada de dia em UTC e diferença entre instantes), fila, CSV e robô. Diferença de
  horário só por `tempo.diferenca`, que conta em UTC. Um deles falha se aparecer fuso fixo ou
  soma de 24h em qualquer ferramenta. O workflow `testes.yml` roda tudo a cada push.

## Estado

- 2026-09-25: **Semana 1 aprovada pelo Henrique** (`conteudo/fila/2026-09-26.json`). São 14 Pins
  de dica, 2 por dia de 26/09 a 02/10, às 12h15 e 20h30, e 7 posts no Telegram às 19h30.
  O Pinterest recebeu o perfil `achadinhospracasa`, e o "Criar Pins em massa" existe na
  conta nova (Configurações → Importar conteúdo → Carregar arquivo .csv). A verificação do
  site ficou pendente, porque a aba ficava escondida.
- 2026-09-25: **Telegram pronto.** Canal `@achadinhospracasa_oficial` e bot
  `@Achadinhospracasa_oficial_bot`, este só com permissão de publicar. A verificação no
  GitHub passou. O workflow roda a cada 15 minutos e publica os lotes aprovados. (Chegou a
  ser pausado por receio de usar a conta pessoal; o Henrique decidiu seguir depois de
  entender que o bot não acessa as conversas dele.)

- 2026-09-25: site no ar em https://thenrynadai-oss.github.io/achadinhos-pra-casa/. Commit
  `46fd8a7`: Pins em JPG (113 a 213 KB), CSV do Pinterest e robô do Telegram. O robô rodou no
  GitHub sem token, respondeu no horário de Brasília e não publicou nada, como devia. Nada
  publicado em rede social ainda, e nenhuma conta criada.

## Estrutura

```
conteudo/          dicas, produtos, pins, fila (JSON): a fonte de tudo
conteudo/fila/     lotes semanais do que vai ao ar e quando
pins/modelos/      modelos HTML dos Pins (1000 x 1500)
web/               modelo base, CSS e favicon do site
ferramentas/       geradores, publicadores, testes
site/              vitrine pública (GitHub Pages) e imagens
```
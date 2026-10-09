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
| Post do Telegram = foto do produto + 1 ou 2 linhas + link da Shopee + `#publi` | Pedido do Henrique em 08/10: "a explicação já tá na página da compra, a gente só tem que vender o peixe". O `#publi` fica porque o CONAR pede anúncio identificado. |
| Amazon nunca vai direto no Telegram | A Central de Associados proíbe link de Associado em app de mensagem. O botão "Também tem na Amazon" leva à página do produto no site. Um teste trava post do Telegram com link da Amazon. |
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
- **Pinterest:** `python ferramentas/pinterest_csv.py --lote <semana>` gera
  `saida/pinterest-lote-<semana>.csv`. Ele é enviado pelo menu "Criar Pins em massa" do
  Pinterest Business: um upload por semana. Cada CSV leva um lote só: o lote anterior já foi
  enviado e ainda tem Pins no futuro, e misturar os dois criaria esses Pins em dobro. Se mais
  de um lote tiver Pins no futuro e o `--lote` faltar, o gerador se recusa. A data vai em UTC, e a conversão já está feita e testada. Pin marcado para menos
  de 3 horas depois da geração fica de fora do CSV (aparece como FORA), porque o Pinterest
  leva cerca de 2 horas para criar os Pins depois do upload.
- **Telegram:** o workflow `telegram.yml` está agendado para cada 15 minutos no GitHub. Ele
  publica o que venceu e registra em `conteudo/publicados/telegram.json` com um commit do
  robô, para nunca repetir post.
  - **Na prática, o GitHub não roda a cada 15 minutos.** Medido de 25 a 28/09/2026: foram
    23 execuções, com intervalos de 2,5 a 6 horas. Os dois primeiros posts, marcados para
    19:30, saíram às 20:54 e às 22:10.
  - Por isso, desde 28/09 os posts ficam na fila às **18:00** e a tolerância é de **8 horas**.
    Post que passar disso é marcado como perdido, e não sai de madrugada.
  - Desde 08/10 o formato é o novo (campo `botoes`, um botão por linha); os lotes antigos com
    `botao` continuam valendo.
  - **Ritmo (08/10, à tarde):** o Henrique quer tudo no ar no mesmo dia, sem agendamento. Lote
    aprovado vai com a data e a hora da aprovação, e o robô é disparado na hora
    (`gh workflow run telegram.yml`), sem esperar o agendamento do GitHub. O robô espera
    `PAUSA_ENTRE_POSTS` (3,5 s) entre um post e outro, porque o Telegram recusa mais de ~20 por
    minuto no mesmo canal.
  - Horário exato só com um disparador externo. Fica para quando o canal tiver audiência.
- **Produtos:** ficam em `conteudo/produtos.json`.
  - **Escolha:** nota de pelo menos 4,7, mil vendidos ou mais, e resolver o problema de uma
    dica que já está no site.
  - **Link de afiliado:** sai do painel da Shopee, em "Link personalizado", com o Sub_id 1
    marcando a origem: `site` para o botão da página e `telegram` para o post. Assim o
    relatório da Shopee mostra qual canal vende.
  - **Foto:** `python ferramentas/fotos_produtos.py` baixa uma cópia da foto da loja para
    `site/img/produtos/`. Se a loja trocar a foto, a página continua de pé.
  - **Pin do produto:** usa o modelo `pins/modelos/produto.html` e leva à página do produto
    no site, nunca direto à loja.
  - **Aviso:** o `verificar_site.py` barra o site se um link de loja estiver sem
    `rel="sponsored"` ou se a página não tiver o aviso de afiliado. Um teste faz o mesmo com os
    posts do Telegram.
  - **Comissão extra da loja:** desde 01/08/2026 é paga sem retenção de imposto. Aceita pelo
    Henrique em 28/09. Confirmar com contador quando o valor ficar relevante.
- **Antes de qualquer push meu:** `git fetch` e `git pull --rebase`, porque o robô também
  faz commit na `main`. Nunca `--force`.
- **Atenção:** o GitHub desliga agendamento de repositório público depois de 60 dias sem
  atividade. Os commits do robô contam como atividade.
- **Testes:** `python ferramentas/testes.py` roda 18 testes:
  - fuso: horário de verão, virada de dia em UTC e diferença entre instantes;
  - fila;
  - CSV, inclusive a recusa de misturar lotes;
  - robô, inclusive o atraso real do agendamento do GitHub;
  - aviso de afiliado nos posts com link de loja. Diferença de
  horário só por `tempo.diferenca`, que conta em UTC. Um deles falha se aparecer fuso fixo ou
  soma de 24h em qualquer ferramenta. O workflow `testes.yml` roda tudo a cada push.

## Estado

- 2026-09-25: **Semana 1 aprovada pelo Henrique** (`conteudo/fila/2026-09-26.json`). São 14 Pins
  de dica, 2 por dia de 26/09 a 02/10, às 12h15 e 20h30, e 7 posts no Telegram às 19h30.
  O Pinterest recebeu o perfil `achadinhospracasa`, e o "Criar Pins em massa" existe na
  conta nova (Configurações → Importar conteúdo → Carregar arquivo .csv).
- 2026-09-25: **CSV da semana 1 enviado e conferido.** Os 15 Pins programados (14 da semana e
  1 de teste) aparecem com o dia e a hora de Brasília aprovados.
- 2026-09-25: **Site reivindicado no Pinterest** (Configurações → Link para o Pinterest →
  Sites), pela tag HTML, commit `737953c`. O endereço precisa da barra no fim
  (`.../achadinhos-pra-casa/`); sem ela, o Pinterest não verifica. O Pinterest volta a
  conferir a tag de tempos em tempos, então `pinterest_verificacao` em `conteudo/site.json`
  não pode ser apagado.
- 2026-09-25: **Semana 2 aprovada pelo Henrique** (`conteudo/fila/2026-10-03.json`). São 14
  Pins de dica com temas novos, de 03/10 a 09/10, às 12h15 e 20h30, e 7 posts no Telegram
  às 19h30. Continua só com dicas porque a Shopee ainda analisa a inscrição; o lote 3 entra
  com produto se ela aprovar. O site vai a 28 dicas.
- 2026-09-25: **Shopee Afiliados aprovou a inscrição.** Ainda faltam o cadastro de
  pagamento e fiscal (é do Henrique) e a ligação Pinterest ↔ Shopee, que ainda mostra "Link".
- 2026-09-28: **Semana 3 aprovada** (`conteudo/fila/2026-10-10.json`), a primeira com
  produto:
  - 7 dicas às 12h15 e 7 achadinhos da Shopee às 20h30, de 10/10 a 16/10;
  - o achadinho do dia no Telegram às 18h;
  - o site chega a 35 dicas e 7 produtos;
  - cada produto está ligado a uma dica (campo `dica`), e a dica mostra o bloco "Achadinho que
    ajuda nessa dica".
- 2026-10-06: **CSV da semana 3 enviado** (`saida/pinterest-lote-2026-10-10.csv`, 14 Pins de 10/10 a 16/10, conta Achadinhos pra Casa). O Pinterest respondeu "Upload concluído" e cria os Pins em cerca de 2 horas; conferir os agendados. A semana 2 nunca foi enviada (as datas de 03 a 09/10 passaram).
- 2026-10-06: **Amazon entra nos achadinhos** (commit `845c42e`): 6 dos 7 produtos com "Ver na Amazon" (tag `achadinhoshen-20`) e o aviso do Contrato de Associados. Meta: 3 vendas qualificadas antes de ~04/12. Foto e preço da Amazon não entram (contrato). **Semana 4 aprovada e CSV enviado** (14 Pins, 17 a 23/10).
- 2026-10-08: **Telegram no formato novo, aprovado pelo Henrique** (`conteudo/fila/2026-10-08.json`):
  os 7 achadinhos, dois por dia (12:00 e 19:00), de 08/10 a 11/10, com foto, frase curta, link
  da Shopee (Sub_id `telegram`) e `#publi`. Saíram da fila os 7 posts `s3-tg-*` da semana 3 e as
  2 dicas da semana 2 que ainda iam sair (08 e 09/10), para o canal ficar só com achadinho. As
  dicas do Telegram de 17 a 23/10 (semana 4) vão virar produto quando houver links novos.
  - O canal tinha **2 inscritos** (o Henrique e o bot). Divulgação grátis: faixa "Achadinhos
    todo dia no Telegram" em todas as páginas do site, página `/telegram/` (destino dos Pins de
    convite) e "manda pra quem precisa" no fim de cada post. Não divulgar em grupo dos outros.
  - Para produto novo falta o painel de afiliados da Shopee logado no navegador do Claude.
- 2026-10-08: **16 achadinhos novos, aprovados pelo Henrique** (o site vai a 23 produtos):
  - escolhidos pela busca do painel de afiliados (nota a partir de 4,7, mais de mil vendidos, nicho
    casa); 32 links gerados no "Link personalizado" (Sub_id `site` e `telegram`) e conferidos pelo
    redirecionamento, 32/32;
  - Amazon em 11 dos 16, sempre um modelo equivalente com nota a partir de 4,2;
  - Telegram de 12 a 23/10 (`conteudo/fila/2026-10-12.json`): os 16 novos e, de 20 a 23/10, os 7
    primeiros com chamada nova; as dicas da semana 4 saíram do Telegram;
  - Pinterest semana 5 (`conteudo/fila/2026-10-24.json`): 14 achadinhos e 2 Pins de convite para o
    canal (modelo `pins/modelos/telegram.html`, link para `/telegram/`);
  - `fotos_produtos.py` agora amplia foto pequena (há loja que sobe 345 px);
  - o painel da Shopee bloqueia com "verificação de tráfego" depois de umas 60 consultas rápidas;
    uma a cada 15 s passa.
  - **CSV da semana 5 enviado** (`saida/pinterest-lote-2026-10-24.csv`, 16 Pins de 24 a 30/10), no
    Chrome dele, conta Achadinhos pra Casa, depois de conferir no ar as 16 imagens e as 16 páginas.
    O Pinterest respondeu "Upload concluído"; conferir os agendados depois de ~2 horas.
  - À tarde, a pedido dele ("suba tudo hoje sem agendamento"), os 23 achadinhos do Telegram foram
    para 08/10 14:00 e saíram de uma vez; as repetições de 20 a 23/10 foram descartadas.
  - **Reforço do Pinterest** (`conteudo/fila/2026-10-09.json`, "pode subir um pouco mais"): segunda
    arte de 15 achadinhos novos e 2 convites do canal, de 09 a 15/10, somando 4 Pins por dia (5 em
    12/10) com os já agendados. Teto de 5 por dia: a conta tem 2 semanas e recebeu ~14 Pins de uma
    vez em 08/10, quando a outra aba subiu a semana 2 com datas passadas. **CSV enviado** no mesmo
    dia (`saida/pinterest-lote-2026-10-09.csv`, 17 Pins), conta Achadinhos pra Casa, depois de
    conferir no ar as 17 imagens e as 17 páginas; o Pinterest respondeu "Upload concluído".
  - O cabeçalho do site estourava no celular (520 px numa tela de 375): no celular o menu
    passou para a segunda linha.
- 2026-10-09: **10 achadinhos novos e Telegram de 09 a 13/10, aprovados pelo Henrique** ("pode montar
  os posts e subir"; a fila do Telegram estava vazia desde a saída dos 23 em 08/10):
  - escolhidos pela busca do painel de afiliados (10 buscas, uma a cada 15 s; nota a partir de 4,77,
    milhares de vendidos), sem repetir os 23 que já existem; o site vai a 33 produtos;
  - 20 links no "Link personalizado" (Sub_id `site` e `telegram`), conferidos pelo redirecionamento,
    20/20; sem Amazon neste lote;
  - Telegram (`conteudo/fila/2026-10-09-telegram.json`): 2 por dia, 12:00 e 19:00, no formato
    "vender o peixe". Eu disparo o robô na hora de cada post, porque o agendamento do GitHub atrasa
    horas.
  - Ainda sem Pin: o Pinterest segue no teto de ~5 por dia com o reforço de 09 a 15/10.
- 2026-09-25: **Facebook adiado pelo Henrique** até a Shopee aprovar e o Pinterest mostrar os
  primeiros resultados. Motivos: o alcance de uma página nova é quase zero, e ela fica
  pendurada no perfil pessoal dele. Por enquanto, as camadas ativas são Pinterest e Telegram.
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
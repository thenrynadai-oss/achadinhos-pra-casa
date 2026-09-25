# Cadastros — tudo o que é manual, levantado antes de começar

Pesquisado em 2026-09-25 nas páginas oficiais de cada plataforma (fontes no fim). A ideia é
que não apareça nenhum passo novo no final: tudo o que exige o Henrique está aqui, na ordem.

**O que o Claude nunca faz, em nenhuma plataforma:** criar conta, digitar senha, aceitar
termos, receber código (SMS/WhatsApp), mandar documento ou selfie, resolver captcha e
clicar em "autorizar acesso". Por isso esses passos estão todos aqui, juntos, no começo.

## A ordem: primeiro o que pode derrubar o plano

### 1. Pinterest Business (5 min, no computador) — o maior ponto de dúvida
- [ ] Criar a conta em https://www.pinterest.com/business/create/
  - Só funciona pelo navegador do computador (regra do Pinterest para conta Business nova).
  - O e-mail **não pode estar em outra conta do Pinterest**, nem na do Achadinhos antigo.
    Se precisar, use um e-mail novo ou o seu Gmail com "+achadinhos" antes do @.
  - Nome "Achadinhos pra Casa", usuário `achadinhospracasa`.
- [ ] **Teste que decide o plano, na hora:** no menu "Criar", verificar se aparece
  **"Criar Pins em massa"**.
  - Se aparecer: segue tudo como está.
  - Se **não** aparecer: paramos aqui e decidimos antes de criar as outras contas. A
    alternativa oficial (API do Pinterest) exige um vídeo do fluxo de login para
    aprovação, e é justamente o tipo de passo novo que queremos evitar.
- [ ] Verificar o site: o Pinterest mostra um código. Eu coloco no site e publico, e você
  clica em "Verificar".

### 2. Shopee Afiliados (candidatura 10 min; pagamento 15 min + app) — o que demora
- [x] Candidatura em https://affiliate.shopee.com.br com o login da sua conta Shopee.
  **Enviada em 2026-09-25** (conta Individual). A tela confirmou "Cadastro enviado com
  sucesso", e a resposta chega no e-mail cadastrado. Se não vier nada em 3 dias, a própria
  Shopee manda falar com o atendimento.
  - Redes ligadas: o site e o canal do Telegram. O Pinterest **não entra como link**: o
    campo "Other" recusa, porque a Shopee liga o Pinterest por autorização entre as contas.
    Depois da aprovação, isso se faz no Pinterest, em Configurações → Link para o
    Pinterest → Afiliados da Shopee.
  - Aprovação: de 1 a 5 dias úteis.
- [ ] **Ativar a Maree (só no app da Shopee, no celular):** Eu → Maree → Ativar agora →
  código pelo WhatsApp → dados pessoais → PIN. Pode pedir cópia do RG ou da CNH (emitido nos
  últimos 10 anos). Validação: até 3 dias úteis.
- [ ] **Dados de pagamento** (no portal ou no app: Programa de Afiliados → Conta →
  Configurações de pagamento). Separe antes:
  - foto ou PDF do **comprovante do CPF**;
  - foto ou PDF do **RG**;
  - **comprovante de endereço**. ⚠️ Se não estiver no seu nome, veja antes o que a Shopee
    aceita;
  - nome da mãe, data de nascimento e endereço completo;
  - se há **INSS retido em outra empresa**. Como você é CLT, provavelmente sim;
  - ⚠️ **CCM**, se você mora **na cidade de São Paulo**: é a inscrição municipal de
    autônomo. **O Henrique mora na cidade de SP** (confirmado em 2026-09-25). O que a
    pesquisa de 2026-09-25 encontrou:
    - **o CCM não é obrigatório.** A Shopee pergunta se você tem; sem ele, ela retém o
      ISS. Nas palavras dela: "Caso você more na cidade de São Paulo e não esteja registrado
      no CCM, será retido o ISS". A alíquota não aparece na página; uma contabilidade fala
      em 5%;
    - **com CCM, o autônomo pessoa física fica isento de ISS**, mas a prefeitura avisa que,
      a partir de 01/08/2026, a NFS-e pelo Portal Nacional passa a ser obrigatória também
      para os isentos. Isso vira uma tarefa manual todo mês. Também podem entrar a TFE e a
      TRSS;
    - **MEI não serve**: a atividade de afiliado não está entre as permitidas no MEI.
    - Recomendação: começar **sem CCM** e aceitar a retenção. Reavaliar com contador se a
      comissão ficar grande a ponto de os 5% valerem o trabalho mensal da nota.
  - Validação: até 7 dias úteis. A comissão é paga no dia 10 de cada mês, na Maree.

### 3. Telegram — PRONTO em 2026-09-25

- Bot **@Achadinhospracasa_oficial_bot**, criado pelo Henrique no @BotFather. Token no segredo
  `TELEGRAM_TOKEN`. O primeiro token passou pelo chat e foi revogado.
- Canal público **Achadinhos pra Casa**, `@achadinhospracasa_oficial` (segredo
  `TELEGRAM_CANAL`). "Assinar mensagens" desligado, então os posts não mostram o nome do
  Henrique.
- O bot é administrador **só com "Publicar mensagens"**. Todas as outras permissões estão
  desligadas, inclusive "adicionar administradores".
- Verificação no GitHub (run 36164976557): token aceito, canal encontrado, bot pode
  publicar.
- O dono do canal e do bot é a conta pessoal do Henrique, e ele aceitou esse risco. O bot
  não tem acesso às conversas dele.
- [ ] Entrar no Telegram Web (https://web.telegram.org), lendo o QR code com o celular.
  Precisa já ter Telegram no celular.
- [ ] Falar com o @BotFather → `/newbot` → nome "Achadinhos pra Casa" → ele devolve o
  **token**.
- [ ] Criar um **canal público** (Menu → Novo canal) e escolher o endereço.
- [ ] Pôr o bot como **administrador** do canal, com permissão de publicar. A ajuda do
  Telegram diz que no app de celular isso dá menos erro do que no Web.
- [ ] Guardar o token e o canal nos segredos do repositório. O token você mesmo cola:
  ```
  gh secret set TELEGRAM_TOKEN -R thenrynadai-oss/achadinhos-pra-casa
  gh secret set TELEGRAM_CANAL -R thenrynadai-oss/achadinhos-pra-casa --body "@nome-do-canal"
  ```

### 4. Facebook (Página 5 min; app da Meta 15 min) — a segunda camada, por último
- [ ] Criar a **Página** "Achadinhos pra Casa" em https://www.facebook.com/pages/create
  (precisa do seu perfil pessoal do Facebook, que fica como administrador).
- [ ] Virar **desenvolvedor da Meta** em https://developers.facebook.com. Exige:
  - ⚠️ confirmar a conta por **código SMS ou cartão de crédito**;
  - ⚠️ **verificação em duas etapas** ligada.
- [ ] Criar o **app** com o caso de uso de gerenciar Página, e deixar em **modo
  desenvolvimento**. Não passa por revisão da Meta, porque só publica na sua própria
  Página, com você como administrador do app. Eu te guio clique a clique.
- [ ] Gerar o acesso (um clique em "autorizar") e colar num arquivo `.env` local.
  - Daí em diante, eu troco por um acesso de Página de longa duração e guardo nos segredos
    do GitHub, sem nunca mostrar o valor.
  - ⚠️ Se você trocar a senha do Facebook, esse acesso cai e precisa ser gerado de novo.

## O que eu faço sozinho depois disso

- Toda semana: escolho produtos, faço as imagens, textos e links e monto a fila. Você
  aprova com um "aprovado".
- Gero o CSV do Pinterest. O upload leva uns 30 segundos por semana e é seu: fazer isso
  clicando na tela do Pinterest é o tipo de automação que arrisca a conta.
- O Telegram publica sozinho (já está rodando no GitHub, esperando o token).
- O Facebook agenda a semana sozinho, pela API, depois do passo 4.
- Relatório semanal de cliques e vendas.

## Fontes

- Conta Business do Pinterest: https://help.pinterest.com/en/business/article/get-a-business-account
- Pins em massa (CSV): https://help.pinterest.com/en/business/article/bulk-upload-video-pins
- Níveis de acesso da API do Pinterest: https://developers.pinterest.com/docs/key-concepts/access-tiers/
- Pré-requisitos do afiliado Shopee: https://help.shopee.com.br/portal/10/article/163025-Pr%C3%A9-requisitos-para-ser-um-Afiliado-Shopee
- Ativar a Maree: https://help.shopee.com.br/portal/10/article/142201-Como-ativar-a-ShopeePay
- Dados de pagamento (pessoa física): https://help.shopee.com.br/portal/10/article/125654-Pessoa-F%C3%ADsica:-saiba-como-cadastrar-suas-informa%C3%A7%C3%B5es-de-pagamento
- Pagamento das comissões: https://help.shopee.com.br/portal/10/article/163058-Processo-de-pagamento-das-comiss%C3%B5es-validadas
- Registro de desenvolvedor da Meta: https://developers.facebook.com/docs/development/register/
- Modo desenvolvimento sem revisão: https://postproxy.dev/blog/facebook-graph-api-posting-guide/
- Bot como administrador no Telegram: https://help.chatplace.io/en/articles/12670849-how-to-add-a-bot-as-an-admin-to-a-telegram-channel-or-chat

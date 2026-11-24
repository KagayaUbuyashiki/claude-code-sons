# Categorias de som

Referência completa: quando cada categoria toca, qual notificação aparece, quais áudios ela sorteia e quais palavras a disparam.
Tudo isso vem de [`sounds/manifest.json`](../sounds/manifest.json) e pode ser editado lá.

## Resumo

| Categoria | Quando toca | Áudios |
|---|---|---|
| [`inicio`](#inicio) | Ao abrir o Claude Code ou depois de `/clear` | 3 |
| [`fim`](#fim) | Fim de tarefa normal (caso padrão) | 9 |
| [`fim_longa`](#fim_longa) | Fim de uma tarefa que passou de 20 minutos | 1 |
| [`fase_final`](#fase_final) | Tarefa com mais de 10 min chegando no último item da lista de tarefas | 1 |
| [`plano_entregue`](#plano_entregue) | O Claude entregou um plano (plan mode) | 3 |
| [`esperando`](#esperando) | O Claude fez uma pergunta ou pediu permissão | 1 |
| [`plano_esperando`](#plano_esperando) | 5 minutos sem resposta ao plano/pergunta (repete até 3x) | 6 |
| [`bug`](#bug) | Você citou um bug no prompt **ou** a tarefa terminou com erro / com algo para você fazer na mão | 5 |
| [`testes_ok`](#testes_ok) | Fim de tarefa em que os testes rodaram e passaram (às vezes) | 1 |
| [`elogio`](#elogio) | Você elogiou o Claude, ou 3 tarefas seguidas sem bug (às vezes) | 2 |
| [`errou`](#errou) | Você disse que o Claude errou | 2 |
| [`reclamacao`](#reclamacao) | Você reclamou do Claude | 1 |
| [`xingamento`](#xingamento) | Você xingou o Claude | 1 |
| [`palavrao`](#palavrao) | Tem palavrão no prompt | 1 |
| [`longo`](#longo) | Prompt com 700+ caracteres, bloco de código ou 40+ linhas | 2 |
| [`dinheiro`](#dinheiro) | O prompt fala de dinheiro, preço, pagamento… | 3 |
| [`desafio`](#desafio) | O prompt fala de algo difícil / desafio | 1 |
| [`creditos`](#creditos) | Acabaram os créditos / limite de uso | 2 |

## Ordem de prioridade no prompt

Cada mensagem toca **no máximo 1** áudio. Se várias categorias baterem, vence a primeira desta lista:

`xingamento` → `palavrao` → `reclamacao` → `bug` → `errou` → `elogio` → `longo` → `dinheiro` → `desafio`

Em textos longos, `elogio`, `dinheiro` e `desafio` só olham os primeiros 400 caracteres (palavras soltas no meio de um texto grande dão falso positivo).

## inicio

**Quando:** Ao abrir o Claude Code ou depois de `/clear`

**Notificação:** **Claude Code pronto 🚀** — Nova sessão iniciada. Manda a tarefa!

**Áudios** (nome do arquivo: legenda original de quando ele deve tocar):

- `inicio_01.mp3`: _inicio de tarefa etc_
- `inicio_02.mp3`: _inicio do claude ou inicio de novas tarefas, todo inicio de nova tarefa que eu falo é depois de executar o barra clear ou então iniciar um novo chat_
- `inicio_03.mp3`: _toda vez que iniciar uma tarefa do zero, e inicar o claude_

## fim

**Quando:** Fim de tarefa normal (caso padrão)

**Notificação:** **Tarefa finalizada** — {tarefa} foi finalizada.

**Áudios** (nome do arquivo: legenda original de quando ele deve tocar):

- `fim_01.mp3`: _final de tarefa_
- `fim_02.mp3`: _final de tarefa1_
- `fim_03.mp3`: _final de tarefa2_
- `fim_04.mp3`: _final de tarefa22_
- `fim_05.mp3`: _final de tarefa3_
- `fim_06.mp3`: _final de tarefa4_
- `fim_07.mp3`: _finalizar tarefa_
- `fim_08.mp3`: _finalizar tarefa1_
- `fim_09.mp3`: _finalizar uma tarefa_

## fim_longa

**Quando:** Fim de uma tarefa que passou de 20 minutos

**Notificação:** **Tarefa longa finalizada** — {tarefa} foi finalizada.

**Áudios** (nome do arquivo: legenda original de quando ele deve tocar):

- `fim_longa_01.mp3`: _finalizar uma tarefa que passe de 20 minutos em aberto_

## fase_final

**Quando:** Tarefa com mais de 10 min chegando no último item da lista de tarefas

**Notificação:** **Reta final 🏁** — Falta só: {tarefa}

**Áudios** (nome do arquivo: legenda original de quando ele deve tocar):

- `fase_final_01.mp3`: _quando tiver uma tarefa longa e ela entraar nas fases finais essa musica deve tocar_

## plano_entregue

**Quando:** O Claude entregou um plano (plan mode)

**Notificação:** **Plano pronto 📋** — O plano de {tarefa} está esperando sua aprovação.

**Áudios** (nome do arquivo: legenda original de quando ele deve tocar):

- `plano_entregue_01.mp3`: _finalizar plan_
- `plano_entregue_02.mp3`: _na entrega de um plan_
- `plano_entregue_03.mp3`: _quando finalizar um plan_

## esperando

**Quando:** O Claude fez uma pergunta ou pediu permissão

**Notificação:** **Preciso de você** — Estou esperando sua resposta para continuar {tarefa}.

**Áudios** (nome do arquivo: legenda original de quando ele deve tocar):

- `esperando_01.mp3`: _esperando resposta no plan ou esperando o usuario fazer alguma coisa_

## plano_esperando

**Quando:** 5 minutos sem resposta ao plano/pergunta (repete até 3x)

**Notificação:** **Ei, tô te esperando! ⏰** — Já faz {tarefa} min que estou esperando sua resposta.

**Áudios** (nome do arquivo: legenda original de quando ele deve tocar):

- `plano_esperando_01.mp3`: _demora de resposta de plan_
- `plano_esperando_02.mp3`: _demora de resposta de plan1_
- `plano_esperando_03.mp3`: _demora pra resposta de plan_
- `plano_esperando_04.mp3`: _depois de 1 minuto sem resposta no plan, todos esses que tocam enquanto esperam a resposta do plan devem vir acompanhado de uma notificação do windows, detalhe eu falei um minuto mas deixe para 5 minutos sem respostas_
- `plano_esperando_05.mp3`: _ficar sem resposta no plan_
- `plano_esperando_06.mp3`: _quando o cara  receber a notificação do plan mas nn responder depois de 1 minuto_

## bug

**Quando:** Você citou um bug no prompt **ou** a tarefa terminou com erro / com algo para você fazer na mão

**Notificação:** **Bug na área 🐞** — Vou investigar: {tarefa}

**Palavras-chave:** `bug`, `bugs`, `bugou`, `bugado`, `bugada`, `bugando`, `buga`, `erro`, `erros`, `falha`, `falhas`, `crash`, `crashou`, `crasha`, `travou`, `travando`, `trava`, `quebrou`, `quebrado`, `quebrada`, `glitch`, `defeito`, `colisao invisivel`, `nao carrega`, `nao abre`, `sumiu`, `atravessando`, `error`, `exception`, `traceback`

**Áudios** (nome do arquivo: legenda original de quando ele deve tocar):

- `bug_01.mp3`: _bug no codigo ou algo do tipo_
- `bug_02.mp3`: _encontrar algum bug_
- `bug_03.mp3`: _encontrar algum bug, ou algo do tipo. Não sei se todos que estiverme o nome de encontrar bug seja uma boa ativar quando encontrar algum bug, acho que seria legal ativar ele quando finalizar alguma tarefa e ter que alterar alguma coisa na mão_
- `bug_04.mp3`: _erro em testes e bug encontrado_
- `bug_05.mp3`: _quando encontrar algum bug no codigo._

## testes_ok

**Quando:** Fim de tarefa em que os testes rodaram e passaram (às vezes)

**Notificação:** **Testes passando ✅** — {tarefa} foi finalizada e os testes passaram.

**Áudios** (nome do arquivo: legenda original de quando ele deve tocar):

- `testes_ok_01.mp3`: _toda vez que o claude receber elogio, ou ele exutar testes e nn dar erro_

## elogio

**Quando:** Você elogiou o Claude, ou 3 tarefas seguidas sem bug (às vezes)

**Notificação:** **Valeu! 😊** — Obrigado pelo elogio!

**Palavras-chave:** `valeu`, `obrigado`, `obrigada`, `brigado`, `perfeito`, `perfeita`, `mandou bem`, `muito bom`, `muito boa`, `excelente`, `show`, `top`, `incrivel`, `otimo`, `otima`, `parabens`, `brabo`, `braba`, `monstro`, `genio`, `ficou lindo`, `ficou bom`, `ficou otimo`, `amei`, `gostei`, `sensacional`, `maravilha`, `boa claude`

**Áudios** (nome do arquivo: legenda original de quando ele deve tocar):

- `elogio_01.mp3`: _quando o claude receber algum elogio ou no prompt ter ele elogiando o claude_
- `testes_ok_01.mp3`: _toda vez que o claude receber elogio, ou ele exutar testes e nn dar erro_

## errou

**Quando:** Você disse que o Claude errou

**Notificação:** **Foi mal 😅** — Já vou corrigir: {tarefa}

**Palavras-chave:** `errou`, `errado`, `errada`, `erro seu`, `nao era isso`, `nao e isso`, `nao foi isso`, `deu errado`, `nao funcionou`, `voce esqueceu`, `esqueceu de`, `falhou`

**Áudios** (nome do arquivo: legenda original de quando ele deve tocar):

- `errou_01.mp3`: _quando o claude errar_
- `errou_02.mp3`: _toda vez que eu faalar que o claude errou ou dar a entender isso_

## reclamacao

**Quando:** Você reclamou do Claude

**Notificação:** **Claude Code** — Chato é você 😤

**Mensagem no console:** Chato é você 😤

**Palavras-chave:** `chato`, `lento`, `demorando`, `demorou demais`, `que saco`, `pessimo`, `horrivel`, `ruim demais`, `ta ruim`, `nao funciona`, `nao ta funcionando`, `de novo isso`, `ja falei`, `ja disse`, `aff`, `affs`, `cansei`

**Áudios** (nome do arquivo: legenda original de quando ele deve tocar):

- `reclamacao_01.mp3`: _toda vez que o usuario reclamar do claude, ele retorna uma mensagem no console e uma notificação falando que chato é o usuario_

## xingamento

**Quando:** Você xingou o Claude

**Notificação:** **Ei, calma aí 😠** — Respeita o Claude, pô.

**Palavras-chave:** `burro`, `burra`, `idiota`, `imbecil`, `lixo`, `otario`, `estupido`, `inutil`, `cala a boca`, `vai se ferrar`, `vsf`, `vtnc`, `fdp`, `filho da puta`, `fi da puta`, `fe da puta`, `fio da puta`, `filha da puta`, `vai tomar no cu`, `tnc`, `vai se foder`, `se fode`, `vai tomando`, `tomando no`, `tomar no seu`, `bulldo`, `burrao`, `burrinho`, `caraio`, `do carai`, `claudio burro`, `arrombado`, `lerdo`, `jumento`, `anta`, `porcaria de ia`, `ia lixo`, `claude lixo`

**Áudios** (nome do arquivo: legenda original de quando ele deve tocar):

- `xingamento_01.mp3`: _toda vez que xingar o claude ou der patada no ckayde_

## palavrao

**Quando:** Tem palavrão no prompt

**Notificação:** **Olha a boca!** — É feio falar palavrão 🙊

**Palavras-chave:** `porra`, `porr`, `poha`, `porraa`, `caralho`, `krl`, `crl`, `merda`, `puta`, `putaria`, `foda`, `fodase`, `foda-se`, `pqp`, `cacete`, `bosta`, `desgraca`, `desgracado`, `cu`, `buceta`, `shit`, `fuck`

**Áudios** (nome do arquivo: legenda original de quando ele deve tocar):

- `palavrao_01.mp3`: _toda vez que tiver palavrão em algum prompt, subir uma notificação no windows, falando que é feio falar palavrão e tocar esse audio_

## longo

**Quando:** Prompt com 700+ caracteres, bloco de código ou 40+ linhas

**Notificação:** **Calma...** — Estou lendo tudo, já já respondo 📖

**Áudios** (nome do arquivo: legenda original de quando ele deve tocar):

- `longo_01.mp3`: _para prompts longos_
- `longo_02.mp3`: _toda vez que vier um codigo longo que eu pedir pra ler ou prompt com muitos caracteres, vai vir uma notificação falando, calma estou lendo enquanto toca esse audio_

## dinheiro

**Quando:** O prompt fala de dinheiro, preço, pagamento…

**Notificação:** **Assunto de dinheiro 💰** — {tarefa}

**Palavras-chave:** `dinheiro`, `r$`, `preco`, `precos`, `pagamento`, `pagar`, `venda`, `vendas`, `vender`, `lucro`, `salario`, `grana`, `financeiro`, `financas`, `orcamento`, `custo`, `custos`, `fatura`, `pix`, `money`, `reais`, `dolar`, `investimento`, `cobranca`

**Áudios** (nome do arquivo: legenda original de quando ele deve tocar):

- `dinheiro_01.mp3`: _tarefas envolvendo dinheiro_
- `dinheiro_02.mp3`: _tudo que envolver dinheiro_
- `dinheiro_03.mp3`: _tudo que envolver dinheiro1_

## desafio

**Quando:** O prompt fala de algo difícil / desafio

**Notificação:** **Desafio aceito 💪** — {tarefa}

**Palavras-chave:** `desafio`, `dificil`, `complexo`, `complexa`, `complicado`, `complicada`, `impossivel`, `challenge`, `cabeludo`, `parada dura`

**Áudios** (nome do arquivo: legenda original de quando ele deve tocar):

- `desafio_01.mp3`: _toda vez que tiver alguma coisa envolvendo desafio ou ter alguma tarefa dificil_

## creditos

**Quando:** Acabaram os créditos / limite de uso

**Notificação:** **Acabaram os créditos** — Atingi o limite de uso do Claude. Hora do café ☕

**Áudios** (nome do arquivo: legenda original de quando ele deve tocar):

- `creditos_01.mp3`: _acabou os creditos_
- `creditos_02.mp3`: _quando acabar os creditos_

---

`{tarefa}` nas notificações é trocado pelo pedido atual (ou pelo título do plano, pela pergunta, pelo último item da lista, conforme o evento).

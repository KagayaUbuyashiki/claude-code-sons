# Como funciona

## Visão geral

O Claude Code tem **hooks**: comandos que ele roda em certos momentos da sessão, passando um JSON com os detalhes do evento no `stdin` ([documentação oficial](https://docs.claude.com/en/docs/claude-code/hooks)). Este projeto registra 7 hooks que chamam o mesmo script, `sfx.py`, com um argumento diferente para cada evento:

| Hook | Argumento | Para quê |
|---|---|---|
| `SessionStart` | `start` | Som de início (só `startup` e `clear`) |
| `UserPromptSubmit` | `prompt` | Marca o início da tarefa, reage ao texto, `som off/on` |
| `PreToolUse` (`ExitPlanMode\|AskUserQuestion`) | `pretool` | Plano entregue / pergunta, e liga o timer de espera |
| `PostToolUse` (`ExitPlanMode\|AskUserQuestion\|TodoWrite`) | `posttool` | Cancela o timer; detecta a "reta final" pela lista de tarefas |
| `Notification` | `notify` | Pedidos de permissão, limite de uso |
| `Stop` | `stop` | Analisa a tarefa e toca o som de fim certo |
| `StopFailure` | `stopfail` | Erro da API, como limite e créditos |

## Arquivos

```
%USERPROFILE%\.claude\sounds\
├── sfx.py          # cérebro: decide o que tocar
├── player.ps1      # toca a fila de áudios e mostra as notificações
├── manifest.json   # configuração (categorias, áudios, notificações, palavras-chave)
├── pack\           # os MP3
├── queue\          # fila (criada em tempo de execução)
├── state.json      # histórico de sorteio, início da tarefa, timer (tempo de execução)
├── sfx.log         # o que tocou e por quê (só as últimas ~500 linhas)
└── muted.flag      # existe = modo silêncio
```

## Decisão no fim da tarefa (`Stop`)

O `sfx.py` lê o transcript da sessão (arquivo `.jsonl` que o Claude Code mantém) a partir da sua última mensagem e verifica:

1. **Erro de API** (limite/créditos) → `creditos`
2. A tarefa terminou **entregando um plano** → não toca nada (o plano já teve som)
3. **Algo deu errado:**
   - um comando no Bash/PowerShell retornou erro;
   - um teste falhou;
   - a saída de um comando de execução (python, node, npm…) mostrou `Traceback`, `FAILED`, `SyntaxError`, `npm ERR!` etc.;
   - ou a resposta final pede uma **ação manual** ("você precisa reiniciar…", "rode o comando…", "faça isso manualmente"). Trechos entre aspas ou crases são ignorados nessa análise, porque são exemplos e não instruções.

   Qualquer um desses → `bug`.
4. Tarefa com **20 min ou mais** → `fim_longa`
5. **Testes rodaram e passaram** → `testes_ok` (50% das vezes)
6. **3 tarefas seguidas sem bug** → `elogio` (50% das vezes)
7. Senão → `fim`

Comandos que você recusou numa permissão não contam como erro.

## Reação ao prompt (`UserPromptSubmit`)

O texto é normalizado (minúsculas, sem acento) e comparado com as `keywords` de cada categoria, na ordem de `prioridade_prompt`. Toca só a primeira que bater. Palavras precisam aparecer inteiras. Em prompts longos, `elogio`, `dinheiro` e `desafio` só olham o começo do texto, para evitar falso positivo.

## Fila e "um som por vez"

1. O `sfx.py` grava `queue\<timestamp>.json` com o MP3, a notificação e o horário, e lança o `player.ps1` em segundo plano (sem janela, fora do *job* do Claude Code, para não morrer quando o hook termina).
2. O `player.ps1` pega um **mutex nomeado** do Windows (`Global\ClaudeCodeSfxPlayer`). Se outro player já estiver tocando, ele espera a vez.
3. Com o mutex, ele toca os itens da fila em ordem, mostra a notificação e espera o áudio acabar. Itens com mais de 90 s são descartados, e a fila guarda no máximo 3 itens.

O MP3 toca com `System.Windows.Media.MediaPlayer`. A notificação usa a API de *toast* do Windows (WinRT), com o ID de aplicativo do Windows PowerShell, por isso ela aparece como "Windows PowerShell".

## Timer de espera

Quando um plano ou uma pergunta é entregue, o `sfx.py` gera um *token*, guarda no `state.json` e inicia um processo destacado `sfx.py watch <token> <transcript>`. A cada 5 min, esse processo confere se:

- o token ainda é o mesmo (quando você responde, o token é apagado);
- o transcript não mudou (se mudou, alguém respondeu).

Se nada mudou, ele toca `plano_esperando`, até 3 vezes.

## Desempenho

Cada hook leva poucas dezenas de milissegundos (o tempo de iniciar o Python). O `Stop` lê no máximo as últimas 3000 linhas do transcript. Todos os erros são capturados e vão para o `sfx.log`: o script nunca quebra a sessão do Claude.

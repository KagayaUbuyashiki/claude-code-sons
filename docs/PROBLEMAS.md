# Problemas comuns

Antes de tudo, abra o log: `%USERPROFILE%\.claude\sounds\sfx.log`. Cada linha mostra o que tocou (`tocar [categoria] arquivo`), o resultado da análise do fim de tarefa (`stop: {...}`) e eventuais erros (`erro em ...`).

## O instalador diz "Python nao encontrado"
Instale o Python 3 em <https://www.python.org/downloads/>, marcando **"Add python.exe to PATH"**. Feche e abra a pasta de novo e rode o `INSTALAR.bat`.
Se o comando `python` abrir a Microsoft Store, desative os *aliases* em *Configurações → Aplicativos → Configurações avançadas → Aliases de execução de aplicativo* (python.exe e python3.exe).

## Não toca nada
1. **Reinicie o Claude Code.** Os hooks só são lidos ao abrir.
2. Confira se não está em modo silêncio: se existir `%USERPROFILE%\.claude\sounds\muted.flag`, apague o arquivo ou digite `som on`.
3. Teste direto: `py "%USERPROFILE%\.claude\sounds\sfx.py" test fim`.
   - **Tocou:** o problema está nos hooks. Abra `%USERPROFILE%\.claude\settings.json` e veja se os 7 hooks com `sounds/sfx.py` estão lá. No Claude Code, o comando `/hooks` mostra quais estão ativos.
   - **Não tocou:** confira o volume e o dispositivo de saída do Windows, e se o `sfx.log` mostra uma linha `tocar`.
4. Algumas políticas corporativas bloqueiam scripts PowerShell. O player já roda com `-ExecutionPolicy Bypass`, mas uma GPO pode impedir mesmo assim.

## Toca o som, mas a notificação não aparece
- Em *Configurações → Sistema → Notificações*, ative as notificações e, na lista de apps, o **Windows PowerShell**.
- Desligue o **Não incomodar** ou o **Assistente de foco**.

## Tocou o som "errado"
A detecção é por palavras-chave, então às vezes erra (ex.: "o que está *errado* aqui?" dispara `errou`). Procure a linha no `sfx.log`, veja qual categoria venceu e ajuste as `keywords` ou a `prioridade_prompt` no `manifest.json` ([guia](PERSONALIZAR.md#3-palavras-chave-das-reações)).

## O fim da tarefa sempre toca o som de bug
A linha `stop: {...}` do log mostra o motivo:
- `'error': True`: algum comando ou teste falhou durante a tarefa;
- `'manual': True`: a resposta final pediu uma ação sua ("você precisa…", "rode o comando…").

Para mudar as regras, edite `FAIL_RE` e `MANUAL_RE` no `sfx.py`.

## Os sons atrasam ou embolam
Os sons ficam numa fila e tocam um por vez. Se muita coisa acontecer junto, a fila guarda até 3 sons e descarta os que esperaram mais de 90 s. Para filas menores, diminua `max_fila` no `manifest.json`.

## O nome do meu usuário do Windows tem espaço
Funciona: o instalador coloca os caminhos entre aspas quando necessário. Se o Claude Code estiver configurado para rodar hooks no PowerShell em vez do Git Bash e der erro, edite os comandos no `settings.json` colocando `& ` na frente, por exemplo: `& "C:/Users/Meu Nome/.../python.exe" "C:/.../sfx.py" stop`.

## Quero voltar à configuração antiga
O instalador salva `settings.json.bak-DATA` em `%USERPROFILE%\.claude\`. Copie o conteúdo dele de volta para o `settings.json`, ou só rode `DESINSTALAR.bat`.

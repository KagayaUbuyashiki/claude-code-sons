# 🔊 claude-code-sons

**Feedback sonoro para o [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) no Windows.** Em vez de um bipe sem graça, o Claude passa a reagir com áudios (e uma notificação do Windows) ao que acontece na sessão: quando ele termina uma tarefa, entrega um plano, fica esperando você, encontra um bug... e também quando você elogia, reclama, fala de dinheiro ou solta um palavrão.

> 44 áudios · 18 categorias · nada se repete em sequência · um som por vez · instalação com dois cliques

> [!NOTE]
> Projeto da comunidade, **não oficial**. Não tem nenhuma ligação com a Anthropic. Ele só usa os [hooks](https://docs.claude.com/en/docs/claude-code/hooks), um recurso documentado do Claude Code.

---

## Sumário

- [O que ele faz](#-o-que-ele-faz)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Como usar](#-como-usar)
- [Personalizar](#-personalizar)
- [Desinstalar](#-desinstalar)
- [Problemas comuns](#-problemas-comuns)
- [Como funciona por dentro](#-como-funciona-por-dentro)
- [Privacidade e custo](#-privacidade-e-custo)
- [Licença](#-licença)

---

## ✨ O que ele faz

| Momento | O que acontece |
|---|---|
| 🚀 Abriu o Claude ou deu `/clear` | Som de início + notificação *"Claude Code pronto"* |
| ✅ Terminou uma tarefa | **Sempre** toca um dos 9 sons de fim, e a notificação diz *qual* tarefa terminou |
| 🐞 A tarefa teve erro, ou ficou algo para você fazer na mão | Em vez do som de fim, toca um som de **bug** e a notificação avisa *"finalizada com ressalvas"* |
| ⏱️ Tarefa passou de 20 min | Som especial de tarefa longa, com a duração na notificação |
| 🏁 Tarefa longa chegando no fim | "Música de reta final" quando só falta 1 item da lista de tarefas |
| 📋 Entregou um plano | Som de plano + *"O plano de … está esperando sua aprovação"* |
| ❓ Fez uma pergunta ou pediu permissão | Som de espera com a pergunta na notificação |
| ⏰ 5 min sem você responder | Som de cobrança + notificação (repete até 3 vezes) |
| 💬 Você mandou uma mensagem | Reage ao conteúdo: xingamento, palavrão, reclamação, bug, "você errou", elogio, texto longo, dinheiro, desafio |
| 💸 Acabaram os créditos | Som de créditos + aviso |

**Para não ficar repetitivo:**
- Os áudios de cada categoria são sorteados e os últimos 3 que tocaram ficam de fora.
- Os sons entram numa **fila**: nunca tocam dois ao mesmo tempo.
- Avisos que esperaram mais de 90 s na fila são descartados.
- Eventos que acontecem durante o trabalho (erros, testes) só viram som **no final**, num resumo do que rolou.

A lista completa de categorias, palavras-chave e áudios está em **[docs/CATEGORIAS.md](docs/CATEGORIAS.md)**.

---

## 📦 Requisitos

| | |
|---|---|
| **Sistema** | Windows 10 ou 11. O som e as notificações usam PowerShell e as APIs do Windows. |
| **Claude Code** | Qualquer versão recente: CLI, app desktop ou extensão do VS Code/JetBrains |
| **Python** | 3.8 ou mais novo, de [python.org](https://www.python.org/downloads/). Na instalação, marque **"Add python.exe to PATH"**. |

Não precisa instalar nenhuma biblioteca: o projeto usa só a biblioteca padrão do Python.

---

## 🛠️ Instalação

### Opção 1: download direto (mais fácil)

1. Baixe o projeto: botão verde **`<> Code` → `Download ZIP`** (ou pegue o arquivo na aba [Releases](../../releases)).
2. Extraia numa pasta qualquer.
3. Dê **dois cliques em `INSTALAR.bat`**.
4. Vai tocar um som de teste. Depois disso, **feche e abra o Claude Code** de novo.

### Opção 2: pelo terminal

```powershell
git clone https://github.com/KagayaUbuyashiki/claude-code-sons.git
cd claude-code-sons
py -3 instalar.py        # ou: python instalar.py
```

### Opção 3: deixe o Claude instalar

Abra o Claude Code na pasta extraída e peça:

```
Leia o README.md desta pasta e rode o instalar.py para mim.
```

### O que o instalador mexe no seu PC

| Onde | O quê |
|---|---|
| `%USERPROFILE%\.claude\sounds\` | Copia os scripts e os 44 MP3 |
| `%USERPROFILE%\.claude\settings.json` | Adiciona 7 hooks (`SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Notification`, `Stop`, `StopFailure`) |
| `%USERPROFILE%\.claude\settings.json.bak-DATA` | Backup da sua configuração anterior |

O resto da sua configuração, **inclusive outros hooks que você já tenha**, continua do jeito que estava. Rodar o instalador de novo atualiza a instalação sem duplicar nada.

> [!TIP]
> Na primeira vez que um hook rodar, o Claude Code pode pedir para você revisar ou aprovar os hooks novos. É normal: aprove.

---

## 🎮 Como usar

Depois de instalado, é só usar o Claude Code normalmente. Alguns extras:

| Comando (no prompt do Claude) | Efeito |
|---|---|
| `som off` | Silencia tudo. A mensagem **não** é enviada ao Claude. |
| `som on` | Liga de novo |

Para ouvir uma categoria pelo terminal:

```powershell
py "%USERPROFILE%\.claude\sounds\sfx.py" test fim
py "%USERPROFILE%\.claude\sounds\sfx.py" test bug
py "%USERPROFILE%\.claude\sounds\sfx.py" test elogio
```

Para testar as reações a mensagens, mande ao Claude coisas como *"valeu, mandou bem!"*, *"tem um bug na tela de login"* ou *"quanto custa isso em R$?"*.

---

## 🎨 Personalizar

Tudo fica em **`%USERPROFILE%\.claude\sounds\manifest.json`**, e não é preciso mexer em código. Guia completo em **[docs/PERSONALIZAR.md](docs/PERSONALIZAR.md)**. Resumo:

```jsonc
"elogio": {
  "files": ["elogio_01", "elogio_02"],                   // MP3 da pasta pack\ (nome exato ou prefixo*)
  "toast": ["Valeu! 😊", "Obrigado pelo elogio!"]        // [título, texto] da notificação
}
...
"keywords": {
  "elogio": ["valeu", "obrigado", "mandou bem", "top"]   // sem acento, minúsculas
}
...
"settings": {
  "espera_plano_segundos": 300,     // tempo até cobrar resposta
  "tarefa_longa_minutos": 20,
  "prompt_longo_caracteres": 700
}
```

**Trocar os áudios pelos seus:** jogue os MP3 em `sounds\pack\` e coloque o nome deles na categoria. Dá para usar sua voz, efeitos sonoros ou o que quiser.

---

## 🗑️ Desinstalar

Dê dois cliques em **`DESINSTALAR.bat`**, ou rode `py -3 instalar.py --remover`. Isso tira **só** os hooks deste projeto do `settings.json`. Depois, se quiser, apague a pasta `%USERPROFILE%\.claude\sounds`.

---

## 🩺 Problemas comuns

Detalhes em **[docs/PROBLEMAS.md](docs/PROBLEMAS.md)**. Os mais frequentes:

| Sintoma | Solução |
|---|---|
| `Python nao encontrado` | Instale o Python marcando *Add to PATH* e rode o `INSTALAR.bat` de novo |
| Não toca nada | Reinicie o Claude Code. Veja se não está em `som off`. Rode `sfx.py test fim`. |
| Toca, mas não aparece notificação | Ative as notificações do **Windows PowerShell** em *Configurações → Sistema → Notificações* e desligue o *Não incomodar* |
| Tocou o som "errado" | A detecção é por palavra-chave. Veja o motivo em `%USERPROFILE%\.claude\sounds\sfx.log` e ajuste as `keywords`. |

---

## ⚙️ Como funciona por dentro

```
Claude Code ──(hook + JSON no stdin)──► sfx.py ──► decide a categoria e sorteia o áudio
                                           │
                                           ▼
                                   sounds\queue\*.json  (fila)
                                           │
                                           ▼
                                      player.ps1  ──► toca o MP3 + mostra a notificação
                                   (mutex: 1 por vez)
```

- **`sfx.py`** é chamado pelos hooks. Ele lê o evento, analisa o prompt ou o histórico da tarefa (para achar erros, testes e pedidos de ação manual), escolhe a categoria e põe o áudio na fila. Termina em milissegundos e nunca trava o Claude.
- **`player.ps1`** toca a fila em ordem, um áudio por vez, garantido por um mutex do Windows.
- **`manifest.json`** guarda toda a configuração.

Detalhes técnicos em **[docs/COMO-FUNCIONA.md](docs/COMO-FUNCIONA.md)**.

---

## 🔒 Privacidade e custo

- **Roda 100% local.** Nada é enviado para a internet.
- **Não gasta créditos nem tokens.** Os hooks não falam com a API e não colocam nada na conversa com o Claude. As únicas exceções, de propósito, são as mensagens de `som off`/`som on` e da reclamação, que aparecem só para você.
- O `sfx.py` lê o seu prompt e o histórico da sessão (`transcript`) **só na sua máquina**, para decidir o som. O log `sfx.log` guarda apenas a categoria escolhida e o começo do pedido.

---

## 📄 Licença

O código está sob a licença [MIT](LICENSE). Os áudios em `sounds/pack/` foram gravados pelo autor do projeto e são distribuídos para uso com este pacote.

Feito com 🔊 por [@KagayaUbuyashiki](https://github.com/KagayaUbuyashiki). Contribuições e novos pacotes de som são bem-vindos: abra uma *issue* ou um *pull request*.

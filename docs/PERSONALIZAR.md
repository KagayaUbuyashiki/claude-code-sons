# Personalizar

Toda a configuração fica em `%USERPROFILE%\.claude\sounds\manifest.json`. Depois de editar, **não precisa reiniciar nada**: o arquivo é lido de novo a cada evento.

> Edite com cuidado: o arquivo precisa continuar sendo um JSON válido (vírgulas, aspas). Na dúvida, cole o conteúdo em <https://jsonlint.com>. Se algo quebrar, o instalador guarda o anterior em `manifest.json.bak`.

## 1. Trocar ou adicionar áudios

1. Coloque o MP3 em `%USERPROFILE%\.claude\sounds\pack\`.
2. No `manifest.json`, adicione o nome do arquivo **sem `.mp3`** na lista `files` da categoria:

```json
"fim": {
  "files": ["fim_01", "fim_02", "meu_som_de_vitoria"]
}
```

- **Nome exato:** `"fim_01"` casa só com `fim_01.mp3`.
- **Prefixo:** `"fim_*"` casa com todos os arquivos que começam assim (`fim_01`, `fim_02`…).
- Formato: **MP3**. Só arquivos `.mp3` da pasta `pack\` são considerados. Converta outros formatos antes (ex.: com o Audacity).
- Quanto mais áudios numa categoria, menos repetitivo fica: o sorteio deixa de fora os últimos 3 (`settings.evitar_ultimos`).

Teste: `py "%USERPROFILE%\.claude\sounds\sfx.py" test fim`

## 2. Mudar as notificações

```json
"bug": {
  "toast": ["Bug na área 🐞", "Vou investigar: {tarefa}"]
}
```

- O primeiro texto é o título, o segundo é a mensagem.
- `{tarefa}` vira o contexto do evento:

| Categoria | `{tarefa}` vira |
|---|---|
| reações ao prompt (`bug`, `errou`, `dinheiro`, `desafio`…) | o começo da sua mensagem |
| `plano_entregue` | o título do plano |
| `fase_final` | o último item da lista de tarefas |
| `plano_esperando` | os minutos de espera |
| `fim`, `fim_longa` | o pedido que originou a tarefa |

- **Fim de tarefa:** os textos das variações (com erro, testes passando, tarefa longa, sequência sem bug) são montados no `sfx.py` (função `ev_stop`), porque dependem da análise da tarefa.
- **Mensagem no console:** a chave `"console"` (usada em `reclamacao`) mostra um texto no próprio Claude Code.

## 3. Palavras-chave das reações

```json
"keywords": {
  "dinheiro": ["dinheiro", "r$", "preco", "pix"]
}
```

- Escreva **sem acento e em minúsculas**: o texto do prompt é normalizado antes da comparação ("Preço" vira "preco").
- A palavra precisa aparecer inteira: `"top"` não casa com "laptop".
- Frases funcionam: `"mandou bem"`.
- Para `elogio`, um "não" logo antes anula ("não gostei" não conta como elogio).
- Para mudar quem ganha quando várias categorias batem, reordene `prioridade_prompt`.

## 4. Tempos e limites (`settings`)

| Chave | Padrão | O que faz |
|---|---|---|
| `evitar_ultimos` | 3 | Quantos áudios recentes ficam fora do sorteio |
| `max_fila` | 3 | Máximo de sons esperando na fila (o resto é descartado) |
| `espera_plano_segundos` | 300 | Tempo sem resposta até o som de cobrança |
| `espera_plano_repeticoes` | 3 | Quantas vezes a cobrança se repete |
| `fase_final_minutos` | 10 | Duração mínima da tarefa para tocar a "reta final" |
| `tarefa_longa_minutos` | 20 | A partir de quanto o fim conta como tarefa longa |
| `prompt_longo_caracteres` | 700 | Tamanho para considerar o prompt "longo" |
| `chance_testes_ok` | 0.5 | Chance de tocar a comemoração quando os testes passam |
| `sequencia_sem_bug` | 3 | Tarefas seguidas sem bug para (às vezes) ganhar um elogio |

## 5. Criar uma categoria nova

Categorias novas precisam de uma linha de código dizendo **quando** tocar. As de prompt são as mais fáceis:

1. Em `categories`, crie `"cafe": { "files": [...], "toast": ["☕", "{tarefa}"] }`.
2. Em `keywords`, crie `"cafe": ["cafe", "cafezinho"]`.
3. Adicione `"cafe"` em `prioridade_prompt`, na posição que quiser.

Pronto: não precisa mexer no código. Para eventos de outro tipo (ferramentas, tempo…), edite as funções `ev_*` do `sfx.py`.

## 6. Silenciar

- `som off` / `som on` no prompt do Claude.
- Ou crie e apague o arquivo `%USERPROFILE%\.claude\sounds\muted.flag`.

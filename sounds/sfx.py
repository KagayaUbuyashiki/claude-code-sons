"""Dispatcher de sons do Claude Code.

Chamado pelos hooks: python sfx.py <evento>   (JSON do hook no stdin)
Eventos: start, prompt, pretool, posttool, notify, stop, stopfail
Manual:  python sfx.py test <categoria>   |   python sfx.py watch <token> <transcript>
Configuracao em manifest.json; estado em state.json; log em sfx.log.
"""
import json
import os
import random
import re
import subprocess
import sys
import time
import unicodedata
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(HERE, "pack")
QUEUE = os.path.join(HERE, "queue")
STATE = os.path.join(HERE, "state.json")
LOG = os.path.join(HERE, "sfx.log")
MUTED = os.path.join(HERE, "muted.flag")
PLAYER = os.path.join(HERE, "player.ps1")

NO_WINDOW = 0x08000000
DETACHED = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

with open(os.path.join(HERE, "manifest.json"), encoding="utf-8") as fh:
    MAN = json.load(fh)
CFG = MAN["settings"]


# ---------------------------------------------------------------- utilidades
def log(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}\n")
        if os.path.getsize(LOG) > 300_000:
            with open(LOG, encoding="utf-8") as fh:
                tail = fh.readlines()[-500:]
            with open(LOG, "w", encoding="utf-8") as fh:
                fh.writelines(tail)
    except OSError:
        pass


def load_state():
    try:
        with open(STATE, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def save_state(st):
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)


def norm(text):
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


def has_kw(text, words):
    """text ja normalizado. Casa palavra/frase inteira."""
    for w in words:
        pat = r"(?<![\w$])" + re.escape(w) + (r"(?!\w)" if w[-1].isalnum() else "")
        for m in re.finditer(pat, text):
            before = text[max(0, m.start() - 6):m.start()]
            if "nao " in before:  # "nao gostei", "nao e ruim"...
                continue
            return True
    return False


def pack_files():
    return sorted(f[:-4] for f in os.listdir(PACK) if f.lower().endswith(".mp3"))


def resolve(cat):
    stems = pack_files()
    out = []
    for pat in MAN["categories"][cat]["files"]:
        if pat.endswith("*"):
            out += [s for s in stems if s.startswith(pat[:-1])]
        elif pat in stems:
            out.append(pat)
    return sorted(set(out))


def spawn(args, detach=True):
    # BREAKAWAY: sai do Job do processo pai, senao o filho morre quando o hook termina.
    base = NO_WINDOW | (0x00000200 if detach else 0)
    for flags in (base | 0x01000000, base):
        try:
            subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, close_fds=True, creationflags=flags)
            return
        except OSError as exc:
            log(f"spawn falhou ({flags:#x}): {exc!r}")


# ---------------------------------------------------------------- tocar
def play(cat, st, toast=None, tarefa=""):
    """Sorteia um audio da categoria (sem repetir os ultimos) e poe na fila.
    Todo audio sai com notificacao: a passada aqui ou a padrao da categoria
    ({tarefa} no texto e trocado pelo pedido/tarefa atual)."""
    if os.path.exists(MUTED):
        log(f"mudo: {cat}")
        return
    files = resolve(cat)
    if not files:
        log(f"sem arquivos: {cat}")
        return
    hist = st.setdefault("hist", {}).setdefault(cat, [])
    avoid = hist[-min(CFG["evitar_ultimos"], len(files) - 1):] if len(files) > 1 else []
    choice = random.choice([f for f in files if f not in avoid] or files)
    hist.append(choice)
    del hist[:-10]
    st["last_play"] = {"cat": cat, "t": time.time()}

    os.makedirs(QUEUE, exist_ok=True)
    if len([q for q in os.listdir(QUEUE) if q.endswith(".json")]) >= CFG["max_fila"]:
        log(f"fila cheia, descartado: {cat}")
        return
    cdef = MAN["categories"][cat]
    toast = toast or cdef.get("toast") or ["Claude Code", cat]
    tarefa = tarefa or "esta tarefa"
    toast = [s.replace("{tarefa}", tarefa) for s in toast]
    item = {"file": os.path.join(PACK, choice + ".mp3"), "ts": time.time(),
            "cat": cat, "toast": toast}
    name = os.path.join(QUEUE, f"{time.time_ns()}.json")
    with open(name + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(item, fh, ensure_ascii=False)
    os.replace(name + ".tmp", name)
    log(f"tocar [{cat}] {choice}")
    spawn(["powershell.exe", "-NoProfile", "-STA", "-ExecutionPolicy", "Bypass",
           "-WindowStyle", "Hidden", "-File", PLAYER])


def recently(st, cats, seconds):
    lp = st.get("last_play") or {}
    return lp.get("cat") in cats and time.time() - lp.get("t", 0) < seconds


def start_wait(st, data):
    token = str(time.time_ns())
    st["wait_token"] = token
    spawn([sys.executable, os.path.abspath(__file__), "watch", token,
           data.get("transcript_path") or ""])


# ---------------------------------------------------------------- eventos
def ev_start(data, st):
    st.pop("wait_token", None)
    if data.get("source") in ("startup", "clear"):
        play("inicio", st)


def ev_prompt(data, st):
    st.pop("wait_token", None)
    st["turn"] = {"start": time.time(), "fase_final": False}
    raw = data.get("prompt") or ""
    t = norm(raw).strip()

    # Modo silencio
    if t in ("som off", "/som off", "silencio", "sons off"):
        open(MUTED, "w").close()
        print(json.dumps({"decision": "block", "reason": "🔇 Sons desligados. Digite 'som on' para voltar."}, ensure_ascii=False))
        return
    if t in ("som on", "/som on", "sons on"):
        if os.path.exists(MUTED):
            os.remove(MUTED)
        print(json.dumps({"decision": "block", "reason": "🔊 Sons ligados!"}, ensure_ascii=False))
        return

    kw = MAN["keywords"]
    longo = len(raw) >= CFG["prompt_longo_caracteres"] or "```" in raw or raw.count("\n") > 40
    # Em textos longos, palavras soltas (dinheiro, desafio, elogio...) sao frequentes
    # por acaso, entao so olhamos as primeiras linhas para essas categorias.
    head = norm(raw[:400]) if longo else t
    for cat in MAN["prioridade_prompt"]:
        if cat == "longo":
            hit = longo
        else:
            hit = has_kw(head if cat in ("elogio", "dinheiro", "desafio") else t, kw[cat])
        if hit:
            play(cat, st, tarefa=f"“{task_name(raw)}”")
            console = MAN["categories"][cat].get("console")
            if console:
                print(json.dumps({"systemMessage": console}, ensure_ascii=False))
            return


def ev_pretool(data, st):
    name = data.get("tool_name", "")
    inp = data.get("tool_input") or {}
    if name == "ExitPlanMode":
        title = re.search(r"^#\s+(.+)$", str(inp.get("plan") or ""), re.M)
        play("plano_entregue", st, tarefa=f"“{title.group(1).strip()}”" if title else "")
        start_wait(st, data)
    elif name == "AskUserQuestion":
        qs = inp.get("questions") or [{}]
        q = task_name(qs[0].get("question", ""))
        play("esperando", st, ["Tenho uma pergunta ❓", q] if q else None)
        start_wait(st, data)


def ev_posttool(data, st):
    name = data.get("tool_name", "")
    if name in ("ExitPlanMode", "AskUserQuestion"):
        st.pop("wait_token", None)
    elif name == "TodoWrite":
        turn = st.get("turn") or {}
        todos = (data.get("tool_input") or {}).get("todos") or []
        left = [x for x in todos if x.get("status") != "completed"]
        elapsed = time.time() - turn.get("start", time.time())
        if (len(todos) >= 3 and len(left) == 1 and not turn.get("fase_final")
                and elapsed > CFG["fase_final_minutos"] * 60):
            turn["fase_final"] = True
            st["turn"] = turn
            play("fase_final", st, tarefa=task_name(left[0].get("content", "")))


def ev_notify(data, st):
    msg = norm(data.get("message") or "")
    ntype = data.get("notification_type") or ""
    if any(w in msg for w in ("limit", "credit", "credito", "usage")):
        play("creditos", st)
        return
    if ntype == "idle_prompt" or "waiting for your input" in msg:
        return  # o fim da tarefa ja teve som; nao incomodar a cada 60 s
    if recently(st, ("plano_entregue", "esperando"), 20):
        return
    play("esperando", st, ["Preciso de você", task_name(data.get("message") or "")] if data.get("message") else None)
    start_wait(st, data)


def ev_stopfail(data, st):
    play("creditos", st)


TEST_RE = re.compile(r"\b(pytest|unittest|jest|vitest|mocha|npm (run )?test|yarn test|pnpm test|"
                     r"go test|cargo test|dotnet test|phpunit|rspec|test\.py|tests?/)", re.I)
RUN_RE = re.compile(r"\b(python|py|node|npm|npx|tsc|cargo|go|dotnet|java|gradle|make|luac)\b", re.I)
FAIL_RE = re.compile(r"(Traceback \(most recent call last\)|\bFAILED\b|\bfailed\b|AssertionError|"
                     r"SyntaxError|TypeError|ReferenceError|ModuleNotFoundError|\bERROR\b|"
                     r"error TS\d+|npm ERR!|exit code [1-9]|Exit code [1-9])")
MANUAL_RE = re.compile(r"(voce (vai )?precisa(ra)? (rodar|executar|abrir|reiniciar|instalar|copiar|colar|alterar|trocar|fazer|configurar)|"
                       r"voce mesmo (precisa|deve|tem)|voce tera que|faca (isso )?manualmente|altere (isso )?na mao|"
                       r"precisa(ra)? (rodar|executar|abrir|reiniciar|instalar|copiar|colar|alterar|trocar)|"
                       r"rode (o|este|esse)|execute (o|este|esse) comando|reinicie|faca o seguinte)")


def text_of(content):
    if isinstance(content, str):
        return content
    out = []
    for c in content or []:
        if isinstance(c, dict):
            if c.get("type") == "text":
                out.append(c.get("text", ""))
            elif c.get("type") == "tool_result":
                out.append(text_of(c.get("content")))
    return "\n".join(out)


def task_name(prompt):
    """Resumo curto do pedido do usuario para usar na notificacao."""
    text = re.sub(r"<[^>]+>", " ", prompt or "")  # tira tags (comandos, pastes)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 90:
        text = text[:87].rsplit(" ", 1)[0] + "…"
    return text


def analyse_turn(path):
    """Le o transcript do turno atual e devolve um resumo do que aconteceu."""
    res = {"error": False, "tests_ok": False, "manual": False, "plan": False, "api_limit": False, "task": ""}
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()[-3000:]
    except (OSError, TypeError):
        return res
    entries = []
    for ln in lines:
        try:
            entries.append(json.loads(ln))
        except ValueError:
            pass
    # comeco do turno = ultima mensagem real do usuario (nao tool_result)
    start = 0
    for i, e in enumerate(entries):
        if e.get("type") == "user" and not e.get("isMeta"):
            c = (e.get("message") or {}).get("content")
            if isinstance(c, str) or (isinstance(c, list) and any(
                    isinstance(x, dict) and x.get("type") == "text" for x in c)):
                start = i
    if entries:
        res["task"] = task_name(text_of((entries[start].get("message") or {}).get("content")))
    tools = {}
    tests_ran = tests_failed = False
    last_text, last_tool = "", None
    for e in entries[start:]:
        msg = e.get("message") or {}
        content = msg.get("content")
        if e.get("type") == "assistant":
            if e.get("isApiErrorMessage") and re.search(r"limit|credit|usage", text_of(content), re.I):
                res["api_limit"] = True
            for c in content if isinstance(content, list) else []:
                if c.get("type") == "tool_use":
                    tools[c.get("id")] = (c.get("name"), c.get("input") or {})
                    last_tool = c.get("name")
                elif c.get("type") == "text" and c.get("text", "").strip():
                    last_text = c["text"]
                    last_tool = None
        elif e.get("type") == "user" and isinstance(content, list):
            for c in content:
                if not isinstance(c, dict) or c.get("type") != "tool_result":
                    continue
                name, inp = tools.get(c.get("tool_use_id"), ("", {}))
                out = text_of(c.get("content"))
                if re.search(r"doesn't want|rejected|was blocked|user declined|interrupted", out, re.I):
                    continue
                cmd = str(inp.get("command", "")) if name in ("Bash", "PowerShell") else ""
                is_test = bool(cmd and TEST_RE.search(cmd))
                is_run = bool(cmd and RUN_RE.search(cmd))
                failed = bool(c.get("is_error")) and name in ("Bash", "PowerShell")
                if (is_test or is_run) and FAIL_RE.search(out):
                    failed = True
                if is_test:
                    tests_ran = True
                    tests_failed |= failed
                if failed:
                    res["error"] = True
    res["tests_ok"] = tests_ran and not tests_failed
    # Ignora trechos citados ("...", “...”, `...`): exemplos nao sao instrucoes reais
    unquoted = re.sub(r"```.*?```|`[^`]*`|\"[^\"]*\"|“[^”]*”", " ", last_text, flags=re.S)
    res["manual"] = bool(MANUAL_RE.search(norm(unquoted)))
    res["plan"] = last_tool == "ExitPlanMode"
    return res


def ev_stop(data, st):
    if data.get("stop_hook_active"):
        return
    r = analyse_turn(data.get("transcript_path"))
    turn = st.get("turn") or {}
    mins = (time.time() - turn.get("start", time.time())) / 60
    log(f"stop: {r} {mins:.1f}min")
    if r["api_limit"]:
        play("creditos", st)
        return
    if r["plan"]:
        return
    task = f"“{r['task']}”" if r["task"] else "A tarefa"
    if r["error"] or r["manual"]:
        st["streak"] = 0
        motivo = "precisa de uma ação sua" if r["manual"] and not r["error"] else "teve erros pelo caminho"
        play("bug", st, ["Tarefa finalizada com ressalvas", f"{task} foi finalizada, mas {motivo}."])
        return
    st["streak"] = st.get("streak", 0) + 1
    if mins >= CFG["tarefa_longa_minutos"]:
        play("fim_longa", st, ["Tarefa longa finalizada", f"{task} foi finalizada após {int(mins)} min."])
    elif r["tests_ok"] and random.random() < CFG["chance_testes_ok"]:
        play("testes_ok", st, ["Tarefa finalizada", f"{task} foi finalizada e os testes passaram."])
    elif st["streak"] >= CFG["sequencia_sem_bug"] and random.random() < 0.5:
        st["streak"] = 0
        play("elogio", st, ["Tarefa finalizada", f"{task} foi finalizada. {CFG['sequencia_sem_bug']} seguidas sem bug 🔥"])
    else:
        play("fim", st, ["Tarefa finalizada", f"{task} foi finalizada."])


def watch(token, transcript):
    """Processo destacado: avisa se o usuario nao responder ao plano/pergunta."""
    t0 = time.time()
    for n in range(1, CFG["espera_plano_repeticoes"] + 1):
        time.sleep(CFG["espera_plano_segundos"])
        st = load_state()
        if st.get("wait_token") != token:
            return
        try:  # alguem respondeu (transcript andou) -> cancela
            if transcript and os.path.getmtime(transcript) > t0 + 5:
                return
        except OSError:
            pass
        play("plano_esperando", st, tarefa=str(n * CFG["espera_plano_segundos"] // 60))
        save_state(st)


EVENTS = {"start": ev_start, "prompt": ev_prompt, "pretool": ev_pretool, "posttool": ev_posttool,
          "notify": ev_notify, "stop": ev_stop, "stopfail": ev_stopfail}


def main():
    if len(sys.argv) < 2:
        return
    ev = sys.argv[1]
    if ev == "watch":
        watch(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
        return
    if ev == "test":
        st = load_state()
        play(sys.argv[2], st)
        save_state(st)
        return
    try:
        sys.stdin.reconfigure(encoding="utf-8")
        data = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        data = {}
    st = load_state()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        EVENTS[ev](data, st)
    except Exception as exc:  # nunca quebrar o Claude Code
        log(f"erro em {ev}: {exc!r}")
    save_state(st)


if __name__ == "__main__":
    main()

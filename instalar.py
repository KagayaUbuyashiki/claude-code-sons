"""Instalador dos sons do Claude Code (Windows).

    python instalar.py              -> instala / atualiza
    python instalar.py --remover    -> tira os hooks do settings.json (os arquivos ficam)

Copia a pasta sounds/ para %USERPROFILE%\\.claude\\sounds e adiciona os hooks em
%USERPROFILE%\\.claude\\settings.json (faz backup antes e preserva o resto da config).
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLAUDE = Path.home() / ".claude"
DEST = CLAUDE / "sounds"
SETTINGS = CLAUDE / "settings.json"
MARK = "sounds/sfx.py"

EVENTS = {
    "SessionStart": (None, "start"),
    "UserPromptSubmit": (None, "prompt"),
    "PreToolUse": ("ExitPlanMode|AskUserQuestion", "pretool"),
    "PostToolUse": ("ExitPlanMode|AskUserQuestion|TodoWrite", "posttool"),
    "Notification": (None, "notify"),
    "Stop": (None, "stop"),
    "StopFailure": (None, "stopfail"),
}


def load_settings():
    if not SETTINGS.exists():
        return {}
    text = SETTINGS.read_text(encoding="utf-8-sig")
    try:
        return json.loads(text) if text.strip() else {}
    except ValueError:
        sys.exit(f"ERRO: {SETTINGS} nao e um JSON valido. Corrija ou apague o arquivo e rode de novo.")


def strip_ours(hooks):
    """Remove hooks de instalacoes anteriores deste pacote."""
    for ev in list(hooks):
        groups = []
        for g in hooks[ev] or []:
            g = dict(g)
            g["hooks"] = [h for h in g.get("hooks", []) if MARK not in str(h.get("command", "")).replace("\\", "/")]
            if g["hooks"]:
                groups.append(g)
        if groups:
            hooks[ev] = groups
        else:
            del hooks[ev]


def save_settings(cfg):
    CLAUDE.mkdir(parents=True, exist_ok=True)
    if SETTINGS.exists():
        bak = SETTINGS.with_name(f"settings.json.bak-{time.strftime('%Y%m%d-%H%M%S')}")
        shutil.copy2(SETTINGS, bak)
        print(f"Backup da configuracao: {bak}")
    SETTINGS.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    if sys.platform != "win32":
        sys.exit("Este pacote e so para Windows (usa PowerShell para tocar os sons e mostrar notificacoes).")
    remover = "--remover" in sys.argv
    cfg = load_settings()
    hooks = cfg.setdefault("hooks", {})
    strip_ours(hooks)

    if remover:
        if not hooks:
            cfg.pop("hooks")
        save_settings(cfg)
        print("Hooks de som removidos. A pasta", DEST, "pode ser apagada a mao.")
        return

    # 1) arquivos
    DEST.mkdir(parents=True, exist_ok=True)
    src = HERE / "sounds"
    man = DEST / "manifest.json"
    if man.exists():
        shutil.copy2(man, DEST / "manifest.json.bak")
    for item in src.iterdir():
        target = DEST / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)
    (DEST / "queue").mkdir(exist_ok=True)
    print(f"Arquivos copiados para {DEST}")

    # 2) hooks
    # Aspas so quando o caminho tem espaco: assim o comando funciona tanto no
    # Git Bash quanto no PowerShell (que nao aceita "exe entre aspas" sem &).
    def q(p):
        p = Path(p).as_posix()
        return f'"{p}"' if " " in p else p

    py, sfx = q(sys.executable), q(DEST / "sfx.py")
    for ev, (matcher, arg) in EVENTS.items():
        group = {"hooks": [{"type": "command", "command": f"{py} {sfx} {arg}"}]}
        if matcher:
            group = {"matcher": matcher, **group}
        hooks.setdefault(ev, []).append(group)
    save_settings(cfg)
    print(f"Hooks adicionados em {SETTINGS}")

    # 3) teste
    print("Tocando um som de teste...")
    subprocess.run([sys.executable, str(DEST / "sfx.py"), "test", "inicio"])
    print("\nPronto! Feche e abra o Claude Code de novo para os sons comecarem a valer.")


if __name__ == "__main__":
    main()

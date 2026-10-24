#!/usr/bin/env python3
"""Второе мнение от GPT (OpenAI Responses API) — ревью реестров, скелетов глав, фактов.

Ключ — только из окружения OPENAI_API_KEY (~/.zshenv), в файлы и логи не пишется.

    zsh -c 'source ~/.zshenv; python3 tools/ask_gpt.py docs/countries/usa.md --prompt "Найди дыры"' > out.md
    ... | python3 tools/ask_gpt.py - --prompt "..."      текст из stdin
"""
import argparse, json, os, sys, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("file", help="файл с материалом или - для stdin")
ap.add_argument("--prompt", required=True, help="задание для GPT")
ap.add_argument("--model", default="gpt-5.5")
ap.add_argument("--effort", default="high", choices=["low", "medium", "high"])
a = ap.parse_args()

key = os.environ.get("OPENAI_API_KEY") or sys.exit("нет OPENAI_API_KEY (source ~/.zshenv)")
text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
body = {"model": a.model, "reasoning": {"effort": a.effort},
        "input": [{"role": "user", "content": f"{a.prompt}\n\n=====\n{text}"}]}
req = urllib.request.Request("https://api.openai.com/v1/responses", data=json.dumps(body).encode(),
                             headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
d = json.load(urllib.request.urlopen(req, timeout=900))
print("".join(c.get("text", "") for o in d.get("output", []) if o.get("type") == "message" for c in o["content"]))
u = d.get("usage", {})
print(f"\n<!-- {d.get('model')} · in {u.get('input_tokens')} / out {u.get('output_tokens')} токенов -->", file=sys.stderr)

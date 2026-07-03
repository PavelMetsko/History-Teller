import os, json, urllib.request, sys, time

KEY=os.environ["GEMINI_API_KEY"]
MODEL="gemini-2.5-flash"
URL=f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"
I18N="/Users/volhametsko/Developer/History Teller/Content/i18n"
LANGS={"en":"English","es":"Spanish","de":"German","fr":"French","it":"Italian",
       "pt":"Portuguese","pl":"Polish","nl":"Dutch"}

ru=json.load(open(f"{I18N}/ru.json",encoding="utf-8"))
keys=sorted(ru.keys())

def call(payload_text):
    body=json.dumps({"contents":[{"parts":[{"text":payload_text}]}],
                     "generationConfig":{"temperature":0.3,"responseMimeType":"application/json"}}).encode()
    for a in range(4):
        try:
            req=urllib.request.Request(URL,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=180) as r: data=json.loads(r.read())
            txt=data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(txt)
        except Exception as e:
            print(f"      retry {a+1}: {repr(e)[:120]}"); time.sleep(2)
    return None

def translate_lang(code,name):
    out={}
    B=45
    for i in range(0,len(keys),B):
        chunk={k:ru[k] for k in keys[i:i+B]}
        prompt=(f"You are a professional game localizer. Translate the VALUES of this JSON object from "
            f"Russian into {name}. Rules:\n"
            f"- Keep every KEY exactly unchanged.\n"
            f"- Preserve format specifiers like %d and %@ and newlines \\n exactly as in the source.\n"
            f"- For historical figures, dynasties and place names use the conventional {name} form "
            f"(e.g. Henry VIII, Julius Caesar, Cleopatra), not a transliteration of the Russian.\n"
            f"- Keep the tone: literary, evocative, concise. Fact-card texts stay factual.\n"
            f"- Return ONLY a valid JSON object mapping the same keys to translated strings.\n\n"
            f"{json.dumps(chunk,ensure_ascii=False)}")
        res=call(prompt)
        if res is None:
            print(f"    ✗ chunk {i//B} failed for {code}"); return None
        # нормализуем литеральный "\n" (модель иногда экранирует перенос как текст)
        out.update({k: (v.replace("\\n", "\n") if isinstance(v, str) else v) for k, v in res.items()})
        print(f"    {code}: {len(out)}/{len(keys)}")
    return out

targets=sys.argv[1:] if len(sys.argv)>1 else list(LANGS.keys())
for code in targets:
    name=LANGS[code]
    print(f"== {code} ({name}) ==")
    res=translate_lang(code,name)
    if res and len(res)>=len(keys)*0.95:
        # ensure all keys present (fallback to ru for any missing)
        for k in keys:
            if k not in res: res[k]=ru[k]
        json.dump(res,open(f"{I18N}/{code}.json","w",encoding="utf-8"),
                  ensure_ascii=False,indent=1,sort_keys=True)
        print(f"  ✓ {code}.json ({len(res)} keys)")
    else:
        print(f"  ✗ {code} incomplete ({len(res) if res else 0})")
print("done")

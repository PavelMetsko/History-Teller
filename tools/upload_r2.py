#!/usr/bin/env python3
"""Заливка облачного бандла контента в Cloudflare R2 (S3-совместимый API).

Ключи — из окружения (так их отдаёт CI) либо из `.r2.env` в корне репозитория (так удобнее
локально; файл в .gitignore, в гит не попадает):

    CLOUDFLARE_ACCOUNT_ID=...
    R2_ACCESS_KEY_ID=...
    R2_SECRET_ACCESS_KEY=...

Кеш-заголовки ставятся по смыслу раскладки: объекты в `f/` адресуются по sha256 и потому
иммутабельны — их можно кешировать вечно; `manifest.json` меняется при каждой публикации,
поэтому едет с `no-cache`. Из-за этого манифест всегда заливается последним: до тех пор,
пока он не обновлён, клиенты видят прежнюю версию, и полуразложенного состояния не бывает.

Существующие объекты не перезаливаются — сравниваем по имени (оно же хеш) и размеру.

Usage:
    python3 tools/upload_r2.py [--bucket history-teller-content] [--dir dist/content] [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


NEEDED = ("CLOUDFLARE_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY")


def load_env() -> dict:
    """Ключи из окружения (так их отдаёт CI) либо из `.r2.env` (так удобнее локально)."""
    env = {k: os.environ[k] for k in NEEDED if os.environ.get(k)}

    env_file = ROOT / ".r2.env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env.setdefault(k.strip(), v.strip())

    if missing := set(NEEDED) - set(env):
        sys.exit(f"нет ключей R2: {', '.join(sorted(missing))}. "
                 f"Задай их в окружении или в {env_file}")
    return env


def client(env: dict):
    import boto3
    from botocore.config import Config
    return boto3.client(
        "s3",
        endpoint_url=f"https://{env['CLOUDFLARE_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=env["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=env["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
        config=Config(retries={"max_attempts": 5, "mode": "standard"}),
    )


CONTENT_TYPES = {".json": "application/json", ".webp": "image/webp", ".m4a": "audio/mp4"}


def content_type(logical: str) -> str:
    """У объектов в f/ нет расширения — тип берём из логического пути в манифесте."""
    return CONTENT_TYPES.get(Path(logical).suffix, "application/octet-stream")


def existing_objects(s3, bucket: str) -> dict:
    found = {}
    token = None
    while True:
        kw = {"Bucket": bucket, "MaxKeys": 1000}
        if token:
            kw["ContinuationToken"] = token
        resp = s3.list_objects_v2(**kw)
        for o in resp.get("Contents", []):
            found[o["Key"]] = o["Size"]
        if not resp.get("IsTruncated"):
            return found
        token = resp["NextContinuationToken"]


def run(bucket: str, src: Path, dry: bool):
    import json
    env = load_env()
    s3 = client(env)

    manifest_path = src / "manifest.json"
    if not manifest_path.exists():
        sys.exit(f"нет {manifest_path} — сначала python3 tools/publish_content.py")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    # хеш → логический путь, чтобы объекту без расширения проставить осмысленный Content-Type
    kind = {ref["h"]: logical for logical, ref in manifest["files"].items()}

    try:
        have = existing_objects(s3, bucket)
    except s3.exceptions.NoSuchBucket:
        sys.exit(f"бакета {bucket} нет — создай его в R2 или проверь имя")
    print(f"в бакете уже {len(have)} объектов")

    todo = []
    for p in sorted((src / "f").iterdir()):
        key = f"f/{p.name}"
        if have.get(key) == p.stat().st_size:
            continue
        todo.append((p, key))

    total = sum(p.stat().st_size for p, _ in todo)
    print(f"к заливке: {len(todo)} объектов, {total/1e6:.1f} МБ "
          f"(+ manifest.json v{manifest['version']})")
    if dry:
        print("dry-run — ничего не отправлено")
        return

    done = 0

    def put(item):
        nonlocal done
        p, key = item
        s3.put_object(
            Bucket=bucket, Key=key, Body=p.read_bytes(),
            ContentType=content_type(kind.get(p.name, "")),
            CacheControl="public, max-age=31536000, immutable",
        )
        done += 1
        if done % 50 == 0 or done == len(todo):
            print(f"  {done}/{len(todo)}")

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(put, todo))

    # Манифест — последним: он и есть переключатель версии.
    s3.put_object(
        Bucket=bucket, Key="manifest.json", Body=manifest_path.read_bytes(),
        ContentType="application/json", CacheControl="no-cache",
    )
    print(f"manifest.json v{manifest['version']} опубликован — версия переключена")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", default="history-teller-content")
    ap.add_argument("--dir", default="dist/content")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    d = Path(a.dir) if Path(a.dir).is_absolute() else ROOT / a.dir
    run(a.bucket, d, a.dry_run)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 HaGeZi Multi Adblock 列表下载并生成对应的规则文件：
  rules/<name>.json   - sing-box rule-set 源文件
  rules/<name>.list   - Clash/Surge 风格的 DOMAIN-SUFFIX 列表

源文件格式示例：
  ||ads.example.com^
  ! 注释行

用法：
  python3 scripts/build.py
"""

import json
import os
import re
import sys
import urllib.request

# 需要处理的规则源列表：每一项包含源地址和输出文件名（不含扩展名）
SOURCES = [
    {
        "name": "pro.plus",
        "url": "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/pro.plus.txt",
    },
    {
        "name": "pro",
        "url": "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/pro.txt",
    },
]

RULES_DIR = "rules"

# 匹配形如 ||domain.tld^ 的 Adblock 规则行（允许行尾附加 $options，一并忽略）
RULE_PATTERN = re.compile(r"^\|\|([a-zA-Z0-9](?:[a-zA-Z0-9\-_.]*[a-zA-Z0-9])?)\^")


def fetch_source(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (build-script)"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def extract_domains(text: str) -> list:
    domains = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("!") or line.startswith("["):
            continue
        m = RULE_PATTERN.match(line)
        if m:
            domain = m.group(1).lower()
            domains.add(domain)
    return sorted(domains)


def write_json(domains: list, path: str) -> None:
    data = {
        "version": 5,
        "rules": [
            {
                "domain_suffix": domains,
            }
        ],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def write_list(domains: list, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for d in domains:
            f.write(f"DOMAIN-SUFFIX,{d}\n")


def build_one(name: str, url: str) -> bool:
    json_output = os.path.join(RULES_DIR, f"{name}.json")
    list_output = os.path.join(RULES_DIR, f"{name}.list")

    print(f"[{name}] 下载源文件: {url}")
    text = fetch_source(url)

    domains = extract_domains(text)
    if not domains:
        print(f"[{name}] 错误：未提取到任何域名，跳过生成以避免空文件。", file=sys.stderr)
        return False

    print(f"[{name}] 提取到 {len(domains)} 个去重后的域名")

    os.makedirs(os.path.dirname(json_output), exist_ok=True)

    write_json(domains, json_output)
    print(f"[{name}] 已生成 {json_output}")

    write_list(domains, list_output)
    print(f"[{name}] 已生成 {list_output}")

    return True


def main() -> int:
    ok = True
    for source in SOURCES:
        success = build_one(source["name"], source["url"])
        ok = ok and success

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

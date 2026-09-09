#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 HaGeZi Multi PRO++ Adblock 列表下载并生成：
  rules/pro.plus.json   - sing-box rule-set 源文件
  rules/pro.plus.list   - Clash/Surge 风格的 DOMAIN-SUFFIX 列表

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

SOURCE_URL = "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/pro.plus.txt"
JSON_OUTPUT = "rules/pro.plus.json"
LIST_OUTPUT = "rules/pro.plus.list"

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


def main() -> int:
    print(f"下载源文件: {SOURCE_URL}")
    text = fetch_source(SOURCE_URL)

    domains = extract_domains(text)
    if not domains:
        print("错误：未提取到任何域名，终止执行以避免生成空文件。", file=sys.stderr)
        return 1

    print(f"提取到 {len(domains)} 个去重后的域名")

    os.makedirs(os.path.dirname(JSON_OUTPUT), exist_ok=True)

    write_json(domains, JSON_OUTPUT)
    print(f"已生成 {JSON_OUTPUT}")

    write_list(domains, LIST_OUTPUT)
    print(f"已生成 {LIST_OUTPUT}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

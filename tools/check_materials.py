#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交付前的机械检查：motivation letter / research statement（.md）。

用法（在 jobs 文件夹下）：
  python3 tools/check_materials.py letter    applications/<短名>/motivation_letter_<短名>.md
  python3 tools/check_materials.py statement applications/<短名>/research_statement_<短名>.md
  加 --config <路径> 换配置文件；默认读本脚本旁边的 materials_config.json。

个人内容都在 materials_config.json 里（从 materials_config.example.json 复制一份改）：
  name                  署名，也要出现在联系行里
  email                 联系行必须用的邮箱
  contact_must_include  联系行还必须出现的片段（电话国家码、主页域名等）
  sign_off              落款，默认 "Kind regards,"
  letter / statement    词数的目标区和容忍区；letter 另有正文段数范围
  banned_phrases        不许出现的短语（自己写作里的套话、AI 腔，发现新的就加）
  identity_red_lines    不许出现的身份说法（会把自己的身份说错的那些话）
  non_first_author_works 不是自己主导的论文或项目的名字

文件格式：
  第 1 行  **Motivation Letter** 或 **Research Statement**
  第 3 行  联系行：姓名 | 单位 | 邮箱 | 电话 | 主页
  letter 接着是称呼（Dear …,）、正文段落、落款加署名；statement 没有称呼和落款。

检查项（违反即列出，退出码 2）：
- 文件头、联系行、称呼、落款符合上面的格式。
- 正文里没有 markdown 标题、没有加粗（首行除外）、没有 HTML 注释、没有使用说明头注。
- 破折号：不出现 em dash；en dash 只允许在日期和数字范围里（如 2019–2022）。
- 禁用短语、身份红线。
只提醒、不判错的：
- 词数：一律报"超/少多少词"和逐段词数；超出容忍区给 warning。
- 数字清单：列出正文里所有百分比和大数字，供对照 facts.md。
- 署名：non_first_author_works 里的名字出现在 "I built / I designed …" 这类句子里时提醒核对 I/we。
"""
import argparse, io, json, os, re, sys

DEFAULTS = {
    "name": "",
    "email": "",
    "contact_must_include": [],
    "sign_off": "Kind regards,",
    "letter": {"target": [330, 370], "tolerance": [300, 390], "paragraphs": [4, 6]},
    "statement": {"target": [550, 650], "tolerance": [500, 700]},
    "banned_phrases": [],
    "identity_red_lines": [],
    "non_first_author_works": [],
}
I_VERBS = re.compile(r"\bI (built|designed|developed|created|proposed|introduced|released|constructed|implemented)\b")
MONTHS = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
RANGE_OK = re.compile(r"(\d{4}|\d+%?|" + MONTHS + r"( \d{4})?)\s?–\s?(\d{4}|\d+%?|" + MONTHS + r"( \d{4})?)")


def load_config(path):
    if not os.path.exists(path):
        sys.exit("找不到配置文件 %s：把 materials_config.example.json 复制成 materials_config.json，填上自己的信息" % path)
    user = json.load(io.open(path, encoding="utf-8"))
    cfg = dict(DEFAULTS)
    for k, v in user.items():
        if k.startswith("_"):
            continue
        if k not in DEFAULTS:
            sys.exit("配置里有未知的键：%s（可用：%s）" % (k, "、".join(DEFAULTS)))
        if isinstance(DEFAULTS[k], dict):
            merged = dict(DEFAULTS[k])
            merged.update(v)
            cfg[k] = merged
        else:
            cfg[k] = v
    if not cfg["name"] or not cfg["email"]:
        sys.exit("配置里 name 和 email 必填")
    return cfg


def words(s):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-%.]*", s))


def report_words(name, paras, n, target, tol, warnings):
    lo, hi = target
    if n > hi:
        verdict = "超 %d 词" % (n - hi)
    elif n < lo:
        verdict = "少 %d 词" % (lo - n)
    else:
        verdict = "在目标区内"
    per = "；".join("第%d段 %d" % (i + 1, words(p)) for i, p in enumerate(paras))
    print("%s %d 词（目标 %d–%d，%s）｜逐段：%s" % (name, n, lo, hi, verdict, per))
    if not (tol[0] <= n <= tol[1]):
        warnings.append("%s %d 词，%s，超出容忍区 %d–%d" % (name, n, verdict, tol[0], tol[1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["letter", "statement"])
    ap.add_argument("path")
    ap.add_argument("--config", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "materials_config.json"))
    a = ap.parse_args()
    cfg = load_config(a.config)
    name, sign_off = cfg["name"], cfg["sign_off"]

    text = io.open(a.path, encoding="utf-8").read().replace("\r\n", "\n")
    lines = text.split("\n")
    problems, warnings = [], []

    title = "**Motivation Letter**" if a.kind == "letter" else "**Research Statement**"
    if not lines or lines[0].strip() != title:
        problems.append("首行应为 %s，实际：%r" % (title, lines[0][:60] if lines else ""))
    contact = lines[2].strip() if len(lines) > 2 else ""
    for need in [name, cfg["email"]] + list(cfg["contact_must_include"]):
        if need not in contact:
            problems.append("联系行缺 %s：%r" % (need, contact[:80]))

    body = "\n".join(lines[1:])
    if re.search(r"^#{1,6} ", body, re.M):
        problems.append("正文含 markdown 标题")
    if "**" in body:
        problems.append("正文含加粗（只允许首行标题加粗）")
    if "<!--" in text:
        problems.append("含 HTML 注释")
    if re.search(r"^(Note|Usage|说明|使用)", body, re.M | re.I):
        problems.append("疑似含使用说明头注")

    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    # 落款和署名之间空不空行都认：空了一行就并回一段
    if len(paras) >= 2 and paras[-1] == name and paras[-2] == sign_off:
        paras[-2:] = [sign_off + "\n" + name]
    if a.kind == "letter":
        if len(paras) < 4 or not paras[2].startswith("Dear "):
            problems.append("第三段应为称呼 Dear …，实际：%r" % (paras[2][:40] if len(paras) > 2 else ""))
        if not paras[-1].startswith(sign_off) or name not in paras[-1]:
            problems.append("末尾应为 %r 加署名 %r" % (sign_off, name))
        core = paras[3:-1]
        n = sum(words(p) for p in core)
        report_words("letter 正文", core, n, cfg["letter"]["target"], cfg["letter"]["tolerance"], warnings)
        plo, phi = cfg["letter"]["paragraphs"]
        if not (plo <= len(core) <= phi):
            warnings.append("letter 正文 %d 段（设定 %d–%d 段）" % (len(core), plo, phi))
    else:
        if any(p.startswith("Dear ") for p in paras):
            problems.append("statement 不应有称呼")
        if any(p.startswith(sign_off) for p in paras):
            problems.append("statement 不应有落款")
        core = paras[2:]
        n = sum(words(p) for p in core)
        report_words("statement 正文", core, n, cfg["statement"]["target"], cfg["statement"]["tolerance"], warnings)

    if "—" in body:
        problems.append("含 em dash（—），不允许")
    for m in re.finditer(r".{0,25}–.{0,25}", body):
        seg = m.group(0)
        if not RANGE_OK.search(seg):
            problems.append("en dash 用在非范围处：…%s…" % seg.strip())
    low = body.lower()
    for b in cfg["banned_phrases"]:
        if b.lower() in low:
            problems.append("禁用短语：%s" % b)
    for b in cfg["identity_red_lines"]:
        if b.lower() in low:
            problems.append("身份红线：%s" % b)
    others = [k.lower() for k in cfg["non_first_author_works"]]
    for p in paras:
        for sent in re.split(r"(?<=[.!?])\s+", p):
            if I_VERBS.search(sent) and any(k in sent.lower() for k in others):
                warnings.append("非一作的论文或项目出现在 I 句里，核对署名：…%s…" % sent.strip()[:90])
    nums = sorted(set(re.findall(r"\d[\d,.]*\s?%|\b\d{1,3}(?:,\d{3})+\b|\b\d+(?:\.\d+)?\s?(?:million|M|k)\b|\b\d+\.\d+\b", body)))
    print("数字清单（对照 facts.md）：", ", ".join(nums) if nums else "无")
    for w in warnings:
        print("warning:", w)
    if problems:
        print("未通过：")
        print("\n".join(" - " + p for p in problems))
        sys.exit(2)
    print("通过：%s" % a.path)


if __name__ == "__main__":
    main()

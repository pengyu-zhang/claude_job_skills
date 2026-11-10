#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定向 CV：对 LaTeX 母版做"只动文字、不动格式"的修改，并核验。
放在 jobs 文件夹的 tools/ 下，在 jobs 文件夹里跑，读的就是当前母版。

母版要有这些结构（templates/cv_master.tex 是一份能直接用的样例）：
- \\section{About Me}，下面第一段是自我介绍，段后空一行。
- 一行以 "Open to " 开头、\\par 结尾的求职意向。
- 一行连续的 \\pill{...}，\\par 结尾。
- \\section{Experience}，里面的项目用 \\project{名字}{副标题}{出处}；第一组项目之后用一行
  \\par\\Needspace{8\\baselineskip} 隔开后面的组。只有第一组能重排。
- \\section{Skills} 里有一行 \\entry{Methods}{...}。
- Education 里有 Thesis: \\textit{...}（没有论文的话别用 fields.thesis）。
- \\section{Publications} 里用 publist 环境，每条以两个空格加 \\item 开头；导言区定义 \\pubtotal。

用法：
  python3 tools/tailor_cv.py --src cv_master.tex --show
      只读母版：打印五个锚点的当前文本、第一组的 \\project 键、发表条目数、母版指纹。写 edits.json 之前先看这个。
  python3 tools/tailor_cv.py --src cv_master.tex --out applications/<短名>/CV_<短名>.tex --edits ~/work/edits.json

edits.json（所有字段可选）：
{
  "tailored_for": "<单位> - <岗位>",        # 在母版首行后插一行 "% Tailored: ... | master <sha1 前 8 位> <mtime>"
  "fields": {                                # 按语义键给新值；旧文本由脚本从母版按结构定位，不用写 old
    "about":        "…About Me 段新文…",      # \\section{About Me} 后第一段（到空行为止）
    "open_to":      "Open to postdoc and researcher positions.",   # 求职行（脚本自动补 \\par）
    "pills":        ["Time series forecasting", "…", "…", "…", "…"],   # 个数必须和母版一致，脚本拼 \\pill{}
    "skills_mldl":  "Time series forecasting, …, anomaly detection.",   # Skills 节 \\entry{Methods}{…} 的整行内容
    "thesis":       "…"                        # Education 里 Thesis: \\textit{…} 的内容（一般不动）
  },
  "project_order": ["GridCast", "DriftWatch", "RiverBench"],
                                             # Experience 节第一组 \\project 块的新顺序（后面各组位置固定）；键 = \\project 第一个花括号原文（JSON 里 & 写成 \\\\&）
  "experience_order": ["2022 -- present", "2019 -- 2022"],   # Experience 节 \\entry 的新顺序（很少用）
  "selected_publications": ["GridCast", "DriftWatch", …],   # 工业轨：只保留含这些关键词的 \\item，节名改 Selected Publications
  "replace": [ {"label": "…", "old": "…母版原文…", "new": "…"} ]   # 临时用途的精确替换：恰好匹配 1 处，否则退出
}

脚本强制：
- \\begin{document} 之前的导言区一个字节都不变（只放行 tailored_for 插入的那一行注释）。
- 每个锚点在母版里恰好匹配 1 处，否则打印锚点名和母版指纹后退出；不沉默跳过。
- project_order：键集合必须与母版一致；重排前后总字节数不变；导言区逐字节不变。
- 不新增母版没有的 \\project / \\entry。
- 结束时打印母版指纹、改了哪些锚点、\\project 顺序、发表条目数、字节数，供 notes.md 引用。
"""
import argparse, datetime, hashlib, io, json, os, re, sys


def die(msg):
    sys.exit("tailor_cv: " + msg)


def fingerprint(path, text):
    sha = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M")
    return "sha1 %s | mtime %s" % (sha, mtime)


# ---------- 锚点定位（每个返回 (start, end) 或报错） ----------

def find_once(src, pattern, name, flags=re.M):
    ms = list(re.finditer(pattern, src, flags))
    if len(ms) != 1:
        die("锚点 [%s] 在母版里匹配 %d 处（必须恰好 1 处）。母版可能重写过，先跑 --show 看当前结构。" % (name, len(ms)))
    return ms[0]


ANCHORS = {
    # About Me：\section{About Me}\n 之后到第一个空行
    "about": (r"(?<=\\section\{About Me\}\n)(.+?)(?=\n\n)", re.S),
    # 求职行：以 Open to 开头、\par 结尾的一整行
    "open_to": (r"^Open to .*?(?=\\par$)", re.M),
    # pills：一整行连续的 \pill{...}，\par 结尾
    "pills": (r"^(?:\\pill\{[^}]*\})+(?=\\par$)", re.M),
    # Skills 的 Methods 行：花括号里的整行内容
    "skills_mldl": (r"(?<=\\entry\{Methods\}\{)(.*?)(?=\}$)", re.M),
    # Thesis 行
    "thesis": (r"(?<=Thesis: \\textit\{)[^}]*(?=\})", re.M),
}


def locate(src, key):
    pat, flags = ANCHORS[key]
    m = find_once(src, pat, key, flags)
    if key == "skills_mldl":
        return m.start(1), m.end(1)
    return m.start(), m.end()


def project_region(src):
    # 项目在 Experience 节里按角色分组；只在第一组内重排（到 \par\Needspace{8\baselineskip} 这一行为止）
    s0 = find_once(src, r"^\\section\{Experience\}$", "section Experience").start()
    s = src.index("\\project{", s0)
    e = src.index("\\par\\Needspace{8\\baselineskip}", s)
    return s, e


def split_projects(region):
    idxs = [m.start() for m in re.finditer(r"^\\project\{", region, re.M)]
    if not idxs:
        die("Experience 节里没找到 \\project 块")
    head = region[:idxs[0]]
    blocks, keys = {}, []
    for i, st in enumerate(idxs):
        en = idxs[i + 1] if i + 1 < len(idxs) else len(region)
        piece = region[st:en]
        key = re.match(r"\\project\{([^}]*)\}", piece).group(1)
        if key in blocks:
            die("\\project 键重复：%s" % key)
        blocks[key] = piece
        keys.append(key)
    return head, blocks, keys


def entry_region(src, section):
    s = find_once(src, r"^\\section\{%s\}$" % re.escape(section), "section " + section).start()
    e = src.index("\\section{", s + 10)
    return s, e


def split_entries(region):
    idxs = [m.start() for m in re.finditer(r"\\entry\{", region)]
    if not idxs:
        return region, {}, []
    head, chunks, keys = region[:idxs[0]], {}, []
    for i, st in enumerate(idxs):
        en = idxs[i + 1] if i + 1 < len(idxs) else len(region)
        piece = region[st:en]
        key = re.match(r"\\entry\{([^}]*)\}", piece).group(1)
        chunks[key] = piece
        keys.append(key)
    return head, chunks, keys


def pub_count(src):
    m = re.search(r"\\begin\{publist\}(.*?)\\end\{publist\}", src, re.S)
    return len(re.findall(r"^  \\item ", m.group(1), re.M)) if m else 0


# ---------- --show ----------

def show(path, src):
    print("母版指纹：", fingerprint(path, src), "| 首行：", src.split("\n", 1)[0].strip())
    print("\\pubtotal：", (re.search(r"\\newcommand\{\\pubtotal\}\{(\d+)\}", src) or [None, "?"])[1],
          "｜ 发表条目数：", pub_count(src))
    print()
    for key in ANCHORS:
        try:
            s, e = locate(src, key)
            val = src[s:e]
            if key == "pills":
                val = " | ".join(re.findall(r"\\pill\{([^}]*)\}", val))
            print("[%s]\n%s\n" % (key, val))
        except SystemExit as ex:
            print("[%s] 定位失败：%s\n" % (key, ex))
    s, e = project_region(src)
    _, _, keys = split_projects(src[s:e])
    print("\\project 键（母版顺序）：")
    for k in keys:
        print("   -", k)
    print("\nJSON 里的 project_order 写法：", json.dumps(keys, ensure_ascii=False))
    s, e = entry_region(src, "Experience")
    _, _, ekeys = split_entries(src[s:e])
    print("\nExperience \\entry 键：", ekeys)


# ---------- 主流程 ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out")
    ap.add_argument("--edits")
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()

    src = io.open(a.src, encoding="utf-8").read()
    if "\r\n" in src:
        die("母版含 CRLF 换行，先转成 LF 再跑")
    if a.show:
        show(a.src, src)
        return
    if not (a.out and a.edits):
        die("需要 --out 和 --edits（或用 --show 只看母版）")

    ed = json.load(io.open(a.edits, encoding="utf-8"))
    orig = src
    fp = fingerprint(a.src, orig)
    log = []

    def splice(s, e, new, label):
        nonlocal src
        src = src[:s] + new + src[e:]
        log.append(label)

    # 1. 语义字段
    fields = ed.get("fields", {}) or {}
    unknown = set(fields) - set(ANCHORS)
    if unknown:
        die("fields 里有未知键：%s（可用：%s）" % (sorted(unknown), list(ANCHORS)))
    for key in ANCHORS:  # 固定顺序
        if key not in fields:
            continue
        val = fields[key]
        s, e = locate(src, key)
        old = src[s:e]
        if key == "pills":
            if not isinstance(val, list) or not all(isinstance(x, str) for x in val):
                die("fields.pills 必须是字符串列表")
            n_old = len(re.findall(r"\\pill\{", old))
            if len(val) != n_old:
                die("fields.pills 给了 %d 个，母版是 %d 个（个数要和母版一致）" % (len(val), n_old))
            new = "".join("\\pill{%s}" % x for x in val)
        else:
            if not isinstance(val, str):
                die("fields.%s 必须是字符串" % key)
            new = val.strip("\n")
        splice(s, e, new, "fields.%s: %d → %d 字符" % (key, len(old), len(new)))

    # 2. 精确替换（临时用途）
    for item in ed.get("replace", []) or []:
        old, new = item["old"], item["new"]
        n = src.count(old)
        label = item.get("label", old[:30])
        if n != 1:
            die("replace [%s]：匹配 %d 处（必须恰好 1 处）。old 要从当前母版逐字复制，别拿上一岗的 edits.json 当起点。\n母版指纹：%s" % (label, n, fp))
        src = src.replace(old, new)
        log.append("replace: " + label)

    # 3. 第一组项目重排
    if ed.get("project_order"):
        want = ed["project_order"]
        s, e = project_region(src)
        region = src[s:e]
        head, blocks, keys = split_projects(region)
        if sorted(want) != sorted(keys):
            die("project_order 与母版 \\project 键集合不一致：\n  母版=%s\n  给定=%s" % (keys, want))
        new_region = head + "".join(blocks[k] for k in want)
        if len(new_region.encode("utf-8")) != len(region.encode("utf-8")):
            die("project_order：重排前后字节数不一致，拒绝输出")
        src = src[:s] + new_region + src[e:]
        log.append("project_order: %s -> %s" % (keys, want))

    # 4. Experience 重排
    if ed.get("experience_order"):
        want = ed["experience_order"]
        s, e = entry_region(src, "Experience")
        head, chunks, keys = split_entries(src[s:e])
        if sorted(want) != sorted(keys):
            die("experience_order 与母版 \\entry 键不一致：\n  母版=%s\n  给定=%s" % (keys, want))
        src = src[:s] + head + "".join(chunks[k] for k in want) + src[e:]
        log.append("experience_order: %s -> %s" % (keys, want))

    # 5. 工业轨：压缩发表列表
    if ed.get("selected_publications"):
        keep = ed["selected_publications"]
        s = find_once(src, r"^\\section\{Publications\}$", "section Publications").start()
        e = src.find("\\section{", s + 10)
        e = len(src) if e == -1 else e
        block = src[s:e]
        # 先把 \end{publist} 及其后的内容切出来，剩下的按 \item 切
        m = re.search(r"^\\end\{publist\}", block, re.M)
        if not m:
            die("Publications 里找不到 \\end{publist}")
        body, tail = block[:m.start()], block[m.start():]
        items = re.split(r"(?=^  \\item )", body, flags=re.M)
        head, rest = items[0], items[1:]
        kept = [it for it in rest if any(k.lower() in it.lower() for k in keep)]
        if len(kept) != len(keep):
            die("selected_publications 匹配到 %d 条，期望 %d 条：%s" % (len(kept), len(keep), keep))
        head = head.replace("\\section{Publications}", "\\section{Selected Publications}")
        # 倒序编号由 \pubtotal 算，条目少了要在正文里改（导言区不能动）
        head = head.replace("\\begin{publist}", "\\renewcommand{\\pubtotal}{%d}\n\\begin{publist}" % len(kept), 1)
        block = head + "".join(kept) + tail
        src = src[:s] + block + src[e:]
        log.append("selected_publications: %d kept" % len(kept))

    # 6. 头注
    if ed.get("tailored_for"):
        first_nl = src.index("\n")
        note = "%% Tailored: %s | master %s" % (ed["tailored_for"], fp)
        src = src[:first_nl + 1] + note + "\n" + src[first_nl + 1:]
        log.append("tailored_for")

    # 7. 导言区守卫
    cut_o, cut_n = orig.index("\\begin{document}"), src.index("\\begin{document}")
    pre_n = re.sub(r"^% Tailored: .*\n", "", src[:cut_n], count=1, flags=re.M)
    if orig[:cut_o] != pre_n:
        die("导言区被改动，拒绝输出。只能改 \\begin{document} 之后的文字。")

    # 8. 结构守卫：不新增 \project / \entry
    for tag in ("\\project{", "\\entry{"):
        if src.count(tag) > orig.count(tag):
            die("输出里 %s 比母版多，拒绝输出（不新增母版没有的条目）" % tag)

    io.open(a.out, "w", encoding="utf-8", newline="\n").write(src)

    # 9. 核验输出
    print("母版指纹：", fp)
    print("\n".join(log) or "（无改动）")
    s, e = project_region(src)
    _, _, keys = split_projects(src[s:e])
    print("\n\\project 顺序：")
    for k in keys:
        print("   -", k)
    print("\n发表条目数：", pub_count(src), "（母版", pub_count(orig), "）")
    print("字节：", len(src.encode("utf-8")), "（母版", len(orig.encode("utf-8")), "）")
    print("输出：", a.out)


if __name__ == "__main__":
    main()

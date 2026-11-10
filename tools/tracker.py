#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
job_tracker.xlsx 的唯一写入工具。放在 jobs 文件夹的 tools/ 下，在自己电脑上跑。
收什么岗、怎么打分写在 profile/job_profile.md；各列怎么填见下面「各列怎么填」；本脚本负责格式、校验、排序、写入。

工作簿（按此顺序）：学术岗位 / 工业岗位（24 列，完全一致）/ 国内岗位（24 列，国内线自己的列）/
已排除（欧洲线与国内线共用，见过但按收录范围不入表的岗）/ 公司 / 国内公司（都是 公司 | 网址 | 备注）/
说明（上次运行、关键词位置、投递状态、近期截止、已排除行数）。

国内岗位 的列：岗位ID 岗位名称 单位 单位性质 城市 招聘类型 类型 优先级 状态 核验 最后核验日期 截止日期 投递日期
  薪资 编制与合同 主要要求 硬门槛 所需材料 联系人 链接 官网链接 来源渠道 发现日期 备注。
  add/update/remove 里 "sheet": "国内岗位" 即可，其余写法和前两张表一样；没有 级别、工作模式、地点 这几列。
  岗位ID 派生：zhipin.com/job_detail/<id> → boss:<id>；liepin.com/job/<id> → liepin:<id>；
  nowcoder.com/jobs/detail/<id> → nowcoder:<id>；腾讯/字节/阿里/美团/百度/京东/快手/小红书/网易/蚂蚁/拼多多/滴滴/B站/讯飞官网岗位页 → tencent:/bytedance:/alibaba:/meituan:/baidu:/jd:/kuaishou:/xhs:/netease:/ant:/pdd:/didi:/bili:/iflytek:；都派生不出时 <单位短名>-<岗位短名>（中文照留）。
  国内公司表的改动写在 changes.json 的 "cn_companies"（结构同 "companies"）。

各列怎么填（词表见下面的常量，写错脚本会拒收）：
- 状态：未投 / 已投（投出后还没回音）/ 面试（收到邀请及之后的流程）/ 被拒（明确的拒信）/ Offer / 关闭（岗位下线，或截止已过还没投；只从 未投 转来）。
  格里不写日期：投递日写 投递日期 列，拒信日、轮次、撤回这些时间线写备注。已投、面试、Offer 永远算活岗。
- 核验：官网JD = 读过雇主官网或其招聘系统的岗位页全文（学术岗的 AcademicTransfer 岗位页算官网页）；聚合站 = 只读过 LinkedIn、Indeed 这类站的帖；
  未核验 = 读不到正文，备注写清为什么读不到。入表前要读过 JD 正文。聚合站显示在招、招聘系统接口里有，都不等于在招，死活看岗位页本身。
- 优先级：只表示方向匹配。决定不投的岗不降档，在备注里以「决定不投：」开头写理由，挑岗时按这四个字筛掉。
- 链接 = 发现页（来源渠道那个站的岗位页）；官网链接 = 雇主官网或其招聘系统的岗位页；直接从招聘系统扫到的两列相同；拿不到留空。
  核验=官网JD 的行，官网链接不该空。
- 地点：本国的岗写城市；远程岗写雇主或团队所在地加括号，如 Berlin（远程）；没有所在地的写 Remote（EU）。地点以 JD 正文为准，不信列表页。
- 工作模式、级别：JD 没写就是 未标；学术岗位表的级别一律 未标。
- 类型：学术表里 RSE 指大学的技术岗（research software engineer、scientific programmer、data steward）；
  工业表里 MLS 含 ML/Applied/Research Scientist，MLE 含算法工程、AI SWE，DE 含 MLOps、Analytics Engineer，RE 是 Research Engineer。
- 所需材料：看得到表单要求才填，看不到留空。
- 签证/居留：只抄 JD 里写到的签证、担保、居住要求，没写留空。这一列不参与排除，也不参与打分。
- 来源渠道：按 链接 列所在的站填；同一岗别的站也有的，站名写备注。
- 日期列只写 YYYY-MM-DD；没有截止或滚动招聘就留空，不用横线占位。页面互相矛盾时取早的那个，并在备注标 ⚠️。
- 备注：复述和打分（格式在 job_profile.md）、核验的依据、轮次和时间线、材料文件夹名、这个岗自己的待办。有词表、要筛要排的信息进对应的列。
- 不删行：入了表的岗被拒、过期、放弃都只改状态。跨渠道重复的并成一行，被并的那行才删。高匹配但已关闭的岗，备注写「Lead only：恢复在招后再投」。
- 已排除表：见过、按收录范围不收的岗都写进来，排除理由必填（凭标题判的写标题依据，读过 JD 判的抄 JD 原话）。已排除的岗再出现就跳过。
  入表以后才发现不该收的，在岗位表改 关闭，不挪过来。
- 公司表、国内公司表：网址存打开就能看到在招列表的那一页；备注只在光有网址不够时写一句怎么读，不写日期和状态。

用法（在 jobs 文件夹下）：
  python3 tools/tracker.py info      job_tracker.xlsx --today YYYY-MM-DD   # 状态、已知岗位ID、stale、missing_official
  python3 tools/tracker.py companies job_tracker.xlsx [--cn]               # 列出公司表 / --cn 国内公司表（TSV：公司 网址 备注）
  python3 tools/tracker.py apply     job_tracker.xlsx --changes changes.json --today YYYY-MM-DD
  python3 tools/tracker.py check     job_tracker.xlsx [--today YYYY-MM-DD]
        # apply、check 的旧警告默认按类别汇总（每类前 3 条），加 --all-warnings 逐条打印
  python3 tools/tracker.py stats     job_tracker.xlsx                      # 渠道/优先级/类型/核验/级别/工作模式 × 状态
  python3 tools/tracker.py export    job_tracker.xlsx --out rows.json         # 两个岗位表 + 已排除
  python3 tools/tracker.py match     job_tracker.xlsx --jobs jobs.json --out match.json
        # 判重：jobs.json 是 [{"title","company","ids":[jk/AT号/LinkedIn号...],"link"?,...}]，
        # 每条标 在表 / 已排除 / 新（按 id 搜整行，再按 岗位名+单位 模糊比对），新的必须本轮入表或排除
  python3 tools/tracker.py init      job_tracker.xlsx                      # 建空表（仅当文件不存在）

changes.json（每个键都可省）：
{
 "run": {"mode": "scan", "last_run": "2026-01-15（第三轮）", "second_tier": "关键词搜到第 12 个（下轮从第 13 个继续）"},
 "add":    [{"sheet": "工业岗位", "row": {"岗位名称": "...", "单位": "...", "优先级": "High", "状态": "未投", "类型": "MLE",
             "核验": "官网JD", "链接": "https://...", "官网链接": "https://...", "来源渠道": "LinkedIn", "备注": "复述：...｜任务3 证据2＝5 → High"},
             "allow_same_name": false}],
 "update": [{"sheet": "工业岗位", "id": "gh:123", "set": {"状态": "已投", "投递日期": "2026-01-15"}, "append_note": "...", "verified": true}],
 "remove": [{"sheet": "学术岗位", "id": "li:123"}],
 "exclude": [{"岗位名称": "PhD Position X", "单位": "Example University", "地点": "Utrecht", "排除类别": "PhD",
              "排除理由": "PhD 岗，标题写明", "来源渠道": "Indeed", "链接": "https://nl.indeed.com/viewjob?jk=..."}],
 "companies": {"add": [{"公司": "Example Co", "网址": "https://job-boards.greenhouse.io/exampleco", "备注": ""}],
               "update": [{"公司": "Example Co", "set": {"网址": "https://..."}}],
               "remove": ["某公司"]}
}
- run.mode：找岗流水线写 "scan"（才会改 上次运行 与 关键词位置）；对话里改状态写 "update"。
- add：岗位ID 不写（脚本从链接派生：at: / indeed: / li: / gh: / lever: / icims: / wd: / ashby: / 单位-岗位短名）；
  发现日期缺省 --today；核验缺省 未核验，非 未核验 时最后核验日期缺省今天；级别、工作模式缺省 未标。
  任一链接已在表 → 报错改用 update；同名同单位已在表 → 报错，确认不是同一岗再加 allow_same_name。
- update：按 id 匹配；set 可改除岗位ID 外任何列；换链接时旧值自动进备注；set 备注时「决定不投：」段自动保留；
  append_note 用「｜」追加；verified:true 把最后核验日期写成今天；状态改 已投 必须同时 set 投递日期。
- remove：只用于跨渠道重复合并。
- exclude_update：[{"id": "<已排除表岗位ID>", "set": {"排除类别": "...", "排除理由": "..."}}] 改已排除表已有行（规则变更后重判用）。
- exclude：见过、按 job_profile.md 的收录范围不收的岗，写进「已排除」表。排除类别只用词表（EXCL_CATS）；
  排除理由必填，读过 JD 才判的写清依据；链接可空（Indeed 赞助位 pagead 链接不稳定也太长，不填）。
  已在岗位表的岗不许排除（在岗位表里改状态）；已在已排除表的跳过不报错。
  add 一个已排除表里的岗（同链接或同名同单位）时，自动从已排除表移回，日志里写明。
- 每次 apply：未投且截止已过 → 自动转 关闭；两个岗位 sheet 重建并整表重排（活岗在上：有截止按日期，无截止按 High→Mid→Low、
  同级发现日期新的在前；死岗沉底）；链接列一律 HYPERLINK 公式；写完自检，退出码非 0 = 未写成，改 changes.json 重跑。
- 链接列拒收搜索结果页、ATS board 首页；以 /careers /jobs /vacancies /vacatures 结尾的只 warning。
只依赖 openpyxl。
"""
import argparse, datetime as dt, io, json, re, sys
from collections import Counter

try:
    import openpyxl
    from openpyxl.styles import Alignment, Font
    from openpyxl.utils import get_column_letter
except ImportError:
    sys.exit("需要 openpyxl：pip install openpyxl --break-system-packages")

# ---------------------------------------------------------------- 规范常量
COLUMNS = ["岗位ID", "岗位名称", "单位", "地点", "工作模式", "类型", "级别", "优先级", "状态", "核验", "最后核验日期",
           "截止日期", "投递日期", "薪资/Scale", "合同与FTE", "主要要求", "所需材料", "联系人/PI", "签证/居留",
           "链接", "官网链接", "来源渠道", "发现日期", "备注"]
COL = {name: i for i, name in enumerate(COLUMNS)}          # 0-based
NCOL = len(COLUMNS)
WIDTHS = [18, 38, 24, 18, 8, 12, 8, 8, 7, 8, 12, 12, 12, 24, 18, 48, 10, 20, 22, 42, 42, 16, 12, 60]
LINK_COLS = ("链接", "官网链接")
AGGREGATOR_RE = re.compile(r"(academictransfer\.com|indeed\.com|linkedin\.com|euraxess\.|jobs\.ac\.uk|academicpositions\.|glassdoor\.)", re.I)
DECISION_TAG = "决定不投："
SHEETS = ["学术岗位", "工业岗位"]
NOTE_SHEET = "说明"
STATUS = ["未投", "已投", "面试", "被拒", "Offer", "关闭"]
PRIORITY = ["High", "Mid", "Low"]
VERIFY = ["官网JD", "聚合站", "未核验"]
LEVEL = ["Junior", "Medior", "Senior", "Staff+", "未标"]
WORKMODE = ["到岗", "混合", "远程", "未标"]
MATERIALS = ["CV", "CV+信", "CV+信+其他"]
SOURCES = ["AcademicTransfer", "LinkedIn", "Indeed", "校方alert", "官网/ATS", "Euraxess", "远程板", "其他"]
TYPES = {"学术岗位": ["Postdoc", "Researcher", "Research Engineer", "RSE", "实习"],
         "工业岗位": ["MLS", "MLE", "AI Engineer", "RE", "DS", "DE", "咨询", "实习", "其他"]}
DATE_COLS = ["最后核验日期", "截止日期", "投递日期", "发现日期"]

# 国内线
CN_SHEET = "国内岗位"
CN_COLUMNS = ["岗位ID", "岗位名称", "单位", "单位性质", "城市", "招聘类型", "类型", "优先级", "状态", "核验", "最后核验日期",
              "截止日期", "投递日期", "薪资", "编制与合同", "主要要求", "硬门槛", "所需材料", "联系人",
              "链接", "官网链接", "来源渠道", "发现日期", "备注"]
CN_WIDTHS = [20, 34, 24, 10, 8, 8, 8, 8, 7, 8, 12, 12, 12, 18, 18, 48, 30, 10, 16, 42, 42, 12, 12, 60]
CN_FREEZE = "D2"
CN_ORG = ["高校", "科研院所", "新型研发机构", "央企", "国企", "民企", "外企", "其他"]
CN_RECRUIT = ["校招", "社招", "博士后", "人才计划", "实习"]
CN_TYPES = ["算法", "研究", "教职", "数据", "工程", "其他"]
CN_MATERIALS = ["简历", "简历+其他"]
CN_SOURCES = ["官网", "Boss直聘", "猎聘", "牛客", "国聘", "高校人才网", "其他"]
SHEETS_ALL = SHEETS + [CN_SHEET]
CN_COMPANY_SHEET = "国内公司"
SHEET_ORDER = ["学术岗位", "工业岗位", CN_SHEET, "已排除", "公司", CN_COMPANY_SHEET, "说明"]


def cols(sheet):
    return CN_COLUMNS if sheet == CN_SHEET else COLUMNS


ALIVE_FOREVER = {"已投", "面试", "Offer"}
DEAD_STATUS = {"被拒", "关闭"}
STALE_DAYS = 14          # 复核阈值
NOTE_SEP = "｜"
FREEZE = "D2"            # 冻结 岗位ID / 岗位名称 / 单位
FONT = Font(name="Arial", size=10)
FONT_BOLD = Font(name="Arial", size=10, bold=True)
FONT_LINK = Font(name="Arial", size=10, color="0563C1", underline="single")
ALIGN = Alignment(wrap_text=True, vertical="center")
ROW_H, HEAD_H = 14.5, 18

COMPANY_SHEET = "公司"
COMPANY_COLUMNS = ["公司", "网址", "备注"]
COMPANY_WIDTHS = [28, 70, 60]
MANAGED_KEYS = ("上次运行时间：", "本轮第二梯队关键词：")

EXCL_SHEET = "已排除"
EXCL_COLUMNS = ["岗位ID", "岗位名称", "单位", "地点", "排除类别", "排除理由", "来源渠道", "链接", "发现日期"]
EXCL_WIDTHS = [24, 44, 26, 16, 12, 64, 14, 42, 12]
EXCL_CATS = ["PhD", "教职", "培训生", "Lead及以上", "量化交易", "别的学科", "非对口岗", "语言要求", "境外非远程", "硬门槛", "重复", "其他"]
EXCL_SOURCES = SOURCES + [s for s in CN_SOURCES if s not in SOURCES]
EXCL_FREEZE = "C2"
MAX_URL = 255            # Excel HYPERLINK 公式的链接长度上限

# ---------------------------------------------------------------- 工具
HL_RE = re.compile(r'^=HYPERLINK\("([^"]+)"')


def cell_url(v):
    v = "" if v is None else str(v)
    m = HL_RE.match(v)
    if m:
        return m.group(1)
    return v if v.startswith("http") else None


def to_date(v):
    if v is None or v == "":
        return None
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    s = str(v).strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if not m:
        raise ValueError("日期格式必须为 YYYY-MM-DD: %r" % v)
    return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))


def url_key(url):
    """从链接派生稳定标识；派生不出返回 None（由 slug 兜底）。"""
    if not url:
        return None
    pats = [
        (r"academictransfer\.com/en/jobs/(\d{5,7})", "at:"),
        (r"indeed\.com/.*[?&]jk=([0-9a-f]{16})", "indeed:"),
        (r"linkedin\.com/jobs/view/(\d+)", "li:"),
        (r"greenhouse\.io/[^/]+/jobs/(\d+)", "gh:"),
        (r"lever\.co/[^/]+/([0-9a-f-]{36})", "lever:"),
        (r"icims\.com/jobs/(\d+)", "icims:"),
        (r"myworkdayjobs\.com/.*/job/.*?([A-Z]{1,3}[-_]?\d{4,})", "wd:"),
        (r"ashbyhq\.com/[^/]+/([0-9a-f-]{36})", "ashby:"),
        (r"zhipin\.com/job_detail/([0-9A-Za-z_~-]+?)\.html", "boss:"),
        (r"liepin\.com/(?:a/|job/)(\d+)\.shtml", "liepin:"),
        (r"nowcoder\.com/jobs/detail/(\d+)", "nowcoder:"),
        (r"join\.qq\.com/post_detail\.html\?postid=(\d+)", "tencent:"),
        (r"careers\.tencent\.com/.*[?&]postId=(\d+)", "tencent:"),
        (r"jobs\.bytedance\.com/.*/position/(\d+)", "bytedance:"),
        (r"talent(?:-holding)?\.alibaba\.com/.*[?&]positionId=(\d+)", "alibaba:"),
        (r"(?:talent\.taotian\.com|careers\.aliyun\.com|careers-tongyi\.alibaba\.com|talent\.ele\.me|talent\.fliggy\.com|career\.fliggy\.com|aidc-jobs\.alibaba\.com|talent\.dingtalk\.com|talent\.quark\.cn|talent\.amap\.com|talent\.cainiao\.com|jobs\.hujing-dme\.com|hire\.freshippo\.com|careers\.alihealth\.cn)/.*[?&]positionId=(\d+)", "alibaba:"),
        (r"zhaopin\.meituan\.com/.*[?&]jobUnionId=(\d+)", "meituan:"),
        (r"talent\.baidu\.com/.*[?&]postId=([0-9A-Za-z]+)", "baidu:"),
        (r"campus\.jd\.com/#/details\?id=(\d+)", "jd:"),
        (r"zhaopin\.jd\.com/.*[?&]requirementId=(\d+)", "jds:"),
        (r"campus\.kuaishou\.cn/.*job-info/(\d+)", "kuaishou:"),
        (r"zhaopin\.kuaishou\.cn/.*job-info/(\d+)", "kuaishou-s:"),
        (r"xiaohongshu\.com/social/position/([0-9A-Za-z]+)", "xhs-s:"),
        (r"xiaohongshu\.com/.*/(?:position|job)/(?:detail/)?([0-9A-Za-z]+)", "xhs:"),
        (r"campus-talent\.alibaba\.com/campus/position/(\d+)", "alibaba:"),
        (r"campus\.163\.com/app/detail/index\?id=(\d+)", "netease:"),
        (r"talent\.antgroup\.com/campus-position\?positionId=(\d+)", "ant:"),
        (r"talent\.antgroup\.com/off-campus-position\?positionId=(\d+)", "ant:"),
        (r"careers\.pddglobalhr\.com/.*[?&]positionId=([0-9a-f-]+)", "pdd:"),
        (r"campus\.didiglobal\.com/.*#/job/([0-9a-f-]+)", "didi:"),
        (r"talent\.didiglobal\.com/social/jobDetail\?jdId=(\d+)", "didi-s:"),
        (r"jobs\.bilibili\.com/campus/positions/(\d+)", "bili:"),
        (r"jobs\.bilibili\.com/social/positions/(\d+)", "bili-s:"),
        (r"iflytek\.zhiye\.com/.*[?&]jobAdId=([0-9a-f-]+)", "iflytek:"),
        (r"baicgroup\.zhiye\.com/.*[?&]jobAdId=([0-9a-f-]+)", "baic:"),
        (r"shlab\.org\.cn/joinus/detail/(\d+)", "shlab:"),
        (r"mokahr\.com/(?:campus|social)-recruitment/.*#/job/([0-9a-f-]+)", "moka:"),
        (r"talents\.zhejianglab\.com/.*[?&]postId=([0-9a-f]+)", "zjlab:"),
        (r"hr\.pcl\.ac\.cn/.*[?&]postId=([0-9a-f]+)", "pcl:"),
        (r"job\.10086\.cn/.*[?&]id=([0-9a-f-]+)", "cmcc:"),
        (r"iguopin\.com/job/detail\?id=(\d+)", "guopin:"),
        (r"talent\.baidu\.com/jobs/detail/[A-Z_]+/([0-9a-f-]+)", "baidu:"),
        (r"amazon\.jobs/[a-z-]+/jobs/(\d+)", "amazon:"),
        (r"campus\.10jqka\.com\.cn/job/detail\?id=(\d+)", "ths:"),
        (r"campus\.game\.163\.com/app/detail/index\?id=(\d+)", "netease-game:"),
        (r"career\.huawei\.com/cn/job-details\?advertisementId=(\d+)", "huawei:"),
    ]
    for pat, prefix in pats:
        m = re.search(pat, url)
        if m:
            return prefix + m.group(1)
    return None


def slugify(s, n=24):
    s = re.sub(r"[^A-Za-z0-9一-鿿]+", "-", str(s or "")).strip("-")
    return s[:n].rstrip("-") or "x"


def derive_id(row, taken):
    # 官网链接能派生出 ATS 请求号的优先用它（跨渠道稳定），否则用发现页，再否则用短名
    k = url_key(row.get("官网链接")) or url_key(row.get("链接"))
    if not k:
        k = "%s-%s" % (slugify(row.get("单位"), 16), slugify(row.get("岗位名称"), 28))
    base, i = k, 2
    while k in taken:
        k = "%s-%d" % (base, i)
        i += 1
    return k


BAD_LINK = [
    (r"indeed\.com/(jobs|q-)", "Indeed 搜索页"),
    (r"linkedin\.com/jobs/search", "LinkedIn 搜索页"),
    (r"lever\.co/[^/]+/?$", "lever board 首页"),
    (r"greenhouse\.io/[^/]+/?(\?.*)?$", "greenhouse board 首页"),
    (r"academictransfer\.com/en/jobs/?(\?.*)?$", "AcademicTransfer 搜索页"),
    (r"zhipin\.com/web/geek/(job|jobs)\b", "Boss直聘 搜索页"),
    (r"liepin\.com/(zhaopin|job/?$|career/?$)", "猎聘 搜索页"),
    (r"nowcoder\.com/jobs/(school|recommend|fulltime|intern)/", "牛客 列表页"),
]
WARN_LINK = [
    (r"/(careers|jobs|vacancies|vacatures)/?$", "疑似公司职位总页"),
]


def link_problem(url):
    for pat, why in BAD_LINK:
        if re.search(pat, url):
            return why
    return None


def link_warning(url):
    for pat, why in WARN_LINK:
        if re.search(pat, url):
            return why
    return None


def read_rows(ws, sheet=None):
    C = cols(sheet or ws.title)
    n = len(C)
    rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        vals = list(r[:n]) + [None] * (n - len(r[:n]))
        if all(v in (None, "") for v in vals):
            continue
        d = {C[i]: vals[i] for i in range(n)}
        for c in LINK_COLS:
            d[c] = cell_url(d[c])
        for c in DATE_COLS:
            d[c] = to_date(d[c])
        rows.append(d)
    return rows


def is_dead(row, today):
    st = row["状态"]
    if st in ALIVE_FOREVER:
        return False
    if st in DEAD_STATUS:
        return True
    dl = row["截止日期"]
    if st == "未投" and dl and dl < today:
        return True
    return False


def sort_key(row, today):
    dead = is_dead(row, today)
    dl = row["截止日期"]
    found = row["发现日期"]
    pr = PRIORITY.index(row["优先级"]) if row["优先级"] in PRIORITY else len(PRIORITY)
    far = dt.date(9999, 12, 31)
    if not dead:
        return (0, 0 if dl else 1, dl or far, pr, -(found.toordinal() if found else 0))
    return (1, dl or far, pr)


def is_stale(row, today):
    """High/Mid、未投、活岗，且最后核验日期缺失或超过 STALE_DAYS。"""
    if row["状态"] != "未投" or row["优先级"] not in ("High", "Mid") or is_dead(row, today):
        return False
    lv = row["最后核验日期"]
    return (lv is None) or (today - lv).days > STALE_DAYS


def validate_row(sheet, row, where=""):
    errs = []
    cn = sheet == CN_SHEET
    if row["状态"] not in STATUS:
        errs.append("状态词非法 %r" % row["状态"])
    if row["优先级"] not in PRIORITY:
        errs.append("优先级非法 %r" % row["优先级"])
    types = CN_TYPES if cn else TYPES[sheet]
    if row["类型"] not in types:
        errs.append("类型词非法 %r（只允许 %s）" % (row["类型"], "/".join(types)))
    if row["核验"] not in VERIFY:
        errs.append("核验词非法 %r" % row["核验"])
    if cn:
        if row["单位性质"] not in CN_ORG:
            errs.append("单位性质词非法 %r（只允许 %s）" % (row["单位性质"], "/".join(CN_ORG)))
        if row["招聘类型"] not in CN_RECRUIT:
            errs.append("招聘类型词非法 %r（只允许 %s）" % (row["招聘类型"], "/".join(CN_RECRUIT)))
    else:
        if row["级别"] not in LEVEL:
            errs.append("级别词非法 %r" % row["级别"])
        if row["工作模式"] not in WORKMODE:
            errs.append("工作模式词非法 %r（只允许 %s）" % (row["工作模式"], "/".join(WORKMODE)))
    mats = CN_MATERIALS if cn else MATERIALS
    if row["所需材料"] not in (None, "") and row["所需材料"] not in mats:
        errs.append("所需材料词非法 %r（只允许 %s）" % (row["所需材料"], "/".join(mats)))
    srcs = CN_SOURCES if cn else SOURCES
    if row["来源渠道"] not in srcs:
        errs.append("来源渠道词非法 %r（只允许 %s）" % (row["来源渠道"], "/".join(srcs)))
    for c in LINK_COLS:
        if row.get(c):
            why = link_problem(row[c])
            if why:
                errs.append("%s不是岗位页（%s）：%s" % (c, why, row[c]))
    return ["%s%s" % (where, e) for e in errs]


def official_warnings(row):
    """官网链接列与核验列的自洽（只警告不报错）。"""
    w = []
    off = row.get("官网链接")
    if row.get("核验") == "官网JD" and not off:
        w.append("核验=官网JD 但官网链接为空")
    if off and row.get("核验") != "官网JD":
        w.append("官网链接非空但核验=%s" % row.get("核验"))
    if off and AGGREGATOR_RE.search(off):
        w.append("官网链接是聚合站页：%s" % off)
    if off and CN_AGG_RE.search(off) and "认证招聘方自发帖" not in str(row.get("备注") or ""):
        w.append("官网链接是国内聚合站页、备注没写「认证招聘方自发帖」：%s" % off)
    return w


CN_AGG_RE = re.compile(r"(zhipin\.com|liepin\.com|nowcoder\.com)", re.I)


# ---------------------------------------------------------------- 写 sheet
def write_sheet(wb, name, rows, today):
    rows = sorted(rows, key=lambda r: sort_key(r, today))
    C = cols(name)
    W = CN_WIDTHS if name == CN_SHEET else WIDTHS
    if name in wb.sheetnames:
        idx = wb.sheetnames.index(name)
        del wb[name]
    else:
        idx = len(wb.sheetnames)
    ws = wb.create_sheet(name, idx)
    for j, h in enumerate(C, 1):
        c = ws.cell(1, j, h)
        c.font = FONT_BOLD
        c.alignment = ALIGN
        ws.column_dimensions[get_column_letter(j)].width = W[j - 1]
    ws.row_dimensions[1].height = HEAD_H
    for i, r in enumerate(rows, 2):
        for j, h in enumerate(C, 1):
            v = r.get(h)
            c = ws.cell(i, j)
            if h in LINK_COLS:
                if v:
                    c.value = '=HYPERLINK("%s","%s")' % (v, v)
                    c.font = FONT_LINK
                else:
                    c.font = FONT
            elif h in DATE_COLS:
                if v:
                    c.value = dt.datetime(v.year, v.month, v.day)
                c.number_format = "YYYY-MM-DD"
                c.font = FONT
            else:
                c.value = None if v in ("", None) else v
                c.font = FONT
            c.alignment = ALIGN
            c.hyperlink = None
        ws.row_dimensions[i].height = ROW_H
    ws._hyperlinks = []
    ws.freeze_panes = CN_FREEZE if name == CN_SHEET else FREEZE
    ws.auto_filter.ref = "A1:%s%d" % (get_column_letter(len(C)), max(len(rows) + 1, 1))
    return rows


def reorder_sheets(wb):
    order = {n: i for i, n in enumerate(SHEET_ORDER)}
    wb._sheets.sort(key=lambda ws: order.get(ws.title, len(order)))
    wb.active = 0


# ---------------------------------------------------------------- 说明页
def read_notes(wb):
    if NOTE_SHEET not in wb.sheetnames:
        return []
    ws = wb[NOTE_SHEET]
    out = []
    for r in ws.iter_rows(values_only=True):
        v = r[0] if r else None
        if v not in (None, ""):
            out.append(str(v))
    return out


def label(r):
    return "%s（%s）" % (r["岗位名称"], r["单位"])


def build_notes(old_lines, run, sheets_rows, today, excluded=None):
    """说明页只有四样：上次运行时间、关键词轮到哪、投递状态、近期截止。每次整页重生成，不留历史。
    run.mode == "scan" 才改 上次运行时间 与 关键词位置；对话更新保留旧值。"""
    prev = {}
    for l in old_lines:
        for k in MANAGED_KEYS:
            if l.startswith(k):
                prev[k] = l[len(k):]
    scan = run.get("mode", "update") == "scan"
    lines = ["求职岗位汇总 · 规则见 profile/job_profile.md；本表只由 tools/tracker.py 写入"]
    lines.append("上次运行时间：" + ((run.get("last_run") if scan else None) or prev.get("上次运行时间：", "")))
    lines.append("本轮第二梯队关键词：" + ((run.get("second_tier") if scan else None) or prev.get("本轮第二梯队关键词：", "")))
    parts = []
    for sh, rows in sheets_rows.items():
        c = Counter(r["状态"] for r in rows)
        parts.append("%s %d 行（%s）" % (sh, len(rows), "、".join("%s %d" % (st, c[st]) for st in STATUS if c.get(st))))
    lines.append("【投递状态】" + "；".join(parts))
    hot = [label(r) + " " + r["状态"] for rows in sheets_rows.values() for r in rows if r["状态"] in ("面试", "Offer")]
    lines.append("【面试与 Offer】" + ("；".join(hot) if hot else "无"))
    soon = []
    for rows in sheets_rows.values():
        for r in rows:
            dl = r["截止日期"]
            if r["状态"] == "未投" and dl and today <= dl <= today + dt.timedelta(days=14) and not is_dead(r, today):
                soon.append((dl, "%s %s，%s" % (dl.isoformat(), label(r), r["优先级"])))
    soon.sort()
    lines.append("【近期截止 · %s 起 14 天内未投的活岗】%s" % (today.isoformat(), "；".join(s for _, s in soon) if soon else "无"))
    if excluded is not None:
        c = Counter(e["排除类别"] for e in excluded)
        lines.append("【已排除】%d 行（%s）" % (len(excluded), "、".join("%s %d" % (k, c[k]) for k in EXCL_CATS if c.get(k)) or "无"))
    return lines


def write_notes(wb, lines):
    if NOTE_SHEET in wb.sheetnames:
        idx = wb.sheetnames.index(NOTE_SHEET)
        del wb[NOTE_SHEET]
    else:
        idx = len(wb.sheetnames)
    ws = wb.create_sheet(NOTE_SHEET, idx)
    ws.column_dimensions["A"].width = 160
    for i, l in enumerate(lines, 1):
        c = ws.cell(i, 1, l)
        c.font = FONT
        c.alignment = Alignment(wrap_text=True, vertical="top")


# ---------------------------------------------------------------- 公司表
def read_companies(wb, sheet=COMPANY_SHEET):
    if sheet not in wb.sheetnames:
        return []
    out = []
    for r in wb[sheet].iter_rows(min_row=2, values_only=True):
        vals = list(r[:3]) + [None] * (3 - len(r[:3]))
        if not vals[0]:
            continue
        out.append({"公司": str(vals[0]).strip(), "网址": cell_url(vals[1]) or (vals[1] or None), "备注": vals[2] or None})
    return out


def apply_companies(comps, ch, log, tag="company"):
    idx = {c["公司"].casefold(): c for c in comps}
    for name in ch.get("remove", []):
        c = idx.pop(str(name).strip().casefold(), None)
        if not c:
            raise SystemExit("companies.remove：公司表里没有 %s" % name)
        log.append("%s remove | %s" % (tag, name))
    for item in ch.get("update", []):
        c = idx.get(str(item.get("公司", "")).strip().casefold())
        if not c:
            raise SystemExit("companies.update：公司表里没有 %s" % item.get("公司"))
        for k, v in item.get("set", {}).items():
            if k not in COMPANY_COLUMNS:
                raise SystemExit("companies.update：非法列 %s" % k)
            c[k] = v
        log.append("%s update | %s | %s" % (tag, c["公司"], item.get("set")))
    for item in ch.get("add", []):
        name = str(item.get("公司", "")).strip()
        if not name or not item.get("网址"):
            raise SystemExit("companies.add：公司和网址都必填：%r" % item)
        if name.casefold() in idx:
            raise SystemExit("companies.add：%s 已在公司表，改用 update" % name)
        idx[name.casefold()] = {"公司": name, "网址": item["网址"], "备注": item.get("备注") or None}
        log.append("%s add | %s | %s" % (tag, name, item["网址"]))
    for c in idx.values():
        if c["网址"] and not str(c["网址"]).startswith("http"):
            raise SystemExit("公司表网址必须以 http 开头：%s %r" % (c["公司"], c["网址"]))
    return sorted(idx.values(), key=lambda c: c["公司"].casefold())


def write_companies(wb, comps, sheet=COMPANY_SHEET):
    if sheet in wb.sheetnames:
        idx = wb.sheetnames.index(sheet)
        del wb[sheet]
    else:
        idx = wb.sheetnames.index(NOTE_SHEET) if NOTE_SHEET in wb.sheetnames else len(wb.sheetnames)
    ws = wb.create_sheet(sheet, idx)
    for j, h in enumerate(COMPANY_COLUMNS, 1):
        c = ws.cell(1, j, h)
        c.font = FONT_BOLD
        c.alignment = ALIGN
        ws.column_dimensions[get_column_letter(j)].width = COMPANY_WIDTHS[j - 1]
    ws.row_dimensions[1].height = HEAD_H
    for i, r in enumerate(comps, 2):
        ws.cell(i, 1, r["公司"]).font = FONT
        c = ws.cell(i, 2)
        if r["网址"]:
            c.value = '=HYPERLINK("%s","%s")' % (r["网址"], r["网址"])
            c.font = FONT_LINK
        ws.cell(i, 3, r["备注"]).font = FONT
        for j in (1, 2, 3):
            ws.cell(i, j).alignment = ALIGN
        ws.row_dimensions[i].height = ROW_H
    ws._hyperlinks = []
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = "A1:C%d" % max(len(comps) + 1, 1)


# ---------------------------------------------------------------- 已排除表
def read_excluded(wb):
    if EXCL_SHEET not in wb.sheetnames:
        return []
    n = len(EXCL_COLUMNS)
    out = []
    for r in wb[EXCL_SHEET].iter_rows(min_row=2, values_only=True):
        vals = list(r[:n]) + [None] * (n - len(r[:n]))
        if all(v in (None, "") for v in vals):
            continue
        d = {EXCL_COLUMNS[i]: vals[i] for i in range(n)}
        d["链接"] = cell_url(d["链接"])
        d["发现日期"] = to_date(d["发现日期"])
        out.append(d)
    return out


def write_excluded(wb, rows):
    rows = sorted(rows, key=lambda r: (-(r["发现日期"].toordinal() if r["发现日期"] else 0),
                                       str(r["单位"] or "").lower(), str(r["岗位名称"] or "").lower()))
    if EXCL_SHEET in wb.sheetnames:
        idx = wb.sheetnames.index(EXCL_SHEET)
        del wb[EXCL_SHEET]
    else:
        idx = (wb.sheetnames.index(SHEETS[-1]) + 1) if SHEETS[-1] in wb.sheetnames else len(wb.sheetnames)
    ws = wb.create_sheet(EXCL_SHEET, idx)
    for j, h in enumerate(EXCL_COLUMNS, 1):
        c = ws.cell(1, j, h)
        c.font = FONT_BOLD
        c.alignment = ALIGN
        ws.column_dimensions[get_column_letter(j)].width = EXCL_WIDTHS[j - 1]
    ws.row_dimensions[1].height = HEAD_H
    for i, r in enumerate(rows, 2):
        for j, h in enumerate(EXCL_COLUMNS, 1):
            v = r.get(h)
            c = ws.cell(i, j)
            if h == "链接":
                if v:
                    c.value = '=HYPERLINK("%s","%s")' % (v, v)
                    c.font = FONT_LINK
                else:
                    c.font = FONT
            elif h == "发现日期":
                if v:
                    c.value = dt.datetime(v.year, v.month, v.day)
                c.number_format = "YYYY-MM-DD"
                c.font = FONT
            else:
                c.value = None if v in ("", None) else v
                c.font = FONT
            c.alignment = ALIGN
            c.hyperlink = None
        ws.row_dimensions[i].height = ROW_H
    ws._hyperlinks = []
    ws.freeze_panes = EXCL_FREEZE
    ws.auto_filter.ref = "A1:%s%d" % (get_column_letter(len(EXCL_COLUMNS)), max(len(rows) + 1, 1))
    return rows


def normalize_excl(d, today):
    """返回 (row, warnings)；出错 raise ValueError。"""
    e = {c: d.get(c) for c in EXCL_COLUMNS}
    for c in EXCL_COLUMNS:
        if isinstance(e[c], str):
            e[c] = e[c].strip() or None
    where = "exclude %s @ %s：" % (e["岗位名称"], e["单位"])
    errs, warns = [], []
    if not e["岗位名称"] or not e["单位"]:
        errs.append("岗位名称和单位必填")
    if e["排除类别"] not in EXCL_CATS:
        errs.append("排除类别非法 %r（只允许 %s）" % (e["排除类别"], "/".join(EXCL_CATS)))
    if not e["排除理由"]:
        errs.append("排除理由必填")
    if e["来源渠道"] not in EXCL_SOURCES:
        errs.append("来源渠道词非法 %r（只允许 %s）" % (e["来源渠道"], "/".join(EXCL_SOURCES)))
    if e["链接"]:
        why = link_problem(e["链接"])
        if why:
            errs.append("链接不是岗位页（%s）：%s" % (why, e["链接"]))
        elif len(e["链接"]) > MAX_URL or '"' in e["链接"]:
            warns.append(where + "链接超过 %d 字符或含引号，不写入" % MAX_URL)
            e["链接"] = None
    e["发现日期"] = to_date(e["发现日期"]) or today
    if errs:
        raise ValueError("\n".join(where + x for x in errs))
    return e, warns


_TOK_GENERIC = {"bv", "b", "v", "gmbh", "inc", "ag", "nv", "the", "of", "and", "co", "ltd", "company", "group",
                "data", "ai", "solutions", "consulting", "consultancy", "digital", "tech", "technologies", "analytics",
                "labs", "interim", "professionals", "recruitment", "partners", "international", "systems", "e",
                "com", "nl", "io", "ai"}
_TOK_LOCAL = {"nederland", "netherlands", "university", "universiteit", "technology", "research", "medical", "center",
              "centre", "tu", "um", "uva", "delft", "amsterdam", "eindhoven", "utrecht"}


_CJK = re.compile(r"[\u4e00-\u9fff]")
_CN_CO_SUFFIX = re.compile(r"(股份有限公司|有限责任公司|有限公司|集团|控股|科技|技术|网络|信息|中国|北京|上海|深圳|杭州|广州|研究院|分公司)")


def _norm_title(s):
    s = re.sub(r"（[^）]*）|\([^)]*\)", " ", str(s or ""))
    return " ".join(re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", s.lower()).split())


def _company_overlap(a, b):
    if _CJK.search(str(a or "")) or _CJK.search(str(b or "")):
        ca = _CN_CO_SUFFIX.sub("", re.sub(r"[^\u4e00-\u9fffa-z0-9]", "", str(a or "").lower()))
        cb = _CN_CO_SUFFIX.sub("", re.sub(r"[^\u4e00-\u9fffa-z0-9]", "", str(b or "").lower()))
        return bool(ca and cb and (ca in cb or cb in ca))
    ta = set(re.sub(r"[^a-z0-9]+", " ", str(a or "").lower()).split()) - _TOK_GENERIC
    tb = set(re.sub(r"[^a-z0-9]+", " ", str(b or "").lower()).split()) - _TOK_GENERIC
    sa, sb = ta - _TOK_LOCAL, tb - _TOK_LOCAL
    if sa and sb:
        return bool(sa & sb)
    return bool(ta & tb)


# ---------------------------------------------------------------- 自检
SHOW_ALL_WARNINGS = False  # apply/check 加 --all-warnings 时逐条打印


def print_warnings(warnings, keep=3):
    """表里的旧警告有几百条，默认按类别汇总：每类报条数和前 keep 条。"""
    if SHOW_ALL_WARNINGS:
        for w in warnings:
            print("warning:", w)
        return
    groups = {}
    for w in warnings:
        k = re.sub(r"^\S+ 第\d+行 ", "", w)
        k = re.sub(r"第\d+行", "第N行", k.split("：")[0])
        groups.setdefault(k, []).append(w)
    for k, ws in groups.items():
        for w in ws[:keep]:
            print("warning:", w)
        if len(ws) > keep:
            print("warning: …「%s」共 %d 条，其余 %d 条略（--all-warnings 看全部）" % (k, len(ws), len(ws) - keep))


def check_workbook(path, today, expected_urls=None):
    wb = openpyxl.load_workbook(path)
    problems, warnings = [], []
    for name in SHEETS_ALL:
        if name not in wb.sheetnames:
            if name == CN_SHEET:
                warnings.append("缺 sheet：%s（下次 apply 自动建）" % name)
            else:
                problems.append("缺 sheet：%s" % name)
            continue
        ws = wb[name]
        CS = cols(name)
        NC = len(CS)
        CI = {h: k for k, h in enumerate(CS)}
        hdr = [c.value for c in ws[1]][:NC]
        if hdr != CS:
            problems.append("%s 表头不符：%s" % (name, hdr))
            continue
        if len(ws._hyperlinks) != 0:
            problems.append("%s 工作表级超链接索引非空（%d）" % (name, len(ws._hyperlinks)))
        seen_id, seen_url = {}, {}
        for i, r in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
            vals = list(r[:NC]) + [None] * (NC - len(r[:NC]))
            nonempty = [v for v in vals if v not in (None, "")]
            if not nonempty:
                continue
            where = "%s 第%d行 " % (name, i)
            url = cell_url(vals[CI["链接"]])
            for c in LINK_COLS:
                if vals[CI[c]] and not str(vals[CI[c]]).startswith("=HYPERLINK("):
                    problems.append(where + "%s不是 HYPERLINK 公式" % c)
            if len(nonempty) <= 2:
                problems.append(where + "空壳行")
            if not vals[CI["岗位名称"]]:
                problems.append(where + "岗位名称为空")
            jid = vals[CI["岗位ID"]]
            if not jid:
                problems.append(where + "岗位ID 为空")
            elif jid in seen_id:
                problems.append(where + "岗位ID 与第%d行重复：%s" % (seen_id[jid], jid))
            else:
                seen_id[jid] = i
            row = {CS[k]: vals[k] for k in range(NC)}
            row["链接"] = url
            row["官网链接"] = cell_url(vals[CI["官网链接"]])
            problems += validate_row(name, row, where)
            if row["状态"] == "未投":
                warnings += [where + x for x in official_warnings(row)]
            for c in DATE_COLS:
                v = vals[CI[c]]
                if v not in (None, "") and not isinstance(v, (dt.date, dt.datetime)):
                    problems.append(where + "%s 不是真日期：%r" % (c, v))
            if url:
                k = url_key(url) or url.rstrip("/").lower()
                if k in seen_url:
                    warnings.append(where + "与第%d行链接相同（按岗位ID区分）：%s" % (seen_url[k], url))
                seen_url.setdefault(k, i)
                w = link_warning(url)
                if w:
                    warnings.append(where + "%s：%s" % (w, url))
            if expected_urls is not None and url and url not in expected_urls:
                problems.append(where + "链接不在本轮预期集合：%s" % url)
        n = ws.max_row
        want = "A1:%s%d" % (get_column_letter(NC), n)
        if n > 1 and ws.auto_filter.ref != want:
            problems.append("%s 自动筛选范围 %s ≠ %s" % (name, ws.auto_filter.ref, want))
        fz = CN_FREEZE if name == CN_SHEET else FREEZE
        if ws.freeze_panes != fz:
            problems.append("%s 冻结窗格 %s ≠ %s" % (name, ws.freeze_panes, fz))
    if NOTE_SHEET not in wb.sheetnames:
        problems.append("缺 sheet：说明")
    if EXCL_SHEET not in wb.sheetnames:
        warnings.append("缺 sheet：已排除（下次 apply 自动建）")
    else:
        ws = wb[EXCL_SHEET]
        hdr = [c.value for c in ws[1]][:len(EXCL_COLUMNS)]
        if hdr != EXCL_COLUMNS:
            problems.append("已排除 表头不符：%s" % hdr)
        else:
            if len(ws._hyperlinks) != 0:
                problems.append("已排除 工作表级超链接索引非空（%d）" % len(ws._hyperlinks))
            main_ids = set()
            for name in SHEETS_ALL:
                if name in wb.sheetnames:
                    main_ids |= {r[0] for r in wb[name].iter_rows(min_row=2, values_only=True) if r and r[0]}
            seen = {}
            ci = {h: k for k, h in enumerate(EXCL_COLUMNS)}
            for i, r in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
                vals = list(r[:len(EXCL_COLUMNS)]) + [None] * (len(EXCL_COLUMNS) - len(r[:len(EXCL_COLUMNS)]))
                if all(v in (None, "") for v in vals):
                    continue
                where = "已排除 第%d行 " % i
                jid = vals[ci["岗位ID"]]
                if not jid:
                    problems.append(where + "岗位ID 为空")
                elif jid in seen:
                    problems.append(where + "岗位ID 与第%d行重复：%s" % (seen[jid], jid))
                else:
                    seen[jid] = i
                if jid in main_ids:
                    warnings.append(where + "岗位ID 同时出现在岗位表：%s" % jid)
                if vals[ci["排除类别"]] not in EXCL_CATS:
                    problems.append(where + "排除类别非法 %r" % vals[ci["排除类别"]])
                if not vals[ci["排除理由"]]:
                    problems.append(where + "排除理由为空")
                if vals[ci["来源渠道"]] not in EXCL_SOURCES:
                    problems.append(where + "来源渠道词非法 %r" % vals[ci["来源渠道"]])
                lk = vals[ci["链接"]]
                if lk and not str(lk).startswith("=HYPERLINK("):
                    problems.append(where + "链接不是 HYPERLINK 公式")
                v = vals[ci["发现日期"]]
                if v not in (None, "") and not isinstance(v, (dt.date, dt.datetime)):
                    problems.append(where + "发现日期 不是真日期：%r" % v)
            n = ws.max_row
            want = "A1:%s%d" % (get_column_letter(len(EXCL_COLUMNS)), n)
            if n > 1 and ws.auto_filter.ref != want:
                problems.append("已排除 自动筛选范围 %s ≠ %s" % (ws.auto_filter.ref, want))
    for cs in (COMPANY_SHEET, CN_COMPANY_SHEET):
        if cs in wb.sheetnames and len(wb[cs]._hyperlinks) != 0:
            problems.append("%s 工作表级超链接索引非空" % cs)
    n_off = sum(1 for w in warnings if "官网链接" in w)
    print_warnings(warnings)
    if n_off:
        print("warning 汇总：官网链接/核验不自洽 %d 处（未投行）" % n_off)
    return problems


# ---------------------------------------------------------------- 命令
def cmd_info(a):
    today = to_date(a.today) if a.today else dt.date.today()
    wb = openpyxl.load_workbook(a.xlsx)
    notes = read_notes(wb)
    out = {"notes_head": notes[:4], "today": today.isoformat(), "sheets": {}, "known": {}, "stale": {}, "missing_official": {},
           "companies": len(read_companies(wb)), "cn_companies": len(read_companies(wb, CN_COMPANY_SHEET))}
    for name in SHEETS_ALL:
        if name not in wb.sheetnames:
            continue
        rows = read_rows(wb[name], name)
        out["sheets"][name] = {
            "rows": len(rows),
            "status": dict(Counter(r["状态"] for r in rows)),
            "priority": dict(Counter(r["优先级"] for r in rows)),
            "verify": dict(Counter(r["核验"] for r in rows)),
        }
        out["known"][name] = sorted(r["岗位ID"] for r in rows if r["岗位ID"])
        out["known"][name + "_名称单位"] = sorted("%s @ %s" % (r["岗位名称"], r["单位"]) for r in rows)
        out["stale"][name] = [{"id": r["岗位ID"], "岗位": label(r), "优先级": r["优先级"], "核验": r["核验"],
                               "最后核验日期": r["最后核验日期"].isoformat() if r["最后核验日期"] else None, "链接": r["链接"]}
                              for r in sorted(rows, key=lambda r: (PRIORITY.index(r["优先级"]) if r["优先级"] in PRIORITY else 9,
                                                                    r["最后核验日期"] or dt.date(1900, 1, 1)))
                              if is_stale(r, today)]
        out["missing_official"][name] = [{"id": r["岗位ID"], "岗位": label(r), "优先级": r["优先级"], "链接": r["链接"]}
                                         for r in rows if r["状态"] == "未投" and not is_dead(r, today)
                                         and r["核验"] == "官网JD" and not r["官网链接"]]
    exc = read_excluded(wb)
    out["excluded"] = {"rows": len(exc), "by_cat": dict(Counter(e["排除类别"] for e in exc))}
    print(json.dumps(out, ensure_ascii=False, indent=1))


def cmd_companies(a):
    wb = openpyxl.load_workbook(a.xlsx)
    comps = read_companies(wb, CN_COMPANY_SHEET if a.cn else COMPANY_SHEET)
    print("公司\t网址\t备注")
    for c in comps:
        print("%s\t%s\t%s" % (c["公司"], c["网址"] or "", c["备注"] or ""))
    print("（共 %d 家）" % len(comps), file=sys.stderr)


def cmd_export(a):
    wb = openpyxl.load_workbook(a.xlsx)
    out = {}
    for name in SHEETS_ALL:
        if name not in wb.sheetnames:
            continue
        rows = read_rows(wb[name], name)
        for r in rows:
            for c in DATE_COLS:
                r[c] = r[c].isoformat() if r[c] else None
        out[name] = rows
    exc = read_excluded(wb)
    for e in exc:
        e["发现日期"] = e["发现日期"].isoformat() if e["发现日期"] else None
    out[EXCL_SHEET] = exc
    io.open(a.out, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    print("exported", {k: len(v) for k, v in out.items()}, "->", a.out)


def cmd_stats(a):
    wb = openpyxl.load_workbook(a.xlsx)
    for name in SHEETS_ALL:
        if name not in wb.sheetnames:
            continue
        rows = read_rows(wb[name], name)
        print("==", name, len(rows), "行")
        dims = ("来源渠道", "优先级", "类型", "核验", "单位性质", "招聘类型", "城市") if name == CN_SHEET else \
               ("来源渠道", "优先级", "类型", "核验", "级别", "工作模式")
        for dim in dims:
            tab = {}
            for r in rows:
                tab.setdefault(str(r[dim] or "（空）"), Counter())[r["状态"]] += 1
            print("  --", dim)
            for k, c in sorted(tab.items(), key=lambda kv: -sum(kv[1].values())):
                print("     %-28s 共%3d  %s" % (k, sum(c.values()), "  ".join("%s %d" % kv for kv in sorted(c.items()))))


def normalize_row(sheet, d, today):
    C = cols(sheet)
    bad = [k for k in d if k not in C]
    if bad:
        raise ValueError("新增行有 %s 表里没有的列：%s" % (sheet, bad))
    row = {c: d.get(c) for c in C}
    if not row["岗位名称"] or not row["单位"]:
        raise ValueError("新增行缺岗位名称或单位：%r" % d)
    if row["状态"] in (None, ""):
        row["状态"] = "未投"
    if row["核验"] in (None, ""):
        row["核验"] = "未核验"
    if sheet != CN_SHEET:
        if row["级别"] in (None, ""):
            row["级别"] = "未标"
        if sheet == "学术岗位":
            row["级别"] = "未标"
        if row["工作模式"] in (None, ""):
            row["工作模式"] = "未标"
    for c in DATE_COLS:
        row[c] = to_date(row[c])
    for c in C:
        if isinstance(row[c], str) and row[c].strip() in ("", "-", "—", "N/A", "n/a"):
            row[c] = None
    if row["核验"] != "未核验" and not row["最后核验日期"]:
        row["最后核验日期"] = today
    errs = validate_row(sheet, row, "add %s：" % row["岗位名称"])
    if errs:
        raise ValueError("\n".join(errs))
    return row


def cmd_apply(a):
    today = to_date(a.today) if a.today else dt.date.today()
    ch = json.load(io.open(a.changes, encoding="utf-8"))
    wb = openpyxl.load_workbook(a.xlsx)
    old_notes = read_notes(wb)
    sheets_rows = {name: (read_rows(wb[name], name) if name in wb.sheetnames else []) for name in SHEETS_ALL}
    excluded = read_excluded(wb)
    log = []

    def find(sheet, item):
        rows = sheets_rows[sheet]
        if item.get("id"):
            hits = [r for r in rows if r["岗位ID"] == item["id"]]
        elif item.get("url"):
            k = url_key(item["url"])
            u = item["url"].rstrip("/").lower()
            hits = [r for r in rows if any(
                (url_key(r[c]) == k) if k else ((r[c] or "").rstrip("/").lower() == u) for c in LINK_COLS)]
        else:
            raise SystemExit("update/remove 需要 id 或 url：%r" % item)
        if len(hits) != 1:
            raise SystemExit("%s：匹配到 %d 行（需恰好 1 行；多行共用链接时请改用 id）：%r" % (
                "remove" if item in ch.get("remove", []) else "update", len(hits), item.get("id") or item.get("url")))
        return hits[0]

    for item in ch.get("remove", []):
        r = find(item["sheet"], item)
        sheets_rows[item["sheet"]].remove(r)
        log.append("remove %s | %s" % (item["sheet"], label(r)))
    for item in ch.get("update", []):
        r = find(item["sheet"], item)
        for k, v in item.get("set", {}).items():
            if k not in cols(item["sheet"]):
                raise SystemExit("update：%s 表没有这一列 %s" % (item["sheet"], k))
            if k == "岗位ID":
                raise SystemExit("update：岗位ID 由脚本派生，不允许手改")
            if k in LINK_COLS and r[k] and v != r[k]:
                old = str(r["备注"] or "").strip()
                r["备注"] = (old + NOTE_SEP if old else "") + "旧%s %s" % (k, r[k])
            if k == "备注":
                oldn = str(r["备注"] or "")
                kept = [seg for seg in oldn.split(NOTE_SEP) if "决定不投" in seg]
                if kept and "决定不投" not in str(v or ""):
                    v = NOTE_SEP.join(kept + ([str(v)] if v else []))
                    log.append("（保留人工决策段「%s…」：%s）" % (DECISION_TAG, label(r)))
            r[k] = to_date(v) if k in DATE_COLS else v
        if item.get("append_note"):
            old = str(r["备注"] or "").strip()
            r["备注"] = (old + NOTE_SEP if old else "") + item["append_note"]
        if item.get("verified"):
            r["最后核验日期"] = today
        if r["状态"] == "已投" and not r["投递日期"] and item.get("set", {}).get("状态") == "已投":
            raise SystemExit("update：状态改为已投时必须同时 set 投递日期：%s" % label(r))
        errs = validate_row(item["sheet"], r, "update %s：" % label(r))
        if errs:
            raise SystemExit("\n".join(errs))
        log.append("update %s | %s | %s" % (item["sheet"], label(r), item.get("set", {})))
    taken = {r["岗位ID"] for rows in sheets_rows.values() for r in rows if r["岗位ID"]}
    existing_keys = {name: {url_key(r[c]) for r in rows for c in LINK_COLS if url_key(r[c])} for name, rows in sheets_rows.items()}
    existing_names = {name: {(str(r["岗位名称"]).strip().lower(), str(r["单位"]).strip().lower()) for r in rows}
                      for name, rows in sheets_rows.items()}
    for item in ch.get("add", []):
        sheet = item["sheet"]
        try:
            row = normalize_row(sheet, item["row"], today)
        except ValueError as e:
            raise SystemExit(str(e))
        ks = [url_key(row[c]) for c in LINK_COLS if url_key(row[c])]
        k = ks[0] if ks else None
        nk = (str(row["岗位名称"]).strip().lower(), str(row["单位"]).strip().lower())
        for kk in ks:
            if kk in existing_keys[sheet]:
                raise SystemExit("add：链接已存在（%s），改用 update：%s / %s" % (kk, row["链接"], row["官网链接"]))
        if nk in existing_names[sheet] and not item.get("allow_same_name"):
            raise SystemExit("add：同名同单位已存在（跨渠道重复？）：%s @ %s。确认不是同一岗位则加 allow_same_name:true" % nk)
        back = [e for e in excluded if (url_key(e["链接"]) and url_key(e["链接"]) in ks)
                or (str(e["岗位名称"]).strip().lower(), str(e["单位"]).strip().lower()) == nk]
        for e in back:
            excluded.remove(e)
            log.append("（从已排除移回：%s @ %s，原排除理由「%s」）" % (e["岗位名称"], e["单位"], e["排除理由"]))
        if not row["发现日期"]:
            row["发现日期"] = today
        row["岗位ID"] = derive_id(row, taken)
        taken.add(row["岗位ID"])
        sheets_rows[sheet].append(row)
        existing_keys[sheet].update(ks)
        existing_names[sheet].add(nk)
        log.append("add %s | %s | %s | %s" % (sheet, row["岗位ID"], label(row), row["优先级"]))

    # v7：已排除表
    main_keys = set().union(*existing_keys.values())
    main_names = set().union(*existing_names.values())
    excl_taken = taken | {e["岗位ID"] for e in excluded if e["岗位ID"]}
    excl_keys = {url_key(e["链接"]) for e in excluded if url_key(e["链接"])}
    excl_names = {(str(e["岗位名称"]).strip().lower(), str(e["单位"]).strip().lower()) for e in excluded}
    n_excl = 0
    for d in ch.get("exclude", []):
        try:
            e, warns = normalize_excl(d, today)
        except ValueError as ex:
            raise SystemExit(str(ex))
        for w in warns:
            print("warning:", w)
        k = url_key(e["链接"])
        nk = (str(e["岗位名称"]).strip().lower(), str(e["单位"]).strip().lower())
        if (k and k in main_keys) or (nk in main_names and not d.get("allow_same_name")):
            raise SystemExit("exclude：%s @ %s 已在岗位表，去岗位表改状态，不要排除（确属不同岗位则加 allow_same_name:true）" % nk)
        if (k and k in excl_keys) or nk in excl_names:
            log.append("（已在已排除表，跳过：%s @ %s）" % (e["岗位名称"], e["单位"]))
            continue
        e["岗位ID"] = derive_id({"官网链接": None, "链接": e["链接"], "单位": e["单位"], "岗位名称": e["岗位名称"]}, excl_taken)
        excl_taken.add(e["岗位ID"])
        if k:
            excl_keys.add(k)
        excl_names.add(nk)
        excluded.append(e)
        n_excl += 1
        log.append("exclude | %s | %s @ %s | %s" % (e["岗位ID"], e["岗位名称"], e["单位"], e["排除类别"]))
    if n_excl:
        log.append("（本次写入已排除 %d 行）" % n_excl)
    for item in ch.get("exclude_update", []):
        hit = [e for e in excluded if e["岗位ID"] == item.get("id")]
        if len(hit) != 1:
            raise SystemExit("exclude_update：已排除表里按岗位ID找到 %d 行：%s" % (len(hit), item.get("id")))
        e = hit[0]
        for kk, vv in item.get("set", {}).items():
            if kk not in EXCL_COLUMNS or kk == "岗位ID":
                raise SystemExit("exclude_update：非法列 %s" % kk)
            if kk == "排除类别" and vv not in EXCL_CATS:
                raise SystemExit("exclude_update：排除类别不在词表：%s" % vv)
            e[kk] = vv
        log.append("exclude_update | %s | %s" % (e["岗位ID"], item.get("set")))

    # v4：未投且截止已过的行自动转 关闭（状态词表本来就这么定义，但一直没人执行）
    autoclosed = 0
    for name in SHEETS_ALL:
        for r in sheets_rows[name]:
            dl = r["截止日期"]
            if r["状态"] == "未投" and dl and dl < today:
                r["状态"] = "关闭"
                note = "%s 自动转关闭：截止日期 %s 已过且未投（tracker.py）" % (today.isoformat(), dl.isoformat())
                oldn = str(r["备注"] or "").strip()
                r["备注"] = (oldn + NOTE_SEP if oldn else "") + note
                autoclosed += 1
                log.append("auto-close %s | %s | %s | 截止 %s 已过" % (name, r["岗位ID"], label(r), dl.isoformat()))
    if autoclosed:
        log.append("（自动转关闭 %d 行：未投且截止已过）" % autoclosed)

    expected = set()
    for name in SHEETS_ALL:
        sorted_rows = write_sheet(wb, name, sheets_rows[name], today)
        sheets_rows[name] = sorted_rows
        expected |= {r["链接"] for r in sorted_rows if r["链接"]}
    excluded = write_excluded(wb, excluded)
    comps = apply_companies(read_companies(wb), ch.get("companies", {}), log)
    cn_comps = apply_companies(read_companies(wb, CN_COMPANY_SHEET), ch.get("cn_companies", {}), log, tag="cn_company")
    write_notes(wb, build_notes(old_notes, ch.get("run", {}), sheets_rows, today, excluded))
    write_companies(wb, comps)
    write_companies(wb, cn_comps, CN_COMPANY_SHEET)
    reorder_sheets(wb)
    out = a.out or a.xlsx
    wb.save(out)
    problems = check_workbook(out, today, expected_urls=expected)
    print("\n".join(log) if log else "（无行级改动）")
    print("rows:", dict({n: len(sheets_rows[n]) for n in SHEETS_ALL}, **{EXCL_SHEET: len(excluded)}))
    if problems:
        print("自检未过：")
        print("\n".join(" - " + p for p in problems))
        sys.exit(2)
    print("自检通过 →", out)


def cmd_match(a):
    """邮件或搜索结果判重：每条标 在表 / 已排除 / 新。"""
    import difflib
    wb = openpyxl.load_workbook(a.xlsx)
    pool = [(name, r) for name in SHEETS_ALL if name in wb.sheetnames for r in read_rows(wb[name], name)] + \
           [(EXCL_SHEET, e) for e in read_excluded(wb)]
    blobs = [json.dumps(r, ensure_ascii=False, default=str).lower() for _, r in pool]
    jobs = json.load(io.open(a.jobs, encoding="utf-8"))
    res, cnt = [], Counter()
    for j in jobs:
        title = j.get("title") or j.get("岗位名称") or ""
        comp = j.get("company") or j.get("employer") or j.get("单位") or ""
        ids = [str(x).strip() for x in (j.get("ids") or []) if x and len(str(x).strip()) >= 5]
        for key in ("jk", "job_id", "id"):
            if j.get(key) and len(str(j[key]).strip()) >= 5:
                ids.append(str(j[key]).strip())
        k = url_key(j.get("link"))
        if k:
            ids.append(k.split(":", 1)[1])
        ids = sorted(set(ids))
        hits = []
        for (where, r), blob in zip(pool, blobs):
            if any(re.search(r"(?<![0-9a-z])%s(?![0-9a-z])" % re.escape(i.lower()), blob) for i in ids):
                hits.append(("id", 1.0, where, r))
        if not hits:
            nt = _norm_title(title)
            for where, r in pool:
                ratio = difflib.SequenceMatcher(None, nt, _norm_title(r["岗位名称"])).ratio()
                if ratio >= a.threshold and _company_overlap(comp, r["单位"]):
                    hits.append(("名称", round(ratio, 2), where, r))
            hits.sort(key=lambda h: -h[1])
        def brief(h):
            by, score, where, r = h
            d = {"by": by, "score": score, "sheet": where, "岗位ID": r["岗位ID"], "岗位名称": r["岗位名称"], "单位": r["单位"]}
            if where == EXCL_SHEET:
                d.update({"排除类别": r["排除类别"], "排除理由": r["排除理由"]})
            else:
                d.update({"状态": r["状态"], "优先级": r["优先级"]})
            return d
        if hits:
            m = "已排除" if hits[0][2] == EXCL_SHEET else "在表"
        else:
            m = "新"
        cnt[m] += 1
        res.append(dict(j, match=m, hit=brief(hits[0]) if hits else None, others=[brief(h) for h in hits[1:4]]))
    io.open(a.out, "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=1))
    print("共 %d 条：在表 %d、已排除 %d、新 %d → %s" % (len(res), cnt["在表"], cnt["已排除"], cnt["新"], a.out))
    fuzzy = [r for r in res if r["hit"] and r["hit"]["by"] == "名称"]
    if fuzzy:
        print("-- 按名称匹配的（请人工确认是同一岗）：")
        for r in fuzzy:
            h = r["hit"]
            print("   %s @ %s  ≈  [%s] %s @ %s（%s，%.2f）" % (r.get("title") or r.get("岗位名称"), r.get("company") or r.get("单位"),
                                                       h["sheet"], h["岗位名称"], h["单位"], h["岗位ID"], h["score"]))
    print("-- 新（本轮必须入表或排除）：")
    for r in res:
        if r["match"] == "新":
            print("   %s @ %s" % (r.get("title") or r.get("岗位名称"), r.get("company") or r.get("employer") or r.get("单位")))


def cmd_check(a):
    today = to_date(a.today) if a.today else dt.date.today()
    problems = check_workbook(a.xlsx, today)
    if problems:
        print("\n".join(" - " + p for p in problems))
        sys.exit(2)
    print("自检通过")


def cmd_init(a):
    import os
    if os.path.exists(a.xlsx):
        raise SystemExit("文件已存在，不覆盖：%s" % a.xlsx)
    wb = openpyxl.Workbook()
    del wb[wb.sheetnames[0]]
    today = dt.date.today()
    for name in SHEETS_ALL:
        write_sheet(wb, name, [], today)
    write_excluded(wb, [])
    write_notes(wb, build_notes([], {"mode": "scan", "last_run": "", "second_tier": "", "data_source": ""},
                                {n: [] for n in SHEETS_ALL}, today, []))
    write_companies(wb, [])
    write_companies(wb, [], CN_COMPANY_SHEET)
    reorder_sheets(wb)
    wb.save(a.xlsx)
    print("created", a.xlsx)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("info"); s.add_argument("xlsx"); s.add_argument("--today"); s.set_defaults(f=cmd_info)
    s = sp.add_parser("companies"); s.add_argument("xlsx"); s.add_argument("--cn", action="store_true"); s.set_defaults(f=cmd_companies)
    s = sp.add_parser("export"); s.add_argument("xlsx"); s.add_argument("--out", required=True); s.set_defaults(f=cmd_export)
    s = sp.add_parser("apply"); s.add_argument("xlsx"); s.add_argument("--changes", required=True)
    s.add_argument("--out"); s.add_argument("--today"); s.add_argument("--all-warnings", action="store_true"); s.set_defaults(f=cmd_apply)
    s = sp.add_parser("check"); s.add_argument("xlsx"); s.add_argument("--today"); s.add_argument("--all-warnings", action="store_true"); s.set_defaults(f=cmd_check)
    s = sp.add_parser("stats"); s.add_argument("xlsx"); s.set_defaults(f=cmd_stats)
    s = sp.add_parser("match"); s.add_argument("xlsx"); s.add_argument("--jobs", required=True); s.add_argument("--out", required=True)
    s.add_argument("--threshold", type=float, default=0.8); s.set_defaults(f=cmd_match)
    s = sp.add_parser("init"); s.add_argument("xlsx"); s.set_defaults(f=cmd_init)
    a = p.parse_args()
    global SHOW_ALL_WARNINGS
    SHOW_ALL_WARNINGS = getattr(a, "all_warnings", False)
    a.f(a)


if __name__ == "__main__":
    main()

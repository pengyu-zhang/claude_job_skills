---
name: job-search-cn
description: "国内找岗流水线：扫大厂校招和社招官网、Boss直聘、国聘、高校人才网等，读 JD 按 job_profile.md 的标准打分，用 tracker.py 写进求职表的「国内岗位」表。用户说找国内工作、跑国内找岗、更新国内岗位表时用。"
---

# job-search-cn · 国内找岗流水线

终点是更新求职 Excel 的「国内岗位」「已排除」「国内公司」三张表。不做匹配评估、不写材料、不投递、不发消息（Boss直聘上不点「立即沟通」）。欧洲线是另一个 skill `job-search`，两者互不调用。全程中文。

## 规则源与文件

- **用户的要求在 `profile/job_profile.md`**（jobs 文件夹里；放进 Claude Project 的项目文件也行，文件名相同）：「国内岗」写收什么、硬门槛、打分的调整、国内搜索关键词；没写到的按同一文件的「收什么岗」「方向和岗位分类」「打分」。运行开始先读，读不到就停下告诉用户，不凭记忆打分。出生日期、政治面貌、学历、毕业时间、项目和论文、没用过的东西在 `profile/facts.md`。
- **各站读法在 jobs 文件夹的 `cn_sites.md`**（仓库 `docs/` 里带的，三十来个站的接口、请求体、翻页上限、岗位页格式）和「国内公司」表的备注里。本 skill 只写通用手法和几个大站的细节；摸清一家新站就在国内公司表加一行，备注写读法。国内公司表还是空的时候，先按 `job_profile.md`「国内岗」写的目标单位，从 `cn_sites.md` 里挑出来 add 进去。站点会改版，读法对不上时按下面「摸新站的通用手法」重新摸，并更新备注。
- **jobs 文件夹里**：`job_tracker.xlsx`、`tools/tracker.py`（唯一写表工具，用法和各列怎么填都在脚本开头，运行开始读一遍；add 时 `"sheet": "国内岗位"`，国内公司表改动写 `cn_companies`）。新站的岗位页能派生编号的，在 `url_key` 的 pats 里加一条正则（只留一个捕获组），先在表副本上跑通再用。
- **脚本在用户电脑上跑**（云端会话用设备端 shell，路径写 `$HOME/mnt/jobs`，即把 jobs 文件夹直接连给会话时的位置；本地会话直接在 jobs 文件夹下跑）。changes 文件写在 `~/work/`，**不放进 jobs 文件夹**，用 heredoc 直接写。
- 本 skill 要改时，起草完整的新 SKILL.md 交给用户保存。

## 浏览器分工（实测）

| 站 | 浏览器 | 登录 |
|---|---|---|
| 腾讯、字节、阿里、蚂蚁、美团、京东、快手、小红书、网易、拼多多、滴滴、B站、讯飞、中国移动、国聘、各 AI 实验室、高校人才网 | 内置浏览器 | 不用 |
| 牛客 | 内置浏览器 | 要登录 |
| Boss直聘、猎聘、百度 | **只能用用户本地 Chrome**：内置浏览器里页面自己关掉或白屏 | Boss、猎聘要登录 |
| 中科院招聘平台 job.cas.cn 等部分科研院所的站 | 从海外网络两个浏览器都超时 | — |

上表是从海外网络实测的，人在国内时可能不一样；有的站（如部分社招站）对海外 IP 返回 404，在国内网络下再扫。

要登录、扫码、过验证时，**攒成一张清单一次问用户**（站名、哪个浏览器、为什么要登），等的时候先跑别的站。助理不填密码。投递要注册的站（有的要手机验证）只在用户决定投时才提。

在 Boss直聘、猎聘上操作慢一点，像人在用：翻页、开帖之间留间隔，不连着刷，免得账号被封；一出现验证码就告诉用户。看完消息不关页，把消息页留着，方便用户接着回。

## 核验怎么记

- `官网JD`：雇主官网招聘系统里的岗位页，或单位的官方公告。高校和科研院所以人事处或单位官网上的公告为准。
- `聚合站`：Boss直聘、猎聘、牛客、国聘、高校人才网上的帖子。
- 单位没有自己的招聘页、只在 Boss直聘或猎聘上招，发帖人又是该单位认证招聘方的，记 `官网JD`，备注写「认证招聘方自发帖」。

校招和社招都扫：国内公司表里每家的校招入口、社招入口（含研究院、实验室的招聘页）都过一遍；只登记了校招网址的，扫的时候把社招网址补进同一行。不为省事跳站、不抽样。

## 运行前

1. 确认能访问 jobs 文件夹（没有就申请访问）；提醒用户关掉正开着的 Excel。
2. 读状态：
   ```bash
   mkdir -p ~/work && cd "$HOME/mnt/jobs" && python3 tools/tracker.py info job_tracker.xlsx --today YYYY-MM-DD > ~/work/info.json && python3 tools/tracker.py export job_tracker.xlsx --out ~/work/rows.json && python3 tools/tracker.py companies job_tracker.xlsx --cn
   ```
   `rows.json` 里的 `国内岗位` 和 `已排除` 用来判重（按岗位ID、链接里的编号、岗位名+单位）。
3. 复核：国内岗位表里 `最后核验日期` 超过 14 天的 High/Mid 未投岗，先回官网页看还在不在招，再找新岗。有截止日在 3 天内的 High，摘要第一句就提醒。

## 第一层 · 国内公司表直扫

挨个读「国内公司」表，照备注和 `cn_sites.md` 里的读法做。摸新站的通用手法：

1. **找接口**：页面加载后看 `performance.getEntriesByType('resource')` 里的 JSON 请求；拿不到请求体时，先给 `XMLHttpRequest.prototype.open/send/setRequestHeader` 和 `fetch` 打补丁记录，再点一下翻页，抄下 URL、请求体和头，然后同源 fetch 自己翻页。很多站对 pageSize 有上限（10、12、20），超了返回空或报错，先用页面自己的值试。
2. **接口拿不到时读页面**：
   - 返回体加密的（滴滴、智源、通研院这类 Moka 系统）：把列表 URL 的 `pageSize` 调大（`#/jobs?page=1&pageSize=50`）直接读卡片文字，点标题拿岗位页地址。
   - 请求带签名的（中国移动 `digest`）：翻页收 `a[href*=detail.html]` 拿编号，详情用同源隐藏 iframe 加载岗位页、读 `contentDocument.body.innerText`（先压缩空白再截取）。
   - 点标题不跳转的（国聘系）：岗位页格式按备注里写的直接拼。
3. **wecruit 系统**（之江、鹏城）：`POST /wecruit/positionInfo/listPosition/<SU套件号>`，form `isFrompb=true&recruitType=1&pageSize=12&currentPage=N`；详情 `POST /wecruit/positionInfo/listPositionDetail/<SU>` body `postId=<id>`；`recruitType=2` 是社招，助理研究员和工程师常挂在这里。
4. 用户是博士的话：大厂博士专项（腾讯青云、阿里星/T-Star、蚂蚁星、美团北斗、京东 TGT、快手快Star、小红书 REDstar、百度 AIDU、讯飞星火X、移动金种子）按课题招人，先读这些。毕业时间窗口从官网项目说明抄进 `硬门槛`。

**腾讯校招**（join.qq.com）
- 列表：`POST /api/v1/position/searchPosition?timestamp=<毫秒>`，body `{"projectIdList":[],"projectMappingIdList":[],"keyword":"","bgList":[],"workCountryType":0,"workCityList":[],"recruitCityList":[],"positionFidList":[],"pageIndex":1,"pageSize":100}`，翻到不足 100 条。只看 `projectName` 为「应届毕业生」且 `positionFamily` 为 2（技术），以及「青云计划-应届生」全部。
- 正文：`GET /api/v1/jobDetails/getJobDetailsByPostId?timestamp=<毫秒>&postId=<postId>`；普通岗看 `desc`、`request`，青云课题看 `topicDetail`、`topicRequirement`。少数返回 null，跳过并在摘要里报。
- 毕业窗口：`GET /api/v1/position/getProjectMapping` 的 `recruitRangDesc`。岗位页 `https://join.qq.com/post_detail.html?postid=<postId>`；青云记 `人才计划`；单位写「腾讯（部门（BG））」。

**字节跳动校招**（jobs.bytedance.com）
- 先 navigate 到 `/campus/position`，再同源 fetch `POST /api/v1/search/job/posts?keyword=<词>&limit=100&offset=<n>&portal_type=3&portal_entrance=1`，头带 `x-csrf-token`（cookie `atsx-csrf-token` 解码）、`portal-channel: campus`、`portal-platform: pc`、`website-path: campus`，不用 `_signature`。
- 关键词模糊匹配，用 `job_profile.md`「国内岗」的搜索关键词，加上项目名 Top Seed；合并去重后按正式/实习分。ByteIntern 可收（招聘类型 `实习`）。岗位页 `/campus/position/<id>/detail`。

**阿里巴巴**：2027 届在 campus-talent.alibaba.com（旧站 talent.alibaba.com、careers.aliyun.com 显示 0），`_csrf` 从页面资源请求里取；列表直接带 description、requirement。阿里星系列（T-Star、A Star、Bravo Star、C-Star）在标题里标着。

## 第二层 · 站内搜索

**国聘**（iguopin.com，内置浏览器）：接口见 `cn_sites.md`「国聘」。关键词用 `job_profile.md`「国内岗」的搜索关键词；按校招筛（nature）。单位自己的校招官网托管在国聘上的（联通），那是单位自己的招聘系统，记 `官网JD`，来源渠道写 `国聘`；其余国聘帖记 `聚合站`。

**Boss直聘**（Chrome，已登录）
- 列表：在 zhipin.com 搜索页同源 fetch `/wapi/zpgeek/search/joblist.json?scene=1&query=<词>&city=100010000&degree=205&page=<n>&pageSize=30`。**连调四五次就返回 code 37**，每次间隔 4 秒以上，一轮控制在四个词以内；被拦就 navigate 一次搜索页再接着。
- 列表马上存进 `localStorage`（navigate 后页面变量会丢）。和 `rows.json` 里已有的 `boss:` 编号比对，只看新的。
- 搜索结果大半是推荐流噪声（出版、医药、运营），按标题和发帖身份先筛，只读方向相关的。
- 正文逐个 navigate 到 `https://www.zhipin.com/job_detail/<encryptJobId>.html`，等 3 秒，取 `.name h1`、`.salary`、`.job-banner p`、`.boss-info-attr`、`.job-sec-text`。Chrome 扩展单次返回约 1,500 字符，用 `browser_batch` 一次排两到四个岗。
- 关键词用 `job_profile.md`「国内岗」的搜索关键词，一轮四个，轮换着搜。大厂官网已经覆盖的方向，Boss 上只做补漏。
- 猎头帖（「客户公司：……」、发帖人「猎头顾问」）单位写「X（猎头代招）」，封顶 Mid。大厂或外企招聘经理自己发的帖，去该公司官网找同一岗，找到就用官网链接入表。年龄打码「****」的在 `硬门槛` 标⚠️。

**高校人才网**（gaoxiaojob.com）：以教职和博士后公告为主；补科研院所研究岗时按用户的学科筛选读。

**猎聘**（Chrome）：搜索框输入再回车（URL 参数不生效），社招和猎头帖为主，只补漏。

**牛客**（内置浏览器）：本硕批量校招为主，暂不作主力。

## 判重、定档、写表

1. 每条先在 `rows.json` 里查：岗位ID、链接里的编号、岗位名+单位。已在国内岗位表或已排除表的跳过。官网找到了表里 Boss 帖的同一岗：加官网行，`remove` 掉 Boss 行（跨渠道合并）。
2. 标题就能判掉的写 `exclude`，类别用脚本里的词表，理由写标题依据。`job_profile.md` 写了不收的类别（比如博士后、教职）同样写进已排除表：教职的类别写 `教职`，没有对应类别的写 `其他`。
3. 其余读 JD 全文，按 `job_profile.md` 的「打分」写复述、打三个分、降档封顶，备注用那里的格式；「国内岗」里的调整照做。复述里写清和用户哪个项目或哪篇论文对得上（以 facts.md 为准，不凭印象）。
4. 硬门槛对照 facts.md：年龄按公告写的计算基准日对照出生日期；校招岗写了毕业时间范围的，对照用户的毕业时间。不满足的 `exclude`（类别 `硬门槛`，抄原句）；没写基准日或被打码的入表并标⚠️。写「重点院校」「统招」「CET-6」等可能卡人的要求，在备注标⚠️。
5. 截止日写进 `截止日期` 列；**3 天内截止的 High 当场用 SendUserMessage 告诉用户**，不等跑完。
6. 写 changes，先备份再 apply：
   ```bash
   cp "$HOME/mnt/jobs/job_tracker.xlsx" ~/work/backup.xlsx
   cd "$HOME/mnt/jobs" && python3 tools/tracker.py apply job_tracker.xlsx --changes ~/work/cn_changes_a.json --today YYYY-MM-DD
   ```
   国内线 `run.mode` 一律 `update`。`row` 的键和国内岗位表头一字不差；国内表没有 `地点`、`级别`、`工作模式`、`签证/居留`。已排除表的 `地点` 写城市。改 tracker.py 直接在用户电脑上改，先在表副本上跑通。
7. 每跑完两三个来源就 apply 一次，再重新 export `rows.json`。

## 运行摘要（中文）

先说最该动手的 1–3 个岗（`官网JD` 里挑，截止近的在前）和一句理由，再报：各来源读了多少、新入表多少（按单位性质、招聘类型、优先级分）、新排除多少；硬门槛⚠️几条；打不开或被拦的站；要用户登录的站（一张清单）；下一轮要摸的站。截止日期提醒写进 Google 日历（经用户同意）。

## 边界

- 只入表，不投递、不在 Boss/猎聘上沟通、不填表、不注册。
- 规则要变先和用户商量；国内公司表可以增删改。
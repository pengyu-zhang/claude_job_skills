---
name: job-search
description: "找岗并维护求职表（按常驻荷兰写）：复核表里的岗，扫公司招聘页、AcademicTransfer、Indeed、LinkedIn 等站，读 JD、打分，用 tracker.py 写进求职表。用户说找工作、更新求职表、复核求职表，或报告投递、面试、拒信结果时用。"
---

# job-search · 找岗与管道维护流水线

终点是更新求职表。不做匹配评估、不写材料、不填表、不发邮件，也不读邮箱：用户投了岗、收到回复，会自己在对话里说。全程中文。

本 skill 是按常驻荷兰写的：站点（AcademicTransfer、nl.indeed.com）、搜索里的地点参数、远程岗能不能收的判法，都以荷兰为准。住在别的国家，把这些换成当地的站点和参数，流程不变。

## 规则源与文件

- **用户的要求在 `profile/job_profile.md`**（jobs 文件夹里；放进 Claude Project 的项目文件也行，文件名相同）：收什么岗、语言门槛、方向和岗位分类、打分、降档封顶、同档排序、备注格式、搜索关键词、账号表。运行开始先读，读不到就停下告诉用户，不凭记忆打分。用户的项目、论文和没用过、没做过的东西在 `profile/facts.md`。打分的阈值和条件这里不抄。
- **jobs 文件夹里有这些**：`job_tracker.xlsx`（求职表）、`tools/tracker.py`（唯一写表与判重工具；命令、changes.json 的结构、各列怎么填都在脚本开头的说明里，运行开始读一遍：`sed -n '1,/^import argparse/p' tools/tracker.py`）、`profile/`、CV 母版、`applications/`。
- **脚本在用户电脑上直接跑**：云端会话用设备端 shell（`device_bash`），先 `ls $HOME/mnt/` 看挂载名；下文路径写 `$HOME/mnt/jobs`（把 jobs 文件夹直接连给会话时的位置），连的是它的上级文件夹就在后面补上子路径。本地会话（如 Claude Code）直接在 jobs 文件夹下跑。不把 Excel 上传到云端再传回（写回经常报成功却没落盘）。能访问 jobs 文件夹的 shell 都没有时，停下告诉用户。
- **本 skill 需要改时**：起草完整的新 SKILL.md 交给用户保存；脚本要改就直接改 `tools/` 里的文件。不建错误记录或说明文件。

## 每一步都做满，打不开的站先换浏览器

默认时间和 token 都充足，可以等。用户另有交代的按用户说的。

- 这里写到的每个来源、每个关键词、每一页、每家公司都做满，没有配额。没写死的地方按多做：没规定搜几个词就用列出的全部，没规定翻几页就翻到见底。想改范围先停下问用户，用户同意了再改。
- **网站打不开时**（导航失败、页面报错、一直白屏、读不出内容、被人机验证挡住且「先跑别的站、回头再开」也不行）：内置浏览器再试一次；还不行就**直接换用户本地的 Chrome 扩展打开，不用先停下等用户发话**。Chrome 也打不开，才停这一站，接着把其余步骤全部做完，在摘要「打不开的站」里写清站名、网址、两个浏览器各自的现象。不改用转述工具之类的办法绕过，也不把打不开写成「没有新岗」。
- **要登录或要人过验证时停下来叫用户**：登录态过期、人机验证要人点、站点要求登录才能看。说清是哪个站、在哪个浏览器的哪个标签页、要用户做什么；用户弄好说一声就接着跑。等用户的时候先跑别的站。账号在 `job_profile.md` 的账号表；助理只填用户名，密码用户自己输。
- **被限速不算打不开**：LinkedIn 429 就停下等几分钟再接着跑，直到跑完；不因为限速就少跑页。
- **读到的每一条都要有去处**：站内搜索、公司表直扫、推荐流里关键词命中的每一条，最后要么已在岗位表、要么已在已排除表、要么本轮入表、要么本轮写进已排除表。Euraxess 的 AT 镜像（AT 号已在表或已排除的除外）、远程板上按地域规则不收的岗、PhD 与教职也都要写进已排除表并写理由。
- **找到官网链接就当轮读官网全文、重新复述打分、升核验**，不留到下一轮，不允许只补链接不读正文。
- **用子任务并行扫站时**，子任务必须带回每个新岗的完整 JD 正文（职责、要求、地点、语言、年限、截止，不截断），复述和打分由主会话按全文做；子任务只确认「页面还在」的，不能据此升核验。

## 核心原则：一轮做完，别留半成品

一个岗停在只读过 LinkedIn/Indeed 帖的状态（`聚合站`），就会被封顶规则一直压在 Mid。所以目标是：**每个进表的岗，当轮就核验到雇主官网 JD；做不到的，写清为什么。**

先看标题能不能直接判掉：

- **标题就能判掉**：只限 `job_profile.md`「收什么岗」里写明不收、而且标题写得明明白白的（比如不收 PhD 岗的人看到 PhD position，不收管理岗的人看到 Head of/Director/VP）。不入岗位表，写进已排除表（changes.json 的 `exclude`），摘要里分类报数，不开官网页。标题模糊的（"Research Engineer""Scientist""AI Engineer""Intern"）不算。培训生项目（traineeship、graduate、early career、young professional program）不凭标题判，照常读 JD 打分。
- **标题判不了**：剩下全部。打开之前手里没有优先级，只有猜测（标题写 Machine Learning 的可能是网络安全岗；JD 不出现研究方向词的 DS 岗读完可能是推荐与排序）。按渠道成本决定当场开还是排队：

| 渠道 | 拿 JD 全文的成本 | 做法 |
|---|---|---|
| AcademicTransfer、Euraxess、jobs.ac.uk、academicpositions | 同源 fetch，一次调用 5–6 个详情页 | **当场核验**。AT 岗位页等同官网页，直接写 `官网JD`；其他三站只算 `聚合站`，要跟到大学官网页才算 `官网JD` |
| Greenhouse / Lever / Ashby / Workable / SmartRecruiters / Workday / Recruitee | 一次 API 调用返回整家公司在招岗 | **当场核验**，写 `官网JD` |
| LinkedIn / Indeed / 远程板，且公司有 ATS 端点 | 从 ATS 侧按标题匹配 | **当场核验**；顺手把官网链接换成 ATS 岗位页 |
| LinkedIn / Indeed / 远程板，公司自建站或无端点 | 贵的是找到官网页 | **当轮去公司招聘站按标题找官网页并读全文**（LinkedIn 登录态 `companyApplyUrl`、Indeed 外链都先试）；确实找不到（雇主匿名、公司没有招聘页；Jobgether 代发帖先按下文「Jobgether 代发帖查真雇主」查）才入表 `聚合站`，备注写试过什么 |

**一次 `javascript_tool` 调用最多跑 45 秒。** 只读五六个页面可以直接 await；页面多的（翻几十页、读几百条正文）用后台循环：

```js
window.__x={};window.__log=[];
window.__run=(async()=>{for(const u of 待读列表){/* fetch、解析、存进 window.__x、按站点间隔停顿 */window.__log.push(u)}return 'done'})();
'started'
```

这次调用立刻返回，之后每次调用先 `await new Promise(r=>setTimeout(r,20000))`（一次最多等 40 秒）再读 `window.__log` 和结果，直到跑完。超时不是代码错，拆小重跑；已取到的结果存在 `window` 变量里的可以接着读。

- **跑循环的标签页不能 navigate**：页面一跳转 `window` 变量全丢、循环中断。别的站另开标签页（`tabs_create`）做；跨页用的辅助函数要重新定义。
- 后台标签页的计时器会被浏览器节流，进度明显变慢时用 `tabs_select` 把这个标签页切到前台。
- 抓完一批先把列表写进设备端 `~/work/` 的文件，再判（见步骤 5「边做边写」）。

## 运行前

1. 确认能访问 jobs 文件夹（没有就申请访问）。
2. 提醒用户关闭正在打开该 Excel 的程序（Excel 开着会写入失败）。
3. 浏览器：**内置浏览器优先**（`Claude_Browser` 系列：`navigate` 开页、`javascript_tool` 跑 JS——参数名 `action: "javascript_exec"` + `text`，传错会静默返回 undefined——`get_page_text` 读正文；登录态跨会话保留）。Chrome 扩展备用：内置浏览器打不开或读不出的页面直接换 Chrome，要登录时停下叫用户（见上方硬规矩）。标签页中途失效就重新取上下文继续，不算错误。开两三个标签页分工：LinkedIn 一个（登录态、跑长循环），学术站一个，ATS 接口和杂项一个，互不 navigate 对方的页。

## 步骤 0 · 读状态

```bash
mkdir -p ~/work && cd "$HOME/mnt/jobs" && python3 tools/tracker.py info job_tracker.xlsx --today YYYY-MM-DD > ~/work/info.json && python3 tools/tracker.py export job_tracker.xlsx --out ~/work/rows.json
```
`--today` 用用户所在时区的当天日期，以会话里给的时间为准，不用云端容器的 `date`（可能滞后几天）。`info` 输出很长，存文件后用 python 取需要的键：上次运行时间（增量锚点）、两个岗位 sheet 的行数与分布、已知岗位ID 和"岗位名 @ 单位"集合、`stale`（最后核验超过 14 天或未核验的 High/Mid 未投活岗）、`missing_official`（核验=官网JD 但官网链接为空的未投活岗）、公司表家数、`excluded`（已排除表行数与类别分布）。`rows.json` 是全表导出（含 `已排除`），**判重时按 jk、LinkedIn id、ATS 号在整行 JSON 里搜**：岗位ID 只是一个键，同一岗的 ATS 链接常存在别的行的官网链接列或备注里。

**本轮复核队列由两份合成**：`stale` 全部处理；另加**欠账清单**——`核验` 不是 `官网JD` 的 High/Mid 未投活岗，`info` 不输出，自己筛：

```bash
cd "$HOME/mnt/jobs" && python3 -c "
import openpyxl
wb=openpyxl.load_workbook('job_tracker.xlsx')
for sn in ['学术岗位','工业岗位']:
    ws=wb[sn]; h=[c.value for c in ws[1]]; i={k:n for n,k in enumerate(h)}
    for r in ws.iter_rows(min_row=2,values_only=True):
        if r[i['状态']]=='未投' and r[i['优先级']] in ('High','Mid') and r[i['核验']]!='官网JD':
            print(sn,'|',r[i['岗位ID']],'|',str(r[i['岗位名称']])[:44],'|',r[i['单位']],'|',r[i['优先级']],r[i['核验']])
"
```
欠账清单每轮全部消化（High 在前）。雇主匿名的猎头帖永远核不到官网，每轮只确认帖子还在不在。

**Jobgether 代发帖不按匿名处理**：Jobgether 在 LinkedIn 和它自己的 Lever 上挂的「代招」帖，原岗都是别家公司的公开岗，查得到真雇主（做法见步骤 2 后的「Jobgether 代发帖查真雇主」）。查到后按普通岗走：单位改真雇主，官网链接换成雇主岗位页，读全文、升 `官网JD`、重新复述打分，再按地域规则判收不收；表里已有真雇主同岗行的，合并（`remove` 代发行，留痕写进保留行备注）。Jobgether 的 Lever 页 404 不等于原岗下线，以雇主岗位页为准。

## 步骤 1 · 复核队列（先于找新岗）

两份清单合起来，按 High 在前、最旧在前，逐个落到**雇主官网或其 ATS 岗位页**（学术岗的 AT 岗位页等同官网页）：

- 仍在招：`verified:true`，核验升为 `官网JD`，顺手补 `级别`、`工作模式`、`所需材料`、`官网链接`，标题变了改岗位名并备注留痕。**核验后按 JD 全文重新打分**，升档降档都写依据。
- 已下线 / 404 / 跳回职位总页 / 官网在招列表里没有 / 页面还能打开但正文写 "no longer active"：改 `关闭`，备注一句依据；高匹配的加 "Lead only：恢复在招后再投"。雇主没有官网招聘页的，聚合站显示「Deze vacature is verlopen」也可作关闭依据，备注写明。
- 官网页发现当地语言的硬要求超过 `job_profile.md` 写的门槛：改 `关闭`，备注"语言超门槛"。
- 官网页发现是荷兰境外岗：按地域规则判——不是远程或要求住在别国的改 `关闭`；雇主在欧盟/英国之外的先做「雇主所在地核查」，不满足例外的改 `关闭`；可收的远程岗填 `工作模式=远程`，**不降档**。
- 确实找不到官网页：核验保持 `聚合站`，备注写"仅聚合站核验：<试过什么>"。

**读 JD 正文和开雇主官网页是两件事**：读正文是必做项（LinkedIn guest 接口、Indeed viewjob 一次调用读十个左右）；开雇主官网页没有上限：stale、欠账、本轮贵渠道新岗的官网页全部要开，只是按 stale 的 High > 欠账的 High > 本轮贵渠道新岗 > stale/欠账的 Mid > Low 的顺序做。

## 步骤 2 · 主动搜索（三层，每轮全跑）

### 第一层 · 公司表直扫（与步骤 1 合并跑）

```bash
cd "$HOME/mnt/jobs" && python3 tools/tracker.py companies job_tracker.xlsx
```
挨个打开每家的网址，按 `job_profile.md`「搜索关键词」里的标题初筛词初筛，再读 JD，按 `job_profile.md` 的收录范围和打分标准判。备注列写了读法的照做。同时复核：表内该公司的岗不在在招列表里 = 已下线，改 `关闭`；反过来列表里有不等于在招，定档前开岗位页本身。**表里已 `关闭` 的岗重新出现在 ATS 列表、且岗位页可读，恢复 `未投`**，备注写重新出现的日期。

按网址类型读（同一类 ATS 一次调用扫完全部板）：

| 网址形态 | 读法 | 岗位ID |
|---|---|---|
| `job-boards[.eu].greenhouse.io/<board>` | `https://boards-api.greenhouse.io/v1/boards/<board>/jobs`（EU 板也用这个主机）；单岗正文 `/jobs/<id>`；板名猜错时返回 0 个岗而不报错 | `gh:` |
| `jobs[.eu].lever.co/<co>` | `https://api[.eu].lever.co/v0/postings/<co>?mode=json`；单岗 `/v0/postings/<co>/<id>`（404 即下线）；列表为空不等于岗位下线，旧岗位页可能仍开放 | `lever:` |
| `jobs.ashbyhq.com/<org>` | `https://api.ashbyhq.com/posting-api/job-board/<org>`；`secondaryLocations` 列出全部可选办公地，`isRemote` 单独一个字段，正文在 `descriptionPlain`；接口只返回公开挂出的岗，不挂在板上的岗位页仍可能开放，直接开岗位页确认。按板名缓存结果用 `Map`，不用普通对象（板名叫 `constructor` 这类的，会和对象自带的属性重名） | `ashby:` |
| `apply.workable.com/<co>` | 在 apply.workable.com 上同源 `POST /api/v3/accounts/<co>/jobs`（body `{}`，有 `nextPage` 就带上翻页）列岗；`GET /api/v2/accounts/<co>/jobs/<shortcode>` 读正文（`description`、`requirements`，地点看 `location`、`locations`、`remote`、`workplace`）；岗位页 `apply.workable.com/<co>/j/<shortcode>/` | 短名 |
| `jobs.smartrecruiters.com/<Co>/<id>-…` | `https://api.smartrecruiters.com/v1/companies/<Co>/postings?limit=100&offset=<n>`（`totalFound` 看总数）列岗；`/postings/<id>` 读正文，正文在 `jobAd.sections` 的 `jobDescription`、`qualifications`、`additionalInformation`，`location.remote`/`hybrid` 看工作方式。这个接口允许跨域，在任意页面上 fetch 都行 | 短名 |
| `careers-<co>.icims.com/jobs/<id>/…` | `navigate` 到岗位页并在网址末尾加 `?in_iframe=1`，正文在页内同源 iframe 里：`document.querySelector('iframe').contentDocument.body.innerText` | `icims:` |
| `<tenant>.wdN.myworkdayjobs.com/<site>` | `POST /wday/cxs/<tenant>/<site>/jobs`，body `{"limit":20,"offset":0,"searchText":"<关键词>","appliedFacets":{}}`；详情 `GET /wday/cxs/<tenant>/<site>/job/<externalPath>`（404 即下线，`jobPostingInfo.additionalLocations` 看多国帖的真实派驻地）。列表的 "N Locations" 要开详情才知道含不含荷兰。岗位页用 WebFetch 只回空壳 | `wd:` |
| `<slug>.recruitee.com` 或自定义域 Recruitee | `/api/offers/` 一次返回全部岗位含正文；一个 Recruitee 主机下可以接着 fetch 别的租户 | 短名 |
| SAP SuccessFactors 招聘站（careers.tudelft.nl、vacatures.knaw.nl 等） | 老式站点服务端渲染，`/search/?q=&startrow=N` 翻页读表格（每页条数各站不同，TU Delft 每页 20 条）；新式站点（如 KNAW）列表靠前端调 `POST /services/recruiting/v1/jobs` 渲染，`navigate` 到列表页后 `get_page_text` 读全部 | 短名 |
| 其他（自建站、Teamtailor、Eightfold、Phenom） | 内置浏览器打开网址，等渲染，有 Load more 点到底，抓岗位链接；列表是前端渲染时用 `read_network_requests` 找页面调用的 JSON 接口；正文不在 body 里时找页面 JSON-LD 的 `description` 字段 | 按脚本派生 |

- **云端容器直连这些 API 会被代理拒绝；从别的站跨域 fetch 通不通看那个页面的 CSP**（在 jobgether.com 上 fetch Greenhouse、Ashby、Lever 接口可以，在 Ashby 岗位页上会被拦）：被拦就在内置浏览器 `navigate` 到 API 主机本身（boards-api.greenhouse.io、api.eu.lever.co、api.lever.co、api.ashbyhq.com、`<tenant>.myworkdayjobs.com`），再同源 fetch 或 `JSON.parse(document.body.innerText)`；同一 API 主机下别的板可以接着 fetch。
- 远程岗看 location 字段：Greenhouse 常写 "Remote - EMEA"；Lever 看 `categories.location` 与 `workplaceType`；Ashby 看 `isRemote`。多国并列的帖以岗位页正文为准。
- Greenhouse 板名不一定是公司名：开一个岗位页，看 iframe/script 里 `for=<板名>` 参数；嵌在公司站里的，URL 里的 `gh_jid`/`jid` 就是 Greenhouse id。
- 新发现有相关岗的公司，在 changes.json 的 `companies.add` 里加一行（公司、网址，必要时一句备注）；确认网址变了或摸清了读法用 `companies.update`；长期无可收岗位的用 `companies.remove`。备注里写着"网址待核"的，这轮核实后改掉。

### 第二层 · 站内搜索（内置浏览器，同源 fetch 批量）

先 `navigate` 到目标站任一页，再在 `javascript_tool` 里 `await fetch(路径,{credentials:'same-origin'})` 拿 HTML 解析；关键词和页数多的用「核心原则」里的后台循环跑完。

**前端渲染的站**（academicpositions、ResearchGate）fetch 回来的 HTML 里没有岗位列表。不要逐页 navigate（每跳一次变量全丢），在该站任一页上用隐藏 iframe 加载搜索页、等渲染完再读 DOM：

```js
window.__ifr=(url,sel,emptyRe,pick)=>new Promise(res=>{const f=document.createElement('iframe');
 f.style.cssText='position:absolute;left:-5000px;width:1200px;height:2000px';f.src=url;document.body.appendChild(f);
 let t=0;const iv=setInterval(()=>{t++;let d=null;try{d=f.contentDocument}catch(e){}
  const n=d?d.querySelectorAll(sel).length:0;const empty=!!d&&!!d.body&&emptyRe.test(d.body.innerText);
  if(((n>0||empty)&&t>=4)||t>=20){clearInterval(iv);let r;try{r=pick(d)}catch(e){r={err:String(e)}}f.remove();res(r)}},500)});
```

`sel` 是岗位链接的选择器，`emptyRe` 匹配「没有结果」的页面文字，`pick(d)` 从 iframe 的 document 里取出岗位与总数。至少等 2 秒（`t>=4`）让列表渲染完整，最多等 10 秒。各站的 `sel` 和取法写在下面各站里。

**AcademicTransfer**：`https://www.academictransfer.com/en/jobs/?q=<词>&vacancy_type=all`。**必须带 `vacancy_type=all`**：搜索页默认只显示「Academic jobs」栏（等于 `vacancy_type=scientific`），大学和研究所招的 research software engineer、软件开发、AI 平台、数据管理这类岗放在「Non-academic jobs」栏（`non_scientific`），不带参数就一条都看不到（research software engineer 一个词，学术栏近两百条，非学术栏另有二十多条）。非学术栏也带出不少行政、技术支持岗，按标题判掉写进已排除表（非对口岗）。**每个关键词都要读完全部结果，不只前 10 条**：页面一次只显示 10 条，底部按钮「Load more results」写着「10 of N visible」，点到按钮消失才是全部（热门词一个就有几十条）。fetch 拿到的 HTML 只有前 10 条，page 参数无效，API 要登录令牌，所以在 AT 任一页上用隐藏 iframe 打开搜索页、在 iframe 里反复点按钮：

```js
window.__atAll=q=>new Promise(res=>{const f=document.createElement('iframe');
 f.style.cssText='position:absolute;left:-5000px;width:1200px;height:2000px';
 f.src='/en/jobs/?q='+encodeURIComponent(q)+'&vacancy_type=all';document.body.appendChild(f);
 let t=0,gone=0;const iv=setInterval(()=>{t++;let d=null;try{d=f.contentDocument}catch(e){}
  if(t<4||!d||!d.body){if(t<40)return}
  const btn=d&&d.body&&[...d.querySelectorAll('button')].find(b=>/Load more results/i.test(b.textContent));
  if(btn){gone=0;btn.click()}else gone++;
  if(gone<3&&t<120)return;
  clearInterval(iv);const s=new Map();
  (d?[...d.querySelectorAll('a[href*="/en/jobs/"]')]:[]).forEach(a=>{const m=a.getAttribute('href').match(/\/en\/jobs\/(\d{5,7})\//);
   if(m&&!s.has(m[1])){let el=a,txt='';for(let i=0;i<5&&el;i++){el=el.parentElement;if(el&&el.innerText&&el.innerText.trim().length>20){txt=el.innerText.replace(/\s+/g,' ').trim();break}}s.set(m[1],txt.slice(0,95))}});
  f.remove();res([...s].map(([id,x])=>id+'::'+x))},500)});
```

返回 `编号::标题与简介`。按钮连续三次不在才算点完，最多点 60 秒；没有结果的词约 2 秒返回空。AT 的搜索是模糊匹配，一个词常带出几十上百条不相干的，按 `job_profile.md` 的收录范围凭标题判掉、写进已排除表；多个词的结果先按编号去重再判。

关键词（每轮全搜）：`job_profile.md`「搜索关键词」的学术站长清单。

详情页 fetch 后用 DOMParser 取 `main` 的 textContent，从 `Deadline` 附近切到 `Employer information` 就是正文。过期岗位正文会出现 `(the deadline was <日期>)`，这是最可靠的死活信号。拿官网链接：岗位页的 Apply 是 POST 表单（fetch 被 CORS 挡），可在岗位页上跑 `const f=[...document.querySelectorAll('form')].find(x=>x.method.toLowerCase()==='post'&&x.target==='_blank'); f.target='_self'; f.submit();`，跳过去后读 `location.href` 填 `官网链接`，再 navigate 回 AT。这一步可能被权限审核当成提交拦下；被拦就不再试，`官网链接` 直接填 AT 岗位页（脚本只给 warning）或去大学招聘站按标题找。

**AT 不是学术岗的全集。** 研究机构和大学的部分岗只发在自己招聘站和 LinkedIn 上：KNAW 各研究所（走 KNAW 招聘站）、大学图书馆和 IT 部门招的 RSE、data steward、scientific programmer。这些机构对口的就加进公司表，靠公司表直扫和 LinkedIn 学术词兜住，不能因为「AT 上没有」就当作没有。政府研究机构（CBS、KNMI、RIVM、Nationaal Archief 等，走 werkenvoornederland.nl）多数要荷兰语，不单独扫，靠 LinkedIn 兜住（标题常带「De Rijksoverheid zoekt」）。

**Indeed**：`https://nl.indeed.com/jobs?q=<词>&start=0|10|20`（不加地点=全荷兰），**每个关键词三页都要跑**。关键词用 `job_profile.md`「搜索关键词」的工业岗位名。搜索页 HTML 里 `window.mosaic.providerData["mosaic-provider-jobcards"]=` 后面的 JSON 有 `jobkey/title/company/formattedLocation/formattedRelativeTime/sponsored`，正则取出 `JSON.parse` 即可。
- 正文走 `/viewjob?jk=<jk>` 同源 fetch：HTML 里 `"sanitizedJobDescription"`（正则取出 `JSON.parse` 再去标签）、`"jobTitle"`、`"companyName"`、`"formattedLocation"`；出现 `indeedApplyableJobId` = 站内直投，出现 `applystart?jk=` 链接 = 有公司官网外链。读正文时顺手用正则抓语言与年限句（`Nederlands|Dutch|taal`、`\d+\+?\s*(years|jaar)`），当地语言硬要求超门槛的当场排除。**不用 WebFetch 读 Indeed**（会返回别的岗位的正文），也不派子任务读。
- 限速：搜索页和 viewjob 共用额度，fetch 之间隔 2.5–3 秒，一次调用不超过 10 个 viewjob；一轮里搜索页加 viewjob 累计到 30–60 个就可能出 403 验证墙，所以先跑完全部搜索页，再读 viewjob。触发「Additional Verification Required」/Cloudflare 验证墙时等待无效，这是人机验证，不绕：先去跑别的站，回头直接 `navigate` 到 viewjob 页面往往又能读；回头再开也不行，就直接换用户本地 Chrome 接着读（本地 Chrome 通常已过验证）；Chrome 也被挡，就停下请用户在那个标签页手动过一次验证，过了接着读。等用户的时候先跑别的站，alert 里的岗照样从雇主官网核。
- Chrome 扩展的输出过滤器会拦**返回值**里的 16 位十六进制 jk、长数字串、URL、邮箱：把结果存到 `window.__x`，另一次调用只返回清洗过的标题/公司/年限/语言片段；jk 转十进制返回，本地 `'%016x' % int(dec)` 还原；单次返回约 1,500 字符上限，分页输出；页面变量在 navigate 后全丢，要读的 jk 先记在云端。Chrome 下正文在 HTML 内嵌 JSON 的 `"sanitizedJobDescription"` 字段，正则取出后 `JSON.parse` 再去标签。
- 伪造 jk：搜索页混有假 jk，特征是相邻字符在 `0123456789abcdef` 上连续递增或递减，按规律滤：`const H='0123456789abcdef',fake=j=>{let i=1,inc=1,dec=1;for(;i<j.length;i++){const a=H.indexOf(j[i-1]),b=H.indexOf(j[i]);if((a+1)%16!==b)inc=0;if((a+15)%16!==b)dec=0}return inc||dec}`。
- 官网链接：详情页 "Apply on company site"/"Solliciteer op bedrijfswebsite" 的跳转落地页；"Solliciteer via Indeed" 是站内直投，没有官网页。

**LinkedIn**（WebFetch 整站读不了，只走浏览器同源 fetch，不派子任务）：
- 列表：`/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=<词>&location=Netherlands&f_TPR=r<秒数>&start=0|10|20|30|40`。**每页只返回 10 条，start 按 10 递增**（按 25 翻页会漏掉第 10–24 条）。时间窗取「距上次运行天数 + 1」。返回 `<li>` 片段：`jobPosting:(\d+)` 做 id，`base-search-card__title` / `base-search-card__subtitle` / `job-search-card__location` 做标题/单位/地点。
- **linkedin.com 页面上 `DOMParser` 被站点改写了**（解析出来只剩两三个空元素），列表片段和正文页一律用正则拆，不用 DOMParser，也不用 querySelector。
- 正文：`/jobs-guest/jobs/api/jobPosting/<id>`。按下面的正则取字段（`__dec` 负责去标签、把 `<br>`/`</p>`/`</li>` 换成换行、解 HTML 实体）：

  ```js
  window.__dec=s=>s.replace(/<br\s*\/?>/gi,'\n').replace(/<\/(p|li|h\d|div|ul|ol)>/gi,'\n').replace(/<li[^>]*>/gi,'• ').replace(/<[^>]+>/g,'')
   .replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#39;|&#x27;|&apos;/g,"'").replace(/&(nbsp|#160);/g,' ')
   .replace(/&#(\d+);/g,(m,n)=>String.fromCharCode(+n)).replace(/[ \t]+/g,' ').replace(/\n\s*\n+/g,'\n').trim();
  window.__parse=h=>{const g=re=>{const m=h.match(re);return m?window.__dec(m[1]):''};return {
   t:g(/top-card-layout__title[^>]*>([\s\S]*?)<\/h[12]>/), c:g(/topcard__org-name-link[^>]*>([\s\S]*?)<\/a>/),
   l:g(/topcard__flavor--bullet[^>]*>([\s\S]*?)<\/span>/), posted:g(/posted-time-ago__text[^>]*>([\s\S]*?)<\/span>/),
   closed:/No longer accepting applications/i.test(h),
   crit:[...h.matchAll(/description__job-criteria-subheader[^>]*>([\s\S]*?)<\/h3>[\s\S]*?description__job-criteria-text[^>]*>([\s\S]*?)<\/span>/g)].map(m=>window.__dec(m[1])+': '+window.__dec(m[2])).join('; '),
   desc:g(/show-more-less-html__markup[^>]*>([\s\S]*?)<\/div>\s*<button/)||g(/show-more-less-html__markup[^>]*>([\s\S]*?)<\/div>/)}};
  ```
  `closed` 为真（页面写着不再收申请）即已下线。
- **限速**：请求之间停 1.3–1.5 秒，否则整片 429、十几分钟不恢复。一次调用最多读 10 个 id，再多用后台循环。
- 官网外链（登录态，在 linkedin.com 页面上跑）：从 cookie 取 csrf，调 voyager 接口，返回里正则取 `companyApplyUrl`：

  ```js
  const csrf=(document.cookie.match(/JSESSIONID="?([^";]+)/)||[])[1];
  window.__applyUrl=async id=>{const r=await fetch('/voyager/api/jobs/jobPostings/'+id+'?decorationId=com.linkedin.voyager.deco.jobs.web.shared.WebFullJobPosting-65',
   {headers:{'csrf-token':csrf,'accept':'application/json','x-restli-protocol-version':'2.0.0'}});
   const m=(await r.text()).match(/"companyApplyUrl":"([^"]+)"/);return r.status+' '+(m?m[1]:'(none)')};
  ```
  没有 `companyApplyUrl` = 站内申请，没有官网外链。间隔 1.3 秒。外链是 Lever/Greenhouse/Ashby/Workday/SmartRecruiters/Recruitee 时顺手用对应 API 读官网页，升 `官网JD`；外链是 `jobs.lever.co/jobgether/…` 的，按「Jobgether 代发帖查真雇主」查。
- 关键词每个翻 5 页（start=0/10/20/30/40），分两组：
  - 工业组：`job_profile.md`「搜索关键词」的 LinkedIn 工业组。
  - 学术组：`job_profile.md`「搜索关键词」的 LinkedIn 学术组。只发在研究所自己招聘站和 LinkedIn 上、不发 AT 的学术岗，主要靠这一组找到。postdoc 这类宽词会带出大量别的学科的岗，按标题判掉写进已排除表（别的学科）。
- 远程一轮：同一接口加 `&f_WT=2`，`location=European%20Union`，英国另跑 `location=United%20Kingdom&f_WT=2`，用上面的工业组关键词（学术组只搜荷兰），欧盟、英国各翻 5 页。筛出来的岗大多写具体城市，"Remote" 只代表勾了远程，**只按 JD 正文判**：写 EU/EMEA/Europe/worldwide remote、国家列表含荷兰、或未限定国家的才收；雇主在欧盟和英国之外的（美国远程公司、离岸公司）先做下面「雇主所在地核查」，不满足的不收。

**Euraxess**：`/jobs/search?f%5B0%5D=job_country%3A798&f%5B1%5D=keywords%3A<词>&page=<n>`（`?keywords=` 参数无效；`page` 从 0 开始，每页 10 条；`job_country%3A798` 是荷兰），关键词用 `job_profile.md`「搜索关键词」的学术站短清单，每个翻到结果见底（某页一条都没有就是到底了）。同源 fetch 后用 DOMParser 解析：每条是 `article.ecl-content-item`，标题与链接在 `h3 a[href*="/jobs/"]`（`/jobs/<数字>` 是编号），单位和发布日期在 `.ecl-content-block__primary-meta-item`。页面标题变成「Sorry」、正文是多语言的「服务器暂时不可用」时，是 Euraxess 临时故障：先跑别的站，过几分钟回来重跑；回来还不行才按「打不开的站」处理。荷兰岗多是 AT 镜像，主要价值是补漏：镜像岗按 AT 号查表，不在表的照常读正文、落到岗位表或已排除表；非镜像的岗回 AT 或大学站读正文。

**jobs.ac.uk**：`https://www.jobs.ac.uk/search/?keywords=<词>&sortOrder=1&pageSize=25&startIndex=1|26|51|…`。**每页最多 25 条**：`pageSize` 写更大也只回 25 条，`startIndex` 却会按你写的步长跳，中间的就漏了。总数在页面「N JOBS FOUND」，每条是 `.j-search-result__result`，链接 `a[href*="/job/"]`，路径第二段是编号。关键词用学术站短清单，每个翻到结果见底；只收明确写 remote 且允许英国以外居住的，其余写进已排除表（境外非远程）。

**academicpositions**：前端渲染，用上面的 iframe 加载器，在 academicpositions.com 任一页上跑。荷兰：`/find-jobs?search=<词>&page=<n>&locations[0]=netherlands`；远程：`/find-jobs?search=<词>&page=<n>&remote=only`。每页 10 条，总数在页面「N JOBS」；`sel` 用 `a[href*="/ad/"]`，链接形如 `/ad/<单位>/<年份>/<岗位短名>/<编号>`，`emptyRe` 用 `/no results\./i`。关键词同 jobs.ac.uk 这一组；只收 Netherlands 或 remote。直接打开搜索页会先弹地区选择框，iframe 带参数加载不受影响。

**远程板**（来源渠道写 `远程板`）：WeWorkRemotely `weworkremotely.com/remote-jobs/search?term=<词>`（关键词用工业岗位名）；RemoteOK `remoteok.com/api`（JSON，全量过一遍）；aijobs.net（已跳转 foorilla.com）。foorilla 列表页是全球近 60 天的数据与 AI 岗，上万条，`?q=` 搜索参数无效；地区筛选在页面「Regions»」抽屉里（htmx 加载，`countries` 下拉边打字边加载选项），页面上的「Export JSON」链接不登录时只返回首页。在内置浏览器里打开抽屉，选 Netherlands（再单独开 remote_only）后读筛选后的列表；筛不出来就按「打不开的站」写清现象，等用户指示。基本是美国雇主或限定国家：允许从荷兰工作、且雇主在欧盟/英国、或通过「雇主所在地核查」的才收；关键词命中但不收的写进已排除表（理由写雇主所在地、核查结果或限定国家）。

### 第三层 · 推荐流

- LinkedIn 登录态 `fetch('/jobs/collections/recommended/',{credentials:'include'})`：页面只渲染前几张卡，HTML 里用正则 `urn:li:fsd_jobPosting:(\d+)` 取全部 id（`data-occludable-job-id` 已经取不到），去重后走 guest 接口读正文。
- ResearchGate Jobs：前端渲染，用 iframe 加载器，在 researchgate.net 任一页上跑 `/jobs/Research-jobs-in-Netherlands?query=<词>&page=<n>`。每页 20 条，总数在页面「N Research jobs」。**岗位链接是相对路径 `job/<编号>_<短名>`**，`sel` 要写 `a[href^="job/"]`（写 `a[href*="/job/"]` 一条都匹配不到）；同一岗有几个链接，按编号去重、取有文字的那个；完整网址是 `https://www.researchgate.net/job/<编号>_<短名>`。`emptyRe` 用 `/\b0 Research jobs|No jobs/i`。关键词用学术站短清单，每个翻到结果见底。

推荐流的岗照样要跟到官网页才算核验。

### 链接

链接一律从 DOM 直抓或从 API 取，不用网页转述工具的二次总结（会错配标题与编号且看不出异常）。**两个链接列**：`链接` 填发现页，`官网链接` 填雇主官网或其 ATS 岗位页；ATS 直扫的岗两列相同；拿不到留空。两列都只放岗位级页面，搜索结果页、board 首页脚本会拒收。公司官网链接寿命短，改版后常 404 或跳总页，还可能指向别国岗位。

### 雇主所在地核查（荷兰境外远程岗）

雇主在欧盟和英国之外的不收，例外是能证明它在荷兰雇人。雇主总部看起来在欧盟/英国之外（美国、加拿大、亚洲公司，离岸注册）时，定档前做这一步，下面任一成立就按例外收：

1. **招聘板上有荷兰地点**：用上面的 ATS 接口拉这家全部在招岗，看地点字段——Greenhouse `location.name`，Ashby `location` 与 `secondaryLocations`，Lever `categories.location` 与 `categories.allLocations`，Workday 详情的 `additionalLocations`。出现 Netherlands、荷兰城市名或 `Remote - Netherlands` 即成立，不要求是本岗。
2. **荷兰有办公室**：公司官网的 offices、contact、about 页，或 LinkedIn 公司页的地点列表里有荷兰城市。收购了荷兰公司、被收购方还在荷兰运营的，也按这一条算（备注写收购对象）。

公司招聘站有「可雇佣国家」列表页的（常叫 eligible countries / where we hire），以列表为准：列表里没有荷兰的，上面两条都不用再查，直接不收。

总部所在地查不清时（远程优先的小公司常不写），先看官网 about/contact 页，再看 Built In、Crunchbase 这类公司页。成立的，备注写依据（如「招聘板有 Remote - Netherlands 岗，按例外收」）；都不成立的，新岗写进已排除表、表内的改 `关闭`，理由写「雇主 X 总部在 Y，招聘板无荷兰地点、无荷兰办公室」。只写 Remote (world) / Anywhere 的不算成立。

### Jobgether 代发帖查真雇主

内置浏览器打开 `jobgether.com`（已登录），在该页同源 fetch：

1. `/search-offers?keyword=<岗位名>` 拿 HTML，DOMParser 取 `a[href*="/offer/"]`，按标题匹配候选。标题太泛时把原帖标题的后缀一起搜（如 `Senior AI Engineer (f/m/x)`）。
2. 逐个 fetch 候选的 `/offer/<id>-<slug>` 页：`<script type="application/ld+json">` 里的 `hiringOrganization.name` 是真雇主；HTML 里 `applyUrl&#34;:&#34;…&#34;` 解出来（`&#38;` 换回 `&`，去掉 `utm_source=Jobgether` 起的参数）是雇主自己的投递页。
3. 拿 Jobgether 原帖正文的特征（业务、规模、年限、地点）和雇主岗位页比对，确认是同一岗再改。

同一雇主常把同岗按城市分成几帖（如 London、Zurich、Remote - Europe 各一帖），官网链接取能从荷兰做的那帖，其余编号写备注。登录后 `/astroapi/match?filter=all`（按返回的 `pagination.paginationToken` 翻页）也直接给出匹配岗的真雇主和 `applyUrl`。

Jobgether 上也查不到时，用原帖写的办公地组合（如「London、Munich、Zurich 或欧洲远程」）、业务描述和标题猜候选公司，去它们的 ATS 板按标题找同名岗，正文对得上就按真雇主走。还查不到（标题太泛、Jobgether 页已下线）才按匿名代招处理，备注写试过什么。

## 步骤 3 · 去重

搜索发现的岗攒多了，可以写成 JSON 跑 `match` 判重（它连已排除表一起查，格式在脚本开头）。手工判重时先在 `rows.json`（含已排除表）里按 jk、LinkedIn id、ATS 号搜整行，再按"岗位名+单位"比对——同岗常跨渠道重复，合并为一行（官网/ATS 链接优先，AT 次之，其他聚合站最后；被并的链接写备注）。同一 JD 挂两个网址（如 `-2` 后缀）、同一岗不同城市版本（如 Amsterdam 与 Delft、Amsterdam 与别国）、两家猎头转发同一份 JD 的，只入一行。无稳定链接的赞助岗每轮都会被重新"发现"，靠岗位名+单位识别后跳过。**新渠道找到的岗先查表**再决定 add 还是 update；add 时链接已在表，脚本会报错，改成 update 或删掉这条。

## 步骤 4 · 一轮内定档

1. **标题判掉的**：写进已排除表（`exclude`，排除类别用脚本里的词表，理由写标题依据），摘要里按类别报数。读过 JD 才判掉的（语言超门槛、境外非远程、雇主不在欧盟/英国且不满足例外、其实不对口等）同样写 `exclude`，理由抄 JD 依据或核查结果。已在已排除表的岗不重判。
2. **判不了 + 便宜渠道**：当场拉 JD 全文，按 `job_profile.md` 的「打分」走完：先写复述，再打三个分，再降档、封顶，备注按那里的格式写。无年限、无当地语言要求的写进"主要要求"列开头，方便同档排序。
3. **判不了 + 贵渠道**：先读聚合站正文，再当轮去找官网页读全文（做法见「核心原则」表格最后一行），按官网全文定档。确实找不到官网页才入表 `未投` + `聚合站`，备注写"来源：<搜索页 URL>；仅聚合站核验：<试过什么>"，进下轮欠账清单。

提取字段：岗位类型、级别（没写就 `未标`）、学历、FTE 与周工时、合同长度、scale 与月薪、截止日期、语言要求、工作模式与允许的居住国、签证/担保表述、联系人/PI、所需材料（表单可见时填）。页面矛盾标 ⚠️ 并取保守截止日期（"solliciteer voor 14 oktober" 记 10-13）；列表页地点不信，以 JD 正文为准。`来源渠道` 只用八词之一，按链接列所在的站填。

## 步骤 5 · 写入 Excel

把本轮结果写成 changes.json（结构在 `tools/tracker.py` 开头的说明里：`run` / `add` / `update` / `remove` / `exclude` / `companies`），放在设备端 shell 的工作目录（`~/work/`，不放进 jobs 文件夹），字符串值里不用 ASCII 双引号（改用「」）。先备份，大批时分几个文件依次 apply，每次成功就 `cp` 回去再跑下一个：

```bash
mkdir -p ~/work && cp "$HOME/mnt/jobs/job_tracker.xlsx" ~/work/backup.xlsx
cat > ~/work/changes_a.json <<'EOF'
{ ...本轮改动... }
EOF
cd "$HOME/mnt/jobs" && python3 tools/tracker.py apply job_tracker.xlsx --changes ~/work/changes_a.json --out ~/work/new.xlsx --today YYYY-MM-DD && cp ~/work/new.xlsx job_tracker.xlsx && python3 tools/tracker.py check job_tracker.xlsx --today YYYY-MM-DD
```

脚本负责校验词表与链接、派生岗位ID、去重、写已排除表（add 已排除的岗时自动移回岗位表）、备注追加、保留「决定不投」段、未投且截止已过自动转 `关闭`、整表重排、重生成说明页、自检。退出码非 0 = 没写成，改 changes.json 重跑。`cp` 报权限错误多半是 Excel 开着，请用户关掉再试。

- **`run.mode` 必须写**：找岗流水线写 `"scan"`（才会改上次运行时间），分几次 apply 时每个文件写同一个 run；对话里只改状态写 `"update"`。
- 已有行只通过 `update` 改（按 `id`）。**不删行**（跨渠道合并的被并行除外，用 `remove`）。
- `row` 和 `set` 的键必须和表头一字不差（例如 `薪资/Scale`、`签证/居留`、`合同与FTE`），写错一个整批失败。
- **apply 前先自查排除**：本批每条 `exclude` 按「岗位名 @ 单位」对一遍岗位表（`rows.json`）和本批的 `add`。只要有一条重名，整批 apply 都会失败（脚本提示「已在岗位表，去岗位表改状态」）：真是同一岗的，删掉这条 `exclude`，需要改状态就用 `update`；确属不同岗位的才加 `allow_same_name`。

**边做边写，不攒到最后。** 一轮要读上千条，会话中途可能被压缩，只留在浏览器变量和对话里的列表与判定会丢。所以：

1. 每抓完一个来源，把原始列表（编号、标题、单位、地点、链接）用 heredoc 写进设备端 `~/work/` 的文件。
2. 每判完一个来源（或攒到两三百条判定），就写一个 changes 文件 apply 一次（同一个 `run`），再重新 `export` 一份 `rows.json`，后面判重用新的。
3. 被压缩后接着做时，先看 `~/work/` 里的文件和 Excel，从断点继续，不重抓已经写进表的来源。

## 步骤 6 · 运行摘要（中文）

先说**最对口的 1–3 个岗**（只从 `核验=官网JD` 里挑，备注含「决定不投」的不挑，按官网链接去重，并排除同单位已投/被拒岗的重挂）和一句话理由。用户在找工作的时候，这就是最该先投的；`job_profile.md` 写着现在不投的，只当行情说，不催。再说：

- 复核结果：stale 几个、欠账消化几个，各自仍在招 / 改关闭 / 改档多少；**欠账余额**分 sheet 报数，涨了要解释（本轮新增的贵渠道 Mid 和永远核不到的猎头帖分开说）。
- 新增岗位数（分 sheet、渠道、工作模式）；状态变化；14 天内截止的岗；公司表增删了哪几家。
- **打不开的站**：逐条写站名、网址、内置浏览器和 Chrome 各自的现象；一个都没有就写「无」，这一条不能省。正常情况下不应出现其他「跳过或降级」；万一有（例如用户中途叫停），逐条写清哪一步没做完。
- 本轮新排除的按排除类别报数（都已写进已排除表）；被降档、封顶的分类报数。
- 出现的硬日期（截止、面试时间）提醒写入 Google 日历。

提到某个岗时，说清是哪张表的哪个岗，不用自造代号。

## 定期全量复查（每 8–10 轮或每季度一次）

隔了一个多月才跑的那一轮，也做一次。`stale` 只覆盖 High/Mid，Low 岗入表后没人看，死岗会越积越多，也常有被错杀的岗。固定两步，不要倒过来：

1. **批量读正文重打分**（便宜）：所有 `未投` 且 `核验≠官网JD` 的岗，按站点分组批量读正文，重新打分。备注里「决定不投」段必须保留（脚本会自动保留）。
2. **只对升到 High/Mid 的追官网**（贵）。

已排除表抽查：类别为 `其他`、`非对口岗`、`别的学科` 的行按排除理由过一遍，判错的加回岗位表（add 时脚本自动从已排除表移走）。

同时做：大学岗批量判死活——`careers.tudelft.nl/search/?q=&startrow=0`、`20`、`40`… 翻到底，抓全站在招编号比对；AT 岗位页出现 `(the deadline was …)` 即过期。

## 对话中的状态更新（不跑搜索时）

用户报告"我投了 X""X 来面试邀请了""X 拒了""X 给 offer 了"：同样走 `update`。投了→`状态:已投` **且同时 `投递日期`**（脚本强制），材料文件夹名入备注；面试→`面试`+轮次入备注；拒信→`被拒`+日期入备注；offer→`Offer`+decision deadline 入备注。`run` 写 `{"mode":"update"}`。改完看自检通过、回读那一行；面试时间、decision deadline 提醒写入 Google 日历。

## 边界

- 只入表、不投递、不写信、不填表、不发邮件。
- 不改 `job_profile.md` 里的规则（规则要变先问用户）；公司表可以增删改。
- 提醒用户：投递前重新打开官网链接确认仍开放。
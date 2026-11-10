---
name: job-apply
description: "定向投递（按常驻荷兰写）：给岗位链接，读官网岗位页和团队背景，走一遍申请表，先出匹配分析等用户确认，再生成定向 CV 和求职信，然后辅助填网申，停在本人卡点前。用户给岗位链接说想投、帮我准备申请材料、帮我填时用。"
---

# job-apply · 定向投递材料与网申辅助

三段式：①分析（自动跑完停下）→ ②材料（确认后生成）→ ③网申（用户说"开始填"才进）。讨论中文，材料英文。求职 Excel 只在用户说"提交了"或"不投"之后改这一行（第 16 步）。哪些事留给用户本人做，见「本人卡点」。

## 规则源与文件

- **用户的要求在 `profile/job_profile.md`**（jobs 文件夹里；放进 Claude Project 的项目文件也行，文件名相同）：「投递」（定向 CV 怎么改、表单怎么填）、「材料怎么写」（语感、求职信和 research statement 的结构、称呼落款、长度）、语言门槛、「账号」。运行开始先读，读不到就停下告诉用户。
- **事实**：`profile/facts.md`（身份、联系方式、对外怎么说、没用过和没做过的；每个项目和每篇论文的编号结果、贡献和 I/we）。读不到就停，不凭记忆写事实。
- **jobs 文件夹里**：母版 `cv_master.tex`（用户维护，只读不改）、用户自己编译的通用版 `cv_master.pdf`（不覆盖）、脚本 `tools/tailor_cv.py` 与 `tools/check_materials.py`（个人内容在 `tools/materials_config.json`）、输出目录 `applications/<单位-岗位短名>/`。
- **在用户电脑上直接跑脚本、直接写文件**：云端会话用设备端 shell（`device_bash`），先 `ls $HOME/mnt/` 看挂载名；下文路径写 `$HOME/mnt/jobs`（把 jobs 文件夹直接连给会话时的位置），连的是它的上级文件夹就在后面补上子路径。本地会话（如 Claude Code）直接在 jobs 文件夹下跑。这样读到的永远是当前母版，材料也不用上传下载。中间文件（`edits.json`）放 `~/work/`，不进申请文件夹。
- **本 skill 需要改时**：起草完整的新 SKILL.md 交给用户保存；脚本要改就直接改 `tools/` 里的文件。不建错误记录或说明文件。

## 第一段（自动执行，结束后停下）

1. **抓岗位页全文，必须是雇主官网或其 ATS 的岗位页**（学术岗 AcademicTransfer 岗位页等同）。用户给的是 LinkedIn/Indeed 链接时先跳到官网页（Apply on company website 外链，或到公司 careers/ATS board 搜标题），跳不到就说明，只按聚合站信息分析、结论标⚠。内置浏览器优先（导航→等 5 秒→读正文；LinkedIn 懒加载要再滚动等 3 秒）；大学官网的人机验证墙浏览器一般能过。提取：职责与要求、**语言要求（当地语言的原页优先于英文摘要；硬要求超过 `job_profile.md` 写的门槛就直接停，建议不投并让对话把 Excel 改 `关闭`）**、**工作模式与允许的居住国**（要求住在别国的直接停）、**申请材料清单**（决定生成什么；多数岗只要 letter+CV+推荐人，不要求就不写 statement；要录视频、交作品集、做测评这类助理做不了的材料，单独标出来让用户决定投不投）、截止日期、薪资/scale、合同、联系人/PI、级别与年限要求、筛查要求、写给非欧盟申请人的居留条款。页面标题与用户说的岗位名不一致时指出。同一岗位有 Senior 和非 Senior 等几个版本时，各版本的地点条款分开看（Senior 版只收别国、非 Senior 版仍收本地的情况见过）。
1a. **第一段就自己打开申请表走一遍，不先问用户要什么材料**（表单里有 cover letter 上传框或文本框的，选填也写信；性别、族裔、退伍军人这类个人题按 `job_profile.md`「投递」里写的代填，填完在对话里列出请用户确认）：点 Apply 进表单（入口见「各招聘系统填法」），先处理 cookie 弹窗，把姓名、联系方式这些标准字段填上（取自 facts.md），点翻页类按钮（Next、Continue、Save and Continue、"Next: Questions" 这类）一直走到上传文件、同意框、声明题或最终提交之前，把每一步的必填题原文、必传文件、单选题和留给本人的框都记下来。材料清单以表单为准：岗位页常不列材料（AT 页；有的大学表单必传成绩单；Workable 表单常有必答开放题），分析里写的是表单真实要的东西，不写"登录后才知道"。
    - 要建账号或登录才进得去的（如 njoyn、Workday、iCIMS、SuccessFactors）：先查 `job_profile.md` 的账号表有没有这个站的账号。有就填用户名，请用户在浏览器里输密码登录，登录后接着往下走；没有就在第一段一开头告诉用户去建（站名、入口按钮、用哪个邮箱），用户建好后把站点、网址、用户名记进账号表（密码不记）。这是第一段里唯一需要用户动手的事，其余能看的都自己看完。
    - 先走表单再写分析：开放题题目、是否要信、字数限制都会改变第二段要做什么。表单里填过的字段到第三段可能被刷新清空，第三段开填前整页读回一遍。
2. **背景调研**。优先用岗位页内的团队/实验室/PI 链接。学术岗必做 PI 调研：把文末「PI 调研子代理 prompt」填好派一个子代理，十项必答、未核验项一律 ⚠️。工业岗改为调研公司/团队技术栈与产品方向。
3. **输出中文匹配分析**，固定结构：①材料清单 + 截止日期 + 值得注意的条款（permanent contract、安全筛查、Senior 级、年限硬要求、非欧盟居留条款；合同长度和 FTE 各页面写得不一样的都列出来）；②团队调研要点（含与用户工作的接口）；③四栏评估：强项（哪些核心要求被直接满足）/ 真实差距（对照 facts.md 里没用过、没做过的，不回避）/ 桥（两到三个具体的连接点）/ 决策（Apply now、Apply after clarification、Contact PI、Keep as lead、Skip 之一），不为了鼓励把匹配度说高；④主叙事提案：letter 只写透的那**一个**主连接，一句话 + 三个证据项目；⑤CV 改法提案（分学术/工业轨；只要 CV 的岗给"通用版还是定向版"的建议）。

**然后停下等确认。** 先讨论策略再生成文本，这是硬规则。

**只要 CV 的岗**（`所需材料=CV`，或用户说"直接投""只要 CV"）：第 1 步照做，第 2、3 步压成一段话（一句方向判断 + CV 改法提案），确认后第二段只做第 4、7、8、9 步，再进第三段。

## 第二段（确认后执行）

4. **定向 CV**：
   ```bash
   cd "$HOME/mnt/jobs" && python3 tools/tailor_cv.py --src cv_master.tex --show     # 锚点当前文本、第一组 \project 键、母版指纹
   mkdir -p ~/work applications/<短名> && cat > ~/work/edits.json <<'EOF'
   { ... }
   EOF
   python3 tools/tailor_cv.py --src cv_master.tex --out applications/<短名>/CV_<短名>.tex --edits ~/work/edits.json
   ```
   `edits.json` 字段（都可选）：

   | 字段 | 用途 |
   |---|---|
   | `tailored_for` | `"<单位> - <岗位>"`，脚本在首行后插一行注释记母版指纹 |
   | `fields.about` | About Me 段新文 |
   | `fields.open_to` | 求职行（不写 `\par`） |
   | `fields.pills` | 字符串列表，数量必须与母版一致；加起来别太长，否则一行放不下（样例母版约 85 个字符） |
   | `fields.skills_mldl` | Skills 节 `\entry{Methods}{…}` 的整行内容 |
   | `fields.thesis` | Education 里 Thesis 标题，一般不动 |
   | `project_order` | Experience 节第一组 `\project` 的新顺序；键是 `\project` 第一个花括号原文，直接复制 `--show` 打印的 JSON 那行（`&` 写成 `\\&`）。后面各组位置固定；只在发表列表里的论文不是项目条目，要突出就写进 About |
   | `selected_publications` | 工业短版：只保留含这些关键词的发表条目，节名改 Selected Publications，`\pubtotal` 自动改 |
   | `replace` | 临时精确替换（如给在审论文加匿名仓库 Code 链接、加 References 节、母版里与 facts.md 不一致的旧口径），`old` 从 `--show` 或母版逐字复制，恰好匹配 1 处 |

   - 每次从 `--show` 的实时输出写 edits.json，**不拿上一岗的 edits.json 当起点**（母版会改，旧的 `replace` 原文会失效；`fields` 键才是稳定接口）。
   - 链接写 `\href{url}{Label}`，多个用 `\sep ` 连。
   - 脚本保证导言区不变、锚点唯一、重排字节数不变、不新增条目，并打印母版指纹、项目顺序与发表条目数，抄进 notes.md。**只交付 .tex，不编译 PDF**。
   - 学术岗、工业岗各怎么改，按 `job_profile.md`「投递」。通用的几条：不改导言区、宏包、自定义命令；项目条目保持「问题 → 我做了什么 → 结果」的顺序，一作项目用 I，合作论文保持「With X (lead), we」；结果数字加粗，每条一到两处。
   - 母版里和 facts.md 不一致的旧写法（日期、语言水平等）用 `replace` 在定向版里改掉，并在第二段摘要里提醒用户改母版。
5. **Motivation letter**：按 `job_profile.md`「材料怎么写」写。文件模板：首行 `**Motivation Letter**`，空一行，联系行 `姓名 | 单位 | 邮箱 | 电话 | 主页`，称呼，正文纯段落，落款；不带使用说明、HTML 注释、markdown 标题和加粗。用 heredoc 直接写进 `applications/<短名>/motivation_letter_<短名>.md`，然后
   ```bash
   cd "$HOME/mnt/jobs" && python3 tools/check_materials.py letter applications/<短名>/motivation_letter_<短名>.md
   ```
   未通过就改到通过（模板、邮箱、破折号、禁用短语、身份红线）。词数它会报"超/少多少词"和逐段词数，超了按段砍，不整篇重写；看到"非一作论文出现在 I 句里"的 warning 就回头对署名。
6. **其他材料仅当岗位页明确要求**：research statement 按 `job_profile.md`「材料怎么写」，文件头同求职信（标题换 `**Research Statement**`，没有称呼和落款），`check_materials.py statement` 检查；岗位限一页的，脚本的词数 warning 可以不管；交给用户时说明是初稿，学术判断用户自己过。要 references 的在 CV 里用 `replace` 加一节（推荐人按用户当时给的，只放姓名、职务、邮箱），节内用 `\par` 分行写，不用 `\entry`（脚本拒绝新增条目）。要成绩单、学位证这类原件的，由用户自己上传，notes.md 里记一句在哪。
7. **事实自查**（违反即返工；与 facts.md 冲突以 facts.md 原文为准）：身份和对外说法、没用过的东西、语言水平、I/we、每个数字逐项对，非一作的论文尤其看列举句里有没有被写成 I。PI 调研里标了"评论者"的论文不写成 PI 的研究，"未见关系"的不提用户现单位与对方的关系，合同条款打架的只写岗位页原文。
8. **notes.md**：投递页与截止日期、CV 母版指纹与改动、数字引用表（每个数字 | facts.md 条目 | 精确值）；学术岗加团队调研结论（子代理回报的"不得引用清单"整段放进来，标题"不得当事实用"）和面试准备；再加一节"网申字段"，把表单上的单选题、必传文件和留给本人的框先列好。第三段的开放题答案之后追加进来。改动记录、开放题都写进 notes.md，不另开文件。
9. **核对落盘**：`ls -la applications/<短名>/`，确认文件夹里只有 CV、letter、按需 statement 或其他要求的材料、notes.md。
10. **第二段摘要**（中文）：生成了哪几份文件及位置、主叙事一句话、用户要做的事（Overleaf 编译、Google Docs 排版导出成 A4 PDF、推荐人电话若要求、成绩单等原件、提交前重开岗位页）、截止倒计时。然后问一句：现在开始填，还是等 PDF 编好再说。

**PDF 回审**（用户把导出的 PDF 发回时）：`pdfinfo` 看页数和纸张（要 A4、限页数的不超页），`pdftoppm` 渲染看孤行和落款，`pdftotext` 与 .md 逐字比对有没有丢行；再逐句过内容。用户逐条提意见时，每条先说有没有道理和为什么，再改；改完把以后通用的偏好写进 `job_profile.md` 的「材料怎么写」，事实性更正写进 `facts.md`。

## 第三段（用户说"开始填"后执行）

11. **打开投递页**（入口见下方「各招聘系统填法」，浏览器按那里的「浏览器选择」挑）。先处理 cookie 弹窗（一律拒绝非必要，按钮常叫 Necessary Only / Reject all）。
12. **登录、建账号、上传文件**：页面有英文界面的先切英文，再登录，再填（切语言和登录都会刷新页面、清空已填内容）。需要登录的站先查 `job_profile.md` 的账号表：用户名可以填，密码由用户自己输并点登录；没有记录的先停，让用户登录一次，并把新账号加进账号表。需要建账号的先停，让用户建好。**上传文件是用户的事，而且要先传再填**：iCIMS、Ashby、Phenom 上传 CV 会覆盖或清空已填字段。内置浏览器登录态跨会话保留，LinkedIn/Indeed/AcademicTransfer 一般不用再登。
13. **填标准字段**：姓名、邮箱（用 facts.md 指定的求职邮箱）、电话（完整国际号）、LinkedIn/GitHub/主页、地址、城市、邮编、省、国家、出生日期、工作地点/是否搬家/各国工作许可——取自 `facts.md`，不现编。个人题、搬家、工作许可这些怎么答，按 `job_profile.md`「投递」，拿不准就停下问用户。"How did you hear about us" 按 Excel 来源渠道如实选。
14. **开放题**：把题目原文抄给用户，在对话里起草答案（有字数限制按限制，没有的按 `job_profile.md` 写的长度；短句、像用户本人写的，语气按 `job_profile.md`「材料怎么写」；一题只答一件事，不复制 letter 段落；数字照 facts.md 编号条目并在 notes.md 列出条目号），用户确认后填入，同时追加进 notes.md。薪资期望题：选填就留空，必填问用户。
15. **复查并截图**：逐字段读回（隐藏 select 以 `value` 为准，截图可能滞后一步）；**专门回读同意框和数据保留下拉**，荷兰大学与 UMC 的表单常自动填这两样，被填了就撤销并说明。然后截一张图给用户。
16. **停在最后卡点前**：同意框、声明题（"I declare that I have filled in everything truthfully" 这类）、验证码、提交由用户做。用户说"提交了"后：读一下当前页确认已到成功页（读不到就提醒用户保存确认页与确认邮件），当场改 Excel 这一行（顺手把 `官网链接` 换成雇主 ATS 岗位页、填 `所需材料`）；截止日等硬日期提议写日历；用户提交时新建了账号的，把站点、网址、用户名写进 `job_profile.md` 的账号表（密码不记）。改 Excel 的做法（id 不确定就先 `python3 tools/tracker.py export job_tracker.xlsx --out ~/work/rows.json` 查；sheet 是 `学术岗位` 或 `工业岗位`）：
    ```bash
    cat > ~/work/changes_upd.json <<'EOF'
    {"run":{"mode":"update"},"update":[{"sheet":"工业岗位","id":"<id>","set":{"状态":"已投","投递日期":"<YYYY-MM-DD>"},"append_note":"材料：applications/<短名>","verified":true}]}
    EOF
    cd "$HOME/mnt/jobs" && python3 tools/tracker.py apply job_tracker.xlsx --changes ~/work/changes_upd.json --today <YYYY-MM-DD>
    ```
    用户说"不投"时不改状态，只用 `append_note` 追加"决定不投：<原因>"。看到"自检通过"才算改好。

## 各招聘系统填法

**浏览器选择**：默认用内置浏览器（登录态跨会话保留）。内置浏览器过不了 Cloudflare Turnstile（嵌在公司站里的 Ashby、Varbi 都见过卡在这里，只能换本地浏览器重填）。所以页面带 Cloudflare 验证、下表标了 Cloudflare 的系统、或者在内置浏览器验证失败过的站，一开始就改用 Claude in Chrome 扩展，在用户本地 Chrome 里填：先 `tabs_context_mcp` 拿 tab id；`browser_batch` 的子动作写成 `{"name": "<工具名>", "input": {...}}`；验证码和提交由用户在自己的 Chrome 里完成。

**通用**（所有 JS 在 `javascript_tool` 里跑，两个浏览器参数一样：`action: "javascript_exec"` + `text`）：

- React 表单用原生 setter + 事件：
  ```js
  const setNative=(el,v)=>{const p=el.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype;
   Object.getOwnPropertyDescriptor(p,'value').set.call(el,v);
   ['input','change','blur'].forEach(t=>el.dispatchEvent(new Event(t,{bubbles:true})));};
  ```
  不够用时别在可见按钮上加码（合成点击、调 React onClick 都可能无效），去找真正绑定状态的隐藏 input 点它。
- 原生 `<select>` 的弹出层是系统控件，点不进去：直接设 `select.value` 再派发 `change`。option 的 value 常和显示文字不同（月份是 `3` 不是 `03`），按文字找 option 再取它的 value。受控下拉写 value 后状态不跟的，用 `form_input` 按 ref 选，再按 ref 回读。
- SumoSelect 这类自定义下拉：显示文字和底层 select 会不同步，点它自己的选项 `li`，改完两边都核对。
- 题干从 `el.labels[0]` 常拿不到或被截断，从字段往上找祖先容器：
  ```js
  let p=el,lab=''; for(let k=0;k<5&&p;k++){p=p.parentElement; if(!p)break;
    const t=(p.innerText||'').replace(/\s+/g,' ').trim(); if(t.length>3&&t.length<220){lab=t;break;}}
  ```
- 有必答题没有 `name` 属性时，先把"字段下标 → 题干"映射打印出来核对，再按下标填。
- intl-tel 电话控件直接输完整国际号，控件自己识别国家。
- 程序写值不生效、或一上传文件就被清空的文本框：先用 JS `focus()`，再用 `computer` 的 `type` 真键盘输入，最后按 id 读回。
- 页面刷新或重新渲染后，已填字段可能全空，每次提交前都整页读回一遍。

| 系统 | 入口 | 要点 |
|---|---|---|
| Lever | 岗位页 URL 加 `/apply` | 字段有 `name`（`name`、`email`、`phone`、`org`、`urls[LinkedIn]`、`comments`）；`location` 是自建 autocomplete，输入后**必须点下拉项**才会写隐藏字段，下拉搜不出结果且非必填就留空；hCaptcha 在提交前 |
| Greenhouse | 页内 Apply 或 `#app` | 字段用 `id`（`first_name`、`last_name`、`email`、`phone`、`question_<n>`）；**Country/Location 是 react-select，要用 `computer` 真键盘输入再点选项或回车**；嵌在公司站 iframe 里时取 iframe 的 `src` 直接 navigate；岗位页跳回 board 并显示 no longer open = 已关闭；**新版 board 的 react-select 下拉要先 `scrollIntoView` 再按截图坐标真点、打字、回车**，同一批动作里布局会因报错提示移位，做完一个截一次图；美国雇主的表单常有 sponsorship 题（按用户当时的居留状态答，拿不准问用户）、必填的 US zipcode（不在美国就填 N/A 加所在国）、背景调查知情和电子签名这类声明题（留给本人） |
| iCIMS | 官网岗位页 → Apply，需建账号 | 表单在同源 iframe 里，走 `document.querySelector('iframe').contentDocument`；国家/省是隐藏 select + 搜索框 + `ul>li`，写搜索框后对目标 `li` 派发 mousedown/mouseup/click；省份选中后可视标签不刷新，以 `select.value` 为准；**上传 CV 会覆盖已填字段** |
| Recruitee | 岗位页本身 `<co>.recruitee.com/o/<slug>`，表单在页面下半部 | `candidate.name` 是单个全名字段；`candidate.cv` 必传；开放题 `candidate.openQuestionAnswers.<qid>.content`（Yes/No 型是 `.flag`）；radio 用 `el.click()`；无同意框无验证码；**提交成功会跳回公司 careers 首页**，没有单独成功页 |
| Ashby（含嵌在公司站里的 Ashby） | 岗位页 URL 加 `/application` | 没有 `<form>` 元素，按 id 取：`_systemfield_name`（全名）、`_systemfield_email`、`_systemfield_resume`；**Yes/No 题点可见按钮无效，只有 `document.querySelector('[name="<uuid>"]').click()` 点隐藏 checkbox 有效**；**别用顶部 "Autofill from resume" 传简历**（会清空自定义题），那个框显示 "Failed to fetch" 不影响提交；**嵌在公司站里的版本传简历后会清空已填文本框**，传完用真键盘重填；提交前有 reCAPTCHA 或 Cloudflare，后者内置浏览器过不了，用 Chrome 扩展；成功页文字 "Your application was successfully submitted."；Location 题是下拉自动补全，JS 赋值无效，点框后真键盘输入再点选项（有的只收国家级，输国家名）；**有的雇主同一部门 90 天内只收一份申请**，填完点提交才报错（"applied for a position in this domain within the last 90 days"），所以投之前先查表里同公司同部门（岗位页左栏 Department）最近的投递日期，没过期限就不准备材料，在备注写明哪天起能投；**EEO 单选（Gender、Race、Veteran）一题一题点，每点一个等 1 秒**，同一段脚本里连点三个只会留下最后一个 |
| Varbi（北欧和荷兰的大学常用） | 岗位页 Apply → `<org>.varbi.com/en/apply/positionquick/<jobID>/`；一个账号各校通用 | **有 Cloudflare 验证，一开始就用 Chrome 扩展**；字段都有 id：`email`、`confirm-email`、`firstname`、`lastname`；出生日期是三个 select `year`、`month`、`day`（按文字选）；`selectgender`、`address1`、`zipcode`、`city`；`country-select-country` 填国家代码，选完省份下拉 `country-select-subdivisions` 异步加载，等一下再选；`mobile-country-code` 选好后 `mobile` 只填去掉国家码和开头 0 的号码，会自动显示成国际格式；开头几道单选（来源、是否本校员工、是否本校学生）按 id `click()`；"I declare that I have filled in everything truthfully"、GDPR、Varbi 条款、保存到 profile 都留给本人；有的学校另有必传的成绩单；邮箱已注册过的提交时会要求登录，登录后让用户核附件是不是这次的；成功后跳到 profile.varbi.com 的 My applications，顶部写 "Your application has been submitted" |
| Workday | Apply Manually，多数租户需建账号（有的租户不用登录，有的要先建 Candidate Home 账号） | 多步向导，Save and Continue 不是提交；**Email 框只读、等于登录账号的邮箱**，所以必须用账号表里记的账号登录，登错账号就退出重来；字段用 `document.getElementById` 取（`data-automation-id` 选择器常取不到）；My Information 里姓名、街名门牌分开填，Phone Device Type 默认 Landline 要改 Mobile，国家码单选后号码只填本地部分；**日期是月/年分段的 spinbutton**，程序写值会乱，真点月份段，键入月份，再键入年份；**Skills 搜索框** ctrl+a 清不掉旧词、会越积越长，用 `el.select()` 再按 Backspace 清空，合成的 Enter 不触发搜索，要用 `computer` 按真键盘回车；Field of Study 是虚拟列表要滚动找；上传 CV 后自动解析，逐项复查；**有的租户程序写值完全不生效**，文本框也要真键盘：先 `el.focus(); el.select()` 再用 `computer` 打字，打完 Tab；提交后报必填错误时，点错误汇总框里的第一条链接会把焦点送到那个字段，逐条修；How Did You Hear 是分层的 prompt，点类别不展开，直接在 Search 框打来源名回车；School、Field of Study 也是 prompt，打字回车后点结果，Field of Study 回车会自动选第一项，选错点 × 删掉，列表里没有的专业留空；Skills 勾选后搜索框会下移，每勾一个截一次图再点；Languages 每种语言要 Overall、Reading、Speaking、Writing、Comprehension 五个下拉（1 Beginner 到 5 Fluent），用异步脚本逐个点开选；My Experience 只有一个上传框的，CV 和信都传这里 |
| SAP SuccessFactors（大学和研究机构常用） | 各单位租户的账号互不通用；有的站要从岗位页点申请按钮进，直接打开 talentcommunity/apply 链接会跳回职位列表 | 电话框用程序写值会留红字必填提示，要 `triple_click` + 键盘输入再 Tab；Tab 会打开国家下拉，按 Escape 关；**账号会自动挂上一次上传的 CV 和 letter**，提醒用户换成这个岗的文件；**岗位页写只要 CV，表单也可能把 cover letter 设成必传**，所以 SuccessFactors 的岗第二段就备好 letter |
| Hireserve（荷兰的大学和医院常用） | 岗位页点 "Apply now"，有的在当前页弹出两步向导 | 隐藏的 `_full` 电话字段提交时自动填；来源是 SumoSelect；**数据保留下拉与隐私同意框留给本人**；上次空提交留下的服务器端红字不会自己消失，别被吓到；有的学校另有求职者门户（能看交过的文件和招聘启事全文），内容在页面内嵌的框里，读页面文字看不到，要截图点；从门户下载的文件落到用户的 Downloads，同名会被覆盖，下载前先查重名 |
| Phenom | Apply Now → `/<区域>/en/apply?jobSeqNo=…`，不用建账号；有的五步，有的单页 | 先传简历（1MB 以内），解析质量差，职位、日期、技能要逐项改；字段 id：`country`、`firstName`、`lastName`、`email`、`phoneWidget.countryPhoneCode`、`phoneWidget.phoneNumber`、`deviceType`、`gender`，下拉用 `form_input` 按 ref 选；**改 Country 会把电话国家码重置成默认、清空号码**，先选国家，再选国家码（形如 `NLD_31`）、填号码，最后按 id 读回；From 日期是月份选择器，先改年份 select 再点月份格子；数据保留问题留给本人 |
| njoyn | 岗位页右上的 "I'm Interested"（页面源码里的 Apply Now 按钮是隐藏的，别找它）→ 跳到 `clients.njoyn.com` 登录页 | 先拒掉 cookie；登录页左边 New Applicant 填邮箱和所在国家就是建 career profile，由本人建，右边 Returning User 是登录；同一雇主各岗共用一个账号 |
| Notubiz 招聘门户 | 岗位页 Solliciteren 跳 `sollicitatie.notubiz.nl/...?VcSn=<号>` | 只有荷兰语界面；**脚本读不到输入框**，全部用 `computer` 真点、慢速打字，每次输入前后各等 1 秒，不然只进第一个字段；Geboortedatum 打 `dd-mm-yyyy`；Motivatie 是富文本编辑器，打字里的空行会变成两个空段；Bijlagen 必传，CV 和信都放附件；"Mijn gegevens mogen 1 jaar bewaard worden" 开关默认开，由本人定；Informatiebron 下拉里没有实际来源时选 Internet；成功页标题 "Jouw sollicitatie is gelukt!" |
| Homerun | 岗位页 Apply now → `<org>.homerun.co/<slug>/en/apply?&step=1`，不用建账号 | AngularJS 表单，四步 Personal info → Questions → Preview → Submit；第一步字段有 id：`first_name`、`last_name`、`email`、`pronouns`、`country`（普通文本框，直接写国家名）、`phone_number`、`linkedin`、`github`，原生 setter 能写进模型，用 `angular.element(el).scope().formData` 回读；隐藏的 `homerun_required` 是防机器人字段，必须留空；pronouns 标了 * 但空着也能翻页；"Next: Questions" 只是翻页；第二步的题目和必传文件写在页面源码的 `availableQuestions` JSON 里，第一步不填也能看到；Preview 页有数据保留的 consent 框，留给本人；成功页 `step=4` 写 "Your application has been submitted!" |
| 雇主自建表单 | 表单多在岗位页底部，不跳 ATS | 多是普通表单，原生 setter 可填；留意：两个上传框 id 重复时第一个是 CV、第二个是信；有必答题没有 `name`；没有求职信栏但能加传文件的，信放那里；第三方懒加载、会反复折叠的表单，把"点开 → 等 2.5 秒 → 填 → 回读"放在同一次脚本调用里；页面上另有样式相同的 job-alert 邮箱框，别填错；学历头衔这类下拉是学历主张，留给本人 |

新系统先 `read_page` 看字段结构再决定填法；reCAPTCHA/hCaptcha 一律本人过。遇到上表没有的系统或新的控件怪癖，第三段结束时起草更新这张表的新 SKILL.md 交给用户保存。

**本人卡点**（每个表单都一样）：上传文件；建账号、设密码、填密码、点登录；过验证码；勾 GDPR/隐私/数据保留，以及"所填属实"这类声明题；点最终提交并截图确认页。到卡点停下，一句话说清接下来要用户做什么，做完再继续。

## 边界

- 不发邮件、不联系推荐人。
- `job_tracker.xlsx` 只在用户说"提交了"或"不投"之后按第 16 步改这一行，别的行、别的列不动；找岗、打分、新增岗位仍走 job-search。新站点账号写进 `job_profile.md` 的账号表。
- 差距如实写，不虚高匹配度；宁可用户看完决定不投。语言要求超门槛的岗、要求住在荷兰以外的岗直接建议不投。远程岗有没有荷兰实体不是不投的理由，签证在 offer 阶段谈。岗位页建议非欧盟申请人先问校方移民团队的，在分析里列出条款和对用户的影响，问不问由用户定，不替用户发信。
- 不改 `job_profile.md` 里的其他规则；不改 CV 母版。

## PI 调研子代理 prompt

一个岗一个子代理；多位 PI 同一个子代理里分节答。填好 `<>` 后原样发出。申请人背景按 facts.md 的当前内容填，发表去向不写（在审论文的状态会变，调研也用不到）：

---

你在帮一位申请人做一个学术岗位的团队调研。只回报你查到并能给出来源的东西；查不到的明说，不猜。所有未能在一手来源核实的项都用 ⚠️ 标出。

**岗位**：<岗位名>，<单位/系>，岗位页 <URL>
**联系人 / PI**：<姓名（一位或多位）>，<主页或系页 URL（有就给）>
**申请人背景（供你找接口）**：
- 一作：<每篇一作论文的名字加一句话内容，取自 facts.md 各篇的「定位」>
- 合作：<和岗位相关的合作论文，同样每篇一句>
- 主线关键词：<取自 facts.md 的「研究主线」>

**来源限定**：PI 主页、实验室主页、大学 publications 页、DBLP、arXiv、Semantic Scholar、论文原文、岗位页本身。Google Scholar 通常抓不到，不要硬试。大学官网遇验证墙就换来源。PI 维护开源库的，clone 下来读代码结构、测试和提交记录。

**必答十项**，按编号回答，每项给来源 URL：

1. **PI 最近在做什么**：近 2–3 年 5–8 篇最相关论文，每篇一行：标题 | venue 年份 | 一句话内容 | 与岗位的关系。
2. **岗位在 PI 研究计划里解决哪块**：标明哪些是岗位页原文、哪些是你的推断。
3. **申请人哪项工作能直接接上**：具体到"申请人的 X 方法对应 PI 的 Y 问题"，给 1–3 个。
4. **PI 组里独有的东西**：数据集、方法链、软件、合作关系、基础设施；每条给出处。
5. **第一项可执行实验**：入职第一个月能做的一件事，具体到数据和评估方式。
6. **合同条款跨页面交叉核对**：岗位页、AcademicTransfer 页、大学信息栏、项目网站各自写的合同长度、FTE、scale、截止日期、入职日期，列成表；打架就都列出来并标 ⚠️，不自己挑一个。
7. **每篇引用的 PI 论文，PI 是作者还是评论者**：editorial、comment、review 类明确标出；作者位置写清，拿不准写"作者位置未核实 ⚠️"。
8. **组里的空白在哪**：这个组缺什么能力或数据，标明是推断。
9. **与申请人现在的单位、组和导师（<单位、组、导师姓名，取自 facts.md>）有没有可查证的关系**：合著、共同项目、同一 consortium；没查到就写"未见"，**不要把同所、同城说成有交情**。
10. **不得引用清单**：列出所有查不到或只有二手来源的数字、金额、人数、年份。

**格式**：中文，每项一个小标题，条目式；总长度不超过 1,500 字（第 1 项论文表和第 6 项条款表不计入）。最后单独列"⚠️ 未核验项汇总"。

---
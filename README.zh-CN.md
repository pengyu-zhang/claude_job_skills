# claude_job_skills

三个给 Claude 用的求职 skill，加上它们依赖的三个脚本和两份要你自己填的模板。

| skill | 干什么 |
|---|---|
| `job-search` | 找岗：扫公司招聘页、AcademicTransfer、Indeed、LinkedIn、Euraxess 等站，读 JD 全文，按你的标准打分，写进一张 Excel 求职表，每轮复核表里的旧岗 |
| `job-apply` | 投递：给一个岗位链接，读岗位页和团队背景，先出匹配分析等你确认，再做定向 CV 和求职信，然后帮你填网申表单，停在提交之前 |
| `job-search-cn` | 国内找岗：扫大厂校招和社招官网、Boss直聘、国聘、高校人才网，写进同一张表的「国内岗位」页 |

它们是从一份真实用过几个月的私人版本改出来的，个人内容都换成了模板。

## 先说清楚的几件事

- **按常驻荷兰写的。** `job-search` 和 `job-apply` 里的站点、搜索参数、远程岗的判法都以荷兰为准。住在别的国家，流程能用，站点和参数要自己换。
- **按机器学习、数据、科研岗写的。** 求职表里岗位类型的词表（MLE、DS、Postdoc 这些）在 `tools/tracker.py` 开头的常量里，别的行业自己改。
- **内容是中文的。** skill、脚本的提示、求职表的列名都是中文；对外材料（CV、求职信）是英文。
- **匿名版本身只测过脚本。** 三个脚本用样例数据跑通了；三个 skill 的完整流程在这个匿名版上没有整跑过。碰到问题欢迎提 issue。
- **站点会改版。** skill 里记了很多站点的接口和页面结构，都是写的时候的样子，过一阵总会有对不上的，让 Claude 当场重新摸。
- **它用的是你自己登录的浏览器。** 读的是你本来就能看到的岗位页，请求有间隔，遇到验证码停下来叫你。自动化访问是否合乎各站的使用条款，请你自己判断，后果自己承担。
- **不替你提交。** 登录、输密码、上传文件、勾同意框、过验证码、点提交，都留给你本人。

## 需要什么

- Claude，要能用 skill、能操作浏览器、能在你电脑的一个文件夹里跑命令。作者用的是 Claude 桌面应用（内置浏览器，加 Claude in Chrome 扩展备用）；Claude Code 配浏览器工具也行。
- Python 3 和 openpyxl（`pip install openpyxl`）。
- 做定向 CV 要 LaTeX，用 Overleaf 就行。

## 上手

1. **建一个 jobs 文件夹**，放在哪都行，把仓库里这些复制进去：

   ```
   jobs/
     tools/            ← 仓库的 tools/ 整个复制
     profile/          ← 仓库的 profile/ 整个复制
     cv_master.tex     ← templates/cv_master.tex
     cn_sites.md       ← docs/cn_sites.md（只在用 job-search-cn 时需要）
     applications/     ← 空文件夹，每个岗的材料会放在这里
   ```

2. **填两份模板。** `profile/job_profile.md` 写你收什么岗、怎么打分、搜哪些关键词、材料怎么写；`profile/facts.md` 写你的个人信息、项目和论文的事实与数字。里面是虚构人物 Alex Chen 的例子，照着换成你的。省事的办法：把你的 CV 和模板一起交给 Claude，让它先问你问题再起草。

   `facts.md` 值得认真写。助理写材料只认这个文件里的事实，这里写错，信里就错。

3. **换 CV 母版。** `cv_master.tex` 换成你的内容。`tailor_cv.py` 靠母版里的几处固定结构定位（About 段、求职意向行、标签行、项目块、Methods 行、发表列表），列在脚本开头；保留这些结构，版式随你改。

4. **配求职信检查。** 把 `tools/materials_config.example.json` 复制成 `tools/materials_config.json`，填上姓名、邮箱、联系行里必须出现的片段、你不想在信里看到的短语。

5. **建空表。** 在 jobs 文件夹里跑：

   ```
   python3 tools/tracker.py init job_tracker.xlsx
   ```

6. **装 skill。**
   - Claude 应用（claude.ai、桌面应用）：把 `skills/` 下每个文件夹各打成一个 zip（文件夹本身是 zip 的根），在 Customize > Skills 里上传。要先打开代码执行。详见官方说明：[Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude)、[How to create custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)。
   - Claude Code：把三个文件夹复制到 `~/.claude/skills/`。详见 [Claude Code 文档](https://code.claude.com/docs/en/skills)。

7. **开始用。** 让 Claude 能访问 jobs 文件夹，然后说"开始帮我找工作"（job-search）、"跑一遍国内找岗"（job-search-cn），或者给一个岗位链接说"我想投这个"（job-apply）。

   公司表一开始是空的。第一轮 `job-search` 会从各站搜到的岗里把值得盯的公司加进去，你也可以直接告诉 Claude 你想盯哪些公司。

## 仓库里有什么

```
skills/
  job-search/SKILL.md
  job-apply/SKILL.md
  job-search-cn/SKILL.md
profile/
  job_profile.md        你的求职要求（模板）
  facts.md              你的事实（模板）
tools/
  tracker.py            求职表的唯一写入工具：校验、判重、排序、自检
  tailor_cv.py          从 CV 母版生成定向版，只动文字、不动格式
  check_materials.py    求职信和 research statement 的机械检查
  materials_config.example.json
templates/
  cv_master.tex         CV 母版样例
  motivation_letter_example.md
docs/
  cn_sites.md           国内三十来个招聘站的读法
```

三个脚本的用法都写在各自开头的说明里。

## 求职表长什么样

`job_tracker.xlsx` 有七张表：学术岗位、工业岗位、国内岗位、已排除、公司、国内公司、说明。它只由 `tracker.py` 写，不要手改。

- 每个岗一行：优先级（High、Mid、Low）、状态（未投、已投、面试、被拒、Offer、关闭）、核验（读没读过雇主官网的岗位页）、截止日期、链接、备注里的一句复述和打分。
- 见过但不收的岗进「已排除」表，写明理由，下次再出现就跳过。
- 每次写入都会校验词表和链接、判重、整表重排、自检；出错就不写。

## 隐私

- `profile/`、`materials_config.json`、求职表、`applications/` 里都是你的个人信息，留在你自己的电脑上，别提交到公开仓库。
- 账号表只记站点、网址、用户名，不记密码。
- 证件号不要写进 `facts.md`。

## 许可

MIT，见 [LICENSE](LICENSE)。

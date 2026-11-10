# 求职要求

这是模板。下面的内容是虚构人物 Alex Chen 的例子：做能源时间序列预测的博士生，常驻荷兰，同时看荷兰和国内的岗。把每一节换成你自己的情况，节的标题别改，三个 skill 按标题找内容。写完删掉这一段。

怎么填省事：把你的 CV 和这份模板交给 Claude，让它先问你问题再起草，你改。

## 本地文件

都在 jobs 文件夹里。

- `job_tracker.xlsx`：求职表，七张：学术岗位、工业岗位、国内岗位、已排除、公司、国内公司、说明。只用 `tools/tracker.py` 写，不手改。
- `tools/`：`tracker.py`（写表、判重）、`tailor_cv.py`（做定向 CV）、`check_materials.py`（查求职信）。用法在各脚本开头。
- `cv_master.tex`：CV 母版。我自己维护，助理只读，不覆盖。
- `applications/<单位-岗位>/`：每个岗的材料。

## 收什么岗

学术岗和工业岗同等看待。求职表用来排投递顺序：收录范围内的岗都入表，优先级只决定先投谁。不收的岗写进「已排除」表并写明理由。标题写得明明白白的（PhD position、Head of）可以凭标题判，其余读完 JD 再定。

- **地域**：荷兰境内的岗，到岗、混合、远程都收。荷兰境外只收远程岗，而且 JD 允许从荷兰工作。雇主在欧盟和英国之外的，要它在荷兰有办公室，或者它自己的招聘板上有地点写荷兰的岗，才收。聚合站标的地点不作数，看 JD 正文。
- **学术岗**：收 Postdoc、Researcher、Research Engineer、大学里的研究软件工程师。不收 PhD、教职。
- **工业岗**：收机器学习、数据科学、预测相关的岗，Junior 到 Senior 都收。不收 Lead、Head、Director 及以上。
- **方向不沾边的不收**：纯前端、纯运维、别的学科的应用。
- **语言门槛**：荷兰语硬要求超过 A2 的不收，排除理由抄 JD 原句。只写 asset、plus、愿意学的不算硬要求。以雇主官网的荷兰语原页为准，聚合站的英文摘要常把语言要求删掉。
- **不影响收不收，也不降档**：薪资高低、级别、雇主有没有荷兰实体、JD 写不写担保签证。签证和雇佣主体到 offer 阶段再核。工作年限要求只影响打分。

## 方向和岗位分类

主线是时间序列预测和数据漂移下的模型监控，两个一作项目（GridCast、DriftWatch）。副线是数据清洗（MeterClean）和基准构建（RiverBench，合作）。

工业岗按匹配度分三类，同一档里按这个顺序排。引文是投这一类时用的一句话。

1. **预测**（能源、零售、物流的需求预测）。JD 里的词：forecasting、demand planning、time series。
   > I build forecasting models that keep working when the data behind them changes.
2. **模型监控和 MLOps**。JD 里的词：model monitoring、drift detection、ML platform。
   > I build monitors that catch a failing model before the errors arrive.
3. **一般的机器学习建模岗**。岗位最多，但不是主场。

学术岗看时间序列、分布漂移、能源系统这几个方向。

## 打分

读完 JD 正文先写一句复述：这岗每天干什么、用什么数据、交付什么。然后打三个分，各 0 到 3。

**任务重合**：这岗的核心任务和我做过的重合多少，看职责段，不看公司介绍。

- 3，就是主场：时间序列预测；模型上线后的漂移监测和重训。
- 2，主场的邻居：自己建模的常规建模岗；异常检测；数据质量。
- 1，只沾边：数据管线或平台工程带一点机器学习；主要交付洞察的分析岗。
- 0，不沾：纯报表、纯运维、别的学科的应用。

**证据**：这岗的核心要求，我能不能直接摆出项目和数字。

- 3，有一作论文，有公开代码或基准，有能引用的数字：GridCast、DriftWatch。
- 2，有项目和数字，但是合作项目，或者要靠迁移来解释：RiverBench、MeterClean。
- 1，只有工具层面的经验（Python、PyTorch、SQL）。
- 0，落在 facts.md「没用过、没做过的」里。

**差异化**：这岗要不要我的长处，我在候选人里稀不稀缺。

- 3，明确要研究能力，或者要的正好是别人不会的（漂移、无标签监控）。
- 2，不要求博士，但研究能力能直接变成产出：建模、评测设计、方法选型。
- 1，有三年经验的工程师更合适。
- 0，博士反而是负担：纯报表、纯交付型外包。

三项相加，7 分以上 High，4 到 6 分 Mid，3 分以下 Low。然后：

- **降一档**：JD 硬要求 3 年以上工业经验，或者要我没有的领域知识。
- **封顶 Mid**：没读到雇主官网或其招聘系统的岗位页；雇主匿名的猎头帖；级别是 Senior 而且 JD 写了年限要求。
- **同档里的顺序**：没有年限要求的在前，没有当地语言要求的在前，再按上面三类的顺序，再按发现日期，新的在前。

判 Low 要写清这岗实际在做什么，"正文没见到方向词"不算理由。

备注的格式：`复述：<干什么 / 数据 / 交付>｜任务X 证据Y 差异Z＝N → <档>。<降档或封顶的依据>`

## 搜索关键词

job-search 每一轮都把下面的词搜完。

- **标题初筛词**（扫公司招聘页时用）：machine learning、data scien、forecast、time series、research、applied scien
- **学术站长清单**（AcademicTransfer）：time series、forecasting、anomaly detection、distribution shift、energy systems、smart grid、machine learning、data science
- **学术站短清单**（Euraxess、jobs.ac.uk、academicpositions、ResearchGate）：machine learning、time series、forecasting、data science
- **工业岗位名**（Indeed、远程板）：data scientist、machine learning engineer、forecasting、applied scientist
- **LinkedIn 工业组**：data scientist、machine learning engineer、forecasting、demand planning、MLOps
- **LinkedIn 学术组**：postdoc、research software engineer、time series、researcher machine learning

## 投递

- 每次投递都做定向 CV，不用通用版。表单里有放求职信的位置（选填也算）就写信。
- CV 只交 `.tex`，我自己在 Overleaf 编译。改文字要保住页数，不缩字号、不缩留白。不发明母版里没有的内容，数字和母版一致。
- 学术岗的 CV：About 段按岗位重写，项目按相关性重排，发表全留。
- 工业岗的 CV：About 段讲工程和规模，发表列表用短版。
- 表单：页面有英文界面就先切英文。先查下面的账号表，有账号先登录。邮箱填 facts.md 里的求职邮箱。
- 表单里的个人题（称谓、性别、族裔、兵役、残障）：写上你希望助理怎么代填，哪些留给你自己。例：称谓 Mr.；自愿披露的题选不愿回答。
- 是否愿意搬家、各国的工作许可、最早入职时间：写上你的答案。例：荷兰境外一律 No；别国的工作许可照实答没有。
- 表单问到签证担保时怎么答：按你的居留情况写一段现成的话放在这里。

## 材料怎么写

对外材料用英文，清楚、简单、略正式。按你自己的语感改下面这些。

- 每段第一句直接说事，句子短，一段只说一件事。不用空过渡和浮夸的形容词，不写 unique、perfect、ideal candidate。不用破折号，日期范围除外。
- 自己的模型第一次出现，先说它是什么（"a load forecasting model called GridCast"）。
- 自己做过的事直接说，不加 may、partly 这类留余地的词。猜测就说是猜测。
- 差距照实写，直接说没有经验。
- 用项目和做法证明自己，不用形容词。结果数字最多一两个。
- 禁用的短语列在 `tools/materials_config.json` 里，新发现的加到那里。

**求职信**：一页，A4，11 号字。交 `.md`，我自己排版导出。称呼不写人名：学术岗 "Dear members of the hiring committee,"，工业岗 "Dear hiring team,"；落款 "Kind regards,"。五到六段：

1. 我是谁，申请哪个职位，什么时候能入职。
2. 最强的一个连接：先引岗位页的原话，再说自己做的是同一类问题。只写透一个。
3. 证据：一到三个最相关的项目。讲做了什么、怎么做的，段尾一句落到能带过去的思路。
4. 数据和合作（可以没有）。合作项目写明谁牵头，主语用 we。
5. 差距：第一句点明这段讲差距，照实列，最后一句说怎么补。
6. 收尾："Thank you for considering my application. I look forward to hearing from you."

`templates/motivation_letter_example.md` 是按这个结构写的样例。

**Research statement**（岗位要才写）：开头一段先讲问题本身，再讲自己的做法和最重要的发现，最后一句接到对方的项目。然后两到三个方向，主场放第一。每个方向写清问题、和已有工作的关系、第一个能做的实验、用什么数据怎么评。引对方的工作不超过三篇，不写没核过的数字。

**长度**：求职信和 research statement 的词数由 `check_materials.py` 报。表单开放题没有字数限制时 80–150 词。

## Offer

收到 offer，先把下面几项去官网或问 HR 核清，再答复。按你的国籍和居留情况增删。

- 雇主能不能为你办工作许可，走哪种许可，薪资够不够那种许可当年的门槛。
- 远程岗：合同签在哪个法人，有没有本国实体或者用哪家代雇公司，会不会要求搬家。
- FTE、合同长度要书面确认。同一个岗在不同页面上常写得不一样。
- 新许可的生效日和旧许可的到期日接不接得上，入职日照这个谈。

能谈的：级别和起薪、合同长度、FTE、入职日、搬家补贴、会议经费、设备。

## 国内岗

国内的岗记在求职表的「国内岗位」表，找岗用 job-search-cn。这里没写到的，照上面的规矩。不看国内岗的话删掉这一节。

- **收**：机器学习、数据、算法方向的研发岗和研究岗；科研院所的非教职研究岗；方向相关的实习。
- **不收**：方向不沾边的岗；总监及以上；博士后和高校教职。
- **硬门槛**：JD 写明的年龄、户籍、政治面貌、第一学历、毕业时间等要求，对照 facts.md 判。不满足的进已排除表，类别写"硬门槛"，理由抄原句；判不了的入表，标 ⚠️。
- **不影响收不收**：单位性质、城市、薪资、有没有编制、校招还是社招。
- **打分的调整**：国内表没有级别列，没有 Senior 封顶这一条。
- **搜索关键词**：时间序列、预测算法、异常检测、机器学习算法、数据挖掘
- 对外用哪个邮箱和手机号：写在 facts.md。

## 账号

不常用的求职站账号。新注册的站加一行。登录时助理只填用户名，密码我自己输；密码不记在这里，放密码管理器。

| 站点 | 网址 | 用户名 | 备注 |
|---|---|---|---|
| Example University（SAP SuccessFactors） | https://careers.example.edu | alex.chen@example.com | 全校岗位共用 |

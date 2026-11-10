# 事实

这是模板。下面是虚构人物 Alex Chen 的例子，人名、学校、论文和数字都是编的。换成你自己的，节的标题别改。写完删掉这一段。

这个文件是助理写材料、填表单时唯一的事实来源：这里没有的，助理不该写。数字和日期照原件抄，每个数字标上出处（论文的页码或表号），拿不准的标 ⚠️，助理不会引用带 ⚠️ 的条目。证件号这类东西不要放进来，表单里问到时自己填。

## 个人

| 字段 | 内容 |
|---|---|
| 姓名 | Alex Chen |
| 所在地 | Utrecht, the Netherlands |
| 手机 | +31 6 0000 0000 |
| 求职邮箱 | alex.chen@example.com |
| 个人主页 | https://alexchen.example.com |
| LinkedIn | https://www.linkedin.com/in/example |
| GitHub | https://github.com/example |
| 出生日期 | 表单问到时本人填 |

国内岗要用的（不看国内岗就删）：国内手机号、国内用的邮箱、政治面貌、户籍、毕业时间、第一学历的学校是否在 JD 常写的名单里。

## 现在的身份

- Northfield University，Data Systems Lab，计算机博士生，2022-09 起。导师 Prof. Dr. Jane Doe。
- 答辩计划在 2027 年春天。最早入职时间：2027-03。
- 居留和工作许可：写上你现在的情况，以及表单问到时怎么答。

## 教育

- **博士**：Northfield University，Computer Science，2022-09 至今。
- **硕士**：Lakeside Institute of Technology，MSc in Data Science，2019-09 至 2022-06。
- **本科**：Example College，BSc in Mathematics，2015-09 至 2019-06。

## 语言

- 英语：流利。
- 荷兰语：基础。简历写 "Dutch (basic)"。

## 技能

- 编程：Python、SQL、Bash、Git、Linux。
- 机器学习：PyTorch、scikit-learn、NumPy、Pandas。
- 做过的方向：time series forecasting, anomaly detection, distribution shift, probabilistic models。

没用过、没做过的。写材料和评估岗位时照实说，不写成会：

- 流式系统（Kafka、Flink）。
- 云平台上的生产部署。模型都是在研究项目里训练和运行的。
- 深度强化学习。
- 工业界的工作年限是零。

## 对外怎么说

身份：

> I am a PhD candidate in Computer Science at Northfield University, supervised by Prof. Jane Doe.

研究：

> My research is about forecasting models that stay accurate when the data changes.

论文进度：

> I have finished writing my thesis.

不该说的：把会让人误解你身份的说法列在这里，同时加进 `tools/materials_config.json` 的 `identity_red_lines`。

## 研究主线

预测模型在数据变化以后怎么保住精度。GridCast 管模型本身，DriftWatch 管上线以后的监控，RiverBench 和 MeterClean 是数据这一头。

## 项目和论文

写进对外材料的数字，以带编号的条目为准（如 GC-R02）。助理写完会列一张数字引用清单：材料里的数字、条目编号、精确值。

I 和 we：一作且自己主导的部分可以用 I；合作者牵头的项目用 we，名字同时加进 `tools/materials_config.json` 的 `non_first_author_works`。

### GridCast

**元数据**：GridCast: Load Forecasting Under Distribution Shift。Example Conference 2025。Alex Chen, Jane Doe。一作。

**定位**：把负荷里慢的季节结构和快的局部变化分开建模，数据变了只重训快的那部分。

**方法**：两条分支，慢分支冻结，快分支每月重训；用过去一年的数据做验证。

**贡献 / I-we**：我提出想法、实现、做实验、写作；导师参与讨论和修改。允许 I。

**结果编号**

- GC-R01: 数据是约 12,000 个智能电表三年的读数（表 1，第 5 页）。
- GC-R02: 训练和测试隔一年时，误差比最强基线低 12%（表 3，第 7 页）。

**局限**：只在一个国家的数据上验证过。

### DriftWatch

**元数据**：DriftWatch: Monitoring Forecast Quality Without Labels。在审。Alex Chen, Jane Doe。一作。

**定位**：真实值晚几天才到，所以只用输入的统计量估计预测误差，超出训练范围就报警。

**贡献 / I-we**：全部由我完成。允许 I。

**结果编号**

- DW-R01: 在 GridCast 的基准上，10 次注入的传感器故障里有 9 次在一天内报警（表 2，第 6 页）。

### RiverBench

**元数据**：RiverBench: A Benchmark for Hydrological Forecasting。Example Workshop 2024。Sam Lee, Alex Chen, Jane Doe。二作。

**定位**：40 个站点十年的河流水位数据，加上固定划分的预测任务。

**贡献 / I-we**：Sam Lee 牵头。我负责数据清洗和基线实验。用 we。

**结果编号**

- RB-R01: 40 个站点，十年（第 3 页）。

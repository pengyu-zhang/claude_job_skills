# 国内招聘站读法

job-search-cn 用的参考：各家招聘官网在浏览器里怎么读岗位列表和正文。都是在已打开该站的浏览器标签页里做同源请求，读公开的岗位信息，不绕登录和验证码。

这些是 2026 年秋天记下的。站点会改版，接口、参数、翻页上限都可能变；对不上时按 job-search-cn 里「摸新站的通用手法」重新摸，把新读法写进求职表「国内公司」表的备注。请求放慢，别给人家的站添负担。

每条的格式：入口网址，然后是读法。

## 互联网公司

**腾讯**（校招含青云计划、社招）
入口 https://join.qq.com/post.html
校招：`POST /api/v1/position/searchPosition` 拉全量，详情 `GET /api/v1/jobDetails/getJobDetailsByPostId?postId=`（请求体和字段见 job-search-cn）。社招：https://careers.tencent.com/search.html ，岗位页 `https://careers.tencent.com/jobdesc.html?postId=<id>`。

**字节跳动**（校招、社招）
入口 https://jobs.bytedance.com/campus/position
校招：`POST /api/v1/search/job/posts`，带 `x-csrf-token`（cookie `atsx-csrf-token`）和 `portal-channel: campus` 头，不需要 `_signature`；keyword 是模糊匹配，按 recruit_type 分正式和实习。社招：https://jobs.bytedance.com/experienced/position ，同一接口加 `portal_type=2&portal_entrance=1`，头 `website-path: society`、`Portal-Channel: office`（写 experienced 会报站点不存在），按职位类别拉全量；岗位页 `/experienced/position/<id>/detail`。

**阿里巴巴**（校招、社招，含阿里星等专项）
入口 https://campus-talent.alibaba.com/campus/position
校招：新一届在 campus-talent.alibaba.com（talent.alibaba.com、careers.aliyun.com 上的旧批次显示 0）。同源 `POST /position/search?_csrf=<从页面资源请求里取>`，body `{channel:'campus_group_official_site',language:'zh',batchId:'<批次号>',categories:'',deptCodes:[],key:'',pageIndex,pageSize:50,regions:'',subCategories:'',shareType:'',shareId:'',myReferralShareCode:''}`，列表直接带 description、requirement；岗位页 `/campus/position/<id>`。批次号每届不同，从页面网址的 `batchId` 取；日常实习、研究型实习各有自己的批次号。
社招：集团总站 https://talent.alibaba.com/off-campus/position-list?lang=zh 汇总各 BU，接口同上但 `channel:'group_official_site'`、batchId 留空，可按 subCategories 筛类别，单次结果上限 500 条；岗位页 `/off-campus/position-detail?positionId=<id>`。各 BU 另有独立站（淘天 talent.taotian.com、阿里云 careers.aliyun.com、阿里国际 aidc-jobs.alibaba.com、高德 talent.amap.com、菜鸟 talent.cainiao.com 等），可以补读集团站类别之外的岗。

**蚂蚁集团**（校招、社招，含蚂蚁星）
入口 https://talent.antgroup.com/campus-full-list
校招：`POST https://hrcareersweb.antgroup.com/api/campus/position/search?ctoken=<cookie 里的 ctoken>`，body `{channel:'campus_group_official_site',language:'zh',regions:'',subCategories:'',bgCode:'',pageIndex,pageSize:30,recruitType:[],batchIds:[]}`（pageSize 超过 30 报"系统繁忙"），一次返回全部批次，列表直接带 description、requirement、graduationTime、batchName；岗位页 `/campus-position?positionId=<id>`。实习岗的毕业时间窗各不相同，逐条核对。
社招：talent.antgroup.com/off-campus，`POST https://hrcareersweb.antgroup.com/api/social/position/search?ctoken=<同上>`，body `{regions:'',categories:'',subCategories:'',bgCode:'',socialQrCode:'',pageIndex,pageSize:30,channel:'group_official_site',language:'zh'}`（language 用 en 只显示海外岗）；按 categories 文本筛类别；岗位页 `/off-campus-position?positionId=<id>`。

**美团**（校招、社招，含北斗计划）
入口 https://zhaopin.meituan.com/web/position?hiringType=2_1
同源 `POST /api/official/job/getJobList`，body `{page:{pageNo,pageSize:100},jobShareType:'1',keywords:'',cityList:[],department:[],jfJgList:[],jobType:[],typeCode:[<招聘类型>],specialCode:[]}`，pageSize 上限 100。typeCode 决定招聘类型：`'1'` 应届、`'2'` 转正实习、`'6'` 日常实习、`'3'` 社招；jobType 字段不起作用。列表直接带 jobDuty、jobRequirement、jobFamily/jobFamilyGroup，按 jobFamilyGroup 筛类别，再按名称补读。社招的 workYear 多为空，年限看 JD 正文。岗位页 `/web/position/detail?jobUnionId=<id>&highlightType=campus`（社招 social）。

**京东**（校招、社招，含 TGT）
入口 https://campus.jd.com/#/jobs
校招：同源 `POST /api/wx/position/page?type=present`（应届）、`type=talent`（TGT）、`type=internship`（实习），Content-Type 必须是 `application/json;charset=UTF-8`，body `{pageIndex,pageSize:10,parameter:{}}`；pageSize 只能 10，totalNumber 比实际多，翻到返回不足 10 条为止；列表直接带 workContent、qualification；岗位页 `/#/details?id=<publishId>`。
社招：https://zhaopin.jd.com/web/job/job_info_list/3 ，同源 `POST /web/job/job_list`，表单 pageIndex、pageSize（最大 100）、`workCityJson:'[]'`、`jobTypeJson:'[]'`（研发类填 `["YANFA"]`）、`jobSearch:''`、`depTypeJson:'[]'`，返回数组直接带 workContent、qualification。没有单岗详情页，表里的链接用列表页加 `?requirementId=<id>` 区分。社招不给年限字段，看正文。

**快手**（校招、社招，含快Star）
入口 https://campus.kuaishou.cn/recruit/campus/e/#/campus/jobs
校招：`POST /recruit/campus/e/api/v1/open/positions/simple`，body `{pageNum,pageSize:100,recruitSubProjectCodes:[届别代码]}`，列表直接带 description、positionDemand；届别代码查 `GET /recruit/campus/e/api/v1/dictionary/batch?types=recruitSubProject`；岗位页 `/recruit/campus/e/#/campus/job-info/<id>`。
社招：zhaopin.kuaishou.cn，列表接口 `/recruit/e/api/v1/open/positions/simple` 要带签名头（sign、signTimestamp），直接调不通；在页面上翻页，从页面发出的请求里读结果。岗位页 `/recruit/e/#/official/social/job-info/<id>`。社招和校招的岗位编号会撞号。

**小红书**（校招、社招，含 REDstar）
入口 https://job.xiaohongshu.com/campus/position
`POST /websiterecruit/position/pageQueryPosition`，body `{pageNum,pageSize:100,recruitType:'campus'}`（社招 `'social'`），列表带 duty、qualification、directionName/subDirectionName、jobProjectName。校招里常规校招、专项、实习混在一起，按 jobProjectName 分；专项和常规校招常是同一岗的两版，收一版，另一版记重复。岗位页 `/campus/position/<positionId>`、`/social/position/<positionId>`。社招没有经验字段，年限看正文。

**拼多多**（校招）
入口 https://careers.pddglobalhr.com/campus/grad
`POST /api/careers/api/recruit/position/list`，body `{jobList:['technology'],page,pageSize:100,t:null}`（类别码见 `/api/careers/api/recruit/position/detail/type`），列表带 jobDuty；实习用 `/position/train/list`；岗位页 `/campus/grad/detail?positionId=<uuid>`。官网没有社招入口。

**滴滴**（校招、社招）
入口 https://campus.didiglobal.com/campus_apply/didiglobal/96064#/jobs
校招：Moka 系统，接口返回加密，读页面：`#/jobs?page=N&pageSize=50`，岗位卡片的链接带 `#/job/<uuid>`，卡片文字含完整职责要求；有限投次数。
社招：https://talent.didiglobal.com/social ，`GET /recruit-portal-service/api/job/front/list?page=N&size=100&jobType=<码>`（size 最大 100；类型码见 `/recruit-portal-service/api/job/jdpublish/confirm/listJdTypes`），列表直接带 jobDuty、jobQualification；岗位页 `/social/jobDetail?jdId=<jdId>`。

**百度**（校招、社招，含 AIDU）
入口 https://talent.baidu.com/jobs/list?recruitType=GRADUATE
内置浏览器白屏，用本地 Chrome。同源 `POST /httservice/getPostListNew`，form `recruitType=GRADUATE|SOCIAL|INTERN&pageSize=10&curPage=N&keyWord=&projectType=`（pageSize 只能 10），列表直接带 workContent、serviceCondition、postType、projectType；社招没有细分类别，按 postType 加名称关键词筛；岗位页 `/jobs/detail/<GRADUATE|INTERN|SOCIAL>/<postId>`。Chrome 扩展的 JS 返回值过长会截断，批量数据写进页面的 pre 元素再读页面文字。

**哔哩哔哩**（校招、社招）
入口 https://jobs.bilibili.com/campus/positions?type=3
请求头：`X-AppKey: ops.ehr-api.auth`、`X-UserType: 2`、`X-Channel: campus`（社招 social）、`X-CSRF: <先带前三个头 GET /api/auth/v1/csrf/token，取返回的 data>`。校招 `POST /api/campus/position/positionList`，社招 `POST /api/srs/position/positionList`，body `{pageSize:100,pageNum,positionName:'',postCode:[],postCodeList:[],workLocationList:[],workTypeList:[],positionTypeList:[],deptCodeList:[],recruitType:null,practiceTypes:[],onlyHotRecruit:0}`；列表带 positionDescription；按 postCodeName 加名称筛。岗位页 `/campus/positions/<id>`、`/social/positions/<id>`。校招列表页直接打开常加载失败，先开首页再调接口。

**网易**（互联网校招、互娱校招、雷火校招）
入口 https://campus.163.com/app/job/position?id=103
互联网：`GET /api/campuspc/position/getJobList?pageSize=200&currentPage=1&projectId=<项目号>`，带 positionDescription、positionRequirement；项目列表 `/api/campuspc/project/navigation/list`；岗位页 `/app/detail/index?id=<id>&projectId=<项目号>`。互娱在 campus.game.163.com，同一套系统。雷火在 https://leihuo.163.com/campus/ 。社招 hr.163.com 对海外 IP 返回 404，在国内网络下再扫。

**科大讯飞**（校招、社招，含星火X）
入口 https://iflytek.zhiye.com/campus/jobs
北森系统：`POST /api/Jobad/GetJobAdPageList`，body `{PageIndex:0起,PageSize:100,Category:['2'],KeyWords:'',SpecialType:0,PortalId:''}`，列表带 Duty、Require。Category：1 社招、2 校招，专项计划另有编号。岗位页：校招 `/campus/detail?jobAdId=<uuid>`，社招 `/social/detail?jobAdId=<uuid>`。

**同花顺**（校招、社招）
入口 https://campus.10jqka.com.cn/job/list?type=school
`GET /api/v3/school_recruitment/apply/apply_list?applyName=&bases=&page=N&pageCount=10&applyColonyId=&applyRecruitmentSeriesIds=&type=school`（pageCount 只能 10；社招把 type 换成 social），列表直接带 intro、requirement；岗位页 `/job/detail?id=<id>`。

**华为**（国内校招）
入口 https://career.huawei.com/cn/campus-recruitment-job-list?recruitmentType=FRESH_GRADUATE
国内校招在 career.huawei.com/cn（reccampportal 是国际站，看不到国内岗），要登录。岗位分方向，方向和 JD 要点进岗位再看；岗位页 `/cn/job-details?advertisementId=<id>`。登录后在页面上翻页读。

**亚马逊中国**（校招、社招）
入口 https://www.amazon.jobs/en/search?country=CHN
`GET /en/search.json?country=CHN&result_limit=100&offset=N`，按 job_category 筛；岗位页 `/en/jobs/<id>`。

## 运营商和央国企

**国聘**（央国企聚合）
入口 https://www.iguopin.com/job
`POST https://gp-api.iguopin.com/api/jobs/v1/recom-job`，body `{search:{page,page_size,keyword,nature:['115xW5oQ']},recom:{update_time:true,company_nature:true,hot_job:true}}`（这个 nature 是校招），头 `Device: pc`、`Version: 5.0.0`、`Subsite: iguopin`。page_size 写 50 实际只回 20 条，按 20 翻页。关键词是模糊匹配，召回很杂，而且每次召回不完全一样：逐条读 JD，判重除了编号还要按"单位+标题"。岗位页 `/job/detail?id=<job_id>`。国聘上的帖记聚合站；单位把自己的校招官网托管在国聘子站上的（如下面的联通），那是单位自己的招聘系统，记官网JD。限流时报"当前访问人数过多"，请求间隔 300ms 以上。

**中国联通**（校招、社招，国聘托管）
入口 https://zglt.iguopin.com/job
`POST https://gp-api.iguopin.com/api/jobs/v1/project-job`，头同国聘，body `{page,page_size:100,source:"s_job_list",company_id:[<单位ID>],project_id:[<校招项目号>]}`。全量拉取翻页会重复漏条，要按单位拉；单位 ID 表用 `POST /api/company/index/v1/project-company` 或 `GET /api/company/organization/v1/tree?company_id=<集团ID>` 取。去掉 project_id 按单位拉，能拿到校招项目之外各单位自招的岗。字段 contents 是完整 JD。岗位页 `www.iguopin.com/job/detail?id=<job_id>`。校招项目有限投数。

**中国移动**（校招、社招）
入口 https://job.10086.cn
校招：单位列表 `/personal/campus/campus_job_list.html?cId=<单位号>`。社招：`/personal/job/` 列表（`ul.tbs a[href*=detail.html]`，一行里依次是岗位、单位、地点、类别、经验、学历、性质、人数、发布日期），详情 `/personal/job/detail.html?id=<uuid>`，用同源隐藏 iframe 读。搜索接口带签名，不直接调。navigate 会把网址里的 `code=` 打码，带 code 的地址在页面 JS 里拼。投递要手机验证。

**北汽集团**（校招、社招、海外人才）
入口 https://baicgroup.zhiye.com/campus/jobs
北森系统：`POST /api/Jobad/GetJobAdPageList`，body `{PageIndex,PageSize:100,Category:['1' 社招/'2' 校招/'3' 实习/'4' 海外],KeyWords:'',SpecialType:0,PortalId:''}`，列表带 Duty、Require；岗位页 `/campus|social|overseas/detail?jobAdId=<uuid>`。岗位很多，按关键词筛读。

## 实验室和研究院

**上海人工智能实验室**（校招、社招）
入口 https://www.shlab.org.cn/joinus/campus
`GET https://www.shlab.org.cn/api/getJobList?mode=campus（社招 mode=social）&jobFunction=&location=&jobType=&subject=&keyword=&page_token=<上页返回>&limit=10`（limit 大于 10 报 Bad Request），返回带 description、requirement、subject、job_department；接口允许跨域。岗位页 `/joinus/detail/<id>?mode=campus`（社招 social）。

**之江实验室**（校招、社招）
入口 https://talents.zhejianglab.com
wecruit 系统：`POST /wecruit/positionInfo/listPosition/<SU套件号>?iSaJAx=isAjax&request_locale=zh_CN`，form `isFrompb=true&recruitType=<1 校招(含实习)/2 社招/12 博士后>&pageSize=<校招 12、社招 10>&currentPage=N`。pageSize 必须和服务器页大小一致，否则翻页会漏。详情 `POST /wecruit/positionInfo/listPositionDetail/<SU套件号>?iSaJAx=isAjax&request_locale=zh_CN`，body `postId=<id>`，返回 workContent、serviceCondition。SU 套件号在入口页的网址里。校招和社招常有同岗双挂。

**鹏城实验室**
入口 https://hr.pcl.ac.cn/
wecruit 系统，读法同之江，套件号换成它自己的，pageSize=10。

**北京智源人工智能研究院**、**北京通用人工智能研究院**
入口在 app.mokahr.com 的 campus-recruitment 和 social-recruitment 页（从各自官网的招聘入口跳转）。
Moka 系统，读页面：列表收 `a[href*="#/job/"]`，在页面里改 `location.hash` 逐个打开详情读 innerText。两家都有限投数。

## 聚合站

**高校人才网**（科研院所研究岗补漏）
入口 https://www.gaoxiaojob.com/
关键词搜索要登录，不用。职位列表 `GET /home/change-latest-job?columnId=<栏目>&majorId=<学科>&page=N`（不用登录，每页 12 条，返回 HTML 片段；列表里的"已下线"是模板文字）。学科和栏目的编号从页面筛选器的链接里取。详情 `/job/detail/<id>.html`；公告 `/announcement/detail/<id>.html` 正文末尾的"来源链接"是单位官网的原公告，读了原公告才记官网JD；`/announcement/job-list?id=<公告id>` 列出整份公告的全部职位。

Boss直聘、猎聘、牛客的读法写在 job-search-cn 的正文里。

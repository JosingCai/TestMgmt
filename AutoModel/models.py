# models.py
# 有一个数据表，就对应有一个模型
from django.db import models  # 模型类要继承models.Model类


# 第一个元素是存储在数据库里面的值
# 第二个元素是页面显示的值
YES_NO = (
    ('yes', "yes"),
    ('no', "no")
    )
HTTP_METHODS = (
    ('get', "get"),
    ('post', "post"),
    ('put', "put"),
    ('delete', "delete")
    )
TREU_FALSE = (
    ('True', "True"),
    ('False', "False")
    )
HTTP_HTTPS = (
    ('http', "http"),
    ('https', "https"),
    )

# Create your models here.
class Host(models.Model):
    USER_MODE = (
    ('uam', "uam"),
    ('native', "native"),
    ('uc', "uc"),
    )
    TEST_MODE = (
    ('normal', "normal"),
    ('abnormal', "abnormal"),
    ('regression', "regression"),
    ('all', "all"),
    )
    project_id = models.CharField(max_length=255,verbose_name="产品/版本名称",
        help_text="请输入产品名称", primary_key=True)
    ip = models.GenericIPAddressField(blank=True, null=True)
    protocol = models.CharField(max_length=5,choices=HTTP_HTTPS,verbose_name="协议",
        default="http", help_text="请选择协议http/https")
    auth = models.CharField(max_length=3, choices=YES_NO,verbose_name="是否鉴权",
        default="yes", help_text="请选择鉴权yes/no")
    prepath = models.CharField(max_length=255,blank=True,verbose_name="api前缀",
        default="", help_text="请输入api前缀")
    testmode = models.TextField(verbose_name="测试模式", choices=TEST_MODE, help_text="请选择测试模式",
        blank=True, null=True, default="normal")
    debug = models.CharField(max_length=5, choices=TREU_FALSE,verbose_name="调试模式",
        default="False", help_text="请选择模式True/False")
    threading = models.CharField(max_length=5, choices=TREU_FALSE,verbose_name="是否多线程",
        default="False", help_text="请选择模式True/False")
    usermode = models.CharField(max_length=6, choices=USER_MODE,verbose_name="用户模式",
        default="uam", help_text="请选择模式uam/native/uc")
    dbconfig = models.CharField(max_length=255, blank=True,null=True,verbose_name="目标数据库",
        default="", help_text="请输入目标数据库信息,e.g.: user:pasword:10.x.x.x:3306:databasename")
    token = models.TextField(verbose_name="token", help_text="请输入token信息",
        blank=True, null=True, default="")

    def __str__(self):
         return self.project_id

    class Meta:
        db_table = 'host'
        verbose_name = '测试环境'
        verbose_name_plural = "测试环境"

class TestReport(models.Model):
    allCount = models.IntegerField(blank=True, null=True,verbose_name="API总数")
    automatableCount = models.IntegerField(blank=True,null=True,verbose_name="可自动化API总数")
    unautomatableCount = models.IntegerField(blank=True,null=True,verbose_name="不可自动化API总数")
    autoTestCount = models.IntegerField(blank=True,null=True,verbose_name="自动测试API总数")
    unTestCount = models.IntegerField(blank=True,null=True,verbose_name="未自动化测试API总数")
    passCount = models.IntegerField(blank=True,null=True,verbose_name="测试通过API总数")
    failCount = models.IntegerField(blank=True,null=True,verbose_name="测试失败API总数")
    autoPer = models.FloatField(max_length=8,blank=True,null=True,verbose_name="自动化测试百分比")
    passPer = models.FloatField(max_length=8,blank=True,null=True,verbose_name="自动化测试成功百分比")
    failPer = models.FloatField(max_length=8,blank=True,null=True,verbose_name="自动化测试失败百分比")
    # project = models.CharField(max_length=255,blank=True,null=True,verbose_name="产品/版本名称")
    project = models.ForeignKey(Host, blank=True,null=True,on_delete=models.CASCADE,verbose_name="关联项目")
    countTime = models.DateTimeField(primary_key=True, verbose_name="统计时间",db_index=True)
    
    def __str__(self):
         return self.countTime

    class Meta:
        db_table = 'api_sum_up'
        verbose_name = 'API结果统计'
        verbose_name_plural = "API结果统计"


class Dependency(models.Model):
    case_id = models.CharField(max_length=255, primary_key=True,verbose_name="用例ID",
        help_text="请输入用例ID")
    runNum= models.IntegerField(default=1,verbose_name="执行次数",
        help_text="请输入执行的次数, 0代表不执行, 1代表全遍历执行, 其他代表执行的指定次数")
    beforeCase = models.CharField(max_length=255,blank=True,verbose_name="前置用例",
        help_text='请输入前置用例,e.g: ["get_/path", "post_/path"]')
    afterCase= models.CharField(max_length=255,blank=True,verbose_name="后置用例",
        help_text='请输入后置用例,e.g: ["get_/path", "post_/path"]')
    outVars= models.CharField(max_length=255,blank=True,verbose_name="提供依赖变量",
        help_text='请定义依赖变量,e.g: {"id: "content-id"}')
    chkVars= models.CharField(max_length=255,blank=True,verbose_name="验证返回变量",
        help_text='请转义验证变量,e.g: {"number: "content-id"}')
    param_def= models.CharField(max_length=255,blank=True,verbose_name="依赖用例",
        help_text='请定义依赖用例,e.g: ["get_/path", "post_/path"]')
    raw =  models.TextField(blank=True,null=True,verbose_name="api信息",
        default="", help_text="请输入API信息")
    project = models.ForeignKey(Host, blank=True,null=True,on_delete=models.CASCADE,verbose_name="关联项目")
    def __str__(self):
        return self.case_id

    class Meta:
        db_table = "dependency"
        ordering = ['case_id']  #ordering['-id'] id按降序排列 排序会增加数据库开销
        verbose_name = '用例依赖'
        verbose_name_plural = "用例依赖"
        unique_together = ('project','case_id')

class Result(models.Model):
    case_id = models.CharField(max_length=255,primary_key=True)
    requestVars = models.TextField(blank=True,null=True)
    result = models.CharField(max_length=255,blank=True)
    outVars = models.TextField(blank=True,null=True,verbose_name="输出信息",
        default="", help_text="请输入输出信息")
    project = models.ForeignKey(Host, blank=True,null=True,on_delete=models.CASCADE,verbose_name="关联项目")
    def __str__(self):
        return self.case_id

    class Meta:
        db_table = "result"
        ordering = ['case_id']
        verbose_name = '测试结果'
        verbose_name_plural = "测试结果"
        unique_together = ('project','case_id')

class Source(models.Model):
    APIFunction = models.CharField(max_length=255,blank=True)
    protocol = models.CharField(max_length=5,choices=HTTP_HTTPS)
    http_method = models.CharField(max_length=6,choices=HTTP_METHODS)
    path = models.CharField(max_length=255)
    header = models.CharField(max_length=255,blank=True)
    pathVar = models.CharField(max_length=255, blank=True)
    queryParam = models.CharField(max_length=255, blank=True)
    body = models.CharField(max_length=255, blank=True)
    response = models.TextField(blank=True)
    case_id = models.CharField(max_length=255, primary_key=True)
    project = models.ForeignKey(Host, blank=True,null=True,on_delete=models.CASCADE,verbose_name="关联项目")
    def __str__(self):
        return self.case_id

    class Meta:
        db_table = "source"
        ordering = ['case_id']
        verbose_name = 'API源信息'
        verbose_name_plural = "API源信息"
        unique_together = ('project','case_id')

class ComVar(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    value = models.TextField(blank=True)
    project = models.ForeignKey(Host, blank=True,null=True,on_delete=models.CASCADE,verbose_name="关联项目")
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = "comvar"
        ordering = ['name']
        verbose_name = '公用变量'
        verbose_name_plural = "公用变量"
        unique_together = ('project','name')

class TestDetail(models.Model):
    case_id = models.CharField(max_length=255)
    APIFunction = models.CharField(max_length=255,blank=True)
    url = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    response = models.TextField(blank=True)
    failReason = models.TextField(blank=True)
    testTime = models.CharField(max_length=255,blank=True)
    testResult = models.CharField(max_length=255,blank=True)
    project = models.ForeignKey(Host, blank=True,null=True,on_delete=models.CASCADE,verbose_name="关联项目")
    
    def __str__(self):
        return self.case_id

    class Meta:
        db_table = "testdetail"
        ordering = ['case_id']
        verbose_name = 'API测试详情'
        verbose_name_plural = "API测试详情"
        #unique_together = ('project','case_id')

class CaseTestCount(models.Model):
    case_id = models.CharField(max_length=255, primary_key=True)
    APIFunction = models.CharField(max_length=255)
    runTimes = models.IntegerField(blank=True)
    testTimes = models.IntegerField(blank=True)
    passTimes = models.IntegerField(blank=True)
    failTimes = models.IntegerField(blank=True)
    untestTimes = models.IntegerField(blank=True)
    testResult = models.CharField(max_length=255,blank=True)
    failReason = models.CharField(max_length=255,blank=True)
    project = models.ForeignKey(Host, blank=True,null=True,on_delete=models.CASCADE,verbose_name="关联项目")
    
    def __str__(self):
        return self.case_id

    class Meta:
        db_table = "casetestcount"
        ordering = ['case_id']
        verbose_name = 'API测试统计'
        verbose_name_plural = "API测试统计"
        unique_together = ('project','case_id')

class ProductInfo(models.Model):
    # 产品线信息表

    product_name = models.CharField(
        max_length=32, verbose_name="产品线名称",
        help_text="请输入产品线名称", db_index=True)
    # 产品线名称，并创建索引
    product_describe = models.TextField(
        verbose_name="产品描述", help_text="请输入产品描述",
        blank=True, null=True, default="")
    # 产品描述
    product_manager = models.CharField(
        max_length=11, verbose_name="产品经理", help_text="请输入产品经理")
    # 产品经理
    developer = models.CharField(
        max_length=11, verbose_name="开发人员",
        blank=True, null=True, default="", help_text="请输入开发人员")
    # 开发人员
    tester = models.CharField(
        max_length=11, verbose_name="测试人员",
        blank=True, null=True, default="", help_text="请输入测试人员")
    # 测试人员
    create_time = models.DateTimeField(
        auto_now_add=True, blank=True, null=True, verbose_name="创建时间")
    # 创建时间
    update_time = models.DateTimeField(
        auto_now=True, blank=True, null=True, verbose_name="修改时间")

    # 修改时间

    class Meta:
        db_table = 'product_info'  #To override the database tablename,use the db_table parameter in class Meta.

        verbose_name = '产品线列表'
        verbose_name_plural = "产品线列表"

    def __str__(self):
        return self.product_name

    def module_sum(self):
        # 用例总数
        return self.products.all().count()

    # 利用外键反向统计语句

    module_sum.short_description = '<span style="color: red">模块总数</span>'
    module_sum.allow_tags = True  #allow_tags attribute on methods of ModelAdmin has been deprecated


class ModuleInfo(models.Model):
    # 模块信息表

    module_group = models.ForeignKey(
        ProductInfo, on_delete=models.CASCADE,
        verbose_name="产品线", related_name="products",
        help_text="请选择产品线")
    # 外键，关联产品线id
    module_name = models.CharField(
        max_length=32, verbose_name="模块名称",
        help_text="请输入模块名称", db_index=True)
    # 模块名称，并创建索引
    module_describe = models.TextField(
        verbose_name="模块描述", help_text="请输入模块描述",
        blank=True, null=True, default="")
    # 模块描述
    create_time = models.DateTimeField(
        auto_now_add=True, blank=True, null=True, verbose_name="创建时间")
    # 创建时间
    update_time = models.DateTimeField(
        auto_now=True, blank=True, null=True, verbose_name="修改时间")

    # 修改时间

    class Meta:
        db_table = 'module_info'

        verbose_name = '模块列表'
        verbose_name_plural = "模块列表"

    def __str__(self):
        return self.module_name


class CaseGroupInfo(models.Model):
    # 用例组信息表

    case_group_name = models.CharField(
        max_length=32, verbose_name="用例组名称",
        help_text="请输入用例组名称", db_index=True)
    # 用例组名称，并创建索引
    case_group_describe = models.CharField(
        max_length=255, verbose_name="用例组描述",
        blank=True, null=True, default="", help_text="请输入用例组描述")
    # 用例组描述
    create_time = models.DateTimeField(
        auto_now_add=True, blank=True, null=True, verbose_name="创建时间")
    # 创建时间
    update_time = models.DateTimeField(
        auto_now=True, blank=True, null=True, verbose_name="修改时间")

    # 修改时间

    class Meta:
        db_table = 'case_group_info'

        verbose_name = '用例组列表'
        verbose_name_plural = "用例组列表"

    def __str__(self):
        return self.case_group_name

    def case_sum(self):
        # 用例总数
        return self.groups.all().count()

    # 利用外键反向统计语句

    case_sum.short_description = '<span style="color: red">用例总数</span>'
    case_sum.allow_tags = True


class InterfaceInfo(models.Model):
    # 用例信息表

    mode_choice = (
        ("GET", "GET"),
        ("POST", "POST"),
        ("PUT", "PUT"),
        ("DELETE", "DELETE"),
        ("PATCH", "PATCH"),
    )
    # 请求方式枚举
    # 第一个元素是存储在数据库里面的值
    # 第二个元素是页面显示的值
    body_choice = (
        ("x-www-form-urlencoded", "application/x-www-form-urlencoded"),
        ("json", "application/json"),
        ("form-data", "multipart/form-data"),
        ("xml", "text/xml"),
    )
    # 请求体类型枚举
    assert_choice = (
        ("包含", "包含"),
        ("相等", "相等"),
    )
    # 断言方式枚举
    regular_choice = (
        ("开启", "开启"),
        ("不开启", "不开启"),
    )
    # 是否开启正则表达式枚举

    case_group = models.ForeignKey(
        CaseGroupInfo, on_delete=models.CASCADE,
        verbose_name="用例组", related_name="groups",
        help_text="请选择用例组")
    # 外键，关联用例组id
    case_name = models.CharField(
        max_length=32, verbose_name="用例名称",
        help_text="请输入用例名称", db_index=True)
    # 用例名称，并创建索引
    interface_url = models.CharField(
        max_length=255, verbose_name="接口地址", help_text="请输入接口地址")
    # 接口地址
    request_mode = models.CharField(
        choices=mode_choice, max_length=11,
        verbose_name="请求方式", default="GET",
        help_text="请选择请求方式")
    # 请求方式
    request_parameter = models.TextField(
        verbose_name="请求参数", blank=True, null=True,
        help_text="请输入字典格式的请求参数", default="")
    # 请求参数
    request_head = models.TextField(
        verbose_name="请求头", blank=True, null=True,
        help_text="请输入字典格式的请求头", default="")
    # 请求头
    body_type = models.CharField(
        choices=body_choice, max_length=21,
        blank=True, null=True,
        verbose_name="请求体类型", default="x-www-form-urlencoded",
        help_text="请选择请求体类型")
    # 请求体类型
    request_body = models.TextField(
        verbose_name="请求体", blank=True, null=True,
        help_text="请输入浏览器原生表单、json、文件或xml格式的请求体", default="")
    # 请求体
    expected_result = models.TextField(
        verbose_name="预期结果", blank=True, null=True,
        help_text="请输入预期结果", default="")
    # 预期结果
    response_assert = models.CharField(
        choices=assert_choice, max_length=2,
        blank=True, null=True,
        verbose_name="响应断言方式", default="包含",
        help_text="请选择断言方式")
    # 响应断言方式
    wait_time = models.FloatField(
        max_length=5, verbose_name="等待时间", default=0.1,
        blank=True, null=True, help_text="请输入等待时间，单位：秒")
    # 等待时间
    regular_expression = models.CharField(
        choices=regular_choice, max_length=3,
        blank=True, null=True,
        verbose_name="开启正则表达式", default="不开启",
        help_text="请选择是否开启正则表达式")
    # 开启正则表达式
    regular_variable = models.CharField(
        max_length=11, blank=True, null=True,
        verbose_name="正则表达式变量名", default="",
        help_text="请输入正则表达式变量名")
    # 正则表达式变量名
    regular_template = models.CharField(
        max_length=255, blank=True, null=True,
        verbose_name="正则表达式模板", default="",
        help_text="请输入正则表达式模板")
    # 正则表达式模板
    response_code = models.IntegerField(
        verbose_name="响应代码", blank=True, null=True)
    # 响应代码
    actual_result = models.TextField(
        verbose_name="实际结果", blank=True, null=True)
    # 实际结果
    pass_status = models.BooleanField(
        verbose_name="是否通过", blank=True, null=True)
    # 是否通过，1为通过，0为不通过
    create_time = models.DateTimeField(
        auto_now_add=True, blank=True, null=True, verbose_name="创建时间")
    # 创建时间
    update_time = models.DateTimeField(
        auto_now=True, blank=True, null=True, verbose_name="修改时间")

    # 修改时间

    class Meta:
        db_table = 'interface_info'

        verbose_name = '用例列表'
        verbose_name_plural = "用例列表"

    def __str__(self):
        return self.case_name


class PerformanceInfo(models.Model):
    # 压测信息表

    script_introduce = models.CharField(
        max_length=32, verbose_name="脚本简介",
        help_text="请输入压测脚本简介", db_index=True)
    # 脚本简介，并创建索引
    jmeter_script = models.FileField(
        upload_to="jmeter/%Y%m%d%H%M%S",
        max_length=100, verbose_name="压测脚本",
        help_text="请上传JMeter脚本")
    # 压测脚本的相对路径
    sample_number = models.IntegerField(
        blank=True, null=True,
        verbose_name="请求数", default=1,
        help_text="请输入请求数")
    # 请求数
    duration = models.IntegerField(
        blank=True, null=True,
        verbose_name="持续时间", default=1,
        help_text="请输入持续时间，单位：秒")
    # 持续时间
    create_time = models.DateTimeField(
        auto_now_add=True, blank=True, null=True, verbose_name="创建时间")
    # 创建时间
    update_time = models.DateTimeField(
        auto_now=True, blank=True, null=True, verbose_name="修改时间")

    # 修改时间

    class Meta:
        db_table = 'performance_info'

        verbose_name = '压测脚本列表'
        verbose_name_plural = "压测脚本列表"

    def __str__(self):
        return self.script_introduce

    def run_sum(self):
        # 运行次数
        return self.scripts.all().count()

    # 利用外键反向统计语句

    run_sum.short_description = '<span style="color: red">运行次数</span>'
    run_sum.allow_tags = True


class PerformanceResultInfo(models.Model):
    # 压测结果表

    script_result = models.ForeignKey(
        PerformanceInfo, on_delete=models.CASCADE,
        verbose_name="压测脚本", related_name="scripts",
        help_text="请选择压测脚本")
    # 外键，关联压测脚本id
    test_report = models.CharField(
        max_length=100, verbose_name="测试报告",
        blank=True, null=True,
        help_text="测试报告", db_index=True)
    # 测试报告，并创建索引
    jtl = models.CharField(
        max_length=100, verbose_name="jtl文件",
        blank=True, null=True,
        help_text="jtl文件")
    # jtl文件
    dashboard_report = models.CharField(
        max_length=100, verbose_name="Dashboard Report文件",
        blank=True, null=True,
        help_text="Dashboard Report文件")
    # Dashboard Report文件
    run_time = models.DateTimeField(
        auto_now_add=True, blank=True, null=True, verbose_name="运行时间")

    # 运行时间

    class Meta:
        db_table = 'performance_result_info'

        verbose_name = '压测结果列表'
        verbose_name_plural = "压测结果列表"

    def __str__(self):
        return self.test_report

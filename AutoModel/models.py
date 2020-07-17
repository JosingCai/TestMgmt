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
    requestVars = models.CharField(max_length=255,blank=True)
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
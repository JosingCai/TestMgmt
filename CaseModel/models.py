from django.db import models
from django.core.validators import RegexValidator
from AutoModel.models import Host,Dependency

# Create your models here.
class TestCase(models.Model):
    CASE_TYPE = (
    ('基本功能测试','基本功能测试'),
    ('场景测试','场景测试'),
    ('异常测试','异常测试'),
    ('长时间测试','长时间测试'),
    ('压力测试','压力测试'),
    ('UI交互测试','UI交互测试')
    )
    PRIORITY = (
    ('Level0','Level0'),
    ('Level1','Level1'),
    ('Level2','Level2'),
    ('Level3','Level3'),
    ('Level4','Level4'),
    ('Level5','Level5')
    )
    AUTO = (
    ('yes', "yes"),
    ('no', "no")
    )
    TEST_MEMBER = (
    ('测试人员1','测试人员1'),
    ('测试人员2','测试人员2'),
    ('未分配','未分配')
    )
    DEV_MEMBER = (
    ('开发人员1','开发人员1'),
    ('开发人员2','开发人员2'),
    ('未分配','未分配')
    )
    TEST_RESULT = (
    ('PASS','PASS'),
    ('FAIL','FAIL'),
    ('未测试','未测试'),
    ('废弃','废弃'),
    ('未合入','未合入')
    )

    case_number = models.CharField(primary_key=True,max_length=50,verbose_name="用例编号", help_text="请输入用例编号")
    case_name = models.CharField(max_length=255,blank=True,null=True, verbose_name="用例名称",
        default="", help_text="请输入用例名称")
    case_type = models.CharField(max_length=10,blank=True,null=True,choices=CASE_TYPE,verbose_name="用例类型",
        default="基本功能测试", help_text="请选择测试类型")
    priority = models.CharField(max_length=6,blank=True,null=True,choices=PRIORITY,verbose_name="优先级",
        default="Level0", help_text="请选择优先级")
    pre_condition = models.TextField(blank=True,null=True,verbose_name="预置条件",
        default="", help_text="请输入预置条件")
    test_range = models.TextField(blank=True,null=True,verbose_name="测试范围",
        default="", help_text="请输入测试范围")
    test_steps = models.TextField(blank=True,null=True,verbose_name="测试步骤",
        default="", help_text="请输入测试步骤")
    expect_result = models.TextField(blank=True,null=True,verbose_name="预期结果",
        default="", help_text="请输入预期结果")
    auto = models.CharField(max_length=3,blank=True,null=True,choices=AUTO,verbose_name="是否自动化",
        default="yes", help_text="请选择自动化模式")
    case = models.ForeignKey(Dependency,blank=True,null=True, on_delete=models.CASCADE,verbose_name="关联API")
    fun_developer = models.CharField(max_length=10,blank=True, null=True, choices=DEV_MEMBER,verbose_name="功能开发者",
        default="未分配", help_text="请选择开发人员")
    case_designer = models.CharField(max_length=10,blank=True,null=True, choices=TEST_MEMBER,verbose_name="用例设计者",
        default="未分配", help_text="请选择用例设计人员")
    case_executor = models.CharField(max_length=10,blank=True,null=True, choices=TEST_MEMBER,verbose_name="用例执行者",
        default="未分配", help_text="请选择用例执行人员")
    test_time = models.DateTimeField(auto_now=True, blank=True,null=True, verbose_name="测试时间",help_text="请选择测试时间")
    test_result = models.CharField(max_length=5,blank=True,null=True, choices=TEST_RESULT, verbose_name="测试结果",
        default="未测试", help_text="请选择测试结果")
    project = models.ForeignKey(Host, blank=True,null=True,on_delete=models.CASCADE,verbose_name="关联项目")
    module = models.CharField(max_length=255,blank=True,null=True,verbose_name="用例模块",
        default="", help_text="请输入用例模块")
    remark = models.TextField(blank=True,null=True,verbose_name="备注",
        default="", help_text="请输入备注")
    
    def __str__(self):
        return self.case_number

    class Meta:
        db_table = "testcase"
        ordering = ['case_number']
        verbose_name = '测试用例'
        verbose_name_plural = "测试用例"
        unique_together = ('project','case_number')

class ProductDir(models.Model):
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')
    pid = models.IntegerField(primary_key=True)
    name_cn = models.CharField(max_length=50,blank=True,verbose_name="目录名称",
        default="", help_text="请输入用例模块")
    name_en = models.CharField(max_length=50, validators=[alphanumeric],verbose_name="目录名称")
    remark = models.TextField(blank=True,null=True, verbose_name="备注",
        default="", help_text="请输入备注")
    def __str__(self):
        return self.pid

    class Meta:
        db_table = "productdir"
        ordering = ['name_en']
        verbose_name = '产品目录树'
        verbose_name_plural = "产品目录树"

class Product_Gitlab(models.Model):
    repo = models.CharField(max_length=50,blank=True,verbose_name="URL",
        default="http://gitlab.idcos.com", help_text="请输入gitlab url")
    product_id = models.CharField(max_length=50, verbose_name="产品", help_text="请输入产品", default="")
    milestone = models.CharField(max_length=50,verbose_name="版本分支",
        default="all", help_text="请输入milestone")
    rss_token = models.CharField(max_length=50,blank=True,verbose_name="RSS_TOKEN",
        default="", help_text="请输入rss_token")
    project = models.ForeignKey(Host, related_name="gitlab_project",blank=True,null=True,on_delete=models.CASCADE,verbose_name="关联项目")
    remark = models.TextField(blank=True,null=True, verbose_name="备注",
        default="", help_text="请输入备注")
    def __str__(self):
        return self.product_id

    class Meta:
        db_table = "product_gitlab"
        ordering = ['product_id']
        verbose_name = 'Gitlab列表'
        verbose_name_plural = "Gitlab列表"
        unique_together = ('project','product_id','milestone')

class Issue_Milestone_Count(models.Model):
    milestone = models.CharField(max_length=50,verbose_name="版本分支",
        default="all", help_text="请输入milestone")
    product = models.CharField(max_length=50, verbose_name="产品", help_text="请输入产品项目", default="")
    all_count = models.IntegerField(verbose_name="总数",
        default=0, help_text="请输入全部issue数")
    open_count = models.IntegerField(verbose_name="Open状态数",
        default=0, help_text="请输入Open状态数")
    closed_count = models.IntegerField(verbose_name="Closed状态数",
        default=0, help_text="请输入Closed状态数")
    project = models.ForeignKey(Host, related_name="issue_project",blank=True,null=True,on_delete=models.CASCADE,verbose_name="关联产品")
    remark = models.TextField(blank=True,null=True, verbose_name="备注",
        default="", help_text="请输入备注")
    def __str__(self):
        return self.milestone

    class Meta:
        db_table = "issue_milestone_count"
        ordering = ['milestone']
        verbose_name = 'issue版本统计'
        verbose_name_plural = "issue版本统计"
        unique_together = ('project','product','milestone')

class Issue_Tag_Count(models.Model):
    product = models.CharField(max_length=50, verbose_name="产品", help_text="请输入产品项目", default="")
    milestone = models.CharField(max_length=50,verbose_name="版本分支",
        default="", help_text="请输入版本分支")
    tag = models.CharField(max_length=50,verbose_name="标签",
        default="", help_text="请输入标签")
    all_count = models.IntegerField(verbose_name="总数",
        default=0, help_text="请输入总数")
    open_count = models.IntegerField(verbose_name="Open状态数",
        default=0, help_text="请输入Open状态数")
    closed_count = models.IntegerField(verbose_name="Closed状态数",
        default=0, help_text="请输入Closed状态数")
    project = models.ForeignKey(Host, related_name="tag_project",blank=True,null=True,on_delete=models.CASCADE,verbose_name="关联产品")
    remark = models.TextField(blank=True,null=True, verbose_name="备注",
        default="", help_text="请输入备注")
    def __str__(self):
        return self.tag

    class Meta:
        db_table = "issue_tag_count"
        ordering = ['tag']
        verbose_name = 'issue标签统计'
        verbose_name_plural = "issue标签统计"
        unique_together = ('project','product','milestone', 'tag')

class Issue_Info(models.Model):
    ISSUE_TYPE = (
    ('需求','需求'),
    ('BUG','BUG'),
    ('优化','优化'),
    ('未知','未知')
    )
    RESULT = (
    ('PASS','PASS'),
    ('FAIL','FAIL'),
    ('未知','未知')
    )
    REOPEN = (
    ('是','是'),
    ('否','否'),
    ('未知','未知')
    )
    product = models.CharField(max_length=50, verbose_name="产品", help_text="请输入产品项目", default="")
    #milestone = models.ForeignKey(Product_Gitlab,related_name="issueinfo_milestone", on_delete=models.CASCADE,verbose_name="版本分支")
    milestone = models.CharField(max_length=50,verbose_name="版本分支",
        default="", help_text="请输入版本分支")
    issue_id = models.CharField(max_length=255,verbose_name="No.",
        default="", help_text="请输入issue超链")
    issue_type = models.CharField(max_length=8,blank=True,null=True,choices=ISSUE_TYPE,verbose_name="类型",
        default="未知", help_text="请选择类型")
    name = models.CharField(max_length=255,verbose_name="名称",
        default="", help_text="请输入名称")
    author = models.CharField(max_length=255,verbose_name="提交人",
        default="", help_text="请输入提交人")
    assignees = models.CharField(max_length=255,verbose_name="解决人",
        default="", help_text="请输入解决人")
    test = models.CharField(max_length=255,verbose_name="回归人",
        default="", help_text="请输入回归人")
    updated = models.CharField(max_length=255,verbose_name="更新时间",
        default="", help_text="请输入更新时间")
    result = models.CharField(max_length=8,blank=True,null=True,choices=RESULT,verbose_name="回归结果",
        default="未知", help_text="请选择回归结果")
    reopen = models.CharField(max_length=8,blank=True,null=True,choices=REOPEN,verbose_name="是否ReOpen",
        default="未知", help_text="请选择是否ReOpen")
    tag = models.CharField(max_length=255,verbose_name="标签",
        default="", help_text="请输入标签")
    project = models.ForeignKey(Host, related_name="issueinfo_project",blank=True,null=True,on_delete=models.CASCADE,verbose_name="关联产品")
    remark = models.TextField(blank=True,null=True, verbose_name="备注",
        default="", help_text="请输入备注")
    def __str__(self):
        return self.issue_id

    class Meta:
        db_table = "issue_info"
        ordering = ['issue_id']
        verbose_name = 'issue信息'
        verbose_name_plural = "issue信息"
        unique_together = ('issue_id','product', "milestone")

class Test_Plan_Schedule(models.Model):
    PRIORITY = (
    ('高','高'),
    ('中','中'),
    ('低','低'),
    ('回归','回归')
    )
    task_id = models.CharField(max_length=255,verbose_name="任务名称",
        default="", help_text="请输入任务名称")
    p_start_time = models.DateField(auto_now=False, blank=True, null=True, verbose_name="计划开始时间",
        default="", help_text="请输入计划开始时间")
    p_finish_time = models.DateField(auto_now=False, blank=True, null=True, verbose_name="计划结束时间",
        default="", help_text="请输入计划结束时间")
    a_start_time = models.DateField(auto_now=False, blank=True, null=True, verbose_name="实际开始时间",
        default="", help_text="请输入实际开始时间")
    a_finish_time = models.DateField(auto_now=False, blank=True, null=True, verbose_name="实际结束时间",
        default="", help_text="请输入实际结束时间")
    progress = models.CharField(max_length=4,verbose_name="完成进度",
        default="", help_text="请输入完成进度")
    milestone = models.CharField(max_length=12,verbose_name="版本分支",
        default="", help_text="请输入版本分支")
    priority = models.CharField(max_length=6,blank=True,null=True,choices=PRIORITY,verbose_name="优先级",
        default="中", help_text="请选择优先级")
    executor = models.CharField(max_length=12,verbose_name="执行人员",
        default="未分配", help_text="请输入执行人员")
    project = models.ForeignKey(Host, blank=True,null=True,on_delete=models.CASCADE,verbose_name="关联产品")
    remark = models.TextField(blank=True,null=True, verbose_name="备注",
        default="", help_text="请输入备注")

    def __str__(self):
        return self.task_id

    class Meta:
        db_table = "test_progress_schedule"
        ordering = ['p_start_time']
        verbose_name = '测试计划进度表'
        verbose_name_plural = "测试计划进度表"
        unique_together = ('task_id','milestone','project')



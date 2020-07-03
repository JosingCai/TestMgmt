# testplan.py
import datetime
import plotly as py
import plotly.figure_factory as ff
from django.conf import settings
from CaseModel.models import Test_Plan_Schedule

def create_gantt(project, milestone):
    print(project,milestone)
    test_plan = list(Test_Plan_Schedule.objects.filter(milestone=milestone,project_id=project).values())
    if len(test_plan) > 0:
        p_info_list = []
        a_info_list = []
        for item in test_plan:
            a_status = '未知'
            p_status = '未知'
            c_str_time = datetime.date.today().strftime("%Y%m%d%H%M%S")
            if item['p_start_time'] is not None:
                p_str_time = item['p_start_time'].strftime("%Y%m%d%H%M%S")
                if p_str_time > c_str_time:
                    p_status = '未开始'
                    a_status = '未开始'
            if item['a_start_time'] is not None:
                a_str_time = item['a_start_time'].strftime("%Y%m%d%H%M%S")
                if item['p_start_time'] is not None:
                    p_str_time = item['p_start_time'].strftime("%Y%m%d%H%M%S")
                    if p_str_time < a_str_time and a_str_time <= c_str_time:
                        p_status = '延迟'
                        a_status = "进行中"
                    elif p_str_time < a_str_time and a_str_time <= c_str_time:
                        p_status = '延迟'
                        a_status = "进行中"
                    elif p_str_time >= a_str_time:
                        p_status = '正常'
            if (item['p_finish_time'] is not None) and (item['a_finish_time'] is not None):
                pf_str_time = item['p_finish_time'].strftime("%Y%m%d%H%M%S")
                af_str_time = item['a_finish_time'].strftime("%Y%m%d%H%M%S")
                if (af_str_time <= af_str_time) and (af_str_time <= c_str_time):
                    a_status = '已完成'

            p_info_dict = {"Task":item["task_id"], "Start":item['p_start_time'], "Finish":item['p_finish_time'], "Complete":int(item['progress']), "Status":p_status}
            a_info_dict = {"Task":item["task_id"], "Start":item['a_start_time'], "Finish":item['a_finish_time'], "Complete":int(item['progress']), "Status":a_status}
            p_info_list.append(p_info_dict)
            a_info_list.append(a_info_dict)

        pyplt = py.offline.plot
         
        colors = {'未开始': 'rgb(190,190,190)',
             '进行中': 'rgb(245,255,250)',
             '已完成': 'rgb(0,128,0)',
             '未知': 'rgb(128,128,128)',
             '延迟': 'rgb(255,127,80)',
             '进行中': 'rgb(255,228,196)',
             '正常': 'rgb(0,205,102)'}    
        
        t_cur_time = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        p_fig = ff.create_gantt(p_info_list, index_col='Status', colors=colors, title='%s %s %s %s'%(project, milestone, "测试计划时间表", t_cur_time), group_tasks=True, show_hover_fill=True,show_colorbar=True, bar_width=0.3, showgrid_x=True, showgrid_y=True)
        a_fig = ff.create_gantt(p_info_list, index_col='Status', colors=colors, title='%s %s %s %s'%(project, milestone, "测试进行时间表", t_cur_time),  group_tasks=True, show_hover_fill=True,show_colorbar=True, bar_width=0.3, showgrid_x=True, showgrid_y=True)
        # p_fig = ff.create_gantt(p_info_list, index_col='Complete', colors="Blues", title='%s %s %s %s'%(project, milestone, "测试计划时间表", t_cur_time), group_tasks=True, show_hover_fill=True,show_colorbar=True, bar_width=0.2, showgrid_x=True, showgrid_y=True)
        # a_fig = ff.create_gantt(p_info_list, index_col='Complete', colors="Blues", title='%s %s %s %s'%(project, milestone, "测试进行时间表", t_cur_time),  group_tasks=True, show_hover_fill=True,show_colorbar=True, bar_width=0.2, showgrid_x=True, showgrid_y=True)
        # # pyplt(fig, filename='1.html')
        f_cur_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        pyplt(p_fig, filename='static/raw/chart/%s_%s_%s_%s.html'%(project, milestone, "plan", f_cur_time))
        pyplt(a_fig, filename='static/raw/chart/%s_%s_%s_%s.html'%(project, milestone, "actual",f_cur_time))
    else:
        print("请先录入测试计划数据")    

        
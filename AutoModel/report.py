#from AutoModel.models import Dependency, Result, TestDetail, TestReport
from __future__ import absolute_import
from CaseModel.models import Issue_Milestone_Count

from HTMLTable import HTMLTable

import datetime
import plotly as py
import plotly.figure_factory as ff

import plotly.offline as pltoff
from plotly.graph_objs import Scatter, Layout
import plotly.graph_objs as go
pltoff.init_notebook_mode(connected=True)
import pandas as pd
import numpy as np


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

def issue_report():
    issue_lable = list(Issue_Milestone_Count.objects.filter(milestone="3.6.0",project_id="BOOT3X").values())
    print("issue_lable", issue_lable)
    table = HTMLTable(caption='Issue统计')
    table.append_header_rows(())

def create_HTML():
    # 标题
    table = HTMLTable(caption='测试报告')
    # 表头行
    table.append_header_rows((
          ('名称',  '产量 (吨)',  '环比',       ''),
          ('',    '',       '增长量 (吨)',   '增长率 (%)'),
    ))

    # 合并单元格
    table[0][0].attr.rowspan = 2
    table[0][1].attr.rowspan = 2
    table[0][2].attr.colspan = 2

    # 数据行
    table.append_data_rows((
          ('荔枝', 11, 1, 10),
          ('芒果', 9, -1, -10),
          ('香蕉', 6, 1, 20),
    ))

    # 标题样式
    table.caption.set_style({
         'font-size': '15px',
    })

    # 表格样式，即<table>标签样式
    table.set_style({
      'border-collapse': 'collapse',
      'word-break': 'keep-all',
      'white-space': 'nowrap',
      'font-size': '14px',
    })

    # 统一设置所有单元格样式，<td>或<th>
    table.set_cell_style({
      'border-color': '#000',
      'border-width': '1px',
      'border-style': 'solid',
      'padding': '5px',
    })    

    # 表头样式
    table.set_header_row_style({
      'color': '#fff',
      'background-color': '#48a6fb',
      'font-size': '18px',
    })    

    table.set_header_cell_style({
      'padding': '15px',
    })    

    # 调小次表头字体大小
    table[1].set_cell_style({
      'padding': '8px',
      'font-size': '15px',
    })    

    # 遍历数据行，如果增长量为负，标红背景颜色
    for row in table.iter_data_rows():
      if row[2].value < 0:
        row.set_style({
          'background-color': '#ffdddd',
        })

    html = table.to_html()
    with open("test.html", "w+") as f:
         f.write(html)

def pie_charts(project, chart_title, **info):
    cur_time = cur_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename='static/raw/chart/%s_%s_%s.html'%(project, "piechart", cur_time)
    lables = list(info.keys())
    values = list(info.values())
    dataset = {
      'labels': lables,
      'values':values}
    data_g = []
    tr_p = go.Pie(
    labels = dataset['labels'],
    values = dataset['values']
   
    )
    data_g.append(tr_p)
    layout = go.Layout(title=chart_title)
    fig = go.Figure(data=data_g, layout=layout)
    # cur_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    pltoff.plot(fig, filename=filename)

def bar_charts(name="bar_charts.html"):
    dataset = {'x':['man', 'woman'],
          'y1':[35, 26],
          'y2':[33, 30]}
    data_g = []
    tr_y1 = go.Bar(
      x = dataset['x'],
      y = dataset['y1'],
      name = '2016'
   
    )
    data_g.append(tr_y1)
   
    tr_y2 = go.Bar(
    x = dataset['x'],
    y = dataset['y2'],
    name = '2017'
   
    )
    data_g.append(tr_y2)
    layout = go.Layout(title="bar charts",
      xaxis={'title':'x'}, yaxis={'title':'value'})
    fig = go.Figure(data=data_g, layout=layout)
    pltoff.plot(fig, filename=name)
   


if __name__ == '__main__':
   create_HTML()

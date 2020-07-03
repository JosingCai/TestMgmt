#!/usr/bin/env python
# -*- coding: utf-8 -*-

from local.function.comModVar import *

path_head = "http://10.0.3.8"

path_source = "/Users/josing/Yunji/Code/cloudboot/src/idcos.com/cloudboot/server/cloudbootserver"
path_sql_inject = "/Users/josing/Yunji/CodeDevel/Python/sqlmap-dev"
DEBUG = True
cookie = "user-authentication=MTU2ODYyNjgwMHxEdi1CQkFFQ180SUFBUkFCRUFBQV84N19nZ0FGQm5OMGNtbHVad3dHQUFST1lXMWxCbk4wY21sdVp3d1JBQV9vdG9YbnVxZm5ycUhua0libGtaZ0djM1J5YVc1bkRBWUFCRkp2YkdVR2MzUnlhVzVuREE4QURVRmtiV2x1YVhOMGNtRjBiM0lHYzNSeWFXNW5EQTBBQzBGalkyVnpjMVJ2YTJWdUJuTjBjbWx1Wnd3aUFDQTJPRGMyUWpoR1JqSkZRemhDTlRBd09VSkdOakkwT1RBeVFrTkJPREUxTVFaemRISnBibWNNQkFBQ1NVUUVkV2x1ZEFZQ0FBRUdjM1J5YVc1bkRBb0FDRlZ6WlhKdVlXMWxCbk4wY21sdVp3d0hBQVZoWkcxcGJnPT18wYzRf38L4RYPSJobIHLlb9NWECLk-6Pw7O2x3nFuViw="

def logRecord(string, Type=0):
        info = {0: "Info", 1: "Error"}
        curTime=datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        String = "[ %s ] %s: %s\n"%(curTime, info[Type], string)
        if DEBUG is True:
            print(String)
        with open("sqlInject.log", 'a+') as f:
            f.write(String)

def get_api():
    with open("%s/routes.go" %path_source) as f:
        content = f.read()
    lines = content.split("\n")
    api_list = []
    for line in lines:
        if line.startswith("\tmux"):
            api_dict = {}
            tmp = line.split("(")[0]
            http_method = tmp.split(".")[1]
            tmp = line.split(",")[0]
            api_path = tmp.split("(")[1].replace("\"", "")
            api_dict["method"] = http_method
            api_dict["path"] = api_path
            api_list.append(api_dict)
    return api_list

def sql_inject_scan(*apis):
    define_dict = {"sn": "3Q28132", "ext": "no", "task_item_id": "n"}
    define_data = {"company": "dell","UserID":0, "Status":"success", "Sn":"2102310LXP10E3101791", "Username":"admin","Password":"zaq1@WSX", "userid": 2,"Network":"192.168.1.1/24","Netmask":"255.255.255.0","Gateway":"192.168.1.1", "category": "black"}
    for api in apis:
        if "{sn}" in api["path"]:
            api["path"] = api["path"].replace("{sn}", define_dict["sn"])
        elif "{task_item_id}" in api["path"]:
            api["path"] = api["path"].replace("{task_item_id}", define_dict["task_item_id"])
        cmd = 'echo "y" | %s/sqlmap.py -u "%s%s" --level 3 --method %s --data \"%s\" --cookie "%s" --dbs' %(path_sql_inject, path_head, api["path"], api["method"], define_data, cookie)
        # if api['method'] == "Get":
        #     #cmd = 'echo "y" | %s/sqlmap.py -u "%s%s" --method %s --cookie "%s" --dbs' %(path_sql_inject, path_head, api["path"], api["method"], cookie)
        #     cmd = 'echo "y" | %s/sqlmap.py -u "%s%s" --method %s --data \"%s\" --cookie "%s" --dbs' %(path_sql_inject, path_head, api["path"], api["method"], define_data, cookie)
        # else:
        #     cmd = 'echo "y" | %s/sqlmap.py -u "%s%s" --method %s --data \"%s\" --cookie "%s" --dbs' %(path_sql_inject, path_head, api["path"], api["method"], define_data,cookie)
        logRecord(cmd)
        status, output = commands.getstatusoutput(cmd)
        logRecord(output)
        sys.exit

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="SQL Injection")
    parser.add_argument('--debug', dest="debug", action="store", default='Y', help="[Y/N] Y as Yes, N as Not, default value is N")
    args = parser.parse_args()

    if args.debug.upper() == "Y":
        DEBUG = True
    else:
        DEBUG = False

    apis = get_api()
    sql_inject_scan(*apis)

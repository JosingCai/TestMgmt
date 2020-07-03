#common.py
import threading

def raw2dict(*info_list):
    ret_list = []
    for info in info_list[0]:
        api_dict = {}
        if not info[0].strip():
            continue
        api_list = info[0].split("|")
        api_dict['APIFunction'] = api_list[0]
        api_dict['protocol'] = api_list[1]
        api_dict['http_method'] = api_list[2]
        api_dict['path'] = api_list[3]
        api_dict['header'] = api_list[4]
        api_dict['pathVar'] = api_list[5]
        api_dict['queryParam'] = api_list[6]
        api_dict['body'] = api_list[7]
        api_dict['response'] = api_list[8]
        api_dict['case_id'] = "%s_%s" %(api_dict['http_method'], api_dict['path'])
        ret_list.append(api_dict)
    return ret_list

class MyThread(threading.Thread):
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
 
    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception as e:
            print("exception: ", e)
            return {}

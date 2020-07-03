# apicase.py
import datetime
import random
import uuid
import requests
import os
from AutoModel.models import Host, Dependency, Result, Source, TestDetail, ComVar,TestReport
from itertools import product
from AutoModel.common import MyThread

DEBUG = False
today = datetime.datetime.now().strftime('%Y-%m-%d')
curPath = os.getcwd()
LogPath = "log"

class RawAPI(object):
    """docstring for RawAPI"""
    def __init__(self,  module, apiString):
        self.apiDict = {}
        #print("apiString: ", apiString.replace("\"", "'"))
        #apiList = apiString.replace("\"", "'").split("|")
        apiList = apiString.split("|")
        try:
            self.apiDict["APIFunction"] = apiList[0]
            self.apiDict["http_method"] = apiList[2]
            self.apiDict["path"] = apiList[3]
            if len(apiList[5]) != 0:
                self.apiDict["pathVariable"] = eval(apiList[5])
            else:
                self.apiDict["pathVariable"] = apiList[5]
            if len(apiList[6]) != 0:
                self.apiDict["queryParameter"] = eval(apiList[6])
            else:
                self.apiDict["queryParameter"] = apiList[6]
            if len(apiList[7]) != 0:
                print(apiList[7])
                self.apiDict["body"] = eval(apiList[7])
            else:
                self.apiDict["body"] = apiList[7]
            if len(apiList[8]) != 0:
                self.apiDict["response"] = eval(apiList[8])
            else:
                self.apiDict["response"] = apiList[8]
        except Exception as e:
            print("exception: ", e)
            print("apiString: ", apiString)
            print("apiList: ", apiList)
        self.apiDict["section"] = "%s_%s"%(self.apiDict["http_method"], self.apiDict["path"])
        host_ret = list(Host.objects.filter(project_id=module).values())
        self.hostDict = host_ret[0]
        DEBUG = self.hostDict["debug"]
        #print("host_info: ", self.hostDict)
        headers = {"Accept": "application/json"}
        if self.hostDict["debug"] == "yes":
            DEBUG = True
        else:
            DEBUG = False
        if ("auth" in self.hostDict) and (self.hostDict["auth"].lower() == "yes"):
            if "BOOT" in module:
                headers["Authorization"] = self.hostDict["token"]
            else:
                headers["access-token"] = self.hostDict["token"]
        self.hostDict["headers"] = headers

class API(RawAPI):
    """docstring for API"""
    def __init__(self, module, apiString):
        #RawAPI.__init__(self, apiString)
        super(API, self).__init__(module, apiString)
        self.module = module
        self.logFile = "%s-API-%s.log"%(self.module, today)
        case_ret = list(Dependency.objects.filter(case_id=self.apiDict["section"]).values())
        self.case_info = case_ret[0]
        beforeCase = self.case_info["beforeCase"]
        afterCase = self.case_info["afterCase"]
        runNum = self.case_info["runNum"]
        param_def = self.case_info["param_def"]
        self.depIDs = []
        if beforeCase:
            self.depIDs = eval(beforeCase)
        self.chkIDs = []
        if afterCase:
            self.chkIDs = eval(afterCase)
        self.runNum = 1
        if runNum:
            self.runNum = runNum
        self.param_def = []
        if param_def:
            self.param_def = eval(param_def)
    
    def expectAPI(self):
        if self.runNum == 0:
            if DEBUG:
                print("%s has 0 runNum test ..."%self.apiDict["section"])
            response = {"status": "untested", "message": "未测试"}
            url = self.getRawUrl()
            data = ""
            self.saveTestReport(url, data, response)
            return True, "%s has 0 runNum test ..."%self.apiDict["section"]
        return False, "Common Test"

    def hadRun(self):
        if self.sf.hasSection(self.apiDict["section"]):
            return True, "%s had already Test ... "%self.apiDict["section"]

    def getRawUrl(self):
        if len(self.hostDict["prepath"]) != 0:
            tmpPath = "%s%s"%(self.hostDict["prepath"], self.apiDict["path"])
            url = "%s://%s%s"%(self.hostDict["protocol"], self.hostDict["ip"], tmpPath)
        else:
            url = "%s://%s%s"%(self.hostDict["protocol"], self.hostDict["ip"], self.apiDict["path"])
        return url

    def getDepVars(self):
        depOutVars = {}
        if self.depIDs and len(self.depIDs) > 0:
            for depID in self.depIDs:
               out_ret = list(Result.objects.filter(case_id=depID, project=self.module).values())
               outVars = out_ret[0]
               if DEBUG:
                   print("befOutVars: ", outVars)
               if outVars and len(outVars) != 0:
                   print("befOutVars: ", outVars)
                   depOutVars.update(eval(outVars['outVars']))
        all_param_def = []
        if self.depIDs and len(self.depIDs) > 0:
            all_param_def = all_param_def + self.param_def + [self.apiDict['section']]
        else:
            all_param_def.append(self.apiDict['section'])
        for item in all_param_def:
            print(self.module)
            # print("item: ", item)
            item_ret = list(ComVar.objects.filter(name=item, project_id=self.module).values())
            # print("item_ret: ", item_ret)
            if item_ret and len(item_ret) > 0:
                ret = item_ret[0]
                depOutVars.update(eval(ret['value']))
        print("depOutVars: ", depOutVars)
        return depOutVars

    def getRandomStr(self, randomlength=16):
        randomStr = ''
        baseStr = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
        length = len(baseStr) - 1
        for i in range(randomlength):
            randomStr += baseStr[random.randint(0, length)]
        return randomStr

    def getAbDef(self, Type):
        valueList = []
        if Type == "int" or Type == "integer":
            valueList = [1-2**16, 1-2**8, -1, 0, 2**8-1, 2**16-1]
        elif Type == "string":
            specStr = '~!@#$%^&*()_+=|[]{}<>,.?/"'
            str255 = getRandomStr(255)
            str256 = getRandomStr(256)
            str257 = getRandomStr(257)
            valueList = [str255, str256, str257, specStr]
        return valueList

    def getArray(self, *items):
        maxLen = len(items[0])
        for item in items:
            if len(item) > maxLen:
                maxLen = len(item)
        productList = []
        list0 = [0]
        arrayList = []
        for item in items:
            tmpList = []
            if len(item) < maxLen:
                tmpList = list0*(maxLen-len(item)) + item
                productList.append(tmpList)
            else:
                productList.append(item)
        for item in product(*productList):
            arrayList.append(item)
        return arrayList

    def prameter_format(self, **depOutVars):
        pamras = []
        if len(self.apiDict["pathVariable"]):
            pamras.append("pathVariable")
        if len(self.apiDict["queryParameter"]):
            pamras.append("queryParameter")
        if len(self.apiDict["body"]):
            pamras.append("body")
        ramStr12 = self.getRandomStr(12)
        ramStr8 = self.getRandomStr(8)
        int_10 = random.randint(0,9)
        curTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        uuid_str = uuid.uuid1()
        defDict = {"description": "自动化-描述-%s"%self.apiDict["APIFunction"], "pid": 0, "tenantId": "default", \
        "remark": "自动化-备注-%s"%self.apiDict["APIFunction"], "name": "自动化-名称-%s"%ramStr8, \
        "number": "auto%s"%ramStr8, "date": curTime, "acquire_time": curTime, \
        "started_at": curTime, "onshelve_at": curTime, "fixed_asset_number": ramStr12, "sn": ramStr12, "uuid": uuid_str}
        for pamra_type in pamras:
            key_list = self.apiDict[pamra_type].keys()
            for Key in key_list:
                key_ret = list(ComVar.objects.filter(name=Key).values())
                if len(key_ret) > 0:
                    keyVar = key_ret[0]
                else:
                    keyVar = False

                if (Key not in depOutVars) and (Key in defDict):
                    depOutVars[Key] = defDict[Key]

                if self.hostDict["testmode"] == "abnormal":
                    if self.apiDict[pamra_type][Key] == "string":
                        depOutVars[Key] = ["", " "]
                    elif (self.apiDict[pamra_type][Key] == "integer") or (self.apiDict[pamra_type][Key] == "long"):
                        depOutVars[Key] = [-1, 65536]
                    elif self.apiDict[pamra_type][Key] == "array":
                        depOutVars[Key] = [[], {}, '']
                elif self.hostDict["testmode"] == "regression":
                    pass
                elif self.hostDict["testmode"] == "normal":
                    # if (Key not in depOutVars) and (Key not in defDict):
                    #     String = "Not Define Var: %s"%(Key)
                    #     if DEBUG:
                    #         print(String)
                    #     return False, String
                    if self.apiDict[pamra_type][Key] == "string":
                        if Key not in depOutVars:
                            if keyVar and (not isinstance(keyVar['value'], dict)):
                                depOutVars[Key] = keyVar
                            else:
                                depOutVars[Key] = ramStr12
                        # if (Key in depOutVars) and (not isinstance(depOutVars[Key], dict)):
                        #     depOutVars[Key] = depOutVars[Key]
                        # elif keyVar and (not isinstance(keyVar['value'], dict)):
                        #     depOutVars[Key] = keyVar
                        # else:
                        #     depOutVars[Key] = ramStr12
                    elif self.apiDict[pamra_type][Key] == "integer":
                        if Key not in depOutVars:
                            if keyVar and (not isinstance(keyVar['value'], dict)):
                                depOutVars[Key] = keyVar
                            else:
                                depOutVars[Key] = int_10
                        #     depOutVars[Key] = depOutVars[Key]
                        # elif keyVar:
                        #     depOutVars[Key] = eval(keyVar['value'])
                        # else:
                        #     depOutVars[Key] = int_10
                elif self.hostDict["testmode"] == "all":
                    if self.apiDict[pamra_type][Key] == "string":
                        if (Key in depOutVars) and (not isinstance(depOutVars[Key], dict)):
                            depOutVars[Key] = ["", " "] + depOutVars[Key]
                        elif keyVar and (not isinstance(keyVar['value'], dict)):
                            depOutVars[Key] = ["", " "].append(keyVar)
                        else:
                            depOutVars[Key] = ["", " "].append(ramStr12)
                    elif self.apiDict[pamra_type][Key] == "integer":
                        if Key in depOutVars:
                            depOutVars[Key] = [-1, 65536] + depOutVars[Key]
                        elif keyVar:
                            depOutVars[Key] = [-1, 65536] + eval(keyVar['value'])
                        else:
                            depOutVars[Key] = [-1, 65536] + int_10
        return True, depOutVars

    def getUrlPath(self, url, **depOutVars):
        urlList = []
        status, depOutVars = self.prameter_format(**depOutVars)
        print("getUrlPath DepVars: ", depOutVars)
        if not status:
            return False, depOutVars
        key_all = self.apiDict['pathVariable']
        if "{" not in url:
            urlList.append(url)
        else:
            for Key in key_all:
                if isinstance(depOutVars[Key], list):
                    for index in range(len(depOutVars[Key])):
                        value = depOutVars[Key][index]
                        URL = url.replace("{%s}"%Key, str(value))
                        urlList.append(URL)
                else:
                    URL = url.replace("{%s}"%Key, str(depOutVars[Key]))
                    urlList.append(URL)

        print("urlList: ", urlList)
        return True, urlList

    def getQueryStr(self, dep_mode="no", **depOutVars):
        queryStrList = []
        multi_no_list = ["page", "page_size"]
        if len(self.apiDict["queryParameter"]) != 0:
            uni_ret = list(ComVar.objects.filter(name="uniVar").values())
            if len(uni_ret) > 0:
                uniVars = uni_ret[0]["value"]
            else:
                uniVars = []
            keyList = []
            productList = []
            status, depOutVars = self.prameter_format(**depOutVars)
            if not status:
                return False, depOutVars
            key_all = depOutVars.keys()
            for Key in key_all:
                if isinstance(depOutVars[Key], list):
                    keyList.append(Key)
                    productList.append(depOutVars[Key])
                    for item in depOutVars[Key]:
                        queryString = Key + "=" + str(item)
                        queryStrList.append(queryString)
                else:
                    queryString = Key + "=" + str(depOutVars[Key])
                    queryStrList.append(queryString)

            if DEBUG:
                print("productList length: ", len(productList))
                print("keyList length: ", len(keyList))

            if len(productList) > 6:
                if DEBUG:
                    print("More Value: ", productList)
                    print("More Key : ", keyList)
                #productList = random.sample(productList,6)
                productList = productList[:6]
                keyList = keyList[:6]
                
            arrayList = []
            for item in product(*productList):
                arrayList.append(item)
            for info in arrayList:
                String = ""
                for i in range(len(keyList)):
                    if info[i] != 0:
                        if len(String) == 0:
                            String = keyList[i] + "=" + str(info[i])
                        else:
                            String = String + "&" + keyList[i] + "=" + str(info[i])
                queryStrList.append(String)
        if DEBUG:
            print("queryStrList: ", queryStrList)
            print("queryStrList length: ", len(queryStrList))
        print("queryStrList: ", queryStrList)
        return True, queryStrList

    def chkUniVar(self, name):
        uni_ret = list(ComVar.objects.filter(name="uniVar").values())
        if len(uni_ret) > 0:
            uniVars = uni_ret[0]["value"]
            for value in eval(uniVars):
                if name.strip() == value.strip():
                    return True
        return False

    def getBody(self, **depOutVars):
        bodyList = []
        status, depOutVars = self.prameter_format(**depOutVars)
        if not status:
            return False, depOutVars
        print("self.apiDict: ", self.apiDict)
        key_all = []
        print(len(self.apiDict["body"]))
        print(self.apiDict["body"])
        if len(self.apiDict["body"]):
            key_all = self.apiDict["body"].keys()
        #key_all = depOutVars.keys()
        keyList = []
        for Key in key_all:
            if isinstance(depOutVars[Key], list):  #and len(depOutVars[Key])> 1:
                keyList.append(Key)
        # print("keyList:", keyList)
        forList = []
        productList = []
        for Key in keyList:
            productList.append(depOutVars[Key])
        # print("productList: ", productList)
        for items in product(*productList):
            forList.append(items)
        # print("forList: ", forList)
        # print(len(forList))
        for j in range(len(forList)):
            infoDict = {}
            if len(self.apiDict["body"]):
                for Key in self.apiDict["body"].keys():
                    infoDict[Key] = depOutVars[Key]
                for i in range(len(keyList)):
                    Key = keyList[i]
                    Value = forList[j][i]
                    infoDict[Key] = Value
                bodyList.append(infoDict)
        print("bodyList: ", bodyList)
        return True, bodyList

    def assembleData(self, dep_mode="no"):
        url = self.getRawUrl()
        depOutVars = self.getDepVars()
        # if DEBUG:
        print("%s depOutVars: %s"%(self.apiDict["section"], depOutVars))
        status, urlList = self.getUrlPath(url, **depOutVars)
        if not status:
            return status, urlList
        if self.apiDict["http_method"] == "get" and dep_mode == "yes":
            reqDict = {}
            if len(urlList) > 0:
                reqDict["url"] = urlList[0]
                reqDict["body"] = ""
                return True, [reqDict]
            else:
                reqDict["url"] = ""
                reqDict["body"] = ""
                return False, "No Dep Data"
        status, queryList = self.getQueryStr(dep_mode=dep_mode,**depOutVars)
        if not status:
            return status, queryList
        status, bodyList = self.getBody(**depOutVars)
        if not status:
            return status, bodyList
        reqList = []
        tmpList = []
        productList = [urlList]
        if len(queryList) != 0:
            productList.append(queryList)
        if len(bodyList) != 0:
            productList.append(bodyList)
        for items in product(*productList):
            tmpList.append(items)
        if len(tmpList) == 0:
            return False, depOutVars
        length = len(tmpList[0])
        for items in tmpList:
            reqDict = {}
            if length == 1:
                reqDict["url"] = items[0]
                reqDict["body"] = ""
            elif length == 3:
                url = items[0] + "?" + items[1]
                reqDict["url"] = url
                reqDict["body"] = items[2]
            elif length == 2:
                if self.apiDict["http_method"] == "get": 
                    url = items[0] + "?" + items[1]
                    reqDict["url"] = url
                    reqDict["body"] = ""
                else:
                    reqDict["url"] = items[0]
                    reqDict["body"] = items[1]
            reqList.append(reqDict)

        return True, reqList

    def runMethod(self, url, data):
        if self.apiDict["http_method"] == "get":
            resp = requests.get(url, headers=self.hostDict["headers"], json=None, verify=False)
        elif self.apiDict["http_method"] == "post":
            resp = requests.post(url, headers=self.hostDict["headers"], json=data, verify=False)
        elif self.apiDict["http_method"] == "put":
            resp = requests.put(url, headers=self.hostDict["headers"], json=data, verify=False)
        elif self.apiDict["http_method"] == "delete":
            resp = requests.delete(url, headers=self.hostDict["headers"], json=data, verify=False)
        curTime=datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        logFilePath = "%s/%s/%s"%(curPath, LogPath, self.logFile)
        # if not os.path.exists(logFilePath):

        # with open("%s/%s/%s"%(curPath, LogPath, self.logFile), "a+") as f:
        #     f.write("[ %s ]\n"%curTime)
        #     f.write("%s: %s\n"%(self.apiDict["http_method"], url))
        #     f.write("headers: %s\n"%(self.hostDict["headers"]))
        if data:
            # f.write("request: %s\n"%data)
            ret_old = list(Result.objects.filter(case_id=self.apiDict["section"], project_id=self.module).values())
            if len(ret_old) > 0:
                obj = Result.objects.filter(case_id=self.apiDict["section"],project_id=self.module).update(requestVars=data)
            else:
                obj = Result(case_id=self.apiDict["section"],requestVars=data, project_id=self.module)
                obj.save()
            # f.write("response: %s"%resp.content)
        if not resp.ok:
            try:
                info = resp.json()
                if DEBUG:
                    print("response: ", info)
                
                if ("message" in info) and ("status" in info):
                    response = {"status": info["status"], "message": "执行失败", "failReason": info["message"]}
                elif ("resultMessage" in info) and ("isSuccess" in info):
                    response = {"status": info["isSuccess"], "message": "执行失败", "failReason": info["resultMessage"]}
            except Exception as e:
                print("runMethod 1 exception: ", e)
                response = {"status": "failure", "message": "执行失败", "failReason": resp.content}
            return False, response
        try:
            response = resp.json()
        except Exception as e:
            print("runMethod 2 exception: ", e)
            response = {"status": "success", "message": "执行成功", "failReason": " "}
        if "status" not in response:
            if isinstance(response,list):
                response = {"status": "success", "message": "执行成功", "failReason": " ", "content": response}
            else:
                response.update({"status": "success", "message": "执行成功", "failReason": " "})
        else:
            response.update({"failReason": " "})
        return True, response
    
    def saveTestReport(self, url, data, response):
        TestTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if "content" not in response:
            response["content"] = ""
        if "failReason" not in response:
            response["failReason"] = ""
        else:
            response["failReason"] = str(response["failReason"]).replace("\n", "")
        if "content" not in response:
            response["content"] = ""
        else:
            if isinstance(response["content"], str):
                response["content"] = str(response["content"]).replace("\n", "")
        project = Host.objects.filter(project_id=self.module)[0]
        # print("project: ", project)
        if not response["content"]:
            response["content"] = "No Content"
        obj = TestDetail(case_id=self.apiDict["section"],APIFunction=self.apiDict["APIFunction"], url=url, body=str(data), response=response["content"], failReason=response['failReason'], testTime=TestTime,testResult=response['status'], project_id=project)
        obj.save()
        return True

    def saveOutVar(self, response):
        outVarsDict = {}
        ret_list = list(Dependency.objects.filter(case_id=self.apiDict["section"]).values())
        if len(ret_list) == 0:
            return True, "No Special Out Vars"
        outVars = ret_list[0]['outVars']
        if len(outVars) == 0:
            return True, "No Special Out Vars"
        outVarItems = eval(outVars)
        Keys = outVarItems.keys()
        for Key in Keys:
            tmp = response
            if "-" in outVarItems[Key]:
                items = outVarItems[Key].split("-")
                values = []
                for item in items:
                    if "*" in item:
                        subItems = item.split("*")
                        for index in range(len(tmp[subItems[0]])):
                            value = tmp[subItems[0]][index][subItems[1]]
                            values.append(value)
                        tmp = values
                    else:
                        if isinstance(tmp, list):
                            subValues = []
                            for index in range(len(tmp)):
                                subValues.append(tmp[index][item])
                            tmp = subValues
                        else:
                            tmp = tmp[item]
            else:
                tmp = tmp[outVarItems[Key]]
            if isinstance(tmp, list):
                items = []
                for item in tmp:
                    if isinstance(item, int):
                        items.append(item)
                    else:
                        if len(item) == 0:
                            continue
                        if len(item) == 1 and isinstance(item, list) and len(item[0]) == 0:
                            continue
                        try:
                            if isinstance(item, list):
                                items.append(item)
                            else:
                                items.append(item)
                        except Exception as e:
                            print("saveOutVar exception: ", e)
                outVarsDict[Key] = items
            else:
                if isinstance(tmp, int):
                    outVarsDict[Key] = [tmp]
                else:
                    outVarsDict[Key] = [tmp]
        ret_old = list(Result.objects.filter(case_id=self.apiDict["section"],project_id=self.module).values())
        if len(ret_old) > 0:
            obj = Result.objects.filter(case_id=self.apiDict["section"], project=self.module).update(outVars=outVarsDict)
        else:
            project_in = Host.objects.get(project_id=self.module)
            obj = Result(case_id=self.apiDict["section"],outVars=outVarsDict, project=project_in)
            obj.save()
        return True, "Get Vars to Output Success"

    def chkItem(self, reqDict, chkDict):
        nochk_ret = list(ComVar.objects.filter(name="noChkVar").values())
        if len(uni_ret) > 0:
            noChkVars = uni_ret[0]["value"]
        # noChkVars = self.cf.getOption("common", "noChkVar")
        # passList = []
        cmpDict = {}
        chkVars = {}
        flag = "pass"
        ret_list = list(Dependency.objects.filter(case_id=self.apiDict["section"]).values())
        chkVars = {}
        if len(ret_list) > 0:
            chkVars = eval(ret_list[0]['chkVars'])
        chkInfo = chkDict["content"]
        if not isinstance(chkInfo, dict):
            return True, "No need Check"
        if len(chkVars) != 0:
            Keys = chkVars.keys()
            for Key in Keys:
                tmp = chkDict
                if "-" in chkVars[Key]:
                    items = chkVars[Key].split("-")
                    values = []
                    for item in items:
                        try:
                            if "*" in item:
                                subItems = item.split("*")
                                for index in range(len(tmp[subItems[0]])):
                                    value = tmp[subItems[0]][index][subItems[1]]
                                    values.append(value)
                                tmp = values
                            else:
                                tmp = tmp[item]
                        except Exception as e:
                            print("chkItem 1 exception: ", e)
                            tmp = "Not Found Var: %s"%item

                if isinstance(tmp, list):
                    values = []
                    for item in tmp:
                        if isinstance(item, int):
                            items.append(item)
                        else:
                            try:
                                items.append(item.encode("utf-8"))
                            except Exception as e:
                                print("chkItem 2 exception: ", e)
                                items.append("")
                    chkVars[Key] = items
                else:
                    if isinstance(tmp, int):
                        chkVars[Key] = tmp
                    else:
                        try:
                            chkVars[Key] = tmp.encode("utf-8") 
                        except Exception as e:
                            print("chkItem 3 exception: ", e)
                            chkVars[Key] = tmp
            chkInfo.update(chkVars)

        Keys = reqDict.keys() 
        if DEBUG:
            print("reqDict: ", reqDict)
        for Key in Keys:
            if Key not in noChkVars:
                if Key not in chkInfo:
                    cmpDict[Key] = "Actual: , Expected: %s"%(reqDict[Key])
                    flag = "false"
                if isinstance(reqDict[Key], list):
                    if len(list(set(reqDict[Key]).difference(set(chkInfo[Key])))) != 0:
                        cmpDict[Key] = "Actual: %s, Expected: %s"%(chkInfo[Key], reqDict[Key])
                        flag = "false"
                elif reqDict[Key] != chkInfo[Key]:
                    cmpDict[Key] = "Actual: %s, Expected: %s"%(chkInfo[Key], reqDict[Key])
                    flag = "false"
                else:
                    passList.append(Key)
        # if DEBUG:
        print("passList: ", passList)
        return flag, cmpDict

    def analysisReponse(self, url, data, response):
        if not self.saveTestReport(url, data, response):
            print("Save Test Result Failed ... ")
        if response["status"] != "success":
            result = "FAIL"
        else:
            result = "PASS"
        ret_old = list(Result.objects.filter(case_id=self.apiDict["section"]).values())
        if len(ret_old) > 0:
            obj = Result.objects.filter(case_id=self.apiDict["section"]).update(result=result)
        else:
            obj = Result(case_id=self.apiDict["section"],result=result)
            obj.save()
        if response["status"] != "success":
            return False, response['failReason']
        else:
            status, output = self.saveOutVar(response)
            return True, output

def threadRun(handle, url, body):
    retDict = {}
    retDict["case_id"] = handle.apiDict["section"]
    retDict["url"] = url
    retDict["body"] =  body
    retDict["header"] = handle.hostDict["headers"]
    status, response = handle.runMethod(url, body)
    retDict["response"] = response
    retDict["failReason"] = "%s: %s"%(response["message"], response["failReason"])
    retDict["testResult"] = response["status"]
    status, output = handle.analysisReponse(url, body, response)
    return status, retDict

def runAPI(module, apiString, number=1, mode="single", chkMode="no", dep_mode="no"):
    # 依赖用例chkMode置为no, 只执行beforeCase, afterCase不执行
    api = API(module, apiString)
    if api.runNum != 0 and api.runNum != 1:
        number = api.runNum

    status, output = api.expectAPI()
    if status:
        retDict = {}
        retDict["case_id"] = api.apiDict["section"]
        retDict["response"] = output
        return status, [retDict]

    if api.depIDs:
        for depID in api.depIDs:
            retDict = {}
            retDict["case_id"] = api.apiDict["section"]
            ret_list = list(Dependency.objects.filter(case_id=depID,project_id=module).values())
            if len(ret_list) > 0:
                apiString = ret_list[0]['raw']
            if not apiString:
                retDict["response"] = "Not Get Raw Info for Test"
                return False, [retDict]
            status, outputList = runAPI(module, apiString, number=1, mode="single", chkMode="no")
            if not status:
                return status, outputList

    if mode == "single":
        status, reqList = api.assembleData(dep_mode="yes")
        print("reqList: ", reqList)
        reqList = [reqList[0]]
    elif number != 1:
        status, reqList = api.assembleData(dep_mode="yes")
        if len(reqList) < number:
            loopNum = int(number/len(reqList)) + 1
            for i in range(loopNum):
                status, tmpList = api.assembleData()
                reqList = reqList + tmpList
        #reqList = reqList[:number]
        # if DEBUG:
        # print("Init List: ", reqList[:40])
        reqList = random.sample(reqList, number)
        # if DEBUG:
        print("Run List: ", reqList)
        #return False, [{"case_id":api.apiDict["section"], "response": reqList}]
    else:
        status, reqList = api.assembleData()
    if not status:
        return False, [{"case_id":api.apiDict["section"], "response": reqList}]
    
    # if DEBUG:
    print("reqList: ", reqList)
    resultList = []
    if (len(api.chkIDs) != 0 or chkMode == "no") and mode != "single":
        chkID = ""
        delID = ""    

        for case_id in api.chkIDs:
            if case_id.startswith("get"):
                chkID = case_id
            elif case_id.startswith("delete"):
                delID = case_id    

        for info in reqList:
            retDict = {}
            retDict["case_id"] = api.apiDict["section"]
            retDict["url"] = info['url']
            retDict["body"] =  info['body']
            retDict["header"] = api.hostDict["headers"]
            status, response = api.runMethod(info['url'], info['body'])
            if not status:
                retDict["response"] = response["failReason"]
                retDict["failReason"] = response["message"]
                retDict["testResult"] = response["status"]
                resultList.append(retDict)
                return False, resultList
            status, output = api.analysisReponse(info['url'], info['body'], response)
            retDict["response"] = output
            if not status:
                resultList.append(retDict)
                return False, resultList    
            if chkID.strip():
                chkDict = {}
                chkDict["case_id"] = chkID
                status, apiString = getSpecApi(module, chkID)
                if not status:
                    chkDict["response"] = apiString
                    resultList.append(chkDict)
                    return False, resultList
                chkApi = API(module, apiString)
                status, chkList = chkApi.assembleData()
                if not status:
                    chkDict["response"] = chkList
                    resultList.append(chkDict)
                    return False, resultList
                status, chkDict = threadRun(chkApi, chkList[0]["url"], chkList[0]["body"])
                resultList.append(chkDict)
                if not status:
                    return False, [chkDict]
                if api.apiDict["section"].startswith("delete"):
                    retDict["testResult"] = "pass"
                    retDict["failReason"] = ""
                else:
                    flag, failList = chkApi.chkItem(info['body'], chkDict["response"])
                    retDict["testResult"] = flag
                    retDict["failReason"] = failList    

            if delID.strip():
                delDict = {}
                delDict["case_id"] = delID
                status, apiString = getSpecApi(module, delID)
                if not status:
                    delDict["response"] = apiString
                    resultList.append(delDict)
                    return False, resultList
                delApi = API(module, apiString)
                status, delList = delApi.assembleData()
                if not status:
                    delDict["response"] = delList
                    resultList.append(delDict)
                    return False, resultList
                status, delDict = threadRun(delApi, delList[0]["url"], delList[0]["body"])
                resultList.append(delDict)
                if not status:
                    return False, [delDict]
            resultList.append(retDict)
    else:
        if api.hostDict["threading"] == "False":
            for info in reqList:
                status, retDict = threadRun(api, info["url"], info["body"])
                resultList.append(retDict)
        else:
            threads = []
            length = len(reqList)
            for i in range(length):
                t = MyThread(threadRun, (api, reqList[i]["url"], reqList[i]["body"]))
                threads.append(t)
            for i in range(length):
                threads[i].start()
            for i in range(length):
                threads[i].join()
                status, retDict = threads[i].get_result()
                resultList.append(retDict)
    return True, resultList

def runTargetAPI(module, method_API, number=1, mode="loop"):
    ret_list = list(Dependency.objects.filter(case_id=method_API).values())
    if len(ret_list) > 0:
        apiString = ret_list[0]['raw']
    if not apiString:
        return False, [{"case_id": method_API, "response": "Get API raw info failed, Please Check it ~ "}]
    status, output = runAPI(module, apiString, number, mode, chkMode="yes")
    if not status:
        # if DEBUG:
        print("run output: ", output)
    return True, output

def runAPIs(module):
    ret_list = list(Dependency.objects.filter(project_id=module).values())
    resultList = []
    for item in ret_list:
        case_id = item["case_id"]
        print("case_id: ", case_id)
        status, loopList = runTargetAPI(module, case_id, mode="single")
        resultList = resultList + loopList
    return resultList

class RunCase(object):
    """docstring for RunCase"""
    def __init__(self, project):
        self.project = project.upper()
        rConfig = "%s-API-Result.ini"%self.project
        config = "%s-API-Dependancy.ini"%self.project
        tConfig = "%s-TestReport.csv"%self.project
        self.rfileName = "%s/local/%s/%s"%(curPath, configPath, rConfig)
        self.cfileName = "%s/local/%s/%s"%(curPath, configPath, config)
        self.rf = localConfigParser(self.rfileName)
        self.cf = localConfigParser(self.cfileName)
        self.tfileName = "%s/local/%s/%s"%(curPath, LogPath, tConfig)

    def run(self, **info):
        case_id = list(info.keys())[0]
        status, retList = runTargetAPI(self.project, case_id, mode="loop")
        if not status:
            return retList
        return retList

    def runAll(self):
        items = self.cf.getAllItem("common")
        curTime = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
        if os.path.exists(self.tfileName):
            cmd = "mv %s %s_%s.bak"%(self.tfileName, self.tfileName, curTime)
            status, output = commands.getstatusoutput(cmd)
            if status != 0:
                print("output: ", output)
                return "Back up %s Failed: %s"%(self.rfileName, output)
        # rf = localConfigParser(self.rfileName)
        # for item in items.keys():
        #     rf.writeSection("common", item, items[item])
        return runAPIs(self.project)

class Case(object):
    def __init__(self, project):
        self.project = project.upper()
        cConfig = "%s-API-Dependancy.ini"%self.project
        rConfig = "%s-API-Result.ini"%self.project
        lConfig = "%s-TestReport.csv"%self.project
        self.cfileName = "%s/local/%s/%s"%(curPath, configPath, cConfig)
        self.rfileName = "%s/local/%s/%s"%(curPath, configPath, rConfig)
        self.lfileName = "%s/local/%s/%s"%(curPath, configPath, lConfig)
        if not os.path.exists(self.cfileName):
            f = open(self.cfileName, 'w')
            f.close()
        if not os.path.exists(self.rfileName):
            f = open(self.rfileName, 'w')
            f.close() 
        self.cf = localConfigParser(self.cfileName)
        self.rf = localConfigParser(self.rfileName)

    def getCaseDetail(self, case_id):
        infoDict = {}
        cContent =  self.cf.getSection(case_id)
        rContent =  self.rf.getSection(case_id)
        if cContent is False:
            cContent = {}
            cContent["beforeCase"] = " "
            cContent["outVars"] = " "
            cContent["chkVars"] = " "
            cContent["afterCase"] = " "
        if rContent is False:
            rContent = {}
            rContent["requestVars"] = " "
            rContent["outVarsTest"] = " "
            rContent["result"] = " "
        infoDict = cContent
        infoDict["case_id"] = case_id
        if "requestVars" in rContent:
            infoDict["requestVars"] = rContent["requestVars"]
        else:
            infoDict["requestVars"] = " "
        if "outVars" in rContent:
            infoDict["outVarsTest"] = rContent["outVars"]
        else:
            infoDict["outVarsTest"] = " "
        if "result" in rContent:
            infoDict["result"] = rContent["result"]
        else:
            infoDict["result"] = " "
        return infoDict

    def getCase(self, **info):
        if len(info) == 0:
            sections = self.cf.getAllSection()
            infoList = []
            for section in sections:
                if section == "common":
                    continue
                ret = self.getCaseDetail(section)
                if ret is False:
                    continue
                infoList.append(ret)
            return infoList
        Keys = list(info.keys())
        case_id = Keys[0]
        infoDict = self.getCaseDetail(case_id)
        return [infoDict]

    def delCase(self, case_id):
        status, output = self.cf.removeSection(case_id)
        if status is False:
            return output
        status, output = self.rf.removeSection(case_id)
        if status is False:
            return output
        return "Remove %s Config Info Success ~ "%case_id

    def getCaseDep(self, **info):
        # if DEBUG:
        # print(info)
        if len(info) != 0:
            section = list(info.keys())[0]
            ret = self.getCaseDetail(section)
            return [ret]
        sections = self.cf.getAllSection()
        infoList = []
        for section in sections:
            if section == "common":
                continue
            ret = self.getCaseDetail(section)
            if ret is False:
                continue
            infoList.append(ret)
        return infoList

    def postCaseDep(self, **info):
        section = info["case_id"]
        if len(section) == 0:
            return "Please Input Case ID "
        for option in info.keys():
            if option == "modify" or option == "case_id":
                continue
            value = info[option].strip()
            self.cf.writeSection(section, option, value)
        return "Add %s Success "%section

    def syncCaseDep(self):
        sHandle = Source(self.project)
        infoList = sHandle.getSConfig()
        sections = self.cf.getAllSection()
        for info in infoList:
            case_id = "%s_%s"%(info["http_method"], info["path"])
            count = 0 
            if len(sections) == 0:
                self.cf.writeSection(case_id, "beforeCase", "[]")
                self.cf.writeSection(case_id, "outVars", "{}")
                self.cf.writeSection(case_id, "chkVars", "{}")
                self.cf.writeSection(case_id, "afterCase", "[]")
                self.cf.writeSection(case_id, "runNum", "1")
                #self.cf.writeSection(case_id, "param_def", '["%s"]' %info["path"])
                self.cf.writeSection(case_id, "param_def", '["%s"]' %info["case_id"])
                self.cf.writeSection(case_id, "raw", '"%s"' %info["raw"])
            else:
                for section in sections:
                    if case_id == section:
                        if not self.cf.getOption(case_id,"beforeCase"):
                            self.cf.writeSection(case_id, "beforeCase", "[]")
                        if not self.cf.getOption(case_id,"outVars"):
                            self.cf.writeSection(case_id, "outVars", "{}")
                        if not self.cf.getOption(case_id,"chkVars"):
                            self.cf.writeSection(case_id, "chkVars", "{}")
                        if not self.cf.getOption(case_id,"afterCase"):
                            self.cf.writeSection(case_id, "afterCase", "[]")
                        if not self.cf.getOption(case_id,"runNum"):
                            self.cf.writeSection(case_id, "runNum", "1")
                        if not self.cf.getOption(case_id,"param_def"):
                            #self.cf.writeSection(info["case_id"], "param_def", '["%s"]' %info["path"])
                            self.cf.writeSection(case_id, "param_def", '["%s"]' %info["case_id"])
                        if not self.cf.getOption(case_id,"raw"):
                            self.cf.writeSection(case_id, "raw", '"%s"' %info["raw"])
                        break
                    else:
                        count = count + 1
                    if count == len(sections):
                        self.cf.writeSection(case_id, "beforeCase", "[]")
                        self.cf.writeSection(case_id, "outVars", "{}")
                        self.cf.writeSection(case_id, "chkVars", "{}")
                        self.cf.writeSection(case_id, "afterCase", "[]")
                        self.cf.writeSection(case_id, "runNum", "1")
                        #self.cf.writeSection(case_id, "param_def", '["%s"]' %info["path"])
                        self.cf.writeSection(case_id, "param_def", '["%s"]' %info["case_id"])
                        self.cf.writeSection(case_id, "raw", '"%s"' %info["raw"])

    def delCaseDep(self, **info):
        section = list(info.keys())[0]
        self.cf.removeSection(section)
        return "Delete %s Succuss "%section

    def delCaseResult(self, **info):
        section = list(info.keys())[0]
        self.rf.removeSection(section)
        return "Delete %s Succuss "%section

    def getCaseResult(self, **info):
        # if DEBUG:
        # print(info)
        if len(info) != 0:
            section = list(info.keys())[0]
            ret = self.getCaseDetail(section)
            return [ret]
        sections = self.rf.getAllSection()
        infoList = []
        for section in sections:
            if section == "common":
                continue
            ret = self.getCaseDetail(section)
            if ret is False:
                continue
            infoList.append(ret)
        return infoList

    def getDictResult(self, strInfo):
        retDict = {}
        strList = strInfo.split("|")
        if len(strList) < 7:
            print("raw: ", strInfo)
        try:
            retDict["APIFunction"] = strList[0]
            retDict["http_method"] = strList[1]
            retDict["path"] = strList[2]
            retDict["url"] = strList[3]
            retDict["body"] = strList[4]
            retDict["TestTime"] = strList[5]
            retDict["TestResult"] = strList[6]
            if len(strList) >= 8:
                retDict["FailReason"] = strList[7]
            else:
                retDict["FailReason"] = ""
            if len(strList) >= 9:
                retDict["Response"] = strList[8]
            else:
                retDict["Response"] = ""
        except Exception as e:
            print("getDictResult exception: ", e)
            print("strInfo", strInfo)
            print("retDict", retDict)
        retDict["case_id"] = "%s_%s"%(retDict["http_method"], retDict["path"])
        return retDict

    def getCaseLoopResult(self, **info):
        infoList = []
        resultList = getApiStringList(self.project, mode="result")
        if len(info) != 0:
            section = list(info.keys())[0]
            for resultStr in resultList:
                retDict = self.getDictResult(resultStr)
                if section == retDict["case_id"]:
                    infoList.append(retDict)
        else:
            for resultStr in resultList:
                retDict = self.getDictResult(resultStr)
                infoList.append(retDict)
        return infoList

    def getTestReport(self, **info):
        resultList = getApiStringList(self.project, mode="result")
        if len(info) != 0:
            dictInfo = {}
            count = 0
            fCount = 0
            sCount = 0
            uCount = 0
            section = info.keys()[0]
            for resultStr in resultList:
                retDict = self.getDictResult(resultStr)
                if section == retDict["case_id"]:
                    dictInfo["APIFunction"] = retDict["APIFunction"] 
                    count = count + 1
                    if retDict["TestResult"] == "failure":
                        fCount = fCount + 1
                    elif retDict["TestResult"] == "success":
                        sCount = sCount + 1
                    else:
                        uCount = uCount + 1
                    dictInfo["TestResult"] = retDict["TestResult"]
                    dictInfo["FailReason"] = retDict["FailReason"]
            dictInfo["testTimes"] = count
            dictInfo["passTimes"] = sCount
            dictInfo["failTimes"] = fCount
            dictInfo["untestTimes"] = uCount
            dictInfo["case_id"] = section
            return [dictInfo]
        else:
            sections = self.cf.getAllSection()
            #sourceList = getApiStringList(self.project, mode="source")
            infoList = []
            for section in sections:
                if section == "common":
                    continue
                rawString = self.cf.getOption(section, "raw")
                if rawString:
                    apiInfo = rawString.replace("\"", "").split("|")
                else:
                    print("section: ", section)
                    print("rawString: ", rawString)
                    return infoList
            # for strSource in sourceList:
            #     apiInfo = strSource.split("|")
                dictInfo = {}
                section = "%s_%s"%(apiInfo[2], apiInfo[3])
                count = 0
                fCount = 0
                sCount = 0
                uCount = 0
                self.cf.getOption(section, "runNum")
                dictInfo["APIFunction"] = apiInfo[0]
                dictInfo["runTimes"] = self.cf.getOption(section, "runNum") 
                for resultStr in resultList:
                    # if DEBUG:
                    print("result Stry: ", resultStr)
                    retDict = self.getDictResult(resultStr)
                    if section == retDict["case_id"]:
                        count = count + 1
                        if retDict["TestResult"] == "untested":
                            uCount = uCount + 1
                        elif retDict["TestResult"] == "success":
                            sCount = sCount + 1
                        else:
                           fCount = fCount + 1
                        dictInfo["FailReason"] = retDict["FailReason"]
                if sCount > 0:
                    dictInfo["TestResult"] = "success"
                elif fCount > 0:
                    dictInfo["TestResult"] = "failure"
                elif uCount > 0:
                    dictInfo["TestResult"] = "untested"
                if count == 0:
                    dictInfo["TestResult"] = ""
                    dictInfo["FailReason"] = ""
                dictInfo["testTimes"] = count
                dictInfo["passTimes"] = sCount
                dictInfo["failTimes"] = fCount
                dictInfo["untestTimes"] = uCount
                dictInfo["case_id"] = section
                infoList.append(dictInfo)
            return infoList

    def getCountData(self, *infoList):
        sourceList = getApiStringList(self.project, mode="source")
        allCount = len(sourceList)
        sections = self.cf.getAllSection()
        unautomatableCount = 0
        for section in sections:
            runNum = self.cf.getOption(section, "runNum")
            if runNum and int(runNum) == 0:
                unautomatableCount = unautomatableCount + 1
        passCount = 0
        failCount = 0
        unTestCount = 0
        for info in infoList:
            if info["TestResult"] == "failure":
                failCount = failCount + 1
            elif info["TestResult"] == "success":
                passCount = passCount + 1
            elif info["TestResult"] == "untested":
                pass
            else:
                unTestCount = unTestCount + 1
        countDict = {}
        countDict["allCount"] = allCount
        countDict["automatableCount"] = allCount - unautomatableCount
        countDict["unautomatableCount"] = unautomatableCount
        countDict["autoTestCount"] = passCount + failCount
        countDict["unTestCount"] = unTestCount
        countDict["passCount"] = passCount
        countDict["failCount"] = failCount
        if countDict["allCount"] == 0:
            countDict["autoPer"] = 0
        else:
            countDict["autoPer"] = '{:.2%}'.format(round(countDict["automatableCount"], 2) / round(countDict["allCount"], 2))
        if countDict["autoTestCount"] == 0:
            countDict["passPer"] = 0
        else:
            countDict["passPer"] = '{:.2%}'.format(round(countDict["passCount"], 2) / round(countDict["autoTestCount"], 2))
        if countDict["autoTestCount"] == 0:
            countDict["failPer"] = 0
        else:
            countDict["failPer"] = '{:.2%}'.format(round(countDict["failCount"], 2) / round(countDict["autoTestCount"], 2))

        return countDict

class HostEnv(object):
    """docstring for HostEnv"""
    def __init__(self):
       self.hf = localConfigParser("%s/local/%s/%s"%(curPath, configPath, hConfig))

    def postHostEnv_27(self, **info):
        section = info["PRODUCTION"][0]
        if len(section) == 0:
            return 
        for option in info.keys():
            if option == "modify":
                continue
            value = info[option][0]
            self.hf.writeSection(section, option, value)
        return "Add %s Success "%section

    def postHostEnv(self, **info):
        section = info["PRODUCTION"]
        if len(section) == 0:
            return 
        for option in info.keys():
            if option == "modify":
                continue
            value = info[option]
            self.hf.writeSection(section, option, value)
        return "Add %s Success "%section


    def deleteHostEnv(self, **info):
        section = list(info.keys())[0]
        self.hf.removeSection(section)
        return "Delete %s Succuss "%section

    def putHostEnv(self, **info):
        section = info["project_id"]
        for option in info.keys():
            value = info[option]
            self.hf.writeSection(section, option, value)
        return "Modify %s Success "%section

    def getEnvHost(self):
        infoList = []
        sections = self.hf.getAllSection()
        for section in sections:
            options = self.hf.getAllItem(section)
            options["PRODUCTION"] = section
            infoList.append(options)
        return infoList

class Env(object):
    """docstring for Env"""
    def __init__(self, project):
        #rConfig = "%s-API-Result.ini"%project.upper()
        rConfig = "%s-API-Dependancy.ini"%project.upper()
        self.rf = localConfigParser("%s/local/%s/%s"%(curPath, configPath, rConfig))
        commonOption = ["noChkVar", "uniVar"]
        for option in commonOption:
            if not self.rf.getOption("common", option):
                self.rf.writeSection("common",  option, "[]")

    def postEnv(self, var_id, value):
        ret = self.rf.getOption("common", var_id)
        self.rf.writeSection("common", var_id, value)
        return "Save %s Env Var Succuss ~ "%(var_id)

    def getEnv(self, **info):
        if not self.rf.getSection("common"):
            return []
        if len(info) != 0:
            option = info.keys()[0]
            value = self.rf.getOption("common", option)
            if value is False:
                return [{"name": option, "value": "Not Define"}]
            else:
                return [{"name": option, "value": value}]
        options = self.rf.getAllOption("common")
        infoList = []
        for option in options:
            value = self.rf.getOption("common", option)
            if value is False:
                continue
            infoList.append({"name": option, "value": value})
        return infoList

    def deleteEnv(self, **info):
        option = list(info.keys())[0]
        self.rf.removeOption("common", option)
        return "Delete %s Succuss "%option

class Source(object):
    def __init__(self, project):
        self.project = project
        dConfig = "%s-API-Dependancy.ini"%project.upper()
        self.df = localConfigParser("%s/local/%s/%s"%(curPath, configPath, dConfig))

    def getSConfig(self):
        infoList = []
        sections = self.df.getAllSection()
        for section in sections:
            if section == "common":
                continue
            apiString = self.df.getOption(section, "raw")
            if not apiString:
                continue
            apiString = apiString.replace("\"", "")
            apiDict = {}
            # if DEBUG:
            #     print("apiString: ", apiString)
            if len(apiString) == 0:
                continue
            apiList = apiString.split("|")
            # if DEBUG:
                # apiList
            try:
                apiDict["APIFunction"] = apiList[0]
                apiDict["protocol"] = apiList[1]
                apiDict["http_method"] = apiList[2]
                apiDict["path"] = apiList[3]
                if len(apiList[5]) != 0:
                    apiDict["pathVariable"] = eval(apiList[5])
                else:
                    apiDict["pathVariable"] = apiList[5]
                if len(apiList[6]) != 0:
                    apiDict["queryParameter"] = eval(apiList[6])
                else:
                    apiDict["queryParameter"] = apiList[6]
                if len(apiList[7]) != 0:
                    apiDict["body"] = eval(apiList[7])
                else:
                    apiDict["body"] = apiList[7]
                if len(apiList[8]) != 0:
                    apiDict["response"] = eval(apiList[8])
                else:
                    apiDict["response"] = apiList[8]
                apiDict["case_id"] = "%s_%s"%(apiDict["http_method"], apiDict["path"])
                apiDict["raw"] = apiString
                infoList.append(apiDict)
            except Exception as e:
                print("getSConfig exception: ", e)
                print("apiString: ", apiString)
        return infoList

    def postSConfig(self, **info):
        if len(info['http_method'])==0 or len(info['path'])==0:
            return "Please Input http_method and path"
        String = '\"%s|%s|%s|%s|%s|%s|%s|%s|%s\"'%(info['APIFunction'], info['protocol'], info['http_method'], info['path'], str(info['header']).replace('\"', '\''), str(info['pathVar']).replace('\"', '\''), str(info['queryParam']).replace('\"', '\''), str(info['body']).replace('\"', '\''), str(info['response']).replace('\"', '\''))
        section = "%s_%s" %(info['http_method'], info['path'])
        self.df.writeSection(section,"raw", String)
        return True

    def delSConfig(self, **info):
        section = list(info.keys())[0]
        self.df.removeSection(section)
        return True

    def putSConfig(self, **info):
        section = info["section"]
        new_raw = info['new_raw']
        self.df.writeSection(section, "raw", new_raw)
        return True

    def putAllSConfig(self, **info):
        infoList = eval(info["value"])
        for item in infoList:
            self.putSConfig(**item)
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(version='1.1', description="Create API Info File for Auto Test")
    parser.add_argument('-m','--module', dest="module", action="store", default="N", help="%s; default value is N for Not, [ all ] for all modules"%modules.keys())
    parser.add_argument('-r','--run', dest="runAPI", action="store", default="None", help="[ Y/N ] Y for Yes, N for No;default value is [ None ] for Empty")
    parser.add_argument('-t','--api', dest="targetAPI", action="store", default="None", help="[ method_API/all ], [ get_/device/{sn}/app-user ] for special api , [ all ] for all API, default value is [ None ] for Empty")
    parser.add_argument('-H','--human-readable', dest="manRead", action="store", default="Y", help="[ Y/N ] Y for Yes, N for No;default value is [ Y ]")
    parser.add_argument('-n','--number', dest="number", action="store", default=1, help="[ 0/1/xxx ] 1 for all times, xxx for xxx times;default value is [ 1 ]")
    args = parser.parse_args()
    runModes = ["Y", "N"]
    if args.runAPI.upper == "N":
        parser.print_help()
    elif (args.runAPI.upper() == "Y") and (args.targetAPI.upper() == "ALL"):
        runAPIs(args.module.upper())
    elif args.targetAPI == "None":
        parser.print_help()
    else:
        status, output = runTargetAPI(args.module.upper(), args.targetAPI, args.number, mode="loop")
        if not status:
            print(output)

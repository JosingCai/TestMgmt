# apicase.py
import datetime
import random
import uuid
import requests
import os
from pandas.tseries.offsets import Day
from AutoModel.models import Host, Dependency, Result, Source, TestDetail, ComVar,TestReport
from itertools import product
from AutoModel.common import MyThread
import logging
import commands
logger = logging.getLogger(__name__) 

today = datetime.datetime.now().strftime('%Y-%m-%d')
curPath = os.getcwd()
LogPath = "log"

class RawAPI(object):
    """docstring for RawAPI"""
    def __init__(self,  module, apiString):
        self.apiDict = {}
        apiList = apiString.split("|")
        logger.info("apiString: %s" %apiString)
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
                self.apiDict["body"] = eval(apiList[7])
            else:
                self.apiDict["body"] = apiList[7]
            if len(apiList[8]) != 0:
                self.apiDict["response"] = eval(apiList[8])
            else:
                self.apiDict["response"] = apiList[8]
        except Exception as e:
            logger.warning("exception: %s" %e)
            logger.info("apiList: %s" %apiList)
        self.apiDict["section"] = "%s_%s"%(self.apiDict["http_method"], self.apiDict["path"])
        host_ret = list(Host.objects.filter(project_id=module).values())
        self.hostDict = host_ret[0]
        headers = {"Accept": "application/json"}
        if ("auth" in self.hostDict) and (self.hostDict["auth"].lower() == "yes"):
            if "BOOT" in module:
                headers["Authorization"] = self.hostDict["token"]
            else:
                headers["access-token"] = self.hostDict["token"]
        self.hostDict["headers"] = headers
        logger.debug("apiDict: %s" %self.apiDict)
        logger.debug("hostDict: %s" %self.hostDict)

class API(RawAPI):
    """docstring for API"""
    def __init__(self, module, apiString):
        #RawAPI.__init__(self, apiString)
        super(API, self).__init__(module, apiString)
        self.module = module
        self.logFile = "%s-API-%s.log"%(self.module, today)
        case_ret = list(Dependency.objects.filter(case_id=self.apiDict["section"]).values())
        self.case_info = case_ret[0]
        logger.debug("case_info: %s" %self.case_info)
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
        if runNum:
            self.runNum = runNum
        else:
            self.runNum = 1

        self.param_def = []
        if param_def:
            self.param_def = eval(param_def)
    
    def expectAPI(self):
        if self.runNum == 0:
            logger.warning("%s has 0 runNum test ..."%self.apiDict["section"])
            response = {"status": "untested", "message": "未测试"}
            url = self.getRawUrl()
            data = ""
            self.saveTestReport(url, data, response)
            return True, "%s has 0 runNum test ..."%self.apiDict["section"]
        return False, "Common Test"

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
                if out_ret:
                    outVars = out_ret[0]
                    logger.debug("befOutVars: %s" %outVars)
                    if outVars and (len(outVars) != 0) and len(outVars['outVars'])>0:
                        depOutVars.update(eval(outVars['outVars']))
        all_param_def = []
        if self.depIDs and len(self.depIDs) > 0:
            all_param_def = all_param_def + self.param_def + [self.apiDict['section']]
        else:
            all_param_def.append(self.apiDict['section'])
        for item in all_param_def:
            item_ret = list(ComVar.objects.filter(name=item, project_id=self.module).values())
            if item_ret and len(item_ret[0]['value']) > 0:
                ret = item_ret[0]
                if isinstance(item_ret[0]['value'], dict):
                    depOutVars.update(eval(ret['value']))
                elif isinstance(item_ret[0]['value'], list):
                    depOutVars[ret['name']] = eval(ret['value'])
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
            str255 = self.getRandomStr(255)
            str256 = self.getRandomStr(256)
            str257 = self.getRandomStr(257)
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
        ramStr255 = self.getRandomStr(255)
        int_10 = random.randint(0,9)
        curTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        before7day = (datetime.datetime.now() - 7*Day()).strftime('%Y-%m-%d %H:%M:%S')
        uuid_str = uuid.uuid1()
        defDict = {"description": "自动化-描述-%s"%self.apiDict["APIFunction"], "pid": 0, "tenantId": "default", \
        "remark": "自动化-备注-%s"%self.apiDict["APIFunction"], "name": "自动化-名称-%s"%ramStr8, \
        "number": "auto%s"%ramStr8, "date": curTime, "acquire_time": curTime, \
        "started_at": curTime, "onshelve_at": curTime, "fixed_asset_number": ramStr12, "sn": ramStr12, "uuid": uuid_str, \
        "cost_end": curTime, "cost_start": before7day}
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
                    if self.apiDict[pamra_type][Key] == "string":
                        if Key not in depOutVars:
                            if keyVar and (not isinstance(keyVar['value'], dict)):
                                depOutVars[Key] = eval(keyVar['value'])
                            else:
                                depOutVars[Key] = ramStr12
                    elif self.apiDict[pamra_type][Key] == "integer":
                        if Key not in depOutVars:
                            if keyVar and (not isinstance(keyVar['value'], dict)):
                                depOutVars[Key] = keyVar
                            else:
                                depOutVars[Key] = int_10
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
        logger.debug("depOutVars: %s" %depOutVars)
        return True, depOutVars

    def getUrlPath(self, url, **depOutVars):
        urlList = []
        status, depOutVars = self.prameter_format(**depOutVars)
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

        logger.debug("urlList: %s" %urlList)
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

            logger.debug("productList length: %d" %len(productList))
            logger.debug("keyList length: %d" %len(keyList))

            if len(productList) > 6:
                logger.debug("More Value: %s" %productList)
                logger.debug("More Key : %s" %keyList)
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
        logger.debug("queryStrList: %s" %queryStrList)
        logger.debug("queryStrList length: %d" %len(queryStrList))
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
        key_all = []
        if len(self.apiDict["body"]):
            key_all = self.apiDict["body"].keys()
        keyList = []
        for Key in key_all:
            if Key not in depOutVars:
                return False, "No %s Var in depOutVars: %s" %(Key, depOutVars)
            if isinstance(depOutVars[Key], list) and (self.apiDict["body"][Key] != "array"):  #and len(depOutVars[Key])> 1:
                keyList.append(Key)
        forList = []
        productList = []
        for Key in keyList:
            productList.append(depOutVars[Key])
        for items in product(*productList):
            forList.append(items)
        for j in range(len(forList)):
            infoDict = {}
            if len(self.apiDict["body"]):
                for Key in self.apiDict["body"].keys():
                    infoDict[Key] = depOutVars[Key]
                    ret = self.chkUniVar(Key)
                    if ret:
                        infoDict[Key] = "auto%s"%self.getRandomStr(8)
                for i in range(len(keyList)):
                    Key = keyList[i]
                    Value = forList[j][i]
                    infoDict[Key] = Value
                bodyList.append(infoDict)
        logger.debug("bodyList: %s" %bodyList)
        return True, bodyList

    def assembleData(self, dep_mode="no"):
        url = self.getRawUrl()
        depOutVars = self.getDepVars()
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
        elif self.apiDict["http_method"] == "patch":
            resp = requests.patch(url, headers=self.hostDict["headers"], json=data, verify=False)
        elif self.apiDict["http_method"] == "head":
            resp = requests.head(url)
            logger.debug("resp.headers: %s" %resp.headers)
        curTime=datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

        if data:
            ret_old = list(Result.objects.filter(case_id=self.apiDict["section"], project_id=self.module).values())
            if len(ret_old) > 0:
                obj = Result.objects.filter(case_id=self.apiDict["section"],project_id=self.module).update(requestVars=data)
            else:
                obj = Result(case_id=self.apiDict["section"],requestVars=data, project_id=self.module)
                obj.save()
        if not resp.ok:
            logger.warning("resp.ok: %s" %resp.ok)
            try:
                info = resp.json()
                logger.debug("response: %s" %info)
                
                if ("message" in info) and ("status" in info):
                    response = {"status": info["status"], "message": "执行失败", "failReason": info["message"]}
                elif ("resultMessage" in info) and ("isSuccess" in info):
                    response = {"status": info["isSuccess"], "message": "执行失败", "failReason": info["resultMessage"]}
            except Exception as e:
                logger.error("runMethod 1 exception: %s" %e)
                response = {"status": "failure", "message": "执行失败", "failReason": resp.content}
            return False, response
        try:
            response = resp.json()
        except Exception as e:
            logger.error("runMethod 2 exception: %s" %e)
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
        if not response["content"]:
            response["content"] = "No Content"
        obj = TestDetail(case_id=self.apiDict["section"],APIFunction=self.apiDict["APIFunction"], url=url, body=str(data), response=response["content"], failReason=response['failReason'], testTime=TestTime,testResult=response['status'], project_id=project)
        obj.save()
        return True

    def saveOutVar(self, response):
        logger.debug("response: %s" %response)
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
                        try:
                            length = len(tmp[subItems[0]])
                        except Exception as e:
                            logger.error("saveOutVar %s exception: %s"%(item, e))
                            return False, "Get Vars to Output Failed"

                        for index in range(length):
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
                            try:
                                tmp = tmp[item]
                            except Exception as e:
                                logger.error("saveOutVar %s exception: %s"%(item, e))
                                return False, "Get Vars to Output Failed"
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
                            logger.error("saveOutVar %s exception: %s"%(item, e))
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
        noChkVars = {}
        if len(nochk_ret) > 0:
            noChkVars = nochk_ret[0]["value"]
        passList = []
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
                            logger.error("chkItem 1 exception: %s" %e)
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
                                logger.error("chkItem 2 exception: %s" %e)
                                items.append("")
                    chkVars[Key] = items
                else:
                    if isinstance(tmp, int):
                        chkVars[Key] = tmp
                    else:
                        try:
                            chkVars[Key] = tmp.encode("utf-8") 
                        except Exception as e:
                            logger.error("chkItem 3 exception: %s" %e)
                            chkVars[Key] = tmp
            chkInfo.update(chkVars)

        Keys = reqDict.keys() 
        logger.debug("reqDict: %s" %reqDict)
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
        logger.debug("passList: %s" %passList)
        return flag, cmpDict

    def analysisReponse(self, url, data, response):
        if not self.saveTestReport(url, data, response):
            logger.error("Save Test Result Failed ... ")
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

def getSpecApi(module, method_API):
    ret_list = list(Dependency.objects.filter(project_id=module,case_id=method_API).values())
    if len(ret_list) > 0:
        apiString = ret_list[0]['raw']
    if not apiString:
        return False, [{"case_id": method_API, "response": "Get API raw info failed, Please Check it ~ "}]
    else:
        return True, apiString

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
    logger.debug("Run Mode: %s, Run Number: %d" %(mode, number))
    status, output = api.expectAPI()
    logger.debug("status: %s,  output: %s" %(status, output))
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
        logger.debug("single reqList: %s" %reqList)
        reqList = [reqList[0]]
    elif number != 1:
        status, reqList = api.assembleData(dep_mode="yes")
        if len(reqList) < number:
            loopNum = int(number/len(reqList)) + 1
            for i in range(loopNum):
                status, tmpList = api.assembleData()
                reqList = reqList + tmpList
        reqList = random.sample(reqList, number)
        #return False, [{"case_id":api.apiDict["section"], "response": reqList}]
    else:
        status, reqList = api.assembleData()

    if not status:
        return False, [{"case_id":api.apiDict["section"], "response": reqList}]
    
    logger.debug("reqList: %s" %reqList)
    resultList = []
    logger.debug("AfterCase: %s, CheckMode: %s, Mode: %s" %(api.chkIDs, chkMode, mode))
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
        logger.debug("Threading Mode: %s" %api.hostDict["threading"])
        if api.hostDict["threading"] == "False":
            for info in reqList:
                status, retDict = threadRun(api, info["url"], info["body"])
                resultList.append(retDict)
        else:
            threads = []
            length = len(reqList)
            logger.debug("Concurrent Times: %d" %length)
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
    status, output = runAPI(module, apiString, number, mode=mode, chkMode="yes")
    if not status:
        logger.error("run output: %s" %output)
    return True, output

def runAPIs(module):
    ret_list = list(Dependency.objects.filter(project_id=module).values())
    resultList = []
    for item in ret_list:
        case_id = item["case_id"]
        run_result = list(Result.objects.filter(case_id=case_id, project=module).values())
        if len(run_result) > 0:
            logger.info("Already run: %s" %case_id)
            continue
        status, loopList = runTargetAPI(module, case_id, mode="single")
        resultList = resultList + loopList
    return resultList

#swagger.py
import subprocess
import json
from bs4 import BeautifulSoup


def analysis_HTML(content):
    soup = BeautifulSoup(content, "html.parser")
    infoList = []
    for item in soup.body.findAll("li", {"class": "endpoint"}):
        spans = item.h3.findAll("span")
        infoDict = {}
        for span in spans:
            Key = span['class'][0]
            Value = span.a.string
            infoDict[Key] = Value.encode("utf-8").decode("utf-8")
        context = item.findAll("div", {"class": "content"})
        Key = "APIFunction"
        try:
            Value = context[0].div.p.string
            infoDict[Key] = Value.encode("utf-8").decode("utf-8")
        except:
            infoDict[Key] = ""
        content = item.findAll("div", {"class": "signature-container"})
        for i in range(len(content)):
            if i == 0:
                rawInfos = content[i].pre.code.text.encode("utf-8").decode("utf-8")
                res_tmp = rawInfos.replace("\n", "")
                infoDict["response"] = res_tmp.replace("'", "\"")
        parameList = []
        subItems = item.findAll("tr")
        lenEnd = len(subItems)-4
        for tr in subItems[1:lenEnd]:
            tds = tr.findAll("td")
            parameDict = {}
            for i in range(len(tds)):
                if i == 0:
                    try:
                        paramaName = tds[i].label.string.encode("utf-8")
                        parameDict["parameName"] = paramaName.decode("utf-8")
                    except:
                        parameDict["parameName"] = ""
                elif i == 2:
                    try:
                        paramaDesc = tds[i].p.string.encode("utf-8")
                        parameDict["parameDesc"] = paramaDesc.decode("utf-8")
                    except:
                        parameDict["parameDesc"] = ""
                elif i == 3:
                    try:
                        paramaType = tds[i].string.encode("utf-8")
                        parameDict["parameType"] = paramaType.decode("utf-8")
                    except:
                        parameDict["parameType"] = ""
                elif i == 4:
                    if parameDict["parameType"] != "body":
                        try:
                            paramaValue = tds[i].span.string.encode("utf-8")
                            parameDict["parameValue"] = paramaValue.decode("utf-8")
                        except:
                            parameDict["parameValue"] = ""
                    else:
                        indexNum = len(tds) - 1
                        try:
                            rawInfos = tds[indexNum].pre.code.text.encode("utf-8")
                            #parameDict["parameValue"] = rawInfos.replace("\n", "").decode("utf-8")
                            parameDict["parameValue"] = rawInfos.decode("utf-8").replace("\n", "")
                        except:
                            parameDict["parameValue"] = ""
            parameList.append(parameDict)

            headerDict = {}
            queryDict = {}
            bodyDict = {}
            pathDict = {}
            for info in parameList:
                if len(info) == 0:
                    continue
                if info["parameType"] == "header":
                    headerDict[info["parameName"]] = info["parameValue"]
                elif info["parameType"] == "query":
                    queryDict[info["parameName"]] = info["parameValue"]
                elif info["parameType"] == "body":
                    print(info["parameValue"])
                    bodyDict[info["parameName"]] = info["parameValue"]
                elif info["parameType"] == "path":
                    pathDict[info["parameName"]] = info["parameValue"]

            infoDict["header"] = headerDict
            infoDict["queryParameter"] = queryDict
            infoDict["body"] = bodyDict
            infoDict["pathVariable"] = pathDict
        infoList.append(infoDict)
    return infoList

def createJMeterF(module):
    sourceFN = "static/raw/%s.html"%module
    with open(sourceFN) as f:
        context =  f.read()
    infoList = analysis_HTML(context)
    for info in infoList:
        http_method = info["http_method"]
        path = info["path"]
        APIFunction = info["APIFunction"]
        try:
            header = str(info["header"])
        except:
            header = ""
        caseNumber = "%s_%d"%(module, count)
        count = count + 1 
        try:
            if len(info["response"]) == 0:
                response = ""
            else:
                response = str(info["response"]) 
        except:
            response = ""
        try:
            if len(info["header"]) == 0:
                header = ""
            else:
                header = str(info["header"])
        except: 
            header = ""
        try:
            if len(info["pathVariable"]) == 0:
                pathVariable = ""
            else:
                pathVariable = str(info["pathVariable"])
        except: 
            pathVariable = ""
        try:
            if len(info["queryParameter"]) == 0:
                queryParameter = ""
            else:
                queryParameter = str(info["queryParameter"])
        except:
            pathVariable = ""
        try:
            if not info['body'].has_key("form"):
                if len(info["body"]) == 0:
                    body = ""
                else:
                    body = str(info["body"])
            else:
                if len(info["body"]["form"]) == 0:
                    body = ""
                else:
                    body = str(info["body"]["form"])
        except:
            body = ""

        String = runItOrNot + "|" + caseNumber + "|" + APIFunction + "|" + http_method + "|" + path + "|" + body + "|" + response

    return True

def html2string(module):
    sourceFN = "static/raw/%s.html"%module
    with open(sourceFN) as f:
        context =  f.read()
    infoList = analysis_HTML(context)
    all_list = []
    for info in infoList:
        http_method = info["http_method"]
        path = info["path"]
        APIFunction = info["APIFunction"]
        try:
            if len(info["response"]) == 0:
                response = ""
            else:
                response = str(info["response"]) 
        except:
            response = ""
        try:
            if len(info["header"]) == 0:
                header = ""
            else:
                header = str(info["header"])
        except: 
            header = ""
        try:
            if len(info["pathVariable"]) == 0:
                pathVariable = ""
            else:
                pathVariable = str(info["pathVariable"])
        except: 
            pathVariable = ""
        try:
            if len(info["queryParameter"]) == 0:
                queryParameter = ""
            else:
                queryParameter = str(info["queryParameter"])
        except:
            pathVariable = ""
        # try:
        if "form" in info['body']:
            if len(info["body"]["form"]) == 0:
                body = ""
            else:
                body = str(info["body"]["form"])
        elif "JSONBody" in info['body']:
            if len(info["body"]["JSONBody"]) == 0:
                body = ""
            else:
                body = str(info["body"]["JSONBody"])
        else:
            body = str(info['body'])
        # except:
        #     body = ""
        String = str(APIFunction) + "|" + 'http' + "|" + str(http_method) + "|" + str(path) + "|" + str(header) + "|" + str(pathVariable) + "|" + str(queryParameter) + "|" + str(body) + "|" + str(response)
        all_list.append(String)
    return all_list

def analysis(module):
    cmd = "ls static/raw/%s*" %module
    status, output = subprocess.getstatusoutput(cmd)
    if status != 0:
        print("output: ", output)
        return False, "Get %s Swagger File Failed, Please Check it ~" %module
    fileList = output.split("\n")
    fileName = fileList[0]
    with open(fileName) as f:
        content = f.read()
    if fileName.endswith(".yaml"):
        rawDict = yaml.load(content)
    elif fileName.endswith(".json"):
        rawDict = json.loads(content)
    else:
        return False, "Not Support Current %s Format File" %fileName
    # print("rawDict: ", rawDict)
    definitions = rawDict["definitions"]
    simple_def_dict = {}
    full_def_dict = {}
    response_dict = {}
    mult_def_key = []
    informal_def = []

    def_desc_all = {}
    for Key in definitions.keys():
        if "properties" in definitions[Key]:
            properties = definitions[Key]["properties"]
            def_desc = {}
            for subKey in properties.keys():
                if "description" in properties[subKey]:
                    def_desc[subKey] = properties[subKey]["description"]
                else:
                    def_desc[subKey] = ""
        def_desc_all[Key] = def_desc

    for Key in definitions.keys(): 
        if "properties" in definitions[Key]:
            properties = definitions[Key]["properties"]
            subDict = {}
            for subKey in properties.keys():
                if "$ref" in properties[subKey]:
                    def_dict = {}
                    # print("%s : %s" %(subKey, properties[subKey]))
                    obj = properties[subKey]["$ref"].split("/")[-1]
                    def_dict["name"] = subKey
                    def_dict["value"] = obj
                    mult_def_key.append(def_dict)
                    break
                subDict[subKey] = properties[subKey]["type"]
            simple_def_dict[Key] = subDict
        else:
            informal_def.append(Key)
            simple_def_dict[Key] = ""
    # print("informal_def: ", informal_def)
    for Key in definitions.keys(): 
        if "properties" in definitions[Key]:
            properties = definitions[Key]["properties"]
            subDict = {}
            for subKey in properties.keys():
                if "$ref" in properties[subKey]:
                    obj = properties[subKey]["$ref"].split("/")[-1]
                    try:
                        subDict[subKey] = simple_def_dict[obj]
                    except:
                        subDict[subKey] = ""
                else:
                    subDict[subKey] = properties[subKey]["type"]
            Key = Key.encode("utf-8").decode("utf-8")
            full_def_dict[Key] = subDict
    if "responses" in rawDict:
        response_info = rawDict["responses"]
    else:
        response_info = {}
    for Key in response_info.keys():
        if "schema" in response_info[Key]:
            try:
                properties = response_info[Key]["schema"]["properties"]["content"]["properties"]
                sub_dict = {}
                for subKey in properties.keys():
                    sub_dict[subKey] = properties[subKey]["type"] 
                response_dict[Key] = sub_dict
            except Exception as e:
                print("resp exception: ", e)
                print("resp: ", response_info[Key])
        else:
            print("resp: ", response_info[Key])
            print("undef key: ", subKey)
            response_dict[Key] = ""
    simple_def_dict.update(response_dict)
    simple_def_dict.update(full_def_dict)
    items = rawDict["paths"]
    infoList = []
    for item in items.keys():
        path = item.encode("utf-8").decode("utf-8")
        apiCollection = items[item]
        for method in apiCollection.keys():
            infoDict = {}
            infoDict["varDesc"] = {}
            apiInfo = apiCollection[method]
            if "tags" in apiInfo:
                infoDict["group"] = apiInfo["tags"][0]
            else:
                infoDict["group"] = "Other"
            infoDict['http_method'] = method.encode("utf-8").decode("utf-8")
            infoDict['APIFunction'] = apiInfo["summary"].encode("utf-8").decode("utf-8")
            try:
                infoDict['response'] = apiInfo["responses"]
            except Exception as e:
                print("1 exception: ", e)
                infoDict['response'] = ""
            infoDict['path'] = path
            try:
                responseList = apiInfo["responses"]["200"]["$ref"].split("/")
                responseKey = responseList[-1]
            except Exception as e:
                print("2 exception: ", e)
                responseKey = ""
            try:
                infoDict['response'] = simple_def_dict[responseKey]
            except Exception as e:
                print("3 exception: ", e)
                infoDict['response'] = ""
            try:
                parameters = apiInfo["parameters"]
            except Exception as e:
                print("4 exception: ", e)
                parameters = ""

            parameList = []
            headerDict = {}
            queryDict = {}
            bodyDict = {}
            pathDict = {}
            descDict = {}

            for i in range(len(parameters)):
                parameDict = {}
                parameter = parameters[i]
                if parameter["in"] == "body":
                    if "$ref" in parameter['schema']:
                        subparameList = parameter['schema']["$ref"].split("/")
                        defiKey = subparameList[-1]
                        if defiKey =="PostDeviceReq":
                            parameDict["parameValue"] = simple_def_dict['Device']
                        else:
                            try:
                                parameDict["parameValue"] = simple_def_dict[defiKey]
                            except Exception as e:
                                print("7 exception: ", e)
                                parameDict["parameValue"] = ""
                        try:
                            infoDict["varDesc"].update(def_desc_all[defiKey])
                        except Exception as e:
                            print("8 exception: ", e)
                            parameDict["varDesc"] = ""
                    else:
                        parameDict["parameValue"] = parameter['schema']["type"]
                elif parameter["in"] == "query":
                    if "$ref" in parameters[i]:
                        obj = parameters[i]["$ref"].split("/")[-1]
                        parameDict["parameValue"] = simple_def_dict[obj]
                        infoDict["varDesc"].update(def_desc_all[obj])
                    else:
                        try:
                            parameDict["parameValue"] = parameter["type"]
                        except Exception as e:
                            print("5 exception: ", e)
                            parameDict["parameValue"] = ""
                else:
                    try:
                        parameDict["parameValue"] = parameter["type"]
                    except Exception as e:
                        print("type exception: ", e)
                        parameDict["parameValue"] = ""

                parameDict["parameName"] = parameter["name"]
                try:
                    parameDict["parameDesc"] = parameter["description"]
                except Exception as e:
                    print("description exception: ", e)
                    parameDict["parameDesc"] = ""
                parameDict["parameType"] = parameter["in"]
                parameList.append(parameDict)

            for info in parameList:
                if len(info) == 0:
                    continue
                if info["parameType"] == "header":
                    headerDict[info["parameName"]] = info["parameValue"]
                elif info["parameType"] == "query":
                    queryDict[info["parameName"]] = info["parameValue"]
                elif info["parameType"] == "body":
                    bodyDict[info["parameName"]] = info["parameValue"]
                elif info["parameType"] == "path":
                    pathDict[info["parameName"]] = info["parameValue"]
                descDict[info["parameName"]] = info["parameDesc"]
            infoDict["header"] = headerDict
            if "Body" in queryDict:
                infoDict["queryParameter"] = queryDict["Body"]
            else:
                infoDict["queryParameter"] = queryDict
            infoDict["body"] = bodyDict
            infoDict["pathVariable"] = pathDict
            infoDict["varDesc"].update(descDict)
            infoList.append(infoDict)
    return True, infoList

def json2string(project):
    status, infoList = analysis(project)
    all_list = []
    if not status:
        print("A had occured …… ")
    for info in infoList:
        if not info:
            print("info: ", info)
            pass
        http_method = info["http_method"]
        path = info["path"]
        APIFunction = info["APIFunction"]
        group = info["group"]
        try:
            if len(info["response"]) == 0:
                response = ""
            else:
                response = str(info["response"]) 
        except Exception as e:
            print("exception: ", e)
            response = ""
        try:
            if len(info["header"]) == 0:
                header = ""
            else:
                header = str(info["header"])
        except Exception as e:
            print("exception: ", e) 
            header = ""
        try:
            if len(info["pathVariable"]) == 0:
                pathVariable = ""
            else:
                pathVariable = str(info["pathVariable"])
        except Exception as e:
            print("exception: ", e) 
            pathVariable = ""
        try:
            if len(info["queryParameter"]) == 0:
                queryParameter = ""
            else:
                queryParameter = str(info["queryParameter"])
                
        except Exception as e:
            print("exception: ", e)
            pathVariable = ""
        try:
            com_key = "Body"
            if com_key in info['body']:
                if len(info["body"][com_key]) == 0:
                    body = ""
                else:
                    body = str(info["body"][com_key])
            elif com_key in info['body']:
                if len(info["body"][com_key]) == 0:
                    body = ""
                else:
                    body = str(info["body"][com_key])
            elif "data" in info["body"]:
                body = str(info["body"]['data'])
            else:
                body = ""
        except Exception as e:
            print("exception: ", e)
            body = ""
        #String = group + "|" + APIFunction + "|" + PROTOCOL + "|" + http_method + "|" + path + "|" + header + "|" + pathVariable + "|" +queryParameter + "|" + body + "|" + response
        String = APIFunction + "|" + "http" + "|" + http_method + "|" + path+ "|" + header + "|" + pathVariable + "|" + queryParameter + "|" + body + "|" + response
        all_list.append(String)
    return all_list

    if manRead == "Y":
        humanReadable(targetFN)
        return True

class AutoSource(object):
    """docstring for Source"""
    def __init__(self, project):
        self.project = project

    def createAutoData(self):
        html_item = ["REPORT", "DISCOVERY"]
        if self.project.upper() in html_item:
            all_list = html2string(self.project)
        else:
            all_list = json2string(self.project)
        return all_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser(version='1.1', description="Create API Info File for Auto Test")
    parser.add_argument('-m','--module', dest="module", action="store", default="N", help="Project Name; default value is N for Not")
    parser.add_argument('-H','--human-readable', dest="manRead", action="store", default="Y", help="[ Y/N ] Y for Yes, N for No;default value is [ Y ]")
    args = parser.parse_args()

    if args.module.upper() == "N":
        parser.print_help()
    else:
        createCustomF(args.module.upper(), args.manRead)
    

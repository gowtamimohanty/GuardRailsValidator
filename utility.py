import requests,json, os
from os.path import dirname, join

def loadConfigFile():
    configFilePath = join(dirname(__file__), "config","org.json")
    config = json.load(open(configFilePath))    
    return config

def checkResponseCode(response):
    if not(response.status_code >= 200 and response.status_code <= 299):
        print(response.text)
        exit()

def checkAuthError(response):
    if (response.status_code >= 400 and response.status_code <= 499):
        return True
    else:
        return False

def checkKeyFile(privateKey):
    filename = privateKey.filename
    if "." in filename:
        ext = filename.rsplit(".", 1)[1]
        if ext.upper() in ["KEY"]:
            return True
        else:
            return False
    else:
        return False

def checkResponseCode(response):
   if not(response.status_code >= 200 and response.status_code <= 299):
      print(response.text)
      #print("\n"+ response["report"]["detailed-message"])

def checkDuplicateItems(selectedItems,destItems):
    duplicateItems=[]
    copySelectedItems=selectedItems.copy()
    for item in copySelectedItems:
        if item in destItems:
            duplicateItems.append(item)
            selectedItems.remove(item)

    print("Selected Item: ",str(selectedItems))
    print("Duplicate Item: ",str(duplicateItems))
    return selectedItems,duplicateItems

def saveResponseFile(filePath,componentName,componentResponse):
    os.makedirs(os.path.dirname(filePath), exist_ok=True)
    with open(filePath, 'w') as fp:
        json.dump(componentResponse,fp, indent=4)
    print("\n"+ componentName + " response saved in file")

def getAllIdNamespaces(headers):
    url = "https://platform.adobe.io/data/core/idnamespace/identities"
    payload={}
    headers['Accept']='application/json'
    response = requests.request("GET", url, headers=headers, data=payload)
    checkResponseCode(response)
    return response

def getAllMixins(headers):
    url = "https://platform.adobe.io/data/foundation/schemaregistry/stats"
    payload={}
    headers['Accept']='application/json'
    response = requests.request("GET", url, headers=headers, data=payload)
    checkResponseCode(response)
    return response


def getAllSchemas(headers):
    url = "https://platform.adobe.io/data/foundation/schemaregistry/tenant/schemas"
    payload={}
    headers['Accept']='application/vnd.adobe.xed-id+json'
    response = requests.request("GET", url, headers=headers, data=payload)
    checkResponseCode(response)
    return response


def getAllDatasets(headers, start=0, limit=99):
    url = "https://platform.adobe.io/data/foundation/catalog/dataSets?start={start}&limit={limit}&properties=name,description,files".format(start=int(start), limit=int(limit))
    payload={}
    headers['Accept']='application/json'
    response = requests.request("GET", url, headers=headers, data=payload)
    checkResponseCode(response)
    return response



def getAllSegments(headers):
    url = "https://platform.adobe.io/data/core/ups/segment/definitions"
    payload={}
    headers['Accept']='application/json'
    response = requests.request("GET", url, headers=headers, data=payload)
    checkResponseCode(response)
    return response

def getAllClasses(headers):
    url = "https://platform.adobe.io/data/foundation/schemaregistry/stats"
    payload={}
    headers['Accept']='application/json'
    response = requests.request("GET", url, headers=headers, data=payload)
    checkResponseCode(response)
    return response

def getAlldescriptor(headers):
    url = "https://platform.adobe.io/data/foundation/schemaregistry/tenant/descriptors"
    payload={}
    headers['Accept']='application/vnd.adobe.xdm-id+json'
    response = requests.request("GET", url, headers=headers, data=payload)
    checkResponseCode(response)
    return response  

def getAllProfiles(headers):
    url = "https://platform.adobe.io/data/core/ups/previewsamplestatus/report/namespace"
    payload={}
    headers['Accept']='application/json'
    response = requests.request("GET", url, headers=headers, data=payload)
    checkResponseCode(response)
    return response


def getAllDestinations(headers):
    url = "https://platform.adobe.io/data/core/activation/authoring/destinations"
    payload={}
    headers['Accept']='application/json'
    response = requests.request("GET", url, headers=headers, data=payload)
    checkResponseCode(response)
    return response


def getAllQueriess(headers):
    url = "https://platform.adobe.io/data/foundation/query/query-templates/count"
    payload={}
    headers['Accept']='application/json'
    response = requests.request("GET", url, headers=headers, data=payload)
    checkResponseCode(response)
    return response

def getAllschedules(headers):
    url = "https://platform.adobe.io/data/foundation/query/schedules"
    payload={}
    headers['Accept']='application/json'
    response = requests.request("GET", url, headers=headers, data=payload)
    checkResponseCode(response)
    return response

def getAllflows(headers):
    url = "https://platform.adobe.io/data/foundation/flowservice/flows"
    payload={}
    headers['Accept']='application/json'
    response = requests.request("GET", url, headers=headers, data=payload)
    checkResponseCode(response)
    return response


def getAllMergepolicies(headers):
    url = "https://platform.adobe.io/data/core/ups/config/mergePolicies?limit=50"
    payload={}
    headers['Accept']='application/json'
    response = requests.request("GET", url, headers=headers, data=payload)
    checkResponseCode(response)
    return response

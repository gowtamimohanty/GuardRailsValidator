from asyncio.windows_events import NULL
from collections import Counter
from flask import Flask,render_template,request,redirect,url_for,flash
import requests,json
import os
from flask import session
from os.path import dirname, join
from os import path
import pdfkit
import pdfkit
from flask import render_template, make_response,send_file
from utility import *
from auth import getAccessToken
from flask import Flask, send_file
from datetime import datetime
from flask import Flask, render_template, request, redirect, g
import sqlite3



app = Flask(__name__)
app.config['SECRET_KEY'] = 'SS!$#_'
app.config['CONFIG'] = join(dirname(__file__),"config/")
sourceSandboxHeaders={}
sourceSandboxDict={}
idNamespaceDict={}
flowsDict1={}
fieldGroupDict={}
schemaDict={}
mergeDict={}
datasetDict={}
segmentDict={}
profilesDict={}
classesDict={}
flowsDict={}
queryDict2={}
my_dictionary={}
idNamespaceDict2 ={}
idNamespaceDict3 ={}
idNamespaceDict1={}
destinationDict={}
users = []
sandboxDictsByOrg = {}



sourceTenantId = ""
def getTenantId(config):
    url = "https://platform.adobe.io/data/foundation/schemaregistry/stats"
    payload={}
    headers = {
    'Accept': 'application/json', 'Authorization': 'Bearer '+config["ACCESS_TOKEN"], 'x-api-key': config["API_KEY"], 'x-gw-ims-org-id': config["ORG_ID"], 'x-sandbox-name': 'prod',
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response
def loadHeaderFiles(orgName, orgData):
    headerFilePath = join(app.config['CONFIG'], "headerfiles")
    try:
        print(orgName)
        data = {"Accept": "application/json",
        "Authorization": 'Bearer ' + orgData["ACCESS_TOKEN"],
        "x-api-key": orgData["API_KEY"],
        "x-gw-ims-org-id": orgData["ORG_ID"]
        }
        with open(join(headerFilePath,f'{orgName}-headers.json'), 'w') as f:
            json.dump(data, f,indent=4)
            f.close() 
            print("The headerfile has also created/updated.")
    except:
        print(f'{orgData} header file not found! Try to delete and authorise again!')
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('users.db')
        g.db.row_factory = sqlite3.Row
    return g.db





@app.route('/', methods=['GET','POST'])
def home():
    if request.method == "GET":
        return render_template('home.html')
    elif request.method == "POST":
        return redirect(url_for('login'))




@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get the user's name, email, and password from the form
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Add the user to the database
        db = get_db()
        db.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                   (name, email, password))
        db.commit()

        # Set the "logged_in" key to True in the session
        session['logged_in'] = True

        # Redirect to the homepage
        return redirect('/login')

    # If the request method is GET, render the signup page
    return render_template('signup.html')


      



# Define a route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the user's email and password from the form
        email = request.form['email']
        password = request.form['password']

        # Check if the user is registered
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ? AND password = ?',
                          (email, password)).fetchone()
        if user is not None:
            # If the user is registered, redirect to the homepage
            return redirect('auth')

        # If the user is not registered, show an error message
        error = 'Invalid email or password'
        return render_template('login.html', error=error)

    # If the request method is GET, render the login page
    return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    # Clear the session cookie and redirect to the login page
    session.clear()
    return redirect(url_for('login'))



@app.route('/auth', methods = ["GET","POST"])
def auth():
    orgFile = join(app.config['CONFIG'], "orgData.json")
    if not path.isfile(orgFile):
        os.makedirs(os.path.dirname(orgFile), exist_ok=True)
        with open(orgFile, 'w') as fp:
            json.dump({},fp,indent=4)
            fp.close()
        print("org.json created at "+orgFile)
    with open(orgFile, 'r') as fp:
        org = json.load(fp)
        fp.close()
    if request.method == "GET":
        #if len(list(org.keys()))>0:
        try:
            for orgdata in org:
                print("Org Name : ",orgdata)
                config = org[orgdata]
                if "ACCESS_TOKEN" in config.keys():
                    response = getTenantId(config)
                    if checkAuthError(response):
                        print("found expired accessToken. new accessToken will be generated.")
                        getAccessToken(orgdata)
                        with open(orgFile, 'r') as fp:
                            org = json.load(fp)
                            fp.close()
                        config = org[orgdata]
                        response = getTenantId(config)
                    else:
                        print("found working accessToken.")
                    response=json.loads(response.text)
                    config['tenantId'] = response['tenantId']
                    org[orgdata] = config
                    with open(orgFile, 'w') as fp:
                        json.dump(org,fp,indent=4)
                        fp.close()
                    loadHeaderFiles(orgdata, org[orgdata])
                else:
                    print("AccessToken not found! Generating new one.")
                    getAccessToken(orgdata)
            return render_template("auth.html", org=org)
        except:
            print("Error")
            return render_template("auth.html")
    elif request.method == "POST":
        with open(orgFile, 'r') as fp:
            org = json.load(fp)
            fp.close()
        if request.files:
            config=request.files["config-json"]
            privateKey = request.files["private-key"]
            orgName = request.form.get("org-name")
            if config.mimetype=='application/json' and checkKeyFile(privateKey):
                # Save the both the file in the directory and redirect to sandbox browse page
                print(config,privateKey)
                config = json.load(config)
                org[orgName] = config
                print(config)
                # config.save(join(app.config["CONFIG"], f"{orgName}.json"))
                privateKey.save(join(app.config["CONFIG"],"privatekeys", f"{orgName}-private.key"))
                print(org)
                with open(orgFile, 'w') as fp:
                    json.dump(org,fp,indent=4)
                    fp.close()
                print("generated new accessToken from uploaded file rn.")
                getAccessToken(orgName)  # Call auth.getAccessToken to generate token and update in the config file
                flash("Authorization Successfull.", category='success')
                with open(orgFile, 'r') as fp:
                    org = json.load(fp)
                    config = org[orgName]
                    fp.close()
                response = getTenantId(config)
                response=json.loads(response.text)
                config['tenantId'] = response['tenantId']
                org[orgName] = config
                with open(orgFile, 'w') as fp:
                    json.dump(org,fp,indent=4)
                    fp.close()
                return render_template("auth.html", org=org)
            else:
                flash("Invalid File Type!", category='error')
                print("Invalid File type.")
            return render_template("auth.html", org=org)
@app.route('/auth/delete/<orgName>',methods = ["GET","POST"])
def authDelete(orgName):
    orgFile = join(app.config['CONFIG'], "orgData.json")
    with open(orgFile, 'r') as fp:
        org = json.load(fp)
        fp.close()
    del org[orgName]
    with open(orgFile, 'w') as fp:
        json.dump(org,fp,indent=4)
        fp.close()
    headerFilePath = join(app.config['CONFIG'],'headerfiles',f'{orgName}-headers.json')
    privateKeyFilePath = join(app.config['CONFIG'],'privatekeys',f'{orgName}-private.key')
    if os.path.exists(headerFilePath):
        os.remove(headerFilePath)
    else:
        print(f"The {headerFilePath} does not exist")
    if os.path.exists(privateKeyFilePath):
        os.remove(privateKeyFilePath)
    else:
        print(f"The {privateKeyFilePath} does not exist")
    return render_template("auth.html", org=org)
@app.route('/sandbox/<step>', methods=['GET','POST'])
def sandbox(step):
    global sourceSandboxHeaders
    global orgList
    global sourceTenantId
    global sandboxDictsByOrg  # new global variable to store sandbox dictionaries for each source organization
    
    with open(join(app.config["CONFIG"], "orgData.json"),'r') as f:
        orgData = json.load(f)
    
    if request.method=="GET":
        orgList = list(orgData.keys())
        return render_template('organisation.html', orgList=orgList)
    
    if request.method=="POST":
        if step=='org':
            srcOrg = request.form.get("sourceOrg")
            session['srcorg'] = srcOrg
            
            # create a new sandbox dictionary for the selected source organization, and store it in the sandboxDictsByOrg dictionary
            sandboxDictsByOrg[srcOrg] = {}
            
            with open(join(app.config["CONFIG"],"headerfiles", f"{srcOrg}-headers.json"),'r') as f:
                sourceSandboxHeaders = json.load(f)
            
            url = "https://platform.adobe.io/data/foundation/sandbox-management/"
            response = requests.request("GET", url, headers=sourceSandboxHeaders)
            checkResponseCode(response)
            response=json.loads(response.text)
            
            # populate the sandbox dictionary for the selected source organization
            for i in response['sandboxes']:
                sandboxDictsByOrg[srcOrg][i['title']] = i['name']
            
            # get the sandbox list for the selected source organization
            sandboxList=list(sandboxDictsByOrg[srcOrg].keys())
            
            sourceTenantId = orgData[srcOrg]['tenantId']
            return render_template('sandbox.html', sourceOrg=srcOrg, sourceSandboxList=sandboxList)
        
        elif step == 'sandbox':
            srcOrg = session.get('srcorg')
            sourceSandbox = request.form['sourceSandbox']
            
            # get the sandbox name for the selected sandbox in the selected source organization
            sandboxName = sandboxDictsByOrg[srcOrg][sourceSandbox]
            
            # update the sourceSandboxHeaders dictionary with the selected sandbox name
            sourceSandboxHeaders['Accept'] = 'application/vnd.adobe.xed-id+json'
            sourceSandboxHeaders['x-sandbox-name'] = sandboxName
            
            return render_template('menu.html')

@app.route('/segment', methods=['GET','POST'])
def segmentname():
    global segmentDict
    global segmentDict1
    batchsegments=[]
    streamingsegments=[]
    edgesegments=[]
    global sourceSandboxHeaders
    global destSandboxHeaders
    

    try:
        if request.method=="GET":
            response=getAllSegments(sourceSandboxHeaders)
            response=json.loads(response.text) 
            segmentDict={}
            segmentDict1={}  
            segmentDict2={} 
            segmentDict3={} 
            try:
                 for i in response['segments']:
                      segmentDict[i['name']]=i['id']
                      segmentDict1 = i ['evaluationInfo']['batch']
                      segmentDict2 = i ['evaluationInfo']['continuous']
                      segmentDict3 = i ['evaluationInfo']['synchronous']
                      a=(sum(value == True for value in segmentDict1.values()))
                      batchsegments.append(a)
                      b=(sum(value == True for value in segmentDict2.values()))
                      streamingsegments.append(b)
                      c=(sum(value == True for value in segmentDict3.values()))
                      edgesegments.append(c)
            except KeyError:
                 print("There was an issue fetching segment details.")
        sourceSegmentsList=list(segmentDict.keys())
        return render_template('segment.html',ns=len(sourceSegmentsList), bs =Counter(batchsegments)[1], ss =Counter(streamingsegments)[1], es = Counter(edgesegments)[1], segmentDict=segmentDict)
    except Exception as e:
            return(str(e))
@app.route('/idnamespace', methods=['GET','POST'])
def idnamespace():
    global idNamespaceDict
    global idNamespaceDict1
    global idNamespaceDict2
    global idNamespaceDict3
    if request.method=="GET":
            response=getAllIdNamespaces(sourceSandboxHeaders)
            response=json.loads(response.text) 
            for i in response:
                idNamespaceDict[i['name']]=i['id']
    sourceIdNamespaceList3=list(idNamespaceDict.keys())
    for k in response:
        if k ['namespaceType']=='Integration':
            idNamespaceDict2[k['name']]=k['id']
    sourceIdNamespaceList2=list(idNamespaceDict2.keys())
    for i in response:
        if i['namespaceType']=='Standard':
            idNamespaceDict3[i['name']]=i['id']
    sourceIdNamespaceList=list(idNamespaceDict3.keys())
    idNamespaceDict1={}     
    for k in response:
        if k ['namespaceType']=='Custom':
            idNamespaceDict1[k['name']]=k['id']
    sourceIdNamespaceList1=list(idNamespaceDict1.keys())           
    return render_template('idnamespace.html',idNamespaceList=len(sourceIdNamespaceList3),integration=len(sourceIdNamespaceList2),standard=len(sourceIdNamespaceList),custom=len(sourceIdNamespaceList1),idNamespaceDict1=idNamespaceDict1)
@app.route('/class', methods=['GET','POST'])
def classesname():
    global classesDict
    global my_dictionary
    global sourceSandboxHeaders
    global destSandboxHeaders
    global sourceTenantId
    global destinationTenantId
    try:
        if request.method=="GET":
            response=getAllClasses(sourceSandboxHeaders)
            response=json.loads(response.text) 
            classesDict = {}
            SC=response['counts']['schemas']
            FC=response['counts']['mixins']
            for i in response['classUsage']:
                classesDict [i['title']] = i['numberOfSchemas']
            profile=classesDict.get('XDM Individual Profile')
            event=classesDict.get('XDM ExperienceEvent')
            my_dictionary = {i: classesDict[i] for i in classesDict if i not in ['XDM Individual Profile', 'XDM ExperienceEvent']}
        return render_template('classes.html',classesDict=classesDict,SchemaCount=SC,FieldGroupsCount=FC,profile=profile,event=event,cust=SC-(profile+event),my_dictionary=my_dictionary)
    except Exception as e:
            return(str(e))
@app.route('/fieldgroup', methods=['GET'])
def fieldgroupname():
    global fieldGroupDict
    global sourceSandboxHeaders
    global destSandboxHeaders
    global sourceTenantId
    global destinationTenantId
    try:
        if request.method=="GET":
            response=getAllMixins(sourceSandboxHeaders)
            response=json.loads(response.text) 
            fieldGroupDict=response['counts']['mixins']
        return render_template('fieldgroup.html',fieldGroupList=fieldGroupDict)
    except Exception as e:
            return(str(e))             
@app.route('/dataset', methods=['GET'])
def datasetname():
    global sourceSandboxHeaders
    global destSandboxHeaders
    global sourceTenantId
    global destinationTenantId
    global datasetDict
    count = 0
    response = getAllDatasets(sourceSandboxHeaders)
    response_dict = json.loads(response.text)
    for dataset_id, dataset in response_dict.items():
        tags = dataset.get("tags")
        if tags and tags.get("unifiedProfile"):
            if "enabled:true" in tags["unifiedProfile"]:
                count += 1
    print(count)
    start = 0
    limit = 99
    datasetDict = []
    while True:
        response = getAllDatasets(sourceSandboxHeaders, start=start, limit=limit)
        response_dict = json.loads(response.text)
        dataset_keys = list(response_dict.keys())
        datasetDict += dataset_keys
        if len(dataset_keys) < limit:
            break
        start += limit
    print(len(datasetDict))
    return render_template('dataset.html', datasetDict1=len(datasetDict), count=count)
@app.route('/descriptor', methods=['GET','POST'])
def descriptorname():
    global descriptorDict
    global descriptorDict1
    global sourceSandboxHeaders
    global destSandboxHeaders
    global sourceTenantId
    global destinationTenantId
    try:
        if request.method=="GET":
            response = getAlldescriptor(sourceSandboxHeaders)
            response = json.loads(response.text) 
            descriptorDict = response.get('xdm:descriptorOneToOne', [])
            descriptorDict1 = response.get('xdm:descriptorRelationship', [])
        return render_template('descriptor.html', descriptorList=len(descriptorDict), descriptorList1=len(descriptorDict1))
    except Exception as e:
        return(str(e))
@app.route('/profile/', methods=['GET'])
def profilesname():
    global profilesDict
    global sourceSandboxHeaders
    global sourceTenantId
    try:
        if request.method == "GET":
            response = getAllProfiles(sourceSandboxHeaders)
            response = json.loads(response.text) 
            profilesDict = {}
            full_ids_count_sum = 0  # Initialize the variable to zero
            for i in response['data']:
                profilesDict[i['code']] = i['fullIDsCount']
                full_ids_count_sum += i['fullIDsCount']  # Calculate the sum
            return render_template('profile.html', profilesDict=profilesDict, full_ids_count_sum=full_ids_count_sum)
    except Exception as e:
        return str(e)
@app.route('/destination', methods=['GET'])
def destinationname():
    global destinationDict
    global sourceSandboxHeaders
    global destSandboxHeaders
    global sourceDestinationList
    try:
        if request.method=="GET":
            response=getAllDestinations(sourceSandboxHeaders)
            response=json.loads(response.text)
            destinationDict={} 
            for i in response['items']:
              destinationDict[i['instanceId']]=i['name']
        sourceDestinationList=list(destinationDict.keys())
        print(len(sourceDestinationList))   
        return render_template('destination.html',destinations=len(sourceDestinationList))
    except Exception as e:
            return(str(e))      
@app.route('/query', methods=['GET'])
def queryname():
    global queryDict
    global queryDict1
    global queryDict2
    global sourceSandboxHeaders
    global sourceTenantId
    try:
        if request.method=="GET":
            response=getAllQueriess(sourceSandboxHeaders)
            response=json.loads(response.text) 
            queryDict=response['totalCount']
            schedules=getAllschedules(sourceSandboxHeaders)
            queryDict1=schedules
            schedules=json.loads(schedules.text)
            for i in schedules['schedules']:
                queryDict2 [i['id']] = i['state']
        count = 0
        for val in queryDict2.values():
            if val == "ENABLED":
                count += 1
        count1 = 0
        for val in queryDict2.values():
            if val == "DISABLED":
                count1 += 1
        return render_template('query.html',queryDict=queryDict,count=count,count1=count1,count2 =count+count1)
    except Exception as e:
            return(str(e))    
@app.route('/flows', methods=['GET'])
def flowsname():
    global flowsDict
    global flowsDict1
    global sourceSandboxHeaders
    global sourceFlowsList
    global sourceFlowsList1
    try:
        if request.method=="GET":
            response=getAllflows(sourceSandboxHeaders)
            response=json.loads(response.text) 
            for i in response['items']:
                flowsDict[i['id']] = i['name']
        sourceFlowsList=list(flowsDict.keys()) 
        return render_template('flows.html',flows=len(sourceFlowsList))
    except Exception as e:
            return(str(e))
@app.route('/merge', methods=['GET'])
def mergenname():
    global mergeDict
    global sourceSandboxHeaders
    try:
        if request.method=="GET":
            response=getAllMergepolicies(sourceSandboxHeaders)
            response=json.loads(response.text)
            merge=response['_page']['totalCount']
            print (merge)
        return render_template('merge.html',merge=merge)
    except Exception as e:
            return(str(e))
@app.route('/new-page')
def new_page():
    return render_template('new-page.html')
@app.route('/validate', methods=['GET'])
def validatename():
    global segmentDict
    global segmentDict1
    global descriptorDict
    global descriptorDict1
    global classesDict
    global my_dictionary
    Total_Segments = 4000
    profile_schemas = 20
    event_schemas = 20
    Total_Destinations = 100
    merge_policies = 5
    Edge_Segments = 150
    Streaming_Segments = 500
    Batch_Segments = 4000
    descriptor = 5
    batchsegments = []
    streamingsegments = []
    edgesegments = []
    global sourceSandboxHeaders
    global destSandboxHeaders
    global mergeDict
    sandboxselected = sourceSandboxHeaders['x-sandbox-name']

    try:
        if request.method == "GET":
            srcOrg = session.get('srcorg')
            print('srcorg:', srcOrg)
            print("Source Sandbox Name: ", sandboxselected)
            # Merge Policies
            response = getAllMergepolicies(sourceSandboxHeaders)
            response = json.loads(response.text)
            merge = response['_page']['totalCount']
            # RelationShips
            response = getAlldescriptor(sourceSandboxHeaders)
            response = json.loads(response.text)
            descriptorDict = response.get('xdm:descriptorOneToOne', [])
            descriptorDict1 = response.get('xdm:descriptorRelationship', [])
            # Schemas
            response = getAllClasses(sourceSandboxHeaders)
            response = json.loads(response.text)
            classesDict = {}
            SC = response['counts']['schemas']
            FC = response['counts']['mixins']
            for i in response['classUsage']:
                classesDict[i['title']] = i['numberOfSchemas']
            profile = classesDict.get('XDM Individual Profile')
            event = classesDict.get('XDM ExperienceEvent')
            my_dictionary = {i: classesDict[i] for i in classesDict if i not in ['XDM Individual Profile', 'XDM ExperienceEvent']}
            # Segments
            response = getAllSegments(sourceSandboxHeaders)
            response = json.loads(response.text)
            try:
                for i in response['segments']:
                    segmentDict[i['name']] = i['id']
                    segmentDict1 = i['evaluationInfo']['batch']
                    segmentDict2 = i['evaluationInfo']['continuous']
                    segmentDict3 = i['evaluationInfo']['synchronous']
                    a = (sum(value == True for value in segmentDict1.values()))
                    batchsegments.append(a)
                    b = (sum(value == True for value in segmentDict2.values()))
                    streamingsegments.append(b)
                    c = (sum(value == True for value in segmentDict3.values()))
                    edgesegments.append(c)
            except KeyError:
                print("There was an issue fetching segment details.")
        sourceSegmentsList = list(segmentDict.keys())
        # Destinations
        response = getAllDestinations(sourceSandboxHeaders)
        response = json.loads(response.text)
        destinationDict = {}
        for i in response['items']:
            destinationDict[i['instanceId']] = i['name']
        sourceDestinationList = list(destinationDict.keys())
        print(len(sourceDestinationList))

        # The PDF generation part is removed from here

        rendered = render_template('validate.html',
                                   ns=len(sourceSegmentsList),
                                   bs=Counter(batchsegments)[1],
                                   ss=Counter(streamingsegments)[1],
                                   es=Counter(edgesegments)[1],
                                   Total_Segments=Total_Segments,
                                   Streaming_Segments=Streaming_Segments,
                                   Edge_Segments=Edge_Segments,
                                   Batch_Segmentsd=Batch_Segments - Counter(batchsegments)[1],
                                   Streaming_Segmentsd=Streaming_Segments - Counter(streamingsegments)[1],
                                   Edge_Segmentsd=Edge_Segments - Counter(edgesegments)[1],
                                   Total_Segmentsd=Total_Segments - (Counter(batchsegments)[1] + Counter(streamingsegments)[1] + Counter(edgesegments)[1]),
                                   merge=merge,
                                   descriptorList=len(descriptorDict),
                                   descriptorList1=len(descriptorDict1),
                                   descriptor=descriptor,
                                   Total_Relationshipsd=descriptor - len(descriptorDict1),
                                   profile=profile,
                                   event=event,
                                   event_schemas=event_schemas,
                                   profile_schemas=profile_schemas,
                                   Total_indiv=profile_schemas - profile,
                                   Total_event=event_schemas - event,
                                   merge_policies=merge_policies,
                                   merge_policiesd=(merge_policies - merge),
                                   destinations=len(sourceDestinationList),
                                   Total_Destinations=Total_Destinations,
                                   Total_Destinationsd=(Total_Destinations) - (len(sourceDestinationList))
                                   )
        options = {
            'javascript-delay': '10000'  # Wait for 3 seconds (3000 ms) before taking the screenshot
        }
        if not os.path.exists('reports'):
            os.mkdir('reports')

        # Save the HTML file to the reports directory

        version = 1
        now = datetime.now()
        dt_string = now.strftime("%m_%d_%Y")
        while True:
            filename = f"reports/{srcOrg}-{sandboxselected}-v{version}-{dt_string}.html"
            if not os.path.exists(filename):
                break
            version += 1
        with open(filename, 'w') as f:
            f.write(rendered)

        return rendered
    except Exception as e:
        return str(e)




@app.route('/dashboard')
def dashboard():
    reports = []
    for filename in os.listdir('reports'):
        if filename.endswith('.html'):
            name_parts = filename[:-5].split('-')
            srcOrg = name_parts[0]
            sandboxselected = name_parts[1]
            version = name_parts[2][1:] 
            date =  name_parts[3] # remove the 'v' from the version
            path = os.path.join('reports', filename)
            reports.append({'srcOrg': srcOrg, 'sandboxselected': sandboxselected, 'version': version, 'path': path, 'date': date})
    return render_template('dashboard.html', reports=reports)




@app.route('/reports/<filename>')
def serve_report(filename):
    report_path = f'reports/{filename}'
    return send_file(report_path, as_attachment=True)

if __name__ =="__main__":
    app.run(debug=True, port=7377)
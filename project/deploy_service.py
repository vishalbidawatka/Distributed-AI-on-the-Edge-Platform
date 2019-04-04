from flask import Flask,request, render_template
import os,json
from threading import Thread
from time import sleep
import time,requests
import datetime

app = Flask(__name__)

def caller_function(URL,sched) :
    print("dd")
    
    # print("Caller function called")
    # print(type(sched))
    print("Caller function called")
    r=requests.post(url=URL,data=json.dumps(sched))


@app.route('/deployService',methods=['POST'])
def deployModelPhase():
    print("Deploy")
    # modelName = request.args.get('model')
    listOfDict = {}
    port = 45098
    # jsonfile="config.json"
    folderName="./models/"
    commands = '''
if [ -x "$(command -v docker)" ]; then
    echo "Update docker"
else
    echo "Install docker"
    sudo apt-get install curl
    sudo curl -sSL https://get.docker.com/ | sh
fi
    '''
    # data = request.get_json()
    data =request.data
    datadict=json.loads(data)
    print(type(datadict))
    print(datadict)
    sched = {}
    i=datadict
    ip = i['DeployIp']
    fname=i["Type"]
    uname = i['DeployUserName']
    password = i['DeployPassword']
    modelfilename = i['FileName']
    modelName = i['Modelname']
    modelpath = i["ModelPath"]
    start = i["StartTime"]
    end = i["EndTime"]
    count = i["Count"]
    repeat = i["Repeat"]
    stream_ip = i["InputStream"]
    interval = i["Interval"]
    repeat_period = i["Repeat_Period"]
    port = port + 1

    print("------------",modelfilename)
    dynamic1 = "unzip " + modelfilename
    dynamic2 = "echo " + password + " | sudo -S apt-get update"
    dynamic3 = "echo " + password +" | sudo -S docker pull tensorflow/serving"
    dynamic4 = "sudo docker stop $(echo " + password + " | sudo -S docker ps -aq)"
    dynamic5 = "echo " + password + " | sudo -S docker run --name=" + "\"" + modelName + "\"" + " -p 8500:8500 -p 8501:8501 --mount type=bind,source=/home/"+uname+"/"+modelpath+",target=/models/"+modelName+" -e MODEL_NAME="+modelName+" -t tensorflow/serving"
    # dynamic6 = "nohup sshpass -p " + password + " ssh " +  ip +" -l " + uname + " 'docker kill "+modelName + "'" + " &"
    # dynamic7 = "nohup sshpass -p " + password + " ssh " +  ip +" -l " + uname + " 'docker rm "+modelName + "'" + " &"
    dynamic6 = "echo " + password + " | " +"sudo -S docker kill " + modelName
    dynamic7 = "echo " + password + " | " +"sudo -S docker rm " + modelName

    commands = dynamic1 + "\n" + commands + "\n" + dynamic3 +"\n" + dynamic4 + "\n"

    scriptName = "script_" + modelName + ".sh"
    f = open(scriptName,"w+")
    f.write(commands)
    f.close()

    start_s = "start_"+modelName+".sh"
    f = open(start_s,"w+")
    f.write(dynamic5)
    f.close()

    dynamicX = dynamic6 + "\n" + dynamic7
    stop_s = "stop_"+modelName+".sh"
    f = open(stop_s,"w+")
    # f.write()
    f.write(dynamicX)
    f.close()

    path = folderName + "/"
    cmd1 = "sshpass -p " + password + " scp " + scriptName + " " + uname + "@" + ip + ":" + scriptName
    cmd1_1 = "sshpass -p " + password + " scp " + start_s + " " + uname + "@" + ip + ":" + start_s
    cmd1_2 = "sshpass -p " + password + " scp " + stop_s + " " + uname + "@" + ip + ":" + stop_s
    cmd2 = "sshpass -p " + password + " scp " + path + modelfilename + " " + uname + "@" + ip + ":" + modelfilename
    cmd3 = "nohup sshpass -p " + password + " ssh " + ip + " -l " + uname + " bash "+ scriptName + " &"

    print("Before calling")

    os.system(cmd1)
    os.system(cmd1_1)
    os.system(cmd1_2)
    os.system(cmd2)
    os.system(cmd3)

    sched = {'InputStreamIp': stream_ip,'filename':fname,'modelname':modelName,'uname':uname,'password':password,'ip':ip,'port':8501,'start_command':dynamic5,'end_command':dynamic6,
                                                'start':start,'end':end,'repeat':repeat,'count':count,'interval':interval,'repeat_period':repeat_period}

            
    print("Call Schedule")
    url = 'http://127.0.0.1:8897/ScheduleService'
    
    # thread = Thread(target=caller_function,args=(url,sched,))
    # thread.start()
    caller_function(url,sched)
    print("After Thread call")

    # r = json.dumps(sched)
    # url='http://127.0.0.1:8882/ScheduleService'
    # response = requests.post(url,data=r)
    
    return "From deploy"
        
                    


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8890,debug=True,threaded=True)


from django.shortcuts import render, redirect
import paramiko
import re,random

# Create your views here.
def home(request):
        if request.method == 'POST':
                return redirect('/home/test')
        else:
                host = "10.54.81.89"
                port = 22
                username = "rshah"
                password = "Rs@200694"
                command = "date"
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, port, username, password)

                stdin, stdout, stderr = ssh.exec_command(command)
                lines = stdout.readlines()
                return render(request,"home.html")


def test(request):
        return render(request,"login.html")

def imsli(request):
        messages=None
        if request.method == 'POST':
                TargetCriteriaType = request.POST['TargetCriteriaType']
                Target = request.POST['Target']
                TapID = request.POST['TapID']
                print(TargetCriteriaType,Target,TapID)
                if(TargetCriteriaType and Target and TapID):
                        messages="Successful"
                else:
                        messages = "Not Successful"
                print(messages)
                if messages=="Successful":
                        return render(request,'form_component.html',{'messages':messages,})
                else:
                        return render(request,'form_component.html',{'messages':messages,})

        else:
                return render(request,"form_component.html")


def imsli_liserver(request):
        if request.method == 'POST':
                batsserver = request.POST['batsserver']
                msnum = request.POST['msnum']
                batsusername = request.POST['batsusername']
                batspassword = request.POST['batspassword']

                if (batsusername and batspassword and int(msnum) < 16):
                        host = batsserver
                        port = 22
                        username = batsusername
                        password = batspassword
                        command = "cat /etc/network/interfaces | grep \"address\" | head -n 2 | tail -n 1"
                        ssh = paramiko.SSHClient()
                        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        ssh.connect(host, port, username, password)
                        stdin, stdout, stderr = ssh.exec_command(command)
                        lines = stdout.readlines()
                        print(lines)
                        ip1=re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', str(lines)).group()
                        print(ip1)
                        portlist=[]
                        while len(portlist)<(3*int(msnum)):
                                num=random.randint(1001, 50000)
                                print ("Num is ",num)
                                command = "lsof -ni:{}".format(num)
                                ssh = paramiko.SSHClient()
                                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                                ssh.connect(host, port, username, password)
                                stdin, stdout, stderr = ssh.exec_command(command)
                                port = stdout.readlines()
                                if(port not in portlist and int(port)>1000):
                                        portlist.append(port)
                                else:
                                       continue


                else:
                        messages = "Not Successful"
        else:
                return render(request,"form_component_liServer.html")
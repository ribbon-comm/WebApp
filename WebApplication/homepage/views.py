from django.shortcuts import render, redirect
import paramiko
import re,random
from paramiko_expect import SSHClientInteraction
import time

# Create your views here.
global sbcip
global ipInterfaceGroup
global ipInterface
global msnum
global randomlist
global ip1

def home(request):
        if request.method == 'POST':
                pass
        else:
                return render(request,"home.html")

def imsli(request):
        messages=None
        global sbcip
        if request.method == 'POST':
                emsip = request.POST['emsip']
                TargetCriteriaType = request.POST['TargetCriteriaType']
                Target = request.POST['Target']
                TapID = request.POST['TapID']
                sbcip=request.POST['sbcip']
                print(TargetCriteriaType,Target,TapID,sbcip,emsip)

                if (TargetCriteriaType and Target and TapID and emsip and sbcip):
                        host = "10.54.92.182"
                        port = 22
                        username = "rshah"
                        password = "Rs@200694"

                        value = func_calea(host,username,password,sbcip)

                        command2 = "perl /home/rshah/LI/target_create_edited.pl {emsip} {criteriatype} {criteriaid} {tapid}".format(emsip=emsip,criteriatype=TargetCriteriaType,criteriaid=Target,tapid=TapID)
                        print(command2)
                        ssh = paramiko.SSHClient()
                        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        ssh.connect(host, port, username, password)
                        stdin, stdout, stderr = ssh.exec_command(command2)
                        lines = stdout.readlines()
                        print(lines[0])

                        if(lines[0]=="Target Successful"):
                                messages="Successful"
                                print(messages)
                        else:
                                messages = "Not Successful"
                                print(messages)
                else:
                        messages = "Not Successful"
                if messages=="Successful":
                        return render(request,'form_component.html',{'messages':messages,})
                else:
                        return render(request,'form_component.html',{'messages':messages,})

        else:
                return render(request,"form_component.html")


def imsli_liserver(request):
        messages=None
        global sbcip
        global randomlist
        global ip1
        global msnum
        if request.method == 'POST':
                batsserver = request.POST['batsserver']
                msnum = request.POST['msnum']
                batsusername = request.POST['batsusername']
                batspassword = request.POST['batspassword']
                print("SBC IP IS", sbcip)
                func(batsserver,batsusername,batspassword,sbcip)

                if (batsusername and batspassword and int(msnum) < 16):
                        host = batsserver
                        port = 22
                        username = batsusername
                        password = batspassword
                        command1 = "cat /etc/network/interfaces | grep \"address\" | head -n 2 | tail -n 1"
                        ssh = paramiko.SSHClient()
                        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        ssh.connect(host, port, username, password)
                        stdin, stdout, stderr = ssh.exec_command(command1)
                        lines = stdout.readlines()
                        print(lines)
                        ip1=re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', str(lines)).group()
                        print(3*int(msnum))
                        portlist=[]
                        randomlist = random.sample(range(1001, 50000), (3*int(msnum)))
                        print(randomlist)
                        count = 0
                        serversnum = 0
                        for i in randomlist:
                                command = "lsof -ni:{}".format(i)
                                print(command)
                                stdin, stdout, stderr = ssh.exec_command(command)
                                port = stdout.readlines()
                                print("Port is ",port)
                                if(port == []):
                                        print("Length of count is ", count)
                                        portlist.append(i)
                                        count+=1
                                        print("Length of count after increment is ", count)
                                print (portlist)
                                if count==3:
                                        serversnum += 1
                                        commandrun = '/ats/bin/liServer -si {sip} -sp {sport} -tmi {tip} -tmp {tport} -umi {uip} -ump {uport} -multimedia &'.format(sip=ip1,sport=portlist.pop(),tip=ip1,tport=portlist.pop(),uip=ip1,uport=portlist.pop())
                                        #print(commandrun)
                                        stdin, stdout, stderr = ssh.exec_command(commandrun)

                                        stdin, stdout, stderr = ssh.exec_command("\n\n")

                                        portrun = stdout.readlines()
                                        print("Port is ", portrun,serversnum,msnum)
                                        count = 0
                                        portlist.clear()
                        if serversnum==int(msnum):
                                print("Inside success")
                                messages="Successful"
                        else:
                                print("Inside not success 1")
                                messages="Not Successful"
                else:
                        print("Inside not success 2")
                        messages = "Not successful"

                if messages=="Successful":
                        return render(request,'form_component_liServer.html',{'messages':messages,})
                else:
                        return render(request,'form_component_liServer.html',{'messages':messages,})
        else:
                return render(request,"form_component_liServer.html")




def imsli_configs(request):
        messages=""
        global randomlist
        clilist = []
        global msnum
        global ip1
        global sbcip
        clilist.append("configure")
        if request.method == 'POST':
                vendorID = request.POST['vendorID']
                InterceptStandard = request.POST['InterceptStandard']
                IpInterfaceGroupName = request.POST['IpInterfaceGroupName']
                cdccmd = 'set addressContext default intercept callDataChannel CDC interceptStandard {InterceptStandard} vendorId {vendorID} ipInterfaceGroupName {ipInterfaceGroup} mediaIpInterfaceGroupName {mediaipInterfaceGroup}'.format(vendorID=vendorID, InterceptStandard=InterceptStandard, ipInterfaceGroup=IpInterfaceGroupName,mediaipInterfaceGroup=IpInterfaceGroupName)
                clilist.append(cdccmd)
                clilist.append("commit")
                k = 0
                for i in range(2, 3*int(msnum), 3):
                        sigcli = 'set addressContext default intercept callDataChannel CDC mediationServer MS{num} signaling ipAddress ' \
                                 '{liip} portNumber {sigport} state disabled mode outOfService'.format(num=k,
                                                                                                       liip=ip1,
                                                                                                       sigport=randomlist[i])
                        clilist.append(sigcli)
                        clilist.append("commit")
                        sigcli1 = 'set addressContext default intercept callDataChannel CDC mediationServer MS{num} signaling state enabled mode inService'.format(
                                num=k)
                        clilist.append(sigcli1)
                        clilist.append("commit")
                        k += 1
                k = 0
                for j in range(0, 3*int(msnum), 3):
                        udpcli = 'set addressContext default intercept callDataChannel CDC mediationServer MS{num} media udp ipAddress {liip} portNumber {udpport} state disabled mode outOfService'.format(
                                num=k, liip=ip1, udpport=randomlist[j])
                        clilist.append(udpcli)
                        clilist.append("commit")
                        udpcli1 = 'set addressContext default intercept callDataChannel CDC mediationServer MS{num} media udp state enabled mode inService'.format(
                                num=k)
                        clilist.append(udpcli1)
                        clilist.append("commit")
                        k += 1
                clilist.append("exit")

                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(sbcip, username='root', password='sonus1',port=2024)

                ftp = ssh.open_sftp()
                file = ftp.file('/home/Administrator/admin/configs', "w", -1)
                file.seek(0)
                for item in clilist:
                        file.write(item + '\n')
                file.flush()
                ftp.close()
                ssh.close()

                if (1):
                        sagkumar = ssh_connection(sbcip, "sonus1", "root", 2024)
                        interact = SSHClientInteraction(sagkumar, timeout=30, display=True)
                        #time.sleep(5)
                        PROMPT = '.*root@.*# '
                        interact.expect(PROMPT)
                        curlString="cd /home/Administrator/admin/; /opt/sonus/sbx/tailf/bin/confd_cli -u calea"
                        interact.send(curlString)

                        time.sleep(5)
                        PROMPT = 'calea@.*> '
                        interact.expect(PROMPT)
                        time.sleep(5)
                        interact.send("source configs")
                        time.sleep(5)
                        output1 = interact.current_output_clean.strip()
                messages="Successful"

                if messages=="Successful":
                        return render(request,'form_component_liServer_configs.html',{'messages':messages,})
                else:
                        return render(request,'form_component_liServer_configs.html',{'messages':messages,})
        else:
                context = {'ipInterfaceGroup1': ipInterfaceGroup[0],
                           'ipInterfaceGroup2': ipInterfaceGroup[1]
                           }
                return render(request,"form_component_liServer_configs.html",context)



def imsli_configs_stats(request):
        global sbcip
        print("Messages inside stats")
        stats=func_stats(sbcip,"root","sonus1")
        stats_list=list(stats.split(";"))
        print("List without index ", stats_list)
        print("List with index ",stats_list[2])
        print("List with index ",stats_list[1])
        context = {'tcpmediasent': stats_list[1],
                   'tcpmedialost': stats_list[2],
                   'udpmediasent': stats_list[3],
                   'udpmedialost': stats_list[4],
                   'dsrsent': stats_list[6],
                   'dsrlost': stats_list[7],

                   }
        return render(request,'form_component_liServer_configs_stats.html',context)



def ssh_connection(ip_address,password,user_name, port_number):
        client = paramiko.SSHClient()
        # Set SSH key parameters to auto accept unknown hosts
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        hostname = ip_address
        username = user_name
        password = password
        port = port_number
        # Connect to the host
        client.connect(hostname=hostname, port=port ,username=username, password=password)
        return client

def func(host,username,pswd,sbcip):
        global ipInterfaceGroup
        sagkumar=ssh_connection(host,pswd,username,22)
        print(sbcip)
        interact = SSHClientInteraction(sagkumar, timeout=30, display=True)
        interact.send("export PS1=\"> \"")
        interact.expect('> ')
        #curlString ="curl \-k \-i \-\-user admin\:Sonus\@123 \-X GET \"https\:\/\/{mgtIP}\/api\/config\/addressContext\/default\" \>\> 1\.txt".format(mgtIP="10.54.51.109")
        curlString ="curl -k -i --user admin:Sonus@123 -X GET \"https://{mgtIP}/api/config/addressContext/default\" > 1.txt".format(mgtIP=str(sbcip))
        interact.send(curlString)
        interact.expect('> ')
        interact.send("cat 1.txt | grep -P -o -e \"<ipInterfaceGroupName>.*(?=</ipInterfaceGroupName>)\" | cut -d \">\" -f 2")
        interact.expect('> ')
        output1 = interact.current_output_clean.strip()
        output= output1.split("\n")
        print(type(output))
        interface_var1=set(output)
        print(interface_var1)
        ipInterfaceGroup=list(interface_var1)
        ipInterfaceGroup.remove("cat 1.txt | grep -P -o -e \"<ipInterfaceGroupName>.*(?=</ipInterfaceGroupName>) \" | cut -d \">\" -f 2")
        print(ipInterfaceGroup)


def func_calea(host,username,pswd,sbcip):
        global ipInterface
        global ipInterfaceGroup
        global ip1
        sagkumar = ssh_connection(host, pswd, username, 22)
        print(sbcip)
        interact = SSHClientInteraction(sagkumar, timeout=30, display=True)
        time.sleep(5)
        interact.send("export PS1=\"> \"")
        time.sleep(5)
        interact.expect('> ')
        time.sleep(5)
        # curlString ="curl \-k \-i \-\-user admin\:Sonus\@123 \-X GET \"https\:\/\/{mgtIP}\/api\/config\/addressContext\/default\" \>\> 1\.txt".format(mgtIP="10.54.51.109")
        curlString = "curl -kisu admin:Sonus@123 -X POST -H 'Content-Type: application/vnd.yang.data+xml' https://{mgtIP}/api/config/oam/localAuth/users/_operations/set --data \"<set><user>calea</user><group>Calea</group><passwordAgingState>enabled</passwordAgingState><accountAgingState>enabled</accountAgingState><passwordLoginSupport>enabled</passwordLoginSupport><interactiveAccess>enabled</interactiveAccess><m2mAccess>enabled</m2mAccess><accountRemovalState>enabled</accountRemovalState></set>\"".format(
                mgtIP=sbcip)
        # curlString ="date"
        interact.send(curlString)
        interact.expect('> ')
        output1 = interact.current_output_clean
        print(output1)
        print(type(output1))
        x = re.search("Updation successful", output1)
        if (x):
                print("Calea user Already Created ......")
                return 0
        else:
                print("Calea user Not present, Going to create the calea user ......")
                sbc_root = ssh_connection("10.54.51.109", "sonus1", "root", 2024)
                interact = SSHClientInteraction(sbc_root, timeout=30, display=True)
                interact.send("export PS1=\"> \"")
                interact.expect('> ')
                interact.send("passwd calea")
                interact.expect('New password: ')
                interact.send("Ribbon@123")
                time.sleep(5)
                interact.expect('Retype new password: ')
                interact.send("Ribbon@123")
                time.sleep(5)
                interact.expect('> ')
                interact.send("ssh calea@0")
                interact.expect("calea@0's password: ")
                interact.send("Ribbon@123")
                interact.expect('Enter old password: ')
                interact.send("Ribbon@123")
                interact.expect('Enter new password: ')
                interact.send("Sonus@123")
                interact.expect('Re-enter new password: ')
                interact.send("Sonus@123")
                output2 = interact.current_output_clean
                return 1

def func_stats(sbcip,username,pswd):
        sbc_root = ssh_connection(sbcip, pswd, username, 2024)
        interact = SSHClientInteraction(sbc_root, timeout=30, display=True)
        interact.send("export PS1=\"> \"")
        interact.expect('> ')
        interact.send("ssh calea@0")
        interact.expect("calea@0's password: ")
        interact.send("Sonus@123")
        PROMPT = 'calea.*> '
        interact.expect(PROMPT)
        # interact.expect('calea@CEDUBAI> ')
        interact.send("show status addressContext default intercept callDataChannel CDC")
        interact.expect(PROMPT)
        output3 = interact.current_output_clean
        return output3
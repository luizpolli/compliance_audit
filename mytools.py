from getpass import getpass
import requests
import urllib3
import math
import re
import json
import sys
import netmiko

# Netmiko exceptions
netmiko_exceptions = (netmiko.ssh_exception.NetmikoTimeoutException, netmiko.ssh_exception.NetmikoAuthenticationException)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

### Taking the list of IPs from EPNM
def get_ipaddress():
    ipaddress = input("Enter the IP address of EPNM: ")
    while True:
        # Validate the IP Address (RegEx)
        validate_ip = re.compile(r"(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])")
        
        if not validate_ip.fullmatch(ipaddress):
            print("Wrong ip address. Please type again.")
            continue
        else:
            break
    return ipaddress

def create_file_list_of_ips(listdevices, username_epnm, password_epnm, ipaddress_epnm):

    header = {"Content-Type": "application/json", "Accept": "application/json"}
    devices = requests.get(f"https://{username_epnm}:{password_epnm}@{ipaddress_epnm}/webacs/api/v4/data/Devices?.full=true", verify=False, headers=header)
    total = devices.json()["queryResponse"]["@count"]
    division = math.ceil(total/1000)
    firstres = 0
    maxres = 1000
    

    with open(listdevices, "w") as dvc:

        print("Creating devices.json file. Wait a few minutes...")
        devices_file = dvc.write("[")
        for tot in range(division):

            devices = requests.get(f"https://{username_epnm}:{password_epnm}@{ipaddress_epnm}/webacs/api/v4/data/Devices?.full=true&.firstResult={firstres}&.maxResults={maxres}", verify=False, headers=header)
            firstres += 1000
            maxres = 1000

            num = int(len(devices.json()["queryResponse"]["entity"]))

            for i in range(num):
                devices_file = dvc.write("")
                if firstres >= total and i == (total-(firstres - 999)):
                    devices_file = dvc.write(f"""
        {{
            "ip": \"{devices.json()["queryResponse"]["entity"][i]["devicesDTO"]["ipAddress"]}\",
            "device_type": "cisco_xe"
        }}""")
                    devices_file = dvc.write("\n]")
                else:
                    devices_file = dvc.write(f"""
        {{
            "ip": \"{devices.json()["queryResponse"]["entity"][i]["devicesDTO"]["ipAddress"]}\",
            "device_type": "cisco_xe"
        }},""")


### Function used to ask username and password whether python 2 or 3

def get_input(prompt=""):
    try:
        line = raw_input(prompt)
    except NameError:
        line = input(prompt)
    return line

def get_credentials(generaluser):
    while True:
        print("="*79)
        print(f"Creating {generaluser.split()[0]} credentials")
        username = get_input(generaluser)
        password = getpass()
        password_verify = getpass("Retype your password: ")
        if username == "" or password == "":
            print("One of the values are empty. Please, enter a username and password.")
        elif password != password_verify:
            print("Passwords do not match. Try again")
        else:
            break
    return username, password

# Run the commands
class run():
    def run_command():

        # Opening JSON file from arguments
        with open(sys.argv[1]) as devjson:
            devices = json.load(devjson)

        # Opening commands file from arguments
        with open(sys.argv[2]) as file_cmds:
            commands = file_cmds.readlines()
        

        # Asink for devices credentials
        username, password = get_credentials("Device Username: ")

        with open("ASR9xx_OUTPUT.csv", "w") as file_open:
            file_open.write("Command, IP\n")
            for ip in devices:
                try:
                    ipadd = ip["ip"]
                    ip["username"] = username
                    ip["password"] = password
                    print()
                    print("~"*79)
                    print("Connected to device", ipadd)
                    connection = netmiko.ConnectHandler(**ip, global_delay_factor=2.0)

                    for command in commands:
                        command = command.replace("\n","")
                        print("## Running command: " + command)
                        output = connection.send_command(command, delay_factor=2.0)

                        for line in output.split("\n"):
                            if line == command[19:]:
                                pass
                            elif line == "":
                                file_open.write(command[19:] + " does not exists on device, " + ipadd + "\n")
                                print(command[19:] + " does not exists on device, " + ipadd)

                    connection.disconnect()
                except netmiko_exceptions as e:
                    print(f"Failed to connect to {ipadd} {e}")
from __future__ import absolute_import, division, print_function
from pprint import pprint

import mytools
import sys
import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)  # KeyboardInterrupt: Ctrl+C

# Validate the arguments
if len(sys.argv) < 3:
    print("Arguments should include: devices.json commands.txt")
    exit()


# Asking for EPNM API credentials
username_epnm, password_epnm = mytools.get_credentials("EPNM Username: ")
# Get EPNM IP Address
ipaddress_epnm = mytools.get_ipaddress()
# Creating the devices.json files
mytools.create_file_list_of_ips("devices.json", username_epnm, password_epnm, ipaddress_epnm)

# Run the commands and create the output
mytools.run.run_command()
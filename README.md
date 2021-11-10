# compliance_audit

The idea of this script is:

  - Go to device validate if the commands are configured in the device.
  - If configured, it will creates a file telling if command exist or not.
  - The script will not run the command if not exists.

Telling a little about the script

Pre-requirements
 - Edit the commands.txt file already included in the git repository.
 - Access to reach Cisco EPNM software.
 - EPNM REST API priviledges.

The script will get all devices from Cisco EPNM manager using APIs and generates a JSON file called devices.json with all devices in the inventory of EPNM.
You need to edit and add the command you want in the commands.txt file. The script will get the commands from this file and compare with the answer on device.

To run the script:
 - Simply use the command "python <script.py> devices.json commands.txt"
 - If you not include the arguments, it will fail.


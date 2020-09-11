import fileinput
import sys
import subprocess
import re
from pathlib import Path

import pip
failed = pip.main(["install", 'requests'])
print("status of requests install: ", failed)
failed = pip.main(["install", 'pyyaml'])
print("status of pyyaml install: ", failed)

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

# #Declare the directory and file name variables
fileEnterUserInputHereOnly = "/home/agile-cloud/staging/launchpadConfig.yaml"  
pathToVarFiles='/home/agile-cloud/vars/agile-cloud-manager/'
fileAzEnvVars = pathToVarFiles+'set-local-az-client-environment-vars.sh'  
  
def runShellCommand(commandToRun, workingDir ):
    print("Inside runShellCommand(..., ...) function. ")
    print("commandToRun is: " +commandToRun)
    print("workingDir is: " +workingDir)

    proc = subprocess.Popen( commandToRun,cwd=workingDir,stdout=subprocess.PIPE, shell=True)
    while True:
      line = proc.stdout.readline()
      if line:
        thetext=line.decode('utf-8').rstrip('\r|\n')
        decodedline=ansi_escape.sub('', thetext)
        print(decodedline)
      else:
        break
  
#Now call the functions
#First do some provisioning
#Create .aws directory for use below.
Path("/home/agile-cloud/.aws").mkdir(parents=True, exist_ok=True)
chmodCommand1 = 'sudo chown -R agile-cloud:agile-cloud /home/agile-cloud/.aws'
chmodCommand2 = "chmod +x provisioning.sh"
scriptsDir = "/home/agile-cloud/cloned-repos/agile-cloud-manager/setup/" 
setupCommand = "sudo ./provisioning.sh"
runShellCommand(chmodCommand1, scriptsDir)
runShellCommand(chmodCommand2, scriptsDir)
runShellCommand(setupCommand, scriptsDir)

### Now import deploymentFunctions.py and translate the environment variables from yaml into bash
sys.path.insert(0, '/home/agile-cloud/cloned-repos/agile-cloud-manager/pipeline-tasks/')
import deploymentFunctions as depfunc
depfunc.setEnvironmentVars(fileEnterUserInputHereOnly, fileAzEnvVars)

#Third set local environment variables by running the bash script that you just populated
varsDir = "/home/agile-cloud/vars/agile-cloud-manager/"
newChmodCommand = "chmod +x /home/agile-cloud/vars/agile-cloud-manager/set-local-az-client-environment-vars.sh"  
setVarsCommand = "sudo /home/agile-cloud/vars/agile-cloud-manager/set-local-az-client-environment-vars.sh"  
runShellCommand(newChmodCommand, varsDir )
runShellCommand(setVarsCommand, varsDir )

# #Fourth chown the file to aci-user to avoid risk of being owned by root
cmdChownVarFileAzurePipesAgentsStartUpScript = "sudo chown agile-cloud:agile-cloud " + fileAzEnvVars
runShellCommand(cmdChownVarFileAzurePipesAgentsStartUpScript, varsDir )

#Consider further locking down the yaml config files

import fileinput
import sys
import subprocess
import re

import pip
failed = pip.main(["install", 'requests'])
print("status of requests install: ", failed)
failed = pip.main(["install", 'pyyaml'])
print("status of pyyaml install: ", failed)

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

# #Declare the directory and file name variables
fileEnterUserInputHereOnly = "/home/aci-user/staging/launchpadConfig.yaml"  
pathToVarFiles='/home/aci-user/vars/agile-cloud-manager/'
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
chmodCommand = "chmod +x provisioning.sh"
scriptsDir = "/home/aci-user/cloned-repos/agile-cloud-manager/setup/" 
setupCommand = "sudo ./provisioning.sh"
runShellCommand(chmodCommand, scriptsDir)
runShellCommand(setupCommand, scriptsDir)

### Now import deploymentFunctions.py and translate the environment variables from yaml into bash
sys.path.insert(0, '/home/aci-user/cloned-repos/agile-cloud-manager/pipeline-tasks/')
import deploymentFunctions as depfunc
depfunc.setEnvironmentVars(fileEnterUserInputHereOnly, fileAzEnvVars)

#Third set local environment variables by running the bash script that you just populated
varsDir = "/home/aci-user/vars/agile-cloud-manager/"
newChmodCommand = "chmod +x /home/aci-user/vars/agile-cloud-manager/set-local-az-client-environment-vars.sh"  
setVarsCommand = "sudo /home/aci-user/vars/agile-cloud-manager/set-local-az-client-environment-vars.sh"  
runShellCommand(newChmodCommand, varsDir )
runShellCommand(setVarsCommand, varsDir )

# #Fourth chown the file to aci-user to avoid risk of being owned by root
cmdChownVarFileAzurePipesAgentsStartUpScript = "sudo chown aci-user:aci-user " + fileAzEnvVars
runShellCommand(cmdChownVarFileAzurePipesAgentsStartUpScript, varsDir )

#Consider further locking down the yaml config files

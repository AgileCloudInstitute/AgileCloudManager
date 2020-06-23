import fileinput  
  
pathToVarFiles='/home/aci-user/vars/agile-cloud-manager/'  
fileInputsFoundationDemo = pathToVarFiles+'inputs-foundation-demo.tfvars'  
  
def replaceTheLines(fileName):  
    for line in fileinput.input(fileName, inplace=True):  
        print('{} {}'.format(fileinput.filelineno(), line), end='')   
  
replaceTheLines(fileInputsFoundationDemo)  

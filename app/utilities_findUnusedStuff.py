
import os
from os import listdir

def findRedundancies():
  for thisUri in getListOfUris():
    print(thisUri)
    with open(thisUri) as file:  
      for line in file:  
        if "def " in line: 
          fullLine = line.rstrip()
          parensParts = fullLine.split("(")
          partZero = parensParts[0]
          funcName = partZero[4:]
          searchAllFilesForMatches(funcName)
    print("---------------------------------")

def getListOfUris():
  uriList = []
  cwd = os.getcwd()
  for f in os.listdir(cwd):
    myUri = os.path.join(cwd, f)
    if os.path.isfile(myUri):
      if "findUnusedStuff.py" not in myUri:
        uriList.append(myUri)
  return uriList

def searchAllFilesForMatches(func_name):
  totalCount = 0
  fileCountReportList = []
  for this_uri in getListOfUris():
    countInThisUriOnly = 0
    with open(this_uri) as file:
      for line in file:
        matchThis = func_name
        if (matchThis in line) and ("def " not in line):
          countInThisUriOnly+=1
    if countInThisUriOnly >0:
      fileCountReport = str(countInThisUriOnly) + " occurrences of " + func_name + " in file " + this_uri
      print(fileCountReport)
      fileCountReportList.append(fileCountReport)
    totalCount += countInThisUriOnly

#  if totalCount == 0:
  print("Total occurrences of ", func_name, " in ALL files: ", totalCount)
  print("+++++++++++++++++++++++++++++++++++++++++++")

def findVarReferences():
  varNames = [    'yamlInfraConfigFileAndPath', 'yamlApplianceConfigFileAndPath', 'pathToApplicationRoot',
  'app_parent_path', 'configAndSecretsPath',  'dirOfYamlFile', 'dirOfYamlKeys',
  'dirOfReleaseDefJsonParts', 'dirOfReleaseDefYaml', 'dirOfOutput', 'nameOfYamlKeys_IAM_File', 
  'nameOfYamlKeys_AWS_Network_File', 'nameOfYamlKeys_Azure_AD_File', 'nameOfYamlKeys_Azure_Network_File', 
  'tfvarsFileAndPath', 'tfBackendFileAndPath', 'verboseLogFilePath', 'dependenciesBinariesPath', 
  'dependenciesPath', 'dynamicVarsPath', 'relativePathToInstances', 'keySource', 'pub', 'sec', 
  'keysDir', 'tfBkndAzureParams' ]
  for varName in varNames:
    varOccurrences = 0
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("varName is: ", varName)
    for thisUri in getListOfUris():
      inFileOccurrences = 0
      if "cliInputProcessor.py" not in thisUri:
        with open(thisUri) as file:  
          for line in file:  
            varNameSingle = ".get(\'"+varName+"\')"
            varNameDouble = ".get(\""+varName+"\")"
            if (varNameSingle in line) or (varNameDouble in line):
              inFileOccurrences += 1
      if inFileOccurrences > 0:
        print("    ", inFileOccurrences, " of ", varName, " in ", thisUri)
        varOccurrences += inFileOccurrences
        print("    ---------------------------------")
    print(varOccurrences, " of ", varName, " across all searched files.  ")


#findRedundancies()

#findVarReferences()

#searchAllFilesForMatches("logWriter.assembleChangeTaxonomy(")
#searchAllFilesForMatches("After update")
#searchAllFilesForMatches("changes that will be made in this run are itemized in the changesManifest as follows:")
searchAllFilesForMatches("nameOfYamlKeys_AWS")
#searchAllFilesForMatches("match1 and match2 are:")

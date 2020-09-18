module "azure-devops-repo-build" {
  source = "../../modules/azure-devops-repo-build"

  subscriptionId                       = "${var.subscriptionId}"  
  tenantId                             = "${var.tenantId}"  
  clientId                             = "${var.clientId}"  
  clientSecret                         = "${var.clientSecret}"  
  azdoOrgPAT                           = "${var.azdoOrgPAT}"  
  azdoOrgServiceURL                    = "${var.azdoOrgServiceURL}"  
  sourceRepo                           = "${var.sourceRepo}"  
  projectName                          = "${var.projectName}"  
  repoName                             = "${var.repoName}"  
  buildName                            = "${var.buildName}"  
}

#variable "subscriptionId" { }  
#variable "tenantId" { }  
#The client referred to is an App Registration we created for the subscription.
#variable "clientId" { }
#variable "clientSecret" { }
variable "azdoOrgPAT" { }
variable "azdoOrgServiceURL" { }
variable "sourceRepo" { }
variable "projectName" { }
variable "repoName" { }
variable "buildName" { }
  

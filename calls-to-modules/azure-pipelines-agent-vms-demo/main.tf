
module "azure-pipelines-agent-vms-demo" {
  source = "..\\..\\modules\\azure-pipelines-agent-vms"

  subscriptionId                     = "${var.subscriptionId}"
  tenantId                           = "${var.tenantId}"
  clientId                           = "${var.clientId}"
  clientSecret                       = "${var.clientSecret}"
  resourceGroupName                  = "${var.resourceGroupName}"
  resourceGroupLocation              = "${var.resourceGroupLocation}"
  nicName                            = "${var.nicName}"
  adminUser                          = "${var.adminUser}"
  adminPwd                           = "${var.adminPwd}"
  storageAccountDiagName             = "${var.storageAccountDiagName}"
  pathToCloudInitScript              = "${var.pathToCloudInitScript}"
}


##Input variables
variable "subscriptionId" { }
variable "tenantId" { }
#The client referred to is an App Registration.
variable "clientId" { }
variable "clientSecret" { }
variable "resourceGroupName" { }
variable "resourceGroupLocation" { }
variable "nicName" { }
variable "adminUser" { }
variable "adminPwd" { }
variable "storageAccountDiagName" { }
variable "pathToCloudInitScript" { }

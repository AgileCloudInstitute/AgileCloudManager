print('inside app __init__.py')
__all__ = ['acm', 'changes_comparer', 'changes_manifest', 'changes_comparer', 'command_builder', 
'command_formatter', 'command_runner', 'config_cliprocessor', 'config_fileprocessor ', 'config_keysassembler', 
'config_validator', 'controller_arm', 'controller_azdoproject', 'controller_azureadmin', 'controller_cf', 
'controller_custom', 'controller_image', 'controller_packer', 'controller_release', 'controller_terraform', 
'controller_tfbackendazrm', 'log_writer', 'workflow_platform', 'workflow_service_type', 'workflow_setup', 
'workflow_system']

import sys

#import app.acm
import AgileCloudManager.app.acm  as acm
sys.modules['acm'] = acm

#import changes_comparer
import AgileCloudManager.app.changes_comparer  as changes_comparer
sys.modules['changes_comparer'] = changes_comparer

#import changes_manifest
import AgileCloudManager.app.changes_manifest  as changes_manifest
sys.modules['changes_manifest'] = changes_manifest

#import changes_comparer
import AgileCloudManager.app.changes_comparer  as changes_comparer
sys.modules['changes_comparer'] = changes_comparer

#import command_builder
import AgileCloudManager.app.command_builder  as command_builder
sys.modules['command_builder'] = command_builder

#import command_formatter
import AgileCloudManager.app.command_formatter  as command_formatter
sys.modules['command_formatter'] = command_formatter

#import command_runner
import AgileCloudManager.app.command_runner  as command_runner
sys.modules['command_runner'] = command_runner

#import config_cliprocessor
import AgileCloudManager.app.config_cliprocessor  as config_cliprocessor
sys.modules['config_cliprocessor'] = config_cliprocessor

#import config_fileprocessorv 
import AgileCloudManager.app.config_fileprocessor  as config_fileprocessor
sys.modules['config_fileprocessor'] = config_fileprocessor

#import config_keysassembler
import AgileCloudManager.app.config_keysassembler  as config_keysassembler
sys.modules['config_keysassembler'] = config_keysassembler

#import config_validator
import AgileCloudManager.app.config_validator  as config_validator
sys.modules['config_validator'] = config_validator

#import controller_arm
import AgileCloudManager.app.controller_arm  as controller_arm
sys.modules['controller_arm'] = controller_arm

#import controller_azdoproject
import AgileCloudManager.app.controller_azdoproject  as controller_azdoproject
sys.modules['controller_azdoproject'] = controller_azdoproject

#import controller_azureadmin
import AgileCloudManager.app.controller_azureadmin  as controller_azureadmin
sys.modules['controller_azureadmin'] = controller_azureadmin

#import controller_cf
import AgileCloudManager.app.controller_cf  as controller_cf
sys.modules['controller_cf'] = controller_cf

#import controller_custom
import AgileCloudManager.app.controller_custom  as controller_custom
sys.modules['controller_custom'] = controller_custom

#import controller_image
import AgileCloudManager.app.controller_image  as controller_image
sys.modules['controller_image'] = controller_image

#import controller_packer
import AgileCloudManager.app.controller_packer  as controller_packer
sys.modules['controller_packer'] = controller_packer

#import controller_release
import AgileCloudManager.app.controller_release  as controller_release
sys.modules['controller_release'] = controller_release

#import controller_terraform
import AgileCloudManager.app.controller_terraform  as controller_terraform
sys.modules['controller_terraform'] = controller_terraform

#import controller_tfbackendazrm
import AgileCloudManager.app.controller_tfbackendazrm  as controller_tfbackendazrm
sys.modules['controller_tfbackendazrm'] = controller_tfbackendazrm

#import log_writer
import AgileCloudManager.app.log_writer  as log_writer
sys.modules['log_writer'] = log_writer

#import workflow_platform
import AgileCloudManager.app.workflow_platform  as workflow_platform
sys.modules['workflow_platform'] = workflow_platform

#import workflow_service_type
import AgileCloudManager.app.workflow_service_type  as workflow_service_type
sys.modules['workflow_service_type'] = workflow_service_type

#import workflow_setup
import AgileCloudManager.app.workflow_setup  as workflow_setup
sys.modules['workflow_setup'] = workflow_setup

#import workflow_system
import AgileCloudManager.app.workflow_system  as workflow_system
sys.modules['workflow_system'] = workflow_system

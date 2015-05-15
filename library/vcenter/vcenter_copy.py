#!/usr/bin/python

from pyVmomi import vim
from pyVmomi import vmodl
from pyVim.connect import SmartConnect, Disconnect
import atexit
import random
import datetime
import time


DOCUMENTATION = '''
---
module: vcenter
short_description: Perform tasks on a vCenter server
description:
     - Perform tasks on a vCenter server. relies on pyvmomi
version_added: "n/a"
options:
  vcenter_hostname:
    description:
     - hostname of the vCenter server
    required: true
    default: null
    aliases: []
  username:
    description:
      - Username to connect to vCenter server as.
    required: true
    default: null
    aliases: []
  password:
    description:
      - Password of the vCenter user
    required: true
    default: null
    aliases: []
  source:
    description:
      - Source url (i.e. https://vsphere.company.com/folder/ISOS/CentOS-6.5-x86_64-minimal.iso?dcPath=Production&dsName=datastore1
    required: true
    default: null
    aliases: []
  dest:
    description:
      - Source url (i.e. https://vsphere.company.com/folder/ISOS/CentOS-6.5-x86_64-minimal.iso?dcPath=Engineering&dsName=datastore2
    required: true
    default: null
    aliases: []
'''


try:
    import json
except ImportError:
    import simplejson as json


def main():
    """Pulls in params from ansible, sets up connection to vCenter """
    module = AnsibleModule(
        argument_spec=dict(
            vcenter_hostname=dict(required=True, type='str'),
            username=dict(required=True, type='str'),
            password=dict(required=True, type='str'),
            source=dict(required=True, type='str'),
            dest=dict(required=True, type='str'),
        ),
        supports_check_mode=False
    )


# set vars from module
    vcenter_hostname = module.params['vcenter_hostname']
    username = module.params['username']
    password = module.params['password']
    source = module.params['source']
    dest = module.params['dest']
    # set up connection
    try:
        si = SmartConnect(
            host=vcenter_hostname,
            user=username,
            pwd=password,
            port=int(443))
    except Exception as e:
        module.fail_json(msg='failed to connect to vCenter server: %s' % e)

    copy_file(module, source, dest, si)

    # shut this thing down
    atexit.register(Disconnect, si)

def wait_for_task(module, task):
    """
    Wait for a task to complete
    """
    task_done = False
    while not task_done:
        if task.info.state == 'success':
            return task.info.result

        if task.info.state == 'error':
            module.fail_json(
                msg="an error occurred while waiting for task to complete %s" % task.info)

def copy_file(module, source, dest, si):
    task = si.content.fileManager.CopyDatastoreFile_Task(source, None, dest, None)
    wait_for_task(module, task)
    module.exit_json(changed=True, changes='file copied from %s to %s' % (source, dest))

#<<INCLUDE_ANSIBLE_MODULE_COMMON>>
main()

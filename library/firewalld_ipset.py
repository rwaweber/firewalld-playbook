from ansible.module_utils.basic import AnsibleModule

from firewall.client import FirewallClient
from firewall.client import FirewallClientIPSetSettings

def external_state(client, indata):
    if indata['immediate']:
        client.reload()
    if indata['permanent']:
        client.runtimeToPermanent()

def run():
    module_args = dict(
        name=dict(type='str', required=True),
        state=dict(choices=['present', 'absent'], required=True),
        permanent=dict(type='bool', required=False, default=False),
        immediate=dict(type='bool', required=False, default=False),
        addresses=dict(type='list', required=False)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # setup the FirewallDClient
    client = FirewallClient()
    sets = client.getIPSets()
    settings = FirewallClientIPSetSettings()
    settings.setType("hash:ip")
    config = client.config()

    # construct return data
    result = {
        "changed": False,
        "firewalld_ipset_name": module.params['name'],
        "firewalld_ipset_addresses": module.params['addresses']
    }

    if module.check_mode:
        return result

    # Modifying a preexisting ipset
    if module.params['name'] in sets and module.params['state'] == 'present':
        client_ipset_config = config.getIPSetByName(module.params['name'])
        original_entries = client_ipset_config.getEntries()
        client_ipset_config.setEntries(module.params['addresses'])
        external_state(client, module.params)
        new_entries = client_ipset_config.getEntries()
        result['changed'] = (new_entries != original_entries)
        result['firewalld_ipset_addresses'] = new_entries

    # Creating a new ipset because the one proposed in the module declaration
    # does not exist already.
    elif module.params['name'] not in sets and module.params['state'] == 'present':
        client_ipset_config = config.addIPSet(module.params['name'], settings)
        original_entries = client_ipset_config.getEntries()
        client_ipset_config.setEntries(module.params['addresses'])
        external_state(client, module.params)
        new_entries = client_ipset_config.getEntries()
        result['changed'] = (new_entries != original_entries)
        result['firewalld_ipset_addresses'] = new_entries

    # Removing an ipset that exists right now. If an ipset is asked to be
    # removed when it doesn't exist, we should just return an "unchanged"
    # state.
    elif module.params['name'] in sets and module.params['state'] == 'absent':
        client_ipset_config = config.getIPSetByName(module.params['name'])
        original_entries = client_ipset_config.remove()
        external_state(client, module.params)
        result['changed'] = True

    module.exit_json(**result)

def main():
    run()

if __name__ == '__main__':
    main()

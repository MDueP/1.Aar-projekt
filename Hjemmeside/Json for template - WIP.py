import json
        
parameters_json = "C:/Users/Due/Dropbox/IT-Tek/1.års Projekt/Programmering/Hjemmeside/parameters.json"
template_json = "C:/Users/Due/Dropbox/IT-Tek/1.års Projekt/Programmering/Hjemmeside/template.json"
            
            
with open(parameters_json, 'r') as file:
    parameters = json.load(file)
    parameters['parameters']['virtualMachineRG']['value'] = resource_group
    parameters['parameters']['resourceGroup']['value'] = resource_group
    parameters['parameters']['virtualMachineName']['value'] = vm_name
    parameters['parameters']['virtualMachineComputerName']['value'] = vm_name
    parameters['parameters']['adminUsername']['value'] = admin_username
    if admin_password == confirm_password:
        parameters['parameters']['adminPassword']['value'] = admin_password           
        parameters['parameters']['dataDiskResources']['value'][0]['properties']['diskSizeGB'] = int(disk_size.split()[0])
        parameters['parameters']['virtualNetworkName']['value'] = virtual_network
        parameters['parameters']['subnetName']['value'] = subnet
                        
    with open(parameters_json, 'w') as file:
        json.dump(parameters, file, indent=4)
    
        with open(template_json, 'r') as file:
            template = json.load(file)
            template['resources'][3]['properties']['storageProfile']['imageReference']['publisher'] = image_publisher
            template['resources'][3]['properties']['storageProfile']['imageReference']['offer'] = image_offer
            template['resources'][3]['properties']['storageProfile']['imageReference']['sku'] = image_sku
            with open(template_json, 'w') as file:
                json.dump(template, file, indent=4)                           
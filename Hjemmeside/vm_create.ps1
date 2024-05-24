
            Connect-AzAccount
            
            #Azure Account - Info
            $resourcegroup = 'hej'
            $location = 'euwest'
            
            #VM Account - Info
            $adminUsername = "lol"
            $adminPassword = ConvertTo-SecureString "hahahahahha" -AsPlainText -Force
            
            #VM - Info
            $vmName = "med dig"
            $vmSize = "Standard_D2ds_v5"
            $diskSize = 127
            $image = "MicrosoftWindowsServer:WindowsServer:2016-Datacenter"
            
            #Networking
            $Subnet = New-AzVirtualNetworkSubnetConfig -Name subnet -AddressPrefix "10.0.0.0/24"
            $vnet_name = 'vnet'
            
            New-AzResourceGroup -Name $resourcegroup -Location $location
            
            New-AzVirtualNetwork -Name $vnet_name -ResourceGroupName $resourcegroup -Location $location -AddressPrefix "10.0.0.0/16" -Subnet $Subnet
            
            New-AzVm `
                -ResourceGroupName $resourceGroup `
                -Name $vmName `
                -ImageName "MicrosoftWindowsServer:WindowsServer:2016-Datacenter" `
                -Credential (New-Object System.Management.Automation.PSCredential ($adminUsername, (ConvertTo-SecureString $adminPassword -AsPlainText -Force))) `
                -Size Standard_D2ds_v5 `
                -Location $location `
                -VirtualNetworkName $virtualNetwork `
                -SubnetName $subnet `
                -PublicIpAddressName "$vmName-ip" `
                -DataDiskSizeInGB $diskSize
                -AvailabilitySetName     
                -LicenseType
                -SecurityType "Standard"
                -NetworkInterfaceDeleteOption "Delete"
                -EnableAcceleratedNetworking
                -SystemAssignedIdentity
                -AllocationMethod "Static"
            Add-AzVMDataDisk -VM $vmName -Name $vmName_disk1 -DiskSizeInGB 256 -CreateOption "Empty" -DeleteOption "Delete" 
        
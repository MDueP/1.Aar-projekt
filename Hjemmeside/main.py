from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors, re
from flask_bcrypt import Bcrypt
import json
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'mikkelersej'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'pythonlogin'

mysql = MySQL(app)
    
@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM pythonlogin.accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account and bcrypt.check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect Username or Password'
    return render_template('index.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM pythonlogin.accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        
        if account:
            msg = 'Account already exists'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = "Invalid email"
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers'
        elif not username or not password or not email:
            msg = 'Please fill out all the fields'
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            cursor.execute('INSERT INTO pythonlogin.accounts VALUES (NULL, %s, %s, %s)', (username, hashed_password, email,))
            mysql.connection.commit()
            msg = 'Successfully registered'
    elif request.method == 'POST':
        msg = 'Please fill out all the fields '
    return render_template('register.html', msg=msg)

@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/form', methods=['POST', 'GET'])
def form():
    if 'loggedin' in session:
        if request.method == 'POST':
            resource_group = request.form.get("resource_group")
            vm_name = request.form.get("vm_name")
            os_image = request.form.get("OSImage")
            admin_username = request.form.get("admin_username")
            admin_password = request.form.get("admin_password")
            confirm_password = request.form.get("confirm_password")
            disk_size = request.form.get("disk_size")
            virtual_network = request.form.get("virtual_network")
            subnet = request.form.get("subnet")
            
            image_offer, image_publisher, image_sku = os_image.split(';')
            
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
            # Syntax for Shell Script
            # https://learn.microsoft.com/en-us/powershell/module/az.compute/new-azvm?view=azps-12.0.0
            shell_script = f"""
            Connect-AzAccount
            
            #Azure Account - Info
            $resourcegroup = '{resource_group}'
            $location = 'euwest'
            
            #VM Account - Info
            $adminUsername = "{admin_username}"
            $adminPassword = ConvertTo-SecureString "{admin_password}" -AsPlainText -Force
            
            #VM - Info
            $vmName = "{vm_name}"
            $vmSize = "Standard_D2ds_v5"
            $diskSize = 127
            $image = "{image_publisher}:{image_offer}:{image_sku}"
            
            #Networking
            $Subnet = New-AzVirtualNetworkSubnetConfig -Name {subnet} -AddressPrefix "10.0.0.0/24"
            $vnet_name = '{virtual_network}'
            
            New-AzResourceGroup -Name $resourcegroup -Location $location
            
            New-AzVirtualNetwork -Name $vnet_name -ResourceGroupName $resourcegroup -Location $location -AddressPrefix "10.0.0.0/16" -Subnet $Subnet
            
            New-AzVm `
                -ResourceGroupName $resourceGroup `
                -Name $vmName `
                -ImageName "{image_publisher}:{image_offer}:{image_sku}" `
                -Credential (New-Object System.Management.Automation.PSCredential ($adminUsername, (ConvertTo-SecureString $adminPassword -AsPlainText -Force))) `
                -Size Standard_D2ds_v5 `
                -Location $location `
                -VirtualNetworkName $virtualNetwork `
                -SubnetName $subnet `
                -PublicIpAddressName "$vmName-ip" `
                -DataDiskSizeInGB $diskSize
                -AvailabilitySetName     
                -SecurityType "Standard"
                -NetworkInterfaceDeleteOption "Delete"
                -EnableAcceleratedNetworking
                -SystemAssignedIdentity
                -AllocationMethod "Static"
            Add-AzVMDataDisk -VM $vmName -Name $vmName_disk1 -DiskSizeInGB {disk_size.split()[0]} -CreateOption "Empty" -DeleteOption "Delete" 
        """
            powershell_path =  "C:/Users/Due/Dropbox/IT-Tek/1.års Projekt/Programmering/Hjemmeside/vm_create.ps1"
            with open(powershell_path, 'w') as ps_file:
                ps_file.write(shell_script)
            
            return render_template('form.html', username=session['username'], vm_data=parameters)
        return render_template('form.html', username=session['username'])
    return redirect(url_for('login'))
    
app.run(debug=True) #ssl_context=('cert.pem', 'key.pem')
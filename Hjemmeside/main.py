from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors, re
from flask_bcrypt import Bcrypt
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'mikkelersej'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'pythonlogin'

mysql = MySQL(app)

restricted_usernames = {"administrator", "admin", "user", "user1", "test", "user2", "test1", "user3", "admin1",
                         "1", "123", "a", "actuser", "adm", "admin2", "aspnet", "backup", "console", "david", 
                         "guest", "john", "owner", "root", "server", "sql", "support", "support_388945a0", 
                         "sys", "test2", "test3", "user4", "user5"}
def valid_username(username):
    windows_invalid = re.compile(r'[/"\[\]:|<>+=;,?*@&]')
    linux_invalid = re.compile(r'^[a-zA-Z0-9_]+$')
    if username.lower() in restricted_usernames:
        return False, "Username is not allowed"
    if windows_invalid.search(username) or username.endswith('.'):
        return False, "Cannot contain special characters /""[]:|<>+=;,?*@&"
    if not linux_invalid.match(username):
        return False, "Username must only contain letters, numbers, hyphens, and underscores"
    if len(username) > 20:
        return False, "Username exceeds maximum length"
    return True, ""
def valid_password(password):
    password_contains = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{12,123}$')
    return password_contains.match(password)

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
        msg = ''
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
            
            is_valid, error_msg = valid_username(admin_username)
            if not is_valid:
                msg = error_msg
                return render_template('form.html', username=session['username'], msg=msg)
            
            if not valid_password(admin_password):
                msg = "Password is not complex enough"
                return render_template('form.html', username=session['username'], msg=msg)
            
            if admin_password != confirm_password:
                msg = "Passwords do not match"
                return render_template('form.html', username=session['username'], msg=msg)

            
            image_offer, image_publisher, image_sku = os_image.split(';')
            

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
            msg = "Form submitted successfully"
            return render_template('form.html', username=session['username'], msg=msg)
        return render_template('form.html', username=session['username'], msg=msg)
    return redirect(url_for('login'))
    
app.run(debug=True) #ssl_context=('cert.pem', 'key.pem')
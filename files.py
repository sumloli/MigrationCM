import os
import time
import paramiko
import main, platforms


def download(ip, filename, remotepath, localpath=''):
    path = os.getcwd()
    if localpath != '':
        try:
            if not os.path.exists(path + localpath):
                os.makedirs(path + localpath)
        except OSError:
            print(f"Creation of the directory {path + localpath} failed")
        else:
            print(f"Directory {path + localpath}")
    else:
        localpath = '/'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(ip, main.omm_username, main.omm_password)
        ssh.connect(ip, username=main.omm_username, password=main.omm_password)
    except Exception as e:
        print(e)
        print("It doesn't seem to be Prague's VM and credentials are wrong\nPlease check login/pass used to connect")
    sftp = ssh.open_sftp()
    sftp.get(remotepath + filename, path + localpath + filename,
             callback=lambda x, y: print(f'{filename} transferred: {x / y * 100:.0f}%'))
    sftp.close()
    ssh.close()


def upload(ip, filename, remotepath, localpath=''):
    path = os.getcwd()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username="root", password="strom")
    except Exception as e:
        print(e)
        print("It doesn't seem to be Prague's VM \nTrying to use RU credentials instead")
        ssh.connect(ip, username="dboriso", password="B52-a418-C949")
    sftp = ssh.open_sftp()
    try:
        sftp.chdir(remotepath)  # Test if remote_path exists
    except IOError:
        sftp.mkdir(remotepath)  # Create remote_path
        sftp.chdir(remotepath)
    sftp.put(localpath=path + localpath + filename, remotepath=remotepath + filename,
             callback=lambda x, y: print(f' transferred: {x / y * 100:.0f}%'))
    sftp.close()
    ssh.close()


def download_cfgs(ip, module):
    if module != 'see':
        def_cfgs = platforms.get_default_cfgs_list(ip, module)
        if not def_cfgs:
            for cfg in platforms.get_actual_cfgs_list(ip, module):
                print(f'Trying to download {cfg}')
                download(ip=ip, filename=cfg, remotepath=f'/opt/sts/{module}/',
                         localpath=f'/platform/{module}[{ip}]/actualcfg/')
                print(f'Downloaded {cfg}')
        else:
            for cfg in def_cfgs:
                print(f'Trying to download {cfg}')
                download(ip=ip, filename=cfg, remotepath=f'/opt/sts/{module}/defaultcfg/',
                         localpath=f'/platform/{module}[{ip}]/defaultcfg/')
                print(f'Downloaded {cfg}')
            for cfg in platforms.get_actual_cfgs_list(ip, module):
                print(f'Trying to download {cfg}')
                download(ip=ip, filename=cfg, remotepath=f'/opt/sts/{module}/',
                         localpath=f'/platform/{module}[{ip}]/actualcfg/')
                print(f'Downloaded {cfg}')
                if cfg == 'bus.ini':
                    print('!!!!!!!!!!!!bus.ini found!!!!!!!!!!!!!!!!!')
                    # editing bus ini and uploading it with new parameters back
                    busini = f'{os.getcwd()}/platform/{module}[{ip}]/actualcfg/bus.ini'
                    print(busini)
                    with open(busini, 'r', encoding='cp1252') as f:
                        lines = f.readlines()
                        print(lines)
                    with open(busini, 'w') as f:
                        for line in lines:
                            line = line.replace('newcm=false', 'newcm=true')
                            f.write(line)
                            print(line)
                    upload(ip, filename='bus.ini', remotepath=f'/opt/sts/{module}/',
                                 localpath=f'/platform/{module}[{ip}]/actualcfg/')


def download_all_platform_cfgs(omm):
    for vm in platforms.get_modules(omm):
        print(vm)
        print(vm.get('@IP1'))
        if type(vm.get('Module')) == list:
            module = main.module_from_midtype(vm.get('Module', {})[0].get('@MIDType'))
            print(module)
        else:
            module = main.module_from_midtype(vm.get('Module', {}).get('@MIDType'))
            print(module)
        if module != 'see':
            download_cfgs(vm.get('@IP1'), 'bus')
            if type(vm.get('Module')) == list:
                for module in vm.get('Module'):
                    download_cfgs(vm.get('@IP1'), main.module_from_midtype(module.get('@MIDType')))
            else:
                download_cfgs(vm.get('@IP1'), main.module_from_midtype(vm.get('Module', {}).get('@MIDType')))
        else:
            tme = time.localtime()
            with open("log.txt", 'a') as logfile:
                logfile.write(f'{time.strftime("%m/%d/%y %H:%M:%S", tme)}   ------    {vm.get("@IP1")} is Windows\n')


def win_upload_check():
    print('----------Waiting for Windows configs to be uploaded----------')
    file_path = 'win.done'
    try:
        while not os.path.exists(file_path):
            time.sleep(5)
            print('*Ctrl+C to continue...*\n')
    except KeyboardInterrupt:
        print('\nContinuing w/o win configs')
    # if os.path.isfile(file_path):
    #     print('----------Win configs successfully uploaded, proceed----------')
    # else:
    #     raise ValueError("%s isn't a file!" % file_path)

import os
import json
import time
import xmltodict
import paramiko
from pprint import pprint
import files, rest


def rollback(platform):
    folders_list = [f for f in os.listdir(platform) if not f.startswith('.')]
    print(f'Starting rollback of {platform}')
    print(folders_list)
    for folder in folders_list:
        print(f'Module: {folder}')
        ip = folder.split('[')[1][:-1].upper()
        print(ip)
        for cfg in os.listdir(f'{platform}/{folder}/actualcfg'):
            print(cfg)
            if cfg == 'bus.ini':
                # editing bus ini and uploading it with new parameters back
                busini = f'{os.getcwd()}/{platform}/{folder}/actualcfg/bus.ini'
                print(busini)
                with open(busini, 'r') as f:
                    lines = f.readlines()
                    print(lines)
                with open(busini, 'w') as f:
                    for line in lines:
                        line = line.replace('newcm=true', 'newcm=false')
                        f.write(line)
                        print(line)
            # print(f"upload({ip}, filename={cfg}, remotepath='/opt/sts/testmigration_{folder.split('[')[0].lower()}/', localpath='/{platform}/{folder}/actualcfg/')")
            files.upload(ip, filename=cfg, remotepath=f'/opt/sts/{folder.split("[")[0].lower()}/', localpath=f'/{platform}/{folder}/actualcfg/')


def get_modules(omm_ip):
    try:
        files.download(ip=omm_ip, filename='module_registry.xml', remotepath='/opt/sts/omm/')
        print('DOWNLOADED SUCCESSFULLY')
    except Exception as e:
        print('"downloading module_registry.xml from OMM" FAILED')
        print(e)
    with open("module_registry.xml") as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
        xml_file.close()
        data = json.loads(json.dumps(data_dict['ModuleRegistry']['Modules']['BUS']))
        data_json = json.dumps(data_dict['ModuleRegistry']['Modules']['BUS'])
        with open("data.json", "w") as json_file:
            json_file.write(data_json)
            json_file.close()
    pprint(data)
    print('DATATYPE:'+str(type(data)))
    return data


def get_default_cfgs_list(ip, module):
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
        list_of_cfgs = sftp.listdir(f'/opt/sts/{module}/defaultcfg')
        print(list_of_cfgs)
    except Exception as e:
        list_of_cfgs = {}
        print(e)
        tme = time.localtime()
        with open("log.txt", 'a') as logfile:
            logfile.write(f"{time.strftime('%m/%d/%y %H:%M:%S', tme)}   ------    {ip} module {module} doesn't have default configs\n")
        pass
    sftp.close()
    ssh.close()
    return list_of_cfgs


def get_actual_cfgs_list(ip, module):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username="root", password="strom")
    except Exception as e:
        print(e)
        print("It doesn't seem to be Prague's VM \nTrying to use RU credentials instead")
        ssh.connect(ip, username="dboriso", password="B52-a418-C949")
    sftp = ssh.open_sftp()
    list_of_files = sftp.listdir(f'/opt/sts/{module}')
    print(list_of_files)
    list_of_cfgs = [cfg for cfg in list_of_files if cfg.endswith(".xml")]
    if 'bus.xml' in list_of_cfgs:
        list_of_cfgs.append('bus.ini')
    print(list_of_cfgs)
    sftp.close()
    ssh.close()
    return list_of_cfgs


def resolve_dpa():
    # function is finding DPAs in module_registry and finding matching module in DB
    # returns list of dpas in format [ip, mid, id]
    global dpas
    d = get_modules("10.240.206.111")
    print(d)
    dpas = []
    for _ in d:
        print('_____________')

        for k, v in _.items():
            print(f'{k} :: {v}')
            if type(v) == dict:
                print('dictionary here')
                for key, value in v.items():
                    print(f'---{key} :: {value}')
                    if key == '@MIDType' and (value == '0x011' or value == '0xED5'):
                        print('------DPA/EDP IS HERE')
                        print(_)
                        print(f"{_['@IP1']}")
                        print(f"{_['@MID'].replace('0001', '0111')}")
                        print("MAKING REQUEST TO REST API")
                        r = rest.make_request('GET', 'https://10.240.151.60',
                                         '/mr/module?moaftype=1&moduletype=0x011&roleuser=migration')
                        modules = json.loads(r[1])
                        print(modules)
                        for i in modules['module']:
                            ip = _['@IP1']
                            print('_____________')
                            print(i)
                            print(f"---mid:{i['mid']} :: id:{i['id']}")
                            print('_____________')
                            mid = i['mid']
                            id = str(i['id'])
                            listt = [ip, mid, id]
                            if _['@MID'].replace('0001', '0111') == mid or _['@MID'].replace('0001', 'ED51') == mid:
                                dpas.append(listt)
            elif type(v) == list:
                print('list here')
                for module in v:
                    for key, value in module.items():
                        print(f'---{key} :: {value}')
                        if key == '@MIDType' and (value == '0x011' or value == '0xED5'):
                            print('------DPA/EDP IS HERE')
                            print(_)
                            print(f"{_['@IP1']}")
                            print(f"{_['@MID'].replace('0001', '0111')}")
                            print("MAKING REQUEST TO REST API")
                            if value == '0x011':
                                r = rest.make_request('GET', 'https://10.240.151.60',
                                                      '/mr/module?moaftype=1&moduletype=0x011&roleuser=migration')
                            else:
                                r = rest.make_request('GET', 'https://10.240.151.60',
                                                      '/mr/module?moaftype=1&moduletype=0xed5&roleuser=migration')
                            modules = json.loads(r[1])
                            print(modules)
                            for i in modules['module']:
                                ip = _['@IP1']
                                print('_____________')
                                print(i)
                                print(f"---mid:{i['mid']} :: id:{i['id']}")
                                print('_____________')
                                mid = i['mid']
                                id = str(i['id'])
                                listt = [ip, mid, id]
                                if _['@MID'].replace('0001', '0111') == mid or _['@MID'].replace('0001', 'ED51') == mid:
                                    dpas.append(listt)

        print('_____________')
    return dpas
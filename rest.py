import requests
import os
import json
import time
import main, platforms


def make_request(method, base, path, headers=None, params=None, body=None):
    try:
        auth = requests.request('POST', f'{main.mms}/global/activeusers', auth=(main.mms_username, main.mms_password), verify=False)
        if auth.status_code == 201:
            print('Successfully authorized')
        auth.raise_for_status()
        headers = {'Authorization': f'Bearer {auth.headers["X-Token"]}'}
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    if params:
        print(f'{method, path, params}:')
    else:
        print(f'{method, path}:')
    try:
        response = requests.request(method, f'{base + path}', headers=headers, params=params, data=body, verify=False)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print('Http Error:', errh)
        print('URL failed:', errh.request.url)
        print('Fail msg:', errh.response.text)
        # response = errh.response
        response = None
    return [response, response.text, headers]


def import_default_cfgs(platform):
    # platform is platform folder name after download
    folders_list = [f for f in os.listdir(platform) if not f.startswith('.')]
    print(folders_list)
    for folder in folders_list:
        print(f'Module: {folder}')
        print(f"{folder.split('[')[0].upper()}")
        for cfg in os.listdir(f"{platform}/{folder}/defaultcfg"):
            ignored_cfgs = ['endpoints.xml', 'peers.xml', 'peer_router_rules.xml']
            if cfg not in ignored_cfgs:
                print(f'\n\n {folder.split("[")[0].upper()} {cfg}')
                print('\n"POST defaultxml":')
                try:
                    with open(f"{platform}/{folder}/defaultcfg/{cfg}", 'rb') as f:
                        body = f.read()
                        print(f'{platform}/{folder}/defaultcfg/{cfg}')
                        # print(f'opening cfg: {body}')
                    add = make_request('POST', main.mms, '/cm/cfgparams/defaultxmls',
                                       params=dict(moaftype='1',
                                                   moduletype=main.midtype_from_module(folder.split('[')[0].upper()),
                                                   moduleconfigtype=cfg,
                                                   iversion='001.00.00',
                                                   name=f'TESTMIGRATION_DEFAULT_{folder.split("[")[0].upper()}_{cfg}',
                                                   description='TESTMIGRATION_dmytro',
                                                   roleuser=main.roleuser),
                                       body=body)[1]
                    print(json.loads(add))
                    print(type(json.loads(add)))
                    id = json.loads(add)['Id']
                    print(f'id: {id}')
                    print('SUCCESS')
                except Exception as e:
                    print('"POST defaultxml" FAILED')
                    print(e)
                    tme = time.localtime()
                    with open("log.txt", 'a') as logfile:
                        logfile.write(
                            f'{time.strftime("%m/%d/%y %H:%M:%S", tme)}   ------  '
                            f'{platform}/{folder}/defaultcfg/{cfg}  {e}\n')


def create_profile_import_xml(platform):
    # platform is platform folder name after download
    folders_list = [f for f in os.listdir(platform) if not f.startswith('.')]
    print(folders_list)
    pr = 0
    for folder in folders_list:
        print(f'Module: {folder}')
        print(f"{folder.split('[')[0].upper()}")
        for cfg in os.listdir(f"{platform}/{folder}/defaultcfg"):
            ignored_cfgs = ['endpoints.xml', 'peers.xml', 'peer_router_rules.xml']
            if cfg not in ignored_cfgs:
                print(f'\n\n {folder.split("[")[0].upper()} {cfg}')
                print('\n"Create and add xml to profile":')
                if os.path.isfile(f'{platform}/{folder}/actualcfg/{cfg}'):
                    print('Actual cfg found!')
                    try:
                        if cfg == 'local_peer.xml':
                            pr += 1
                            add_profile = make_request('POST', main.mms, '/cm/profiles',
                                                       params=dict(name=f'TESTMIGRATION_ACTUAL_{folder.split("[")[0].upper()}_{folder[-4:][:-1]}_{cfg}',
                                                                   moaftype='1',
                                                                   moduletype=main.midtype_from_module(
                                                                              folder.split('[')[0].upper()),
                                                                   moduleconfigtype=cfg,
                                                                   priority=pr, description='TESTMIGRATION_dmytro',
                                                                   roleuser=main.roleuser))[1]
                        else:
                            add_profile = make_request('POST', main.mms, '/cm/profiles',
                                                       params=dict(
                                                           name=f'TESTMIGRATION_ACTUAL_{folder.split("[")[0].upper()}_{cfg}',
                                                           moaftype='1',
                                                           moduletype=main.midtype_from_module(
                                                               folder.split('[')[0].upper()),
                                                           moduleconfigtype=cfg,
                                                           priority='1', description='TESTMIGRATION_dmytro',
                                                           roleuser=main.roleuser))[1]
                        print(json.loads(add_profile))
                        print(type(json.loads(add_profile)))
                        id = json.loads(add_profile)['Result']['Id']
                        print(f'id: {id}')
                        print('SUCCESSFULLY CREATED PROFILE')
                        with open(f"{platform}/{folder}/actualcfg/{cfg}", 'rb') as f:
                            body = f.read()
                            print(body)
                        import_xml_to_profile = make_request('POST', main.mms, '/cm/cfgparams/importxmls',
                                                             params=dict(profileid=id,
                                                                         iversion='001.00.00',
                                                                         roleuser='migration'),
                                                             body=body)[1]
                        print(json.loads(import_xml_to_profile))
                        print(type(json.loads(import_xml_to_profile)))
                        print('SUCCESSFULLY ADDED XML TO PROFILE(ACTUAL)')
                        if cfg == 'local_peer.xml':
                            for _ in platforms.resolve_dpa():
                                print(f"checking if {_[0]} = {folder.split('[')[1][:-1]}")
                                if _[0] == folder.split('[')[1][:-1]:
                                    try:
                                        print(f'\nAdding module to profile {id}')
                                        add = make_request('PUT', main.mms, f'/cm/profiles/{id}/module', params=dict(
                                            moduleid=_[2],
                                            roleuser=main.roleuser))[1]
                                        print(add)
                                        print(type(json.loads(add)))
                                        print(json.loads(add))
                                        print('SUCCESS')
                                    except Exception as e:
                                        print(f'Adding module to profile {id} FAILED')
                                        print(e)
                                        tme = time.localtime()
                                        with open("log.txt", 'a') as logfile:
                                            logfile.write(
                                                f'{time.strftime("%m/%d/%y %H:%M:%S", tme)}   ------  {platform}/{folder}/actualcfg/{cfg}  {e}\n')
                        else:
                            try:
                                print(f'\nAdding module to profile {id}')
                                add = make_request('PUT', main.mms, f'/cm/profiles/{id}/module', params=dict(
                                                                                                        moduleid='-1',
                                                                                                        roleuser='migration'))[1]
                                print(add)
                                print(type(json.loads(add)))
                                print(json.loads(add))
                                print('SUCCESS')
                            except Exception as e:
                                print(f'Adding module to profile {id} FAILED')
                                print(e)
                                tme = time.localtime()
                                with open("log.txt", 'a') as logfile:
                                    logfile.write(
                                        f'{time.strftime("%m/%d/%y %H:%M:%S", tme)}   ------  {platform}/{folder}/actualcfg/{cfg}  {e}\n')
                    except Exception as e:
                        print('"Create and add xml to profile" FAILED')
                        print(e)
                        tme = time.localtime()
                        with open("log.txt", 'a') as logfile:
                            logfile.write(
                                f'{time.strftime("%m/%d/%y %H:%M:%S", tme)}   ------  {platform}/{folder}/actualcfg/{cfg}  {e}\n')
                else:
                    print('Actual cfg NOT found!')


def migrate_db():
    print('\nConverting EXPORT into JSON\n')
    result = make_request('POST', main.mms, f'/system/migrateoldcm', params=dict(path='/opt/sts/mms/Migration', roleuser='migration'))[1]
    print(result)
    result_json = json.loads(result)
    return result_json['FileResultInFo']['filepath']


def import_db_data(json_path):
    start_time = time.time()
    print('\nUploading JSON to DB\n')
    result = make_request('POST', main.mms, f'/system/import', params=dict(filepath=json_path, roleuser='migration'))[1]
    print(result)
    result_json = json.loads(result)
    print(f"\nUploading took {time.time() - start_time} seconds ---\n")
    return result_json

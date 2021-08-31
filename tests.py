import main, rest, files, platforms
import json

main.main()

def jprint(obj):
    text = json.dumps(json.loads(obj), sort_keys=False, indent=4)
    print(text)


print('\nDEBUG FUNCTION:')
print('DEBUG FUNCTION "GET version":')
try:
    print(rest.make_request('GET', main.mms, '/global/versions'))
    print('SUCCESS')
except Exception as e:
    print('"GET version" FAILED')
    print(e)

print('\nDEBUG FUNCTION:')
print('DEBUG FUNCTION "GET db version":')
try:
    print(rest.make_request('GET', main.mms, '/global/versions', params={'id': 'db'}))
    print('SUCCESS')
except Exception as e:
    print('"GET db version" FAILED')
    print(e)

print('\nDEBUG FUNCTION:')
print('DEBUG FUNCTION "GET modules":')
try:
    jprint(rest.make_request('GET', main.mms, '/mr/module', params={'roleuser': 'Test'})[1])
    print('SUCCESS')
except Exception as e:
    print('"GET modules" FAILED')
    print(e)

print('\nDEBUG FUNCTION:')
print('DEBUG FUNCTION "POST defaultxml":')
try:
    with open('body.xml', 'r') as f:
        body = f.read()
    add = rest.make_request('POST', main.mms, '/cm/cfgparams/defaultxmls', params={'moaftype': '1', 'moduletype': '0x002',
                                                                         'moduleconfigtype': 'TEST_apisecuritydefaults.xml',
                                                                         'iversion': '001.00.00',
                                                                         'name': 'TEST_apisecuritydefaults',
                                                                         'description': 'TEST_dmytro',
                                                                         'roleuser': 'Test'}, body=body)[1]
    print(json.loads(add))
    print(type(json.loads(add)))
    id = json.loads(add)['Id']
    print(f'id: {id}')
    print('SUCCESS')
except Exception as e:
    print('"POST defaultxml" FAILED')
    print(e)

print('\nDEBUG FUNCTION:')
print('DEBUG FUNCTION "GET profile":')
try:
    get = rest.make_request('GET', main.mms, f'/cm/profiles/{id}', params={'roleuser': 'Test'})
    print(get)
    print('SUCCESS')
except Exception as e:
    print('"GET profile" FAILED')
    print(e)

print('\nDEBUG FUNCTION:')
print('DEBUG FUNCTION "DELETE profile":')
try:
    remove = rest.make_request('DELETE', main.mms, f'/cm/profiles/{id}', params={'roleuser': 'Test'})
    print(remove)
    print('SUCCESS')
except Exception as e:
    print('"DELETE profile" FAILED')
    print(e)

print('\nDEBUG FUNCTION:')
print('DEBUG FUNCTION "downloading file":')
try:
    files.download(ip='10.240.151.112', filename='tts.pcap', remotepath='/opt/sts/')
    print('SUCCESS')
except Exception as e:
    print('"downloading file" FAILED')
    print(e)
print('\nDEBUG FUNCTION:')
print('DEBUG FUNCTION "downloading module_registry.xml from OMM":')
try:
    # download(ip='10.97.155.51', filename='module_registry.xml', remotepath='/opt/sts/omm/')
    files.download(ip='10.240.206.111', filename='module_registry.xml', remotepath='/opt/sts/omm/')
    print('SUCCESS')
except Exception as e:
    print('"downloading module_registry.xml from OMM" FAILED')
    print(e)
# print('\nDEBUG FUNCTION:')
# print('DEBUG FUNCTION "receiving modules list":')
# try:
#     for vm in platform.get_modules(main.omm):
#         print(f"Modules at {vm.get('@IP1')}: {main.module_from_midtype(vm.get('Module', {}).get('@MIDType'))}")
#     print('SUCCESS')
# except Exception as e:
#     print('"receiving modules list" FAILED')
#     print(e)
# print('\nDEBUG FUNCTION:')
# print('DEBUG FUNCTION "download configurations":')
# try:
#     files.download_cfgs('10.240.250.149', 'bus')
#     files.download_cfgs('10.240.250.149', 'omm')
#     print('SUCCESS')
# except Exception as e:
#     print('"download configuration')
#     print(e)

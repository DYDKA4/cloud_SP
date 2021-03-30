import argparse
import subprocess
import shutil
import openstack
import json

# python   final.py --name tulin_network_2 --network net-for-83.149.198-sandbox --os centos7 --cpu 4  --ram 4 --size 10 --key tulin_key
acceptable_OS = ("centos7", "ubuntu18.04", "ubuntu20.04")
full_name_OS = ('CentOS-7-x86_64-GenericCloud-2009', 'Ubuntu Server 18.04 LTS (Bionic Beaver)',
                'Ubuntu Server 20.04 LTS (Focal Fossa)')
# можно придумать user interface для подбора наиболе cхожих имён acceptable_OS с именами операционных систем пришедших
# от api
name_dict = dict(zip(acceptable_OS, full_name_OS))
parser = argparse.ArgumentParser()
parser.add_argument("--name", required=True, help="имя виртуальной машины")
parser.add_argument("--network", required=True, help=" id виртуальной сети")
parser.add_argument("--os", required=True,
                    help="операционная система виртуальной машины   , доступные значения \
                    centos7, ubuntu18.04, ubuntu20.04")
parser.add_argument("--cpu", required=True, type=int, help="число виртуальных ядер")
parser.add_argument("--ram", required=True, type=float, help="объем RAM в GB")
parser.add_argument("--size", required=True, type=int, help="размер диска в GB")
parser.add_argument("--key", required=True, help=" имя ключа из key-pair в openstack")
args = parser.parse_args()
if args.os not in acceptable_OS:
    print("FAIL, WRONG OS")
    raise SystemExit(1)

password = input("Enter password: ")
conn = openstack.connect(
    region_name='regionOne',
    auth=dict(
        auth_url='https://sky.ispras.ru:13000',
        username='tulin',
        password=password,
        project_id='e01309aa8f6f4e7eb5a90fa5cbacc628',
        user_domain_name='ispras'),
    compute_api_version='2',
    identity_interface='internal')

flavor_name = ' '
param = [args.cpu, args.ram, args.size]
params = []
summa = []
names = []
for flavor in conn.compute.flavors():
    if flavor.vcpus >= param[0] and flavor.ram/1024 >= param[1] and flavor.disk >= param[2]:
        params.append([flavor.vcpus, flavor.ram / 1024, flavor.disk])
        summa.append(sum([flavor.vcpus, flavor.ram/1024, flavor.disk]))
        names.append(flavor.name)


def ind_eq(arr):
    n = len(arr)
    res = []
    for i in range(n - 1):
        for j in range(i + 1, n):
            if min(arr) == arr[i] and arr[i] == arr[j]:
                res.append((i, j))
    return res
if names == []:
    print("NO SUCH FLAVOR")
    raise SystemExit(5)
else:
    res = ind_eq(summa)
    flavor_name = names[summa.index(min(summa))]
    params_fl = params[summa.index(min(summa))]
    if res != []:
        for ind in res:
            # print(names[ind[0]], " ", names[ind[1]])
            # print(params[ind[0]], " ", params[ind[1]])
            if params_fl[0] < params[ind[1]][0]:
                params_fl = params[ind[1]]
                flavor_name = names[ind[1]]
            elif params_fl[0] == params[ind[1]][0] and params_fl[1] < params[ind[1]][1]:
                params_fl = params[ind[1]]
                flavor_name = names[ind[1]]
            # elif params_fl[1] == params[ind[1]][1] and params_fl[2] < params[ind[1]][2]:
            #     params_fl = params[ind[1]]
            #     flavor_name = names[ind[1]]

name = ' '
for image in conn.compute.images():
    if name_dict[args.os] == image.name:
        name = image.id

shutil.copy("copy_deploy.txt", "deploy.tf")
with open('deploy.tf', 'r') as f:
    old_data = f.read()

new_data = old_data.replace("\"\"", "\"" + password + "\"", 1)
new_data = new_data.replace("\"\"", "\"" + args.name + "\"", 1)
new_data = new_data.replace("\"\"", "\"" + name + "\"", 1)
new_data = new_data.replace("\"\"", "\"" + flavor_name + "\"", 1)
new_data = new_data.replace("\"\"", "\"" + args.key + "\"", 1)
new_data = new_data.replace("\"\"", "\"" + args.network + "\"", 1)

f.close()
with open('deploy.tf', 'w') as f:
    f.write(new_data)

PIPE = subprocess.PIPE
if subprocess.call(["terraform", "init"]):
    print("FAIL,TERRAFORM INIT")
    raise SystemExit(2)

if subprocess.call(["terraform", "plan"]):
    print("FAIL, TERRAFORM PLAM")
    raise SystemExit(3)

if subprocess.call(["terraform", "apply", "-auto-approve"]):
    print("FAIL, TERRAFORM APPLY")
    raise SystemExit(4)


for server in conn.compute.servers():
    server_info = server.to_dict()
    if server_info["name"] == args.name:
        output = {"NAME": args.name, "ID": server_info["id"], 'Created': server_info["created_at"],
                  "FlavorName": flavor_name, "Network": args.network, "Image Name": name_dict[args.os],
                  "Key": args.key, "IP": server_info["addresses"]}
        print("\nOK")
        print(json.dumps(output, indent=2))

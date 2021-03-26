import argparse
import subprocess
import shutil
import openstack
import json

# python   final.py --name tulin_network_2 --network net-for-83.149.198-sandbox --os centos7 --cpu 4\
# --ram 4 --size 10 --key tulin_key
acceptable_OS = ("centos7", "ubuntu18.04", "ubuntu20.04")
parser = argparse.ArgumentParser()
parser.add_argument("--name", required=True, help="имя виртуальной машины")
parser.add_argument("--network", required=True, help=" id виртуальной сети")
parser.add_argument("--os", required=True,
                    help="операционная система виртуальной машины, доступные значения \
                    centos7, ubuntu18.04, ubuntu20.04")
parser.add_argument("--cpu", required=True, type=int, help="число виртуальных ядер")
parser.add_argument("--ram", required=True, type=float  , help="объем RAM в GB")
parser.add_argument("--size", required=True, type=int, help="размер диска в GB")
parser.add_argument("--key", required=True, help=" имя ключа из key-pair в openstack")
args = parser.parse_args()
if args.os not in acceptable_OS:
    print("FAIL")
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

params = []
names = []
for flavor in conn.compute.flavors():
    names.append(flavor.name)
    params.append([flavor.vcpus, flavor.ram / 1024, flavor.disk])
param = [args.cpu, args.ram, args.size, ]

if param in params:
    flavor = (names[params.index(param)])
else:
    print("FAIL")
    raise SystemExit(5)

images_id = []
images_name = []
for image in conn.compute.images():
    # print(image.name)
    images_name.append(image.name)
    images_id.append(image.id)

acceptable_OS = ("centos7", "ubuntu18.04", "ubuntu20.04")
name = "ubuntu18.04"
if name == "centos7":
    name = images_id[images_name.index('CentOS-7-x86_64-GenericCloud-2009')]
elif name == "ubuntu20.04":
    name = images_id[images_name.index('Ubuntu Server 20.04 LTS (Focal Fossa)')]
elif name == "ubuntu18.04":
    name = images_id[images_name.index('Ubuntu Server 18.04 LTS (Bionic Beaver)')]

shutil.copy("copy_deploy.txt", "deploy.tf")
with open('deploy.tf', 'r') as f:
    old_data = f.read()

new_data = old_data.replace("\"\"", "\"" + password + "\"", 1)
new_data = new_data.replace("\"\"", "\"" + args.name + "\"", 1)
new_data = new_data.replace("\"\"", "\"" + name + "\"", 1)
new_data = new_data.replace("\"\"", "\"" + flavor + "\"", 1)
new_data = new_data.replace("\"\"", "\"" + args.key + "\"", 1)
new_data = new_data.replace("\"\"", "\"" + args.network + "\"", 1)

f.close()
with open('deploy.tf', 'w') as f:
    f.write(new_data)

PIPE = subprocess.PIPE
if subprocess.call(["terraform", "init"]):
    print("FAIL")
    raise SystemExit(2)

if subprocess.call(["terraform", "plan"]):
    print("FAIL")
    raise SystemExit(3)

if subprocess.call(["terraform", "apply", "-auto-approve"]):
    print("FAIL")
    raise SystemExit(4)

instance = conn.compute.find_server(args.name, ignore_missing=True)

print("\nOK")
print(json.dumps(instance, indent=2))

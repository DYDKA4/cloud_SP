import argparse
import subprocess
import shutil

# python   read_params.py --name ABC --network 123 --os centos7 --cpu 1 --ram 1024 --size 2048 --key ABC123
acceptable_OS = ("centos7", "ubuntu18.04", "ubuntu20.04")
acceptable_CPU = (8, 2, 1)
acceptable_RAM = (32, 16, 8, 4, 2, 1, 0.5)
acceptable_SIZW = (100, 50, 40, 25, 20, 12, 10, 1)
parser = argparse.ArgumentParser()
parser.add_argument("--name", required=True, help="имя виртуальной машины")
parser.add_argument("--network", required=True, type=int, help=" id виртуальной сети")
parser.add_argument("--os", required=True,
                    help="операционная система виртуальной машины, доступные значения centos7, ubuntu18.04, ubuntu20.04")
parser.add_argument("--cpu", required=True, type=int, help="число виртуальных ядер")
parser.add_argument("--ram", required=True, type=int, help="объем RAM в GB")
parser.add_argument("--size", required=True, type=int, help="размер диска в GB")
parser.add_argument("--key", required=True, help=" имя ключа из key-pair в openstack")
args = parser.parse_args()

shutil.copy("copy_deploy.txt", "deploy.tf")
with open ('deploy.tf', 'r') as f:
  old_data = f.read()

new_data = old_data.replace("\"\"", "\""+input("Enter password: ")+"\"", 1)
new_data = new_data.replace("\"\"", "\""+args.name+"\"", 1)
new_data = new_data.replace("\"\"", "\""+"Заглушка"+"\"", 1)
new_data = new_data.replace("\"\"", "\""+"Заглушка"+"\"", 1)
new_data = new_data.replace("\"\"", "\""+args.key+"\"", 1)

with open ('deploy.tf', 'w') as f:
  f.write(new_data)


if args.os not in acceptable_OS:
    print("Wrong type of OS")
    raise SystemExit(1)

# PIPE = subprocess.PIPE
# subprocess.call(["terraform", "init"], stdout=subprocess.DEVNULL)
# subprocess.call(["terraform", "plan"])
# subprocess.call(["terraform", "apply", "-auto-approve"])


print("\nprocess finished")

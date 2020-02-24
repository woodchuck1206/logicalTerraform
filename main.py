import json
import os
import argparse
import time

import packer_util as packer
import terraform_util as terraform

CONFIG  = "ami.json"
TIMEGAP = 60

# setting lock in case front and back both are triggered to update simultaneously
def set_lock(division):
    for f in os.listdir():
        if f.endswith(".lock"): status = f

    if status != "free.lock":
        return False
    
    os.remove(status)

    with open("lock.lock", "w") as f:
        pass

    return True

# free lock so either can be updated afterwards
def free_lock():
    try:
        os.remove("lock.lock")
    except:
        pass

    with open("free.lock", "w") as f:
        pass

# import current ami 
def import_ami():
    with open(CONFIG, "r") as f:
        raw = f.read()
    parse = json.loads(raw)
    return {
        "front" : str(parse["front"]),
        "back"  : str(parse["back"]),
    }

# export new ami
def export_ami(obj):
    raw = json.dumps(obj)
    with open(CONFIG, "w") as f:
        f.write(raw)

# take division argument
def parse_arg():
    parser  = argparse.ArgumentParser(description="Blue Green Deployment for Devops Landing Project")
    parser.add_argument("-d", "--division", help="Division(front/back) to be updated", required=True)
    args = parser.parse_args()
    if args.division not in ["front", "back"]:
        print("INVALID ARGUMENT, DIVISION MUST BE front OR back")
        return False
    return args.division

def main():
    division    = parse_arg()
    if not division: return

    while True:
        if set_lock(division):
            break
        time.sleep(TIMEGAP)

    print("IMPORTING OLD AMIS...")
    old = import_ami()
    new = {
        "front" : "",
        "back"  : "",
    }
    print("GENERATING NEW AMIS...")
    packer.generate_ami(division)
    print("RETRIEVING NEW AMIS...")
    new[division] = packer.retrieve_ami(division)
    
    print("CHECKING IF IT MEETS THE MINIMUM REQUIREMENTS...")
    for div in ["front", "back"]:
        if (new[div] == "" and old[div] == ""):
            packer.generate_ami(div)
            new[div] = packer.retrieve_ami(div)

    for key in new:
        if new[key] == "":
            new[key] = old[key]
        if old[key] == "":
            old[key] = new[key]

    if ".terraform" not in os.listdir():
        print("INITIATING AWS INFRA...")
        terraform.init_deploy(new)
    else:
        if division == "front":
            print("DEPLOYING FRONT...")
            terraform.deploy_front(old, new)
        else:
            print("DEPLOYING BACK...")
            terraform.deploy_back(old, new)
    
    print("SAVING AMIS...")
    export_ami(new)

if __name__ == "__main__":
    try:
        main()
    except:
        print("UNEXPECTED ERROR OCCURED DURING EXECUTING BLUE/GREEN DEPLOYMENT!")
        print("RELIEVING LOCK...")
        print("TRY AGAIN LATER")
    finally:
        free_lock()
    
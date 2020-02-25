import json
import subprocess
import os

BACKBASE    = "../devops/packer"
FRONTBASE   = "../vue_front"
BASE        = {
    "front" : FRONTBASE,
    "back"  : BACKBASE,
}
INPUT       = "packer.json"
OUTPUT      = "packer-manifest.json"

def parse_ami(artifact_id):
    return artifact_id[artifact_id.find(":")+1:]

def generate_ami(division):
    subprocess.run("cd {};. /home/ubuntu/.tmpEnv;/home/ubuntu/localBin/packer build {}".format(BASE[division], INPUT), shell=True)

def retrieve_ami(division):
    PATH    = os.path.join(BASE[division], OUTPUT)
    with open(PATH, "r") as f:
        raw = f.read()
    parse   = json.loads(raw)
    return parse_ami(parse["builds"][-1]["artifact_id"])

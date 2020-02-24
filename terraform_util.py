import subprocess
import os
from shutil import copyfile
from tfasset import *
import time

TFPATH  = "./main.tf"
ENVPATH = "/home/hyuck/tmpEnv"

def tf_apply(init=False):
    text = '''. {};terraform apply -auto-approve -var="my_access_key=$AWS_ACCESS" -var="my_secret_key=$AWS_SECRET"'''.format(ENVPATH)
    if init:
        text = "terraform init;" + text

    subprocess.run(text, shell=True) 

def make_tf(text):
    # target file config
    with open(TFPATH, "w") as f:
        f.write(text)

def init_deploy(new):
    text = still.format(new["front"], new["front"], new["back"], new["back"])
    make_tf(text)

    tf_apply(init=True)

def deploy_front(old, new):
    text = frontDeploy1.format(old["front"], new["front"], old["back"], old["back"])
    make_tf(text)

    tf_apply()

    # tester

    text = frontDeploy2.format(new["front"], new["front"], old["back"], old["back"])
    make_tf(text)

    tf_apply()

    # tester

    text = still.format(new["front"], new["front"], old["back"], old["back"])
    make_tf(text)

    tf_apply()

def deploy_back(old, new):
    text = backDeploy1.format(old["front"], old["front"], old["back"], new["back"])
    make_tf(text)

    tf_apply()

    # tester

    text = backDeploy2.format(old["front"], old["front"], new["back"], new["back"])
    make_tf(text)

    tf_apply()

    # tester

    text = still.format(old["front"], old["front"], new["back"], new["back"])
    make_tf(text)

    tf_apply()
# AWS stand-alone Linux-based development template

A Python-based demonstration of integrating localstack (which allows development w/o AWS account or related expenses) and CDK (AWS's great Infrastrcture-as-code project).

This demo deploys a functional serverless headend, which is compsed of Lambdas, DyanamoDb and REST-API-gateway.

I have made a couple of unconventional choices, which are explained bellow.
Also, a great effert was done to document the installation process, choices and alternatives.

## Overview

This repository contains the instructions for setup, starting from a clean 20.04 Ubuntu, of a Python-based backend project.

This template uses 3 AWS services:

   - REST API gateway: with IP white-list and the API defined, so the gateway can reject non-well-formed URLs
   - DynamoDB: defined w/two sample tables at the CDK/stack level
   - A single lambda that lists the users in the users table

The technologies demonstrated here are:
                         
   - Well documented installation procedure, using Python Virtual Envirment(s) for most of the packages
   - 100 percent local development, by using the wonderfull 'localstack' project
   - 'single click' infrastrcture deployment, using AWS's CDK project

I love Python. Therefore, almost all this project uses Python:

   - The stack is defined using Python (at infrastrcture/cdk_template/stack.py)
   - The sample lambda (at lambda_functions/handle_url_lambda.py) 
   - Most of the scripts used to 'operate' this project (some are bash)

## Design Choices

CDK: 
I have choosen the use only the "synth" (I.e., genrate CloudFormation template) feature of the CDK, as opposed to the full 'deploy' functionality. This enables a more detailed control and insight of the deployment proces.

 You may prefer using the CDK-deploy - it will make your life much simpler.

A related item: the way Lambdas are deployed is non-optimal, and will break once the Lambda is above a certail size.  TBD to improve.

Another choice is using localstack directly on the host (as opposed to the normal way of running localstack in a Docker container). I just feel it make operating the system easier, but there is a price to pay in the installation !

Also, most, but not all of the requirments packages are installed locally. THe reason some packages are installed globally is that those packages are tyipically used many times and are relativly big. So, it seems a waste of time and disk space to install ther per-project.

Currently, there are two distict virtual envirments: one dedicated to localstack and the other for CDK and everything else.  This is 'just happened' and might be fixed in later releases.


## Installation

This project was developed and tested on Xubuntu 22.04, but will probably work on any recent Ubuntu or Debian.

Note: Perform all the 'global' installation onle one time on your new Linux machine.
Note: The project is called "match_to_the_weight" and is abriviated to 'mttw' or 'MttW'.
      You will probably want to replace those with your own project name :-)

### Globally install the Localstack dependencies:

```
sudo apt install -y python3-pip python3-venv
sudo apt install -y python3-dev libsasl2-dev gcc
sudo apt install -y openjdk-11-jdk
```

### Globaly install the CDK dependencies (nodejs and npm):

```
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs
```
### Globaly install the CDK toolkilt: 

`sudo npm install -g aws-cdk`

### Create the project dir and the Python virtual env

```
mkdir <project folder>
cd <project folder>
python3 -m venv venv
. venv/bin/activate
```

### Install the CDK Python lib: 

```
cd infrastrcture/cdk-template
pip3 install -r requirements.txt   
```

### Install the AWS local services emulation:

'''
cd <project folder>
pip3 install robo3
git clone https://github.com/localstack/localstack
cd localstack
make install
'''

# Running everythong

## Run the local services:

 - Open a terminal
 - `cd <project folder>`
 - `. venv/bin/activate`
 - `./start_localstack`

## Deploy the stack

Notes:
 - You will need to perform this everytime you run the local services, as the open-sourced/free version of localstack forget everything when you turn it off.

 - Make sure you run the local services (previous states)
 - `cd <project folder>/infrastrcture`
 - `. venv/bin/activate`
 - `cd Infrastrcture`
 - `./create_and_deploy_stack`    # Behold the power of the CDK: this single command will deploy all your services !
 - `populate_users_table`         # Since we just deployed a fresh instance of DynamoDB, we need test-p. opulation
 - `. set_stack_env_vars`         # This optional step will set some env vars usefull for other scripts

## Modify the stack
  
  The stack is a definition of all the AWS enteties your project uses.
  If you need to add or change those resources, you will need to edit the file `<project folder>/infrastrcture/cdk_stack/stack.py.
  Then run the procedure "Deploy the stack"

TBD: Lambda update process

TBD: utility functions

debug_lambda_in_loop
show_localstack_lambdas
show_localstack_status
show_restApi_resouces
start_localstack
test
update_lambdas

 
# Updating localstack (do this once in a blue moon)

```
cd localstack
. .venv/bin/activate
git pull
make install
```

## Licenses
This project is under the MIT license

This project relays heavily on the following components:
   - localstack, which has the "Apache License, Version 2.0" license
   - CDK, which also has the "Apache License, Version 2.0" license

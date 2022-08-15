# AWS stand-alone Linux-based development template

A Python-based demonstration of integrating localstack (which allows development w/o AWS account or related expenses) and CDK (AWS's great Infrastructure-as-code project).

This demo deploys a functional serverless backend, which is composed of Lambdas, DynamoDB and REST-API-gateway.

I have made a couple of unconventional choices, which are explained bellow.
Also, a great effort was done to document the installation process, choices and alternatives.

## Overview

This repository contains the instructions for setup, starting from a clean 20.04 Ubuntu, of a Python-based backend project.

This template uses 3 AWS services:

- REST API gateway: with IP white-list and the API defined, so the gateway can reject non-well-formed URLs
- DynamoDB: defined w/two sample tables at the CDK/stack level
- A single lambda that lists the users in the users table

The technologies demonstrated here are:

- Well documented installation procedure, using Python Virtual Environment(s) for most of the packages
- 100 percent local development, by using the wonderful 'localstack' project
- 'single click' infrastructure deployment, using AWS's CDK project

I love Python. Therefore, almost all this project uses Python:

- The stack is defined using Python (at infrastructure/cdk_template/stack.py)
- The sample lambda (at lambda_functions/handle_url_lambda.py) 
- Most of the scripts used to 'operate' this project (some are bash)

## Design Choices

### CDK:

- I have chosen the use only the "synth" (I.e., generate Cloud-Formation template) feature of the CDK, as opposed to the full 'deploy' functionality. This enables a more detailed control and insight of the deployment process.
  You may prefer using the CDK-deploy - it will make your life much simpler.

- Lambdas are deployed by reading the code and including the code as part of the stack.
  This will break once the Lambda is above a certain size.  TBD to improve.

### Localstack

- localstack is used directly on the host (as opposed to the normal way of running localstack in a Docker container). I just feel it make operating the system easier, but there is a price to pay in the installation !

### Installation and Environment

- Some of the packages are installed locally, because those packages are typically used many times and are relatively big. So, it seems a waste of time and disk space to install the per-project.

- Currently, there are two distinct virtual environments: one dedicated to localstack and the other for CDK and everything else.  This is 'just happened' and might be fixed in later releases.

- The cutting-edge versions of the packages, as offered by pip and GitHub, are used. This works well for me, but might cause issues in the future. The common practice is use specific versions, and you might choose this.

## Installation

This project was developed and tested on Xubuntu 22.04, but will probably work on any recent Ubuntu or Debian.

By necessity, we are using 3 different installation methods: using Ubuntu's native `apt`, using Python's native `pip3` and using nodejs/npm (which is required to install the CDK software).

Note: Perform all the 'global' installation only one time on your new Linux machine.
Note: The project is called "match_to_the_weight" and is abbreviated to 'mttw' or 'MttW'.
      You will probably want to replace those with your own project name :-)

### Globally install the Localstack dependencies:

```
sudo apt install -y zip unzip
sudo apt install -y awscli
sudo apt install -y python3-pip python3-venv
sudo apt install -y python3-dev libsasl2-dev gcc
sudo apt install -y openjdk-11-jdk
```

### Globally install the CDK dependencies (nodejs and npm):

```
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs
```

### Globally install the CDK toolkit:

`sudo npm install -g aws-cdk`

### Configure AWS profile

In order to use localstack, we need an AWS profile configured.
If you already have a profile defined, localhost will work fine with the existing definition.
If you do not have a profile defined, the below commands will create a new profile:

```
aws configure set aws_access_key_id dummyKey
aws configure set aws_secret_access_key dummaySecret
aws configure set region us-east-1
aws configure set output json
```

Note: when/if you start working w/the 'real' AWS, you will need to re-run the above with new values. Localstack will work correctly with the new values, as it does not care about the actual values present.

### Create the project dir and the Python virtual env

The remaining installations will be local (I.e., using virtual environment)
You may rename the top folder to reflect the name of your project.
This folder will be referred to in the rest of this document as the <project folder>

### Create the Python virtual environment

```
cd <project folder>
python3 -m venv venv
. venv/bin/activate
```

### Install the CDK Python lib:

```
cd <project folder>
. venv/bin/activate
cd infrastructure
pip3 install -r requirements.txt   
```

### Install the AWS local services emulation:

'''
cd <project folder>
pip3 install boto3
git clone https://github.com/localstack/localstack
cd localstack
make install
'''

## Testing and troubleshooting the installation

### Testing CDK

```
cd <project folder>
. venv/bin/activate
cd infrastructure/cdk_template
cdk synth
```

Running `cdk synth` should emit to the screen the template (which is a JSON string)

### Testing localstack

```
cd <project folder>
./start_localstack
```

You should see many messages, but no error messages.

## Running everything 

The below procedure will run all the various components

### Run the localstack service:

- Open a new terminal
- `cd <project folder>`
- `./start_localstack

### Deploy the stack

You will need to perform this every time you run the local services, as the open-sourced/free version of localstack forget everything when you turn it off.

- Make sure you run the localstack service (previous step)
- Deploy the stack:

```
cd <project folder>`
. venv/bin/activate`
cd infrastructure`
./create_and_deploy_stack`    # Behold the power of the CDK: this single command will deploy all your services !
```

  Answer 'y' to use localstack    # As opposed to using the 'real' AWS

- IMPORTANT: set the needed env. variables:

  ```
  cd ..
  . set_stack_env_vars
  ```

- Optional: Fill the 'users' table with test data

`./populate_users_table`       

### End-to-end test: Run the backend

- Open a terminal
- cd <project folder>
- Run: `. venv/bin/activate`
- `. set_stack_env_vars`         # This optional step will set some env vars useful for other scripts
- Run `./test`

## Modify the stack

  The stack is a definition of all the AWS entities your project uses.
  If you need to add or change those resources, you will need to edit the file `<project folder>/infrastructure/cdk_stack/stack.py`.
  Then run the procedure "Deploy the stack" above

## Lambda update process

  It is assumed that you will spend most of your time iterating on the lambda function(s).
  And this is where this setup shines: since everything is local, this process is much quicker then when using the 'real' AWS.

  The procedure is:
 
  - Perform the procedure "Running everything" above 
  - Run: `debug_lambda`
    This script will let you edit the lambda function, then deploy the modified lambda, then run the `test` script.
    How neat is this ?


## Utility scripts 

### show_localstack_lambdas

Will list all the deployed lambdas

### debug_lambda

The most usefull script when itterating on a Lambda's source code.

This script will vi a Lambda, then deploy the modified code, then run the 'test' script to trigger the Lambda. Rince and repeate.

### show_localstack_status

A script to show which AWS-services are running or avialable by the running localstack instance

show_restApi_resources
start_localstack
test
update_lambdas

## Using in "real AWS" environment (I.e., w/o localstack)

  Of course we want to move to working in the 'real' AWS environment after the heavy development stage is done.

  The only thing you need to do differently is to NOT enter 'y' when you run `./create_and_deploy_stack`


## Updating localstack (do this once in a blue moon)

```
cd localstack
. .venv/bin/activate
git pull
make install
```

## Licenses

This project is under the MIT license

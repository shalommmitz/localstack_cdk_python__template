# AWS Standalone Linux-based Development Template

Using this repository, you will run a fully local, free, AWS development environment. It is meant to be used as a starting point for your own project. Python is used where possible.

The repository contains a Python-heavy cookbook, integrating localstack (which allows development without an AWS account or related expenses) and CDK (AWS's great Infrastructure-as-code project).

As is, this repository contains a working demo of a functional serverless backend, which is composed of the following:

- REST-API-gateway: an HTTP server that accepts URLs. 

- Lambda: a serverless piece of code that process the URLs. 
 The Lambda function is triggered by the gateway.

- A single DynamoDB table, which is accessed by the Lambda.

I have made a couple of unconventional design choices, which are explained in the "Design Choices" section, below.
Furthermore, I took pains to document the installation process, choices and alternatives.

## Overview

This repository contains detailed setup instructions, starting from a clean 20.04 or 22.04 Ubuntu server or Desktop installation.

This template uses a few AWS services:

- REST API gateway: Here used with an IP white list and the API calls defined, so that the gateway can reject non-well-formed URLs and traffic from unwanted IPs.
- DynamoDB: Defined with two sample tables at the CDK/stack level.
- Lambda: A single Lambda is present. It lists the users in the users table.
- CDK and Cloud-Formation: Used to deploy the above resources in a single step.

The technologies demonstrated here are:

- Usage of Python Virtual Environment(s) for most of the packages.
- Optional installation of all the globally installed packages automatically using Ansible.
- 100% local development using the 'localstack' project.
- 'Single-click' infrastructure deployment using AWS's CDK project.

This project uses Python wherever possible:

- The stack is defined using Python (in the file infrastructure/cdk_template/stack.py).
- The sample Lambda (at lambda_functions/handle_url_lambda.py). 
- Most of the scripts used to 'operate' this project were written in Python (although some are bash).

## Design Choices

### CDK:

- Only a part of the normal CDK deployment process is used. Specifically, I have chosen to only use the "synth" (i.e., generate Cloud-Formation template) feature of the CDK. This enables a more detailed control of and insight into the deployment process.
 You may prefer to use CDK-deploy. It will make your life much simpler.

- Lambdas are deployed by reading the code and including the code as part of the stack.
 This will break once the Lambda is above a certain size. Improvements are TBD.

### Localstack

- Localstack is used directly on the host (as opposed to the normal way of running localstack in a Docker container). I feel it makes operating the system easier, but there is a price to pay during installation.

### Installation and Environment

- Some of the packages are installed globally, thus requiring root permissions. As those packages are typically used by more than one project and are relatively big, it is wasteful to install those per-project.

- Localstack has its own virtual environment. Don't worry about this. 

- The cutting-edge versions of the packages, as offered by pip and GitHub, are used. This works well for me, but might cause issues in the future. The common practice is to use specific versions, and you might prefer to do this.

## Installation

This repository was tested on Ubuntu 20.04 and 22.04. It will probably work on any recent Ubuntu or Debian installation. Please do NOT use Ubuntu 18.04 or earlier - it will not work.

By necessity, we are using three different installation methods: Ubuntu's native `apt`, Python's native `pip3` and nodejs/npm (which is required to install the CDK software).

Notes: 

- You might want to change the top folder name (currently: `cdk_python_localstack_template`) to your own project’s name.

- You need to perform all the 'global' installations only once. 

- You may perform all the global installations automatically by running 
  
  `cd ansible; ./INSTALL`
  
  This will globally install the Localstack dependencies, nodejs and the CDK.
  
 You will need to type your user password twice: once to install Ansible and then to allow Ansible to perform the global installation. 

If you choose to install using Ansible, as explained above, jump to the step "Configure AWS profile"

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

In order to use localstack, you need a configured AWS profile.
If you already have a profile defined, localstack will work fine with the existing definition.
If you do not have a profile defined, the following commands will create a new profile:

**Do not execute the following commands if you already have AWS credentials configured.**

```
aws configure set aws_access_key_id dummyKey
aws configure set aws_secret_access_key dummaySecret
aws configure set region us-east-1
aws configure set output json
```

Note: If or when you start working with the 'real' AWS, you will need to re-run the above with valid values. Localstack will continue to work, as it ignores the actual values present.

### Local Installations

The remaining installations will be local to the project folder. This means that you can, if you so choose, delete the whole folder and start anew. 

### Renaming the Project Folder

Optionally, rename the top folder to reflect the name of your project.
This folder will be referred to in the rest of this document as the <project folder>.

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

### Install localstack

Localstack is  the AWS local services emulation.

```
cd <project folder>
pip3 install boto3
git clone https://github.com/localstack/localstack
cd localstack
make install
```



## Sanity testing and troubleshooting the installation

### Testing the  CDK

```
cd <project folder>
. venv/bin/activate
cd infrastructure/cdk_template
cdk synth
```

Running `cdk synth` should emit the template to the screen as a JSON string.

If there are issues:

- Did you activate the virtual environment ?
- Did you change the `stack.py` file ?

### Testing the localstack

```
cd <project folder>
./start_localstack
```

You should see many messages, but no error messages.

On the first run, please wait a few minutes until you see the message "Ready".

You will only need to wait on the first run while some adds-on are being downloaded.

## Running everything

The following procedure will run all the various components.

### Run the localstack service:

- Open a new terminal
- `cd <project folder>`
- `./start_localstack

### Deploy the stack

You will need to re-deploy the stack every time you run the localstack services, as the open-source/free version of localstack forgets everything when you turn it off.

- Make sure the localstack service is running (previous step).
- Deploy the stack:

```
cd <project folder>`
. venv/bin/activate`
cd infrastructure`
./create_and_deploy_stack`    # Behold the power of the CDK: this single command will deploy all your services!
```

  Answer 'y' to use localstack    # As opposed to using the 'real' AWS

- IMPORTANT: set the needed env. variables:
  
  ```
  . set_stack_env_vars
  ```

- Optional: Populate the 'users' table with test data.

`./populate_users_table`       

### End-to-end test: Run the backend

- Open a terminal
- cd <project folder>
- Run: `. venv/bin/activate`
- `. set_stack_env_vars`         # This optional step will set some env vars useful for other scripts
- Run `./test`

## Modifying the stack

  The stack is a definition of all the AWS entities your project uses.
 If you need to add or change those resources, you will need to edit the `<project folder>/infrastructure/cdk_stack/stack.py` file, then run the "Deploy the stack" procedure, above.

## Lambda update process

 You will probably spend most of your time iterating on the Lambda function(s).
 This is where this setup shines: since everything is local, this process is much quicker compared to using the 'real' AWS.

  The procedure is:

- Perform the "Running everything" procedure, above.
- Run: `debug_lambda`
 This script will let you edit the Lambda function, then deploy the modified Lambda, then run the `test` script.


## Utility scripts

### show_localstack_lambdas

Will list all the deployed Lambdas.

### debug_lambda

The most useful script when iterating on a Lambda's source code.

This script will vi a Lambda, then deploy the modified code, then run the 'test' script to trigger the Lambda. Rinse and repeat.

### update_lambdas

This script uploads the current code of the Lambda (present at the folder lambda_functions) to AWS.
This script is called by the 'debug_lambda' script.

### show_localstack_status

This script shows which AWS services are running or available by the running localstack instance.

### show_restApi_resources

This script shows the available REST API paths.

### start_localstack

This script starts the localstack. You will normally execute this script as the first action.

### test

End-to-end example test: sends a URL to the gateway, which runs the Lambda, which accesses the DynamoDB database and returns the result. 

## Using in "real AWS" environment (i.e., without localstack)

  Eventually, you will want to start working in the 'real' AWS environment.
  This is typical done when the heavy development is done.

  The only thing you need to do differently is to enter "r" (for 'real')  when running `./create_and_deploy_stack`

## Updating localstack

It is recommended to do this once in a while, in order to get the most-recent improvements in localstack.

```
cd localstack
. .venv/bin/activate
git pull
make install
```

## Acknowledgments

The work here is 'standing on the shoulders of giants': localstack and CDK.
Also, thanks to Dor Mitz and Devra Ariel for editing of the readme file.

## Licenses

This project is under the MIT license.


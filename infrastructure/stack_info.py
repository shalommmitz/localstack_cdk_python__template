#!/usr/bin/env python3

import boto3
import os

class StackInfo(object):
   def __init__(self, use_localstack=False):
       if use_localstack:
           self.client = boto3.client('cloudformation', endpoint_url="http://localhost:4566")
           self.resource = boto3.resource('cloudformation', endpoint_url="http://localhost:4566")
       else:
           self.client = boto3.client('cloudformation')
           self.resource = boto3.resource('cloudformation')
   def get_num_stacks(self):
       self.connection_success_msg = ""
       num_stacks = 0
       try:
           for stack in self.resource.stacks.all():
               num_stacks += 1
       except:
           msg = "ERROR: could not connect to AWS. Maybe localstack is not running ?"
           self.connection_success_msg = msg
       return num_stacks

   def get_stack_outputs(self, stack_name):
       try:
           stack_details = self.client.describe_stacks(StackName=stack_name)["Stacks"][0]
           return stack_details['Outputs']
       except:
           print("Could not find a stack named", stack_name)
           return None    
   def get_stack_status(self, stack_name):
       try:
           stack_details = self.client.describe_stacks(StackName=stack_name)["Stacks"][0]
           return stack_details['StackStatus']
       except:
           print("Could not find a stack named", stack_name)
           return None    

if __name__=="__main__":
    use_localstack = False
    if "USE_LOCALSTACK" in os.environ.keys():
        if os.environ["USE_LOCALSTACK"].lower()=="true":
            use_localstack = True

    si = StackInfo(use_localstack)
    print("Number of stacks: ", si.get_num_stacks())
    print("Status of stack 'test1':", si.get_stack_status('test1'))


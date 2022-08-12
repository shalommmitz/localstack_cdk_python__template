#!/usr/bin/env python3

import boto3
import os

class StackInfo(object):
   def __init__(self, use_localstack=False):
       #boto3.setup_default_session(profile_name='localstack')
       #self.client = boto3.client('cloudformation',region_name='us-east-1', endpoint_url="http://localhost:4566")
       #self.resource = boto3.resource('cloudformation',region_name='us-east-1', endpoint_url="http://localhost:4566")
       if use_localstack:
           self.client = boto3.client('cloudformation', endpoint_url="http://localhost:4566")
           self.resource = boto3.resource('cloudformation', endpoint_url="http://localhost:4566")
       else:
           self.client = boto3.client('cloudformation')
           self.resource = boto3.resource('cloudformation')
       self.stacks = []
       for stack in self.resource.stacks.all():
           self.stacks.append(stack.name)
       if len(self.stacks)!=1:
           print("Expecting exactly one stack - which is not the case - Aborting")
           exit()
       self.stack_name = self.stacks[0]
       self.stack_details = self.client.describe_stacks(StackName=self.stack_name)["Stacks"][0]
       self.stack_resources = self.client.list_stack_resources(StackName=self.stack_name)
       self.stack_events = self.client.describe_stack_events(StackName=self.stack_name)["StackEvents"]
   def get_stack_status(self):
       self.stack_details = self.client.describe_stacks(StackName=self.stack_name)["Stacks"][0]
       self.stack_status = self.stack_details['StackStatus']
       return self.stack_status

if __name__=="__main__":
    use_localstack = False
    if "USE_LOCALSTACK" in os.environ():
        use_localstack = bool(os.environ["USE_LOCALSTACK"])
    si = StackInfo(use_localstack)
    print("Found the following stacks: ", si.stacks)

    status_to_not_print = ["UPDATE_COMPLETE", "CREATE_COMPLETE", "UPDATE_IN_PROGRESS"]

    print("\nResources info:")
    for r in si.stack_resources["StackResourceSummaries"]:
        id = r["LogicalResourceId"]
        status = r["ResourceStatus"]
        if status in status_to_not_print:
           continue
        print("   ", id, status)

    print("\nStack events:")
    for event in si.stack_events:
        id = event['LogicalResourceId']
        status = event["ResourceStatus"]
        type = event['ResourceType']
        if status in status_to_not_print:
            continue
        print("   ", id, type, status)
        if "ResourceStatusReason" in event.keys():
            print("      ", event["ResourceStatusReason"])

    print("\nStack status:")
    print("   ", si.get_stack_status)

    print("\nStack outputs:")
    for output in si.stack_details['Outputs']:
        print("   ", output['OutputKey'], output['OutputValue'])


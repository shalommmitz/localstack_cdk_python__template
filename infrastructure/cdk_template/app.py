#!/usr/bin/env python3

import aws_cdk as cdk

#from cdk_template.cdk_template_stack import CdkTemplateStack
from stack import CdkTemplateStack

app = cdk.App()
CdkTemplateStack(app, "cdk-template")

app.synth()

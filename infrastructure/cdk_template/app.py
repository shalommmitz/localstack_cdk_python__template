#!/usr/bin/env python3

import aws_cdk as cdk

from stack import CdkTemplateStack

app = cdk.App()
CdkTemplateStack(app, "cdk-template")
app.synth()

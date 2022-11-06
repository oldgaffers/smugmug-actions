#!/usr/bin/env python3
import os

from aws_cdk import (
    App,
    Environment,
    Stack
)
from aws_cdk.cloudformation_include import CfnInclude

env = Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))

stack_name = 'smugmug-create-album'
app = App()
stack = Stack(app, 'wrapper-stack', env=env, stack_name=stack_name)
CfnInclude(stack, 'included-template', template_file=os.path.join(os.getcwd(), 'cfn', 'smugmug-create-album.yaml'))
app.synth()

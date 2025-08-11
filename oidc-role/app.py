#!/usr/bin/env python3

import aws_cdk as cdk
import os
from oidc_role.oidc_role_stack import OidcRoleStack

synth = cdk.DefaultStackSynthesizer(
    qualifier="naats",
    file_assets_bucket_name="naats-bootstrap-bucket",
    image_assets_repository_name="naats-image-assets-repo",
)

app = cdk.App()
OidcRoleStack(app, "OidcRoleStack",
    synthesizer=synth,
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
    role_name='github-actions-oidc-deploy-role',
    github_org='nadeleke',
    github_repo='naats*',
    github_branch='*',
)

app.synth()

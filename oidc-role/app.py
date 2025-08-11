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
    synthesizer=synth, # Remove this if your CDK deployments don't need a synthesizer. i.e. your cdk bootstrap did not involve any specifications
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
    role_name='github-actions-oidc-deploy-role', # Change this to whatever oidc role name you wish
    github_org='nadeleke', # Change this to the appropriate github org
    github_repo='naats*', # Keep this '*' unless you wish to restrict the use of the OIDC to a specific repo or pattern
    github_branch='*', # Keep this '*' unless you wish to restrict the use of the OIDC to a specific branch or pattern
)

app.synth()

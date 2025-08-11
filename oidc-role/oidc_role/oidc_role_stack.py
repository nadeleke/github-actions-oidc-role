from pydoc import describe
from constructs import Construct
from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    aws_iam as iam,
)

class OidcRoleStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, *,
        github_org: str,
        github_repo: str,
        github_branch: str = '*',
        role_name: str = 'github-actions-deploy-role',
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # OIDC provider ARN (pre-created by AWS when first used)
        oidc_provider_arn = f"arn:aws:iam::{self.account}:oidc-provider/token.actions.githubusercontent.com"

        # Trust policy for GitHub Actions OIDC
        github_oidc_principal = iam.OpenIdConnectPrincipal(
            iam.OpenIdConnectProvider.from_open_id_connect_provider_arn(
                self, "GitHubOIDCProvider", oidc_provider_arn
            )
        ).with_conditions({
            "StringEquals": {
                "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                # "token.actions.githubusercontent.com:sub": f"repo:{github_org}/{github_repo}:*"
                "token.actions.githubusercontent.com:sub": f"repo:{github_org}/{github_repo}:{github_branch}"
            }
        })

        # IAM role for GitHub Actions deployments
        deployment_role = iam.Role(
            self,
            "GitHubOIDCDeploymentRole",
            role_name=role_name,
            assumed_by=github_oidc_principal,
            description="Role assumed by GitHub Actions via OIDC for deployments",
            max_session_duration=Duration.hours(1)
        )

        # Example policy: Full access to CloudFormation + S3 (adjust as needed)
        deployment_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
        )

        # Output role ARN
        CfnOutput(self, "DeploymentRoleArn", value=deployment_role.role_arn, description="OIDC Role Arn")
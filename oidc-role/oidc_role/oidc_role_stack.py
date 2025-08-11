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

        # Create the OIDC provider for GitHub Actions
        github_oidc_provider = iam.CfnOIDCProvider(
            self,
            "GitHubOIDCProvider",
            url="https://token.actions.githubusercontent.com",
            client_id_list=["sts.amazonaws.com"],
            thumbprint_list=["6938fd4d98bab03faadb97b34396831e3780aea1"]
        )

        # Now you can refer to this OIDC provider's ARN:
        oidc_provider_arn = github_oidc_provider.attr_arn

        # Trust policy for GitHub Actions OIDC principal
        github_oidc_principal = iam.OpenIdConnectPrincipal(
            iam.OpenIdConnectProvider.from_open_id_connect_provider_arn(
                self, "GitHubOIDCProviderReference", oidc_provider_arn
            )
        ).with_conditions({
            "StringEquals": {
                "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
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

        deployment_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
        )

        CfnOutput(self, "DeploymentRoleArn", value=deployment_role.role_arn, description="OIDC Role Arn")
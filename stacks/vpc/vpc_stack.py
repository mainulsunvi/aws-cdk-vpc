from aws_cdk import (
    aws_ec2 as ec2,
    Stack,
    CfnOutput,
)
from constructs import Construct

class VpcStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            self,
            "cdk-vpc",
            availability_zones=["us-east-1a", "us-east-1b", "us-east-1c"],
            ip_addresses=ec2.IpAddresses.cidr("10.100.0.0/16"),
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public-",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=28,
                ),
                ec2.SubnetConfiguration(
                    name="private-",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=28,
                ),
            ],
        )

        CfnOutput(self, "VpcId", value=vpc.vpc_id, description="VPC ID")
        CfnOutput(
            self,
            "PublicSubnets",
            value=", ".join([subnet.subnet_id for subnet in vpc.public_subnets]),
            description="Public Subnet IDs",
        )
        CfnOutput(
            self,
            "PrivateSubnets",
            value=", ".join([subnet.subnet_id for subnet in vpc.private_subnets]),
            description="Private Subnet IDs",
        )

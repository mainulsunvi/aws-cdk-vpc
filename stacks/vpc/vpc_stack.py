from aws_cdk import (
    aws_ec2 as ec2,
    Stack,
    CfnOutput,
)
from constructs import Construct


class VpcStack(Stack):
    ingress_rules = [
        [ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "Allow SSH from anywhere"],
        [ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP from anywhere"],
    ]

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = self.create_vpc()
        self.public_route_table = self.create_public_route_table()
        self.public_routes = self.create_public_routes()
        self.private_route_table = self.create_private_route_table()
        self.public_host_security_group = self.create_public_host_security_group()

    def create_vpc(self):
        return ec2.Vpc(
            self,
            "cdk-vpc",
            availability_zones=["us-east-1a", "us-east-1b", "us-east-1c"],
            ip_addresses=ec2.IpAddresses.cidr("10.100.0.0/16"),
            nat_gateways=0,
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

    def create_public_route_table(self):
        public_table = ec2.CfnRouteTable(
            self, "cdk-public-route", vpc_id=self.vpc.vpc_id, tags=[{"key": "Name", "value": "Public-route-table"}]
        )
        for subnet in self.vpc.public_subnets:
            ec2.CfnSubnetRouteTableAssociation(
                self,
                f"cdk-public-subnet-{subnet.availability_zone}",
                route_table_id=public_table.ref,
                subnet_id=subnet.subnet_id,
            )

        return public_table

    def create_public_routes(self):
        ec2.CfnRoute(
            self,
            "PublicRoute",
            route_table_id=self.public_route_table.ref,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=self.vpc.internet_gateway_id,
        )

    def create_private_route_table(self):
        private_route_table = ec2.CfnRouteTable(
            self,
            "cdk-private-route-table",
            vpc_id=self.vpc.vpc_id,
            tags=[{"key": "Name", "value": "Private-route-table"}],
        )

        for subnet in self.vpc.private_subnets:
            ec2.CfnSubnetRouteTableAssociation(
                self,
                f"cdk-private-subnet-{subnet.availability_zone}",
                route_table_id=private_route_table.ref,
                subnet_id=subnet.subnet_id,
            )

        return private_route_table

    def create_public_host_security_group(self):
        public_security_group = ec2.SecurityGroup(
            self,
            "cdk-public-hosts-sg",
            security_group_name="public-hosts-sg",
            vpc=self.vpc,
            allow_all_outbound=True,
            description="Security Group for Public Hosts",
        )

        for rule in self.ingress_rules:
            public_security_group.add_ingress_rule(rule[0], rule[1], rule[2])

        return public_security_group

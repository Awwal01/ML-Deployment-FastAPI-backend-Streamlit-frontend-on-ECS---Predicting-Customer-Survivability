from aws_cdk import (
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_ecs as ecs,
    aws_efs as efs,
    custom_resources as cr,
    App, CfnOutput, Duration, Stack,
    Environment,
    Fn,
)

import os

app = App()
stack = Stack(app, "sample-aws-ec2-integ-ecs", 
            env=Environment(
                account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
                region=os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"])
                )
        )

# Create a cluster
vpc = ec2.Vpc(
    stack, "MyVpc",
    max_azs=2,
    nat_gateways=0,
    # nat_gateway_provider=ec2.NatProvider.instance(
    #         instance_type=ec2.InstanceType('t2.micro')
            # ec2.InstanceType.of(
            #              ec2.InstanceClass.BURSTABLE2,
            #              ec2.InstanceSize.MICRO),
    #    )
)

# vpc = ec2.Vpc(
#     stack, "MyVpc",
#     max_azs=2,
#     # cidr="10.0.0.0/16",
#     # enable_dns_hostnames=True,
#     # enable_dns_support=True,
#     nat_gateways=0,
# )

cluster = ecs.Cluster(
    stack, 'EcsCluster',
    vpc=vpc
)
#cluster.cluster_name()

# user_data = ec2.UserData.for_linux()
# user_data.add_commands("#!/bin/bash", 
#                     f"echo ECS_CLUSTER={cluster.cluster_name} >> /etc/ecs/ecs.config;", 
#                     "echo ECS_BACKEND_HOST= >> /etc/ecs/ecs.config;")

ec2.SubnetType.PUBLIC
asg = autoscaling.AutoScalingGroup(
    stack, "DefaultAutoScalingGroup",
    instance_type=ec2.InstanceType.of(
                         ec2.InstanceClass.BURSTABLE2,
                         ec2.InstanceSize.MICRO),
    machine_image=ecs.EcsOptimizedImage.amazon_linux2(),
    vpc=vpc,
    min_capacity=0,
    max_capacity=1,
    # =Fn.base64(user_data.render())
    # user_data=user_data,
    vpc_subnets=ec2.SubnetSelection(
        subnet_type=ec2.SubnetType.PUBLIC
    ),
    
    # vpc_subnet=ec2.SubnetSelection(ec2.SubnetType.PUBLIC)
    # user_data=
)

capacity_provider = ecs.AsgCapacityProvider(stack, "AsgCapacityProvider",
    auto_scaling_group=asg
)

cluster.add_asg_capacity_provider(capacity_provider)

# Create Task Definition

task_definition = ecs.Ec2TaskDefinition(
    stack, "TaskDef")

container = task_definition.add_container(
    "web",
    image=ecs.ContainerImage.from_registry('public.ecr.aws/f3w1s8w6/titan_be:latest'), # ("amazon/amazon-ecs-sample"),
    memory_limit_mib=650 # 256
)

port_mapping = ecs.PortMapping(
    container_port=8000,
    # container_port=80,
    host_port=0,
    protocol=ecs.Protocol.TCP
)

container.add_port_mappings(port_mapping)

capacity_provider_strategy = ecs.CapacityProviderStrategy(
    capacity_provider=capacity_provider.capacity_provider_name, # "capacityProvider",

    # the properties below are optional
    base=0,
    weight=1,
)
# capacity_provider.capacity_provider_name()

# Create Service
service = ecs.Ec2Service(
    stack, "Service",
    cluster=cluster,
    task_definition=task_definition,
    capacity_provider_strategies=[capacity_provider_strategy],
)


# Create ALB
lb = elbv2.ApplicationLoadBalancer(
    stack, "LB",
    vpc=vpc,
    internet_facing=True
)

listener = lb.add_listener(
    "PublicListener",
    port=80,
    open=True
)

asg.connections.allow_from(lb, port_range=ec2.Port.tcp_range(32768, 65535), description="allow incoming traffic from ALB")

health_check = elbv2.HealthCheck(
    interval=Duration.seconds(60),
    path="/health",
    timeout=Duration.seconds(5)
)

# Attach ALB to ECS Service
listener.add_targets(
    "ECS",
    port=80,
    targets=[service],
    health_check=health_check,
)

CfnOutput(
    stack, "LoadBalancerDNS",
    value="http://"+lb.load_balancer_dns_name
)

app.synth()
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
stack = Stack(app, "fe-sample-aws-ec2-integ-ecs", 
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



cluster = ecs.Cluster(
    stack, 'EcsCluster',
    vpc=vpc
)
#cluster.cluster_name()



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

asg.connections.allow_from_any_ipv4(
                port_range=ec2.Port.tcp_range(8501, 8501), description='fe container sec what ever')

capacity_provider = ecs.AsgCapacityProvider(stack, "AsgCapacityProvider",
    auto_scaling_group=asg
)

cluster.add_asg_capacity_provider(capacity_provider)

# Create Task Definition

task_definition = ecs.Ec2TaskDefinition(
    stack, "TaskDef")

container = task_definition.add_container(
    "web",
    image=ecs.ContainerImage.from_registry('public.ecr.aws/f3w1s8w6/titan_fe:latest'), # ("amazon/amazon-ecs-sample"),
    memory_limit_mib=650 # 256
)

port_mapping = ecs.PortMapping(
    container_port=8501,
    # container_port=80,
    host_port=8501,
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




app.synth()
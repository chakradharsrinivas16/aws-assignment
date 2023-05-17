
import boto3

# Specify the region where you want to launch the instance
region = 'us-east-1'

# Specify the AMI ID of the Amazon Linux 2 AMI
ami_id = 'ami-0889a44b331db0194'

# Specify the instance type
instance_type = 't2.micro'

# Specify the security group IDs
security_group_ids = ['sg-066205334fd658af6']

# Specify the IAM role ARN
iam_role_arn = 'arn:aws:iam::618695728591:instance-profile/instance_profile'

# Create a client to interact with EC2 service
ec2_client = boto3.client('ec2', region_name=region)

# Launch the instance with the IAM role specified
response = ec2_client.run_instances(
    ImageId=ami_id,
    InstanceType=instance_type,
    SecurityGroupIds=security_group_ids,
    IamInstanceProfile={
        'Arn': iam_role_arn
    },
    MinCount=1,
    MaxCount=1
)

# Get the instance ID of the launched instance
instance_id = response['Instances'][0]['InstanceId']

# Print the instance ID
print('Launched instance with ID:', instance_id)


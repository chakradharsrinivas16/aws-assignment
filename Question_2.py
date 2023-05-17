import boto3
import json
from botocore.exceptions import ClientError



iam = boto3.client('iam')

#  Put files in S3 bucket from lambda
#  a. Create custom role for AWS lambda which will have only put object access

policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::chakradahars3/*"
            ]
        }
    ]
}

create_policy_response = iam.create_policy(
        PolicyName='chakradhar-put-object-policy',
        PolicyDocument=json.dumps(policy_document)
)

policy_arn = create_policy_response['Policy']['Arn']


role_name = 'chakradhar-put-object-lambda-role'
create_role_response = iam.create_role(
    RoleName=role_name,
    AssumeRolePolicyDocument=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    })
)

create_role_response = iam.attach_role_policy(
    RoleName=role_name,
    PolicyArn=policy_arn
)



#  b. Add role to generate and access Cloud watch logs

cloudwatch_logs_policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:GetLogEvents"
            ],
            "Resource": "*"
        }
    ]
}

cloudwatch_logs_policy_response = iam.create_policy(
    PolicyName='chakradharCloudWatchLogsPolicy',
    PolicyDocument=json.dumps(cloudwatch_logs_policy_document)
)

cloudwatch_logs_policy_arn = cloudwatch_logs_policy_response['Policy']['Arn']


iam.attach_role_policy(
    RoleName=role_name ,
    PolicyArn=cloudwatch_logs_policy_arn
)
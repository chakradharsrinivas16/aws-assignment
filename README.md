# Aws-assignment

## Question - 1
#### a. Create an IAM role with S3 full access
```
aws iam create-role --role-name chakradhar-q1  --assume-role-policy-document file://trustpolicy.json 
```
Here the trust policy json contains the following information

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```
<img width="1002" alt="Screenshot 2023-05-17 at 7 46 49 AM" src="https://github.com/chakradharsrinivas16/aws-assignment/assets/123494344/69b44d97-0bbf-4e68-9dc8-85ff29609203">

Providing the role with S3 full access

```
aws iam attach-role-policy --role-name chakradhar-q1 --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```
#### b.Create an EC2 instance with above role Creating an instance profile

```
aws iam create-instance-profile --instance-profile-name chakradhar_instance_profile_q1 
```

Attaching the role to the instance profile
```
aws iam add-role-to-instance-profile --instance-profile-name chakradhar_instance_profile_q1  --role-name chakradhar-q1
```
Running the instance

```

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


```
<img width="686" alt="Screenshot 2023-05-17 at 7 50 49 AM" src="https://github.com/chakradharsrinivas16/aws-assignment/assets/123494344/ec20bcd9-7e41-4889-9a68-1ebfb8c83e09">

#### c. Creating the bucket

```
aws s3api create-bucket --bucket chakradahars3 --region ap-south-1 --create-bucket-configuration LocationConstraint=ap-south-1 
```
<img width="1036" alt="Screenshot 2023-05-17 at 7 52 00 AM" src="https://github.com/chakradharsrinivas16/aws-assignment/assets/123494344/2f7809f4-07d8-4974-bf2c-c17e0ca81722">

## Question - 2
#### Put files in S3 bucket from lambda
#### Creating clients
```
import boto3
import json
from botocore.exceptions import ClientError
```
#### a.Create custom role for AWS lambda which will only have put object access Creating policy for put object access
```
iam = boto3.client('iam')

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
```
Attach the policy to the role

```
create_role_response = iam.attach_role_policy(
    RoleName=role_name,
    PolicyArn=policy_arn
)

```
####  b. Add role to generate and access Cloud watch logs

```


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

```
Attach the policy to the role

```
iam.attach_role_policy(
    RoleName=role_name ,
    PolicyArn=cloudwatch_logs_policy_arn
)
```
<img width="1061" alt="Screenshot 2023-05-17 at 7 57 35 AM" src="https://github.com/chakradharsrinivas16/aws-assignment/assets/123494344/d8503179-bf0b-4a01-941b-bc22f3af4932">


#### c. Create a new Lambda function using the above role
I had created a lambda function in which, written a python script in such a way that it generates json in given format and saves that file in the specified bucket.
<img width="1320" alt="Screenshot 2023-05-17 at 8 03 39 AM" src="https://github.com/chakradharsrinivas16/aws-assignment/assets/123494344/b332d5bd-c56b-406f-9d6e-75159b5c2871">
#### d. Schedule the job to run every minute. Stop execution after 3 runs
I had written a cloudwatch rule, in such a way that it runs only once per minute and had attached this rule to the written lambda function.
<img width="1182" alt="Screenshot 2023-05-17 at 8 06 57 AM" src="https://github.com/chakradharsrinivas16/aws-assignment/assets/123494344/0203ed7d-a54b-47e3-a652-0ceba100b1c7">
To stop exection after three runs I had initilized a counter variable in which we increases upon after every execution and once the count reaches three, the executions stops by setting its concurrency to 0.
The below is the lamba fuction which does the above said things.
```
import boto3
import datetime, time
import json

s3 = boto3.resource('s3')

bucket_name = 'chakradahars3'
key_name = 'transaction{}.json'

cw_logs = boto3.client('logs')
log_group = 'lambda_logs'
log_stream = 'lambda_stream'
counter=0
def set_concurrency_limit(function_name):
    lambda_client = boto3.client('lambda')
    response = lambda_client.put_function_concurrency(
        FunctionName=function_name,
        ReservedConcurrentExecutions=0
    )
    print(response)
def lambda_handler(event, context):
    global counter
    counter+=1
    try:
        # Generate JSON in the given format
        transaction_id = 12345
        payment_mode = "card/netbanking/upi"
        Amount = 200.0
        customer_id = 101
        Timestamp = str(datetime.datetime.now())
        transaction_data = {
            "transaction_id": transaction_id,
            "payment_mode": payment_mode,
            "Amount": Amount,
            "customer_id": customer_id,
            "Timestamp": Timestamp
        }
        
        # Save JSON file in S3 bucket
        json_data = json.dumps(transaction_data)
        file_name = key_name.format(Timestamp.replace(" ", "_"))
        s3.Bucket(bucket_name).Object(file_name).put(Body=json_data)
        
        # Log the S3 object creation event
        log_message = f"Object created in S3 bucket {bucket_name}: {file_name}"
        cw_logs.put_log_events(
            logGroupName=log_group,
            logStreamName=log_stream,
            logEvents=[{
                'timestamp': int(round(time.time() * 1000)),
                'message': log_message
            }]
        )
        
        # Stop execution after 3 runs
        print(context)
        if counter==1:
            print('First execution')
        elif counter==2:
            print('Second execution')
        elif counter==3:
            print('Third execution')
            print('Stopping execution')
            set_concurrency_limit('chakradharlambdafunction')
    except Exception as e:
        print(e)
```
#### e. Check if cloud watch logs are generated.
<img width="1217" alt="Screenshot 2023-05-17 at 8 11 14 AM" src="https://github.com/chakradharsrinivas16/aws-assignment/assets/123494344/b8323ef1-73f3-411f-bed2-b949dad16c14">

#### Question-3
#### API gateway - Lambda integration
#### a. Modify lambda function to accept parameters
The below is the fucntion which after modification accepts the parameters and returns the succes meesage and filename.
```
import boto3
import datetime
import json

s3 = boto3.resource('s3')
bucket_name = 'chakradahars3'
key_name = 'file{}.json'

def lambda_handler(event, context):
    try:
        # Parse input data
        body = event['body']
        timestamp = str(datetime.datetime.now())
        body["timestamp"] = timestamp
        
        # Save JSON file in S3 bucket
        json_data = json.dumps(body)
        file_name = key_name.format(timestamp.replace(" ", "_"))
        s3.Object(bucket_name, file_name).put(Body=json_data)

        # Log the S3 object creation event
        print(f"Object created in S3 bucket {bucket_name}: {file_name}")

        return {
            "file_name": file_name,
            "status": "success"
        }

    except Exception as e:
        print(e)
        return {
            "status": e
        }
```
#### b. Create a POST API from API Gateway, pass parameters as request body to Lambda job. Return the filename and status code as a response.
To create a post API to feed to lambda job these steps were followed

- Go to the API Gateway console and click "Create API".
- Select "REST API" and click "Build".
- Choose "New API" and enter a name for your API. Click "Create API".
- Click "Create Resource" to create a new resource under your API.
- Enter a name for your resource and click "Create Resource".
- Click "Create Method" and select "POST" from the dropdown.
- Select "Lambda Function" and check the "Use Lambda Proxy integration" box.
- Enter the name of your Lambda function in the "Lambda Function" field and click "Save".
- Go to integration request add mapping template "application/json". Put below code there.
    ```
    #set($inputRoot = $input.path('$'))
    {
        "body": $input.json('$')
    }
    ```
- Deploy your API by clicking "Actions" > "Deploy API". Select "New Stage" and enter a name for your stage. Click "Deploy".
- Note the URL of your API endpoint

<img width="1187" alt="Screenshot 2023-05-17 at 8 20 13 AM" src="https://github.com/chakradharsrinivas16/aws-assignment/assets/123494344/d61d0792-c8bd-4574-8ce8-ee4640378b7d">

<img width="1147" alt="Screenshot 2023-05-17 at 8 20 02 AM" src="https://github.com/chakradharsrinivas16/aws-assignment/assets/123494344/717b29de-26f2-4244-9b34-fdbec10b837a">

#### c. Consume API from the local machine and pass unique data to lambda.

To send the file using local machine i used curl and below command does the said job.

<img width="1030" alt="Screenshot 2023-05-17 at 8 25 02 AM" src="https://github.com/chakradharsrinivas16/aws-assignment/assets/123494344/2b216b24-c112-4ea4-865f-b1b028d47c66">

Verification whether the file were into bucket or not.
<img width="1087" alt="Screenshot 2023-05-17 at 8 25 32 AM" src="https://github.com/chakradharsrinivas16/aws-assignment/assets/123494344/513d9061-6353-4f2d-832d-d3c123cc1f58">




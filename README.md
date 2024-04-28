# aws-sagemaker-cost-optimization-app

## :brain: Amazon SageMaker Cost Optimization App Overview

This [SageMaker Cost Optimization Solution](aws-sagemaker-cost-optimization-app.py) solution streamlines the stopping of on-demand SageMaker resources such as Jupyter Notebooks, Studio apps (e.g. Data Wrangler Flows and Studio Notebooks), and Inference Model Endpoints and enforces best practices through automation.  The solution consists of a set of Python functions that can be run in CLI mode, referenced as part of a larger program or run as a standalone/scheduled Lambda function.  It is intended to be run in Development and Sandbox AWS environments where On-Demand resources should be stopped when they are not used.

![SageMaker Cost Optimization Solution Architecture](./assets/aws_sagemaker_cost_optimization_solution_architecture.png)

### Clone Git repo
git clone https://github.com/bishrtabbaa/aws-sagemaker-cost-optimization-app

### Use Git repo locally
```
cd aws-sagemaker-cost-optimization-app

[uses default credentials and default region in ~/.aws/credentials]
python3 aws-sagemaker-cost-optimization-app.py 

bishrt@3c06302c8f5b aws-sagemaker-cost-optimization-app % python3 aws-sagemaker-cost-optimization-app.py                   
Checking for active SageMaker Resources in region: None
Found credentials in shared credentials file: ~/.aws/credentials
No active SageMaker Studio apps to stop
{'NotebookInstanceName': 'MySageMakerWorkshopNotebook', 'NotebookInstanceArn': 'arn:aws:sagemaker:us-east-2:645411899653:notebook-instance/MySageMakerWorkshopNotebook', 'NotebookInstanceStatus': 'InService', 'Url': 'mysagemakerworkshopnotebook.notebook.us-east-2.sagemaker.aws', 'InstanceType': 'ml.t3.medium', 'CreationTime': datetime.datetime(2024, 4, 28, 11, 8, 1, 401000, tzinfo=tzlocal()), 'LastModifiedTime': datetime.datetime(2024, 4, 28, 11, 11, 53, 787000, tzinfo=tzlocal())}
Stopping arn:aws:sagemaker:us-east-2:645411899653:notebook-instance/MySageMakerWorkshopNotebook
{'EndpointName': 'DEMO-endpoint-2024-04-28-16-48-56', 'EndpointArn': 'arn:aws:sagemaker:us-east-2:645411899653:endpoint/DEMO-endpoint-2024-04-28-16-48-56', 'CreationTime': datetime.datetime(2024, 4, 28, 11, 48, 57, 382000, tzinfo=tzlocal()), 'LastModifiedTime': datetime.datetime(2024, 4, 28, 11, 52, 3, 387000, tzinfo=tzlocal()), 'EndpointStatus': 'InService'}
Stopping SageMaker Model Endpoints
Deleting SageMaker Model Endpoint: arn:aws:sagemaker:us-east-2:645411899653:endpoint/DEMO-endpoint-2024-04-28-16-48-56
Stopped SageMaker Resources: 2

[uses default credentials in ~/.aws/credentials and user-defined region parameter]
bishrt@3c06302c8f5b aws-sagemaker-cost-optimization-app % python3 aws-sagemaker-cost-optimization-app.py --region us-west-2
Checking for active SageMaker Resources in region: us-west-2
Found credentials in shared credentials file: ~/.aws/credentials
No active SageMaker Studio apps to stop
No active SageMaker Notebook instances to stop
No active SageMaker Model Endpoints to stop
Stopped SageMaker Resources: 0
```

### Deploy Serverless app to AWS as CloudFormation stack

Use deployment parameter values for the `region`, `IpamUsageThreshold`, `IpamSnsSubject`, and `IpamSnsTopic` that are appropriate for your environment and use case. It is likely that this solution will reside where you already setup IPAM for your AWS Organization in the management (parent) account.
```
aws cloudformation deploy --template-file aws-sagemaker-cost-optimization-app.yaml --stack-name AwsSageMakerCostOptimizationAppStack --capabilities CAPABILITY_NAMED_IAM --region us-east-2
```
# aws-sagemaker-cost-optimization-app

## :brain: Amazon SageMaker Cost Optimization App Overview

This [SageMaker Cost Optimization Solution](aws-sagemaker-cost-optimization-app.py) solution streamlines the stopping of on-demand SageMaker resources such as Jupyter Notebooks, Studio apps (e.g. Data Wrangler Flows and Studio Notebooks), and Inference Model Endpoints and enforces best practices through automation.  The solution consists of a set of Python functions that can be run in CLI mode, referenced as part of a larger program or run as a standalone/scheduled Lambda function.  It is intended to be run in Development and Sandbox AWS environments where On-Demand resources should be stopped when they are not used.

![SageMaker Cost Optimization Solution Architecture](./assets/aws_sagemaker_cost_optimization_solution_architecture.png)

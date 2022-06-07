"""
You must have an AWS account to use this Python code.
© 2022, Amazon Web Services, Inc. or its affiliates. All rights reserved.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# file: aws-sagemaker-cost-optimization-app.py
# author: bishrt@amazon.com
# date: 06-03-2022
# AWS CLI reference: https://awscli.amazonaws.com/v2/documentation/api/latest/reference/sagemaker/index.html#cli-aws-sagemaker
# AWS Boto3 SDK reference: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html
# Lambda Best Practices reference: https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html
# Lambda Developer reference: https://aws.amazon.com/blogs/architecture/best-practices-for-developing-on-aws-lambda/
# Lambda Python reference: https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html
# Lambda Python example https://github.com/awsdocs/aws-lambda-developer-guide/tree/main/sample-apps/blank-python
# SageMaker Frugal MLOps https://towardsaws.com/mlops-frugality-best-practices-for-managing-ml-costs-using-amazon-sagemaker-eaf35944417a
# SageMaker Cost Practices v1 https://aws.amazon.com/blogs/machine-learning/optimizing-costs-for-machine-learning-with-amazon-sagemaker/
# SageMaker Cost Practices v2 https://aws.amazon.com/blogs/machine-learning/ensure-efficient-compute-resources-on-amazon-sagemaker/ 
# Python reference: https://peps.python.org/pep-0008/
# requirements Python3.6+ (3.6-3.9)
# pip install --upgrade boto3

# IMPORTS
import boto3
import json
import os
import logging
import time
import sys
import traceback

# CONSTANTS
DEFAULT_PAGE_SIZE = 100
DEFAULT_SAGEMAKER_APP_TYPE_KERNEL = "KernelGateway"
DEFAULT_SAGEMAKER_STATUS_TYPE_ACTIVE = "InService"

# LOGGER
logger = logging.getLogger()
# logger.handler == console
csh = logging.StreamHandler()
logger.addHandler(csh)
# logger.level
logger.setLevel(logging.INFO)

# ASSUME current runtime context has appropriate networking connectivity and IAM permissions in AWS account

 # DOMAIN
def get_sagemaker_domains():

    # boto3
    sm = boto3.client("sagemaker")

    # log
    logger.debug('Getting SageMaker domains in region')

    smDomains = sm.list_domains()

    return smDomains

# NOTEBOOK INSTANCES
def get_sagemaker_notebook_instances():

    # boto3
    sm = boto3.client("sagemaker")

    # get SageMaker Notebook Instances
    logger.debug('Getting SageMaker Notebook Instances')

    smNotebookInstances = sm.list_notebook_instances(MaxResults=DEFAULT_PAGE_SIZE)

    return smNotebookInstances['NotebookInstances']

def filter_active_sagemaker_notebook_instances(smNotebookInstances):

    smActiveNotebookInstances = []

    if (smNotebookInstances != None):
        for smNotebookInstance in smNotebookInstances:
            if (smNotebookInstance['NotebookInstanceStatus'] == DEFAULT_SAGEMAKER_STATUS_TYPE_ACTIVE):
                smActiveNotebookInstances.append(smNotebookInstance)
    
    return smActiveNotebookInstances

def stop_sagemaker_notebook_instances(smNotebookInstances):
    nResourcesStopped = 0

    if (smNotebookInstances != None and len(smNotebookInstances) > 0):
        sm = boto3.client("sagemaker")

        for smNotebookInstance in smNotebookInstances:
            # check !Active
            if (smNotebookInstance['NotebookInstanceStatus'] == DEFAULT_SAGEMAKER_STATUS_TYPE_ACTIVE):
                logger.info("Stopping " + smNotebookInstance['NotebookInstanceArn'])
                response = sm.stop_notebook_instance(NotebookInstanceName=smNotebookInstance['NotebookInstanceName'])
                nResourcesStopped += 1
    else:
        logger.info("No active SageMaker Notebook instances to stop")

    return nResourcesStopped

# STUDIO APPS AND NOTEBOOKS
def get_sagemaker_studio_apps():

    # boto3
    sm = boto3.client("sagemaker")

    # get SageMaker Studio apps
    logger.debug('Getting SageMaker Studio Apps')

    smStudioAppResponse = sm.list_apps(MaxResults=DEFAULT_PAGE_SIZE)

    if (smStudioAppResponse != None):
        return smStudioAppResponse['Apps']
    else:
        return None
def filter_active_sagemaker_studio_apps(smStudioApps, smAppType=DEFAULT_SAGEMAKER_APP_TYPE_KERNEL):

    smActiveStudioApps = []

    logger.debug('Filtering active SageMaker Studio Apps')

    if (smStudioApps is not None):
        for smStudioApp in smStudioApps:
            if (smStudioApp['AppType'] == smAppType and smStudioApp['Status'] == DEFAULT_SAGEMAKER_STATUS_TYPE_ACTIVE):
                smActiveStudioApps.append(smStudioApp)

    if (smStudioApps == None or len(smStudioApps) == 0):
        logger.info("Could not find any active SageMaker Studio Apps")

    return smActiveStudioApps

def stop_sagemaker_studio_apps(smStudioApps):

    nResourcesStopped = 0

    if (smStudioApps != None and len(smStudioApps) > 0):
        sm = boto3.client("sagemaker")

        logger.info("Stopping SageMaker Studio Apps")
        for smStudioApp in smStudioApps:
            # check !Active
            if (smStudioApp['Status'] == DEFAULT_SAGEMAKER_STATUS_TYPE_ACTIVE):
                logger.info("Stopping " + smStudioApp['UserProfileName'] + '.' + smStudioApp['AppName'])
                response = sm.delete_app(DomainId=smStudioApp['DomainId'], UserProfileName=smStudioApp['UserProfileName'], AppType=smStudioApp['AppType'], AppName=smStudioApp['AppName'])
                nResourcesStopped += 1
            # else ignore
    else:
        logger.info("No active SageMaker Studio apps to stop")

    return nResourcesStopped
    
# MODEL ENDPOINTS
def get_sagemaker_model_endpoints():

    logger.debug('Getting SageMaker Model Inference Endpoints')

    # boto3

    sm = boto3.client("sagemaker")

    endpoints = sm.list_endpoints(MaxResults=DEFAULT_PAGE_SIZE)

    return endpoints['Endpoints']

def filter_active_sagemaker_model_endpoints(smModelEndpoints):
    smActiveModelEndpoints = []

    if (smModelEndpoints != None and len(smModelEndpoints) > 0):
        for smModelEndpoint in smModelEndpoints:
            if (smModelEndpoint['EndpointStatus'] == DEFAULT_SAGEMAKER_STATUS_TYPE_ACTIVE):
                smActiveModelEndpoints.append(smModelEndpoint)
    
    return smActiveModelEndpoints

def stop_sagemaker_model_endpoints(smModelEndpoints):
    nResourcesStopped = 0
    sm_model_endpoint_name = None

    sm = boto3.client("sagemaker")

    if (smModelEndpoints != None and len(smModelEndpoints) > 0):

        logger.info("Stopping SageMaker Model Endpoints")
               
        for smModelEndpoint in smModelEndpoints:
            if (smModelEndpoint['EndpointStatus'] == DEFAULT_SAGEMAKER_STATUS_TYPE_ACTIVE):
                logger.info('Deleting SageMaker Model Endpoint: ' + smModelEndpoint['EndpointArn'])
                try:
                    sm_model_endpoint_name = smModelEndpoint['EndpointName']
                    response = sm.delete_endpoint(EndpointName=smModelEndpoint['EndpointName'])
                    nResourcesStopped += 1
                except:
                    logger.error("Could not delete SageMaker Model Endpoint " + sm_model_endpoint_name)
                    # dump stack without exiting program 
                    traceback.print_exc()
    else:
        logger.info("No active SageMaker Model Endpoints to stop")
    
    return nResourcesStopped

def stop_sagemaker_resources(smStudioAppType=DEFAULT_SAGEMAKER_APP_TYPE_KERNEL, stopStudioApps=True, stopNotebookInstances=True, stopModelEndpoints=True):

    nResourcesStopped = 0

    # StudioApps.get-filter-stop
    if (stopStudioApps == True):
        mySageMakerStudioApps = get_sagemaker_studio_apps()
        myActiveSageMakerStudioApps = filter_active_sagemaker_studio_apps(mySageMakerStudioApps, smStudioAppType)
        log_list(myActiveSageMakerStudioApps)
        nResourcesStopped += stop_sagemaker_studio_apps(myActiveSageMakerStudioApps)

    # NotebookInstances.get-filter-stop
    if (stopNotebookInstances == True):
        mySageMakerNotebookInstances = get_sagemaker_notebook_instances()
        myActiveSageMakerNotebookInstances = filter_active_sagemaker_notebook_instances(mySageMakerNotebookInstances)
        log_list(myActiveSageMakerNotebookInstances)
        nResourcesStopped += stop_sagemaker_notebook_instances(myActiveSageMakerNotebookInstances)

    # SageMakerInferenceEndpoints.get-filter-stop
    if (stopModelEndpoints == True):
        mySageMakerModelEndpoints = get_sagemaker_model_endpoints()
        myActiveSageMakerModelEndpoints = filter_active_sagemaker_model_endpoints(mySageMakerModelEndpoints)
        log_list(myActiveSageMakerModelEndpoints)
        nResourcesStopped += stop_sagemaker_model_endpoints(myActiveSageMakerModelEndpoints)

    logger.info("Stopped SageMaker Resources: " + str(nResourcesStopped))

    return nResourcesStopped

# ENVIRONMENT VARIABLES 
# SAGEMAKER_STUDIO_APP_TYPE : 
# SAGEMAKER_MODEL_ENDPOINT_DELETE: True | False
# SAGEMAKER_STUDIO_APP_STOP: True | False
# SAGEMAKER_NOTEBOOK_INSTANCE_STOP: True | False
def lambda_handler(event, context):
    logger.debug('Getting OS environment variables.')

    envSageMakerStudioAppType = DEFAULT_SAGEMAKER_APP_TYPE_KERNEL    
    envStopSageMakerModelEndpoint = True
    envStopSageMakerStudioApp = True
    envStopSageMakerNotebookInstance = True

    # get OS environment variables ... and check-set with good defaults
    try:
        envSageMakerStudioAppType = os.environ['SAGEMAKER_STUDIO_APP_TYPE']
    except KeyError:
        logger.warn('Define Lambda Environment Variable: SAGEMAKER_STUDIO_APP_TYPE')

    try:
        envStopSageMakerModelEndpoint = bool(os.environ['SAGEMAKER_MODEL_ENDPOINT_STOP'])
    except KeyError:
        logger.warn('Define Lambda Environment Variable: SAGEMAKER_MODEL_ENDPOINT_STOP')

    try:
        envStopSageMakerStudioApp = bool(os.environ['SAGEMAKER_STUDIO_APP_STOP'])
    except KeyError:
        logger.warn('Define Lambda Environment Variable: SAGEMAKER_STUDIO_APP_STOP')

    try:
        envStopSageMakerNotebookInstance = bool(os.environ['SAGEMAKER_NOTEBOOK_INSTANCE_STOP'])
    except KeyError:
        logger.warn('Define Lambda Environment Variable: SAGEMAKER_NOTEBOOK_INSTANCE_STOP')

    nResourcesStopped = stop_sagemaker_resources(envSageMakerStudioAppType, envStopSageMakerStudioApp, envStopSageMakerNotebookInstance, envStopSageMakerModelEndpoint)

    return {
        "statusCode": 200,
        'body' : json.dumps('Stopped SageMaker Resources: ' + str(nResourcesStopped))
    }

def log_list(myList):
    for myItem in myList:
        logger.info(myItem)

##############################    
# CLI TEST
# main()
# python3 aws-sagemaker-cost-optimization-app.py --apptype KernelGateway
##############################  

if __name__ == '__main__':
    logger.setLevel(logging.INFO)

    mySageMakerAppType = DEFAULT_SAGEMAKER_APP_TYPE_KERNEL
    nResourcesStopped = 0

    args = sys.argv[1:]
    for i in range(1,len(args)):
        if (args[i] == "--apptype"):
            mySageMakerAppType = args[i+1]
        elif (args[i] == "--snstopic"):
            myIpamSnsTopic = args[i+1]
        elif (args[i] == "--snssubject"):
            myIpamSnsSubject = args[i+1]

    nResourcesStopped = stop_sagemaker_resources(mySageMakerAppType,True,True,True)

    # TODO .. training, tuning, processing, and batch transform jobs ... for now ignore them

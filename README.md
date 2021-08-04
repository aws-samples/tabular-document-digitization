# AWS Transactional Document Digitization

AWS workflow for digitizing transactional documents with Amazon Textract and a human-review loop with Amazon Augmented Artificial Intelligence (A2I). Deployed using CDK.

### Architecture

![Architecture Diagram](/docs/architecture-tdd.png)
### Basic Usage Workflow:

* Put a scanned tabular transactional PDF document in s3 at `s3://tdd-<git-branch>-store-resource-<account-number>-<region>/acquire/`
* This action triggers the `tdd-<git-branch>-state-pipeline` step function which will: 
  * Analyze the PDF document with Textract with table extraction 
  * Convert the textract table extractions to a simplified JSON format
  * Apply business rules to the simplified JSON format (currently a pass-through operation)
  * Send the PDF document and simplified JSON to A2I for human review of low-confidence values
  * Once human review is complete, convert output to a spreadsheet that has one sheet per table found in the original PDF document
* Monitor document status in DynamoDB in the `tdd-<git-branch>-table-pipeline` table
* Once your document has reached the `Status` `Augment#Waiting`, it's time to perform human review using the worker portal (descrbied below)
* After human review, find the final Excel spreadsheet in `s3://tdd-<git-branch>-store-resource-<account-number>-<region>/acquire/catalog`

### Human Review Annotation Interface

![Human Review Annotation Interface](/docs/tdd-annotation-ui.png)

This interface allows annotators to review all tables found in a scanned pdf document and perform the following actions:

* Classify each table table with a type
* Classify each table column header with a type
* Make cell-level text corrections to any table cell value.
## Installation
### SageMaker Private Workforce Setup

This application uses SageMaker labeling workforces to manage workers and distribute tasks. Create a private workforce, workers team called `primary` and `quality`, and assign yourself to both teams using these instructions: https://docs.aws.amazon.com/sagemaker/latest/dg/sms-workforce-create-private-console.html#create-workforce-sm-console

Once you’ve added yourself to the private workforce teams and confirmed your email, take note of the worker portal URL from the AWS Console by:

* Navigate to SageMaker
* Navigate to Ground Truth → Labeling workforces
* Click the Private tab
* Note the URL `Labeling portal sign-in` - you will log in here to perform A2I human reviews.

### Application Deployment with CDK

Deploying this application to your AWS account will create various S3 buckets, Lambda functions, IAM policies, an SQS queue, and a step function.

*Pre-Requisites*

1. Install CDK Toolkit

- npm install -g aws-cdk

2. Install Docker, and Run

- For Mac : https://docs.docker.com/docker-for-mac/install
- For Win : https://docs.docker.com/docker-for-windows/install

*Instruction to Deploy Application to AWS Cloud*

1. cd _TabularDocumentDigitization_
3. python3 -m venv .venv --prompt tdd       - Create virtual environment
3. source .venv/bin/activate                - Enter virtual environment
4. pip install .                            - Install dependencies in virtual environment
5. cdk bootstrap                            - Only run this once per account setup
6. edit cdk.json, set your work team name   - Pre-create the workteam via aws console, and make sure to match workteam name in same region/account
7. cdk deploy --all                         - Deploy application

## Deployment Prefix

To deploy the same application multiple times to the same account, either
change your current git branch and redeploy or set the `DEPLOY` env variable.

Ex:
```
DEPLOY="development" cdk deploy --all
DEPLOY="production" cdk deploy --all
```

This will deploy two copies of the application under different prefixes.


## Running Lambda Unit Tests

Install `pytest` dependencies

```
pip install pytest coverage pytest-cov pytest-xdist pytest-env
```

Run lambda unit tests from the base project folder.
Omit `--looponfail` to run the tests once instead of continuously.

```
PYTHONPATH=./source/lambdas/ pytest \
    tests/lambdas/ \
    --cov=source/lambdas/ \
    --cov-report term-missing \
    --looponfail
```

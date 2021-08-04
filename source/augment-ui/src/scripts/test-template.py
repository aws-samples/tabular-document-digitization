#!/usr/bin/env python3

import json

import boto3
import pathlib
from os import path

# Generate worker-template.html for a hardcoded prefix before running:
# aws s3 sync build/ s3://some-bucket/frontend-build
# S3_PREFIX="s3://some-bucket/build/" npm run inject-hitl
SM_EXECUTION_ROLE="arn:<partition>:iam::<account>:<role-name>"

proj_dir = path.join(pathlib.Path(__file__).parent.absolute(), "../")

sagemaker = boto3.client("sagemaker")
with open(path.join(proj_dir, "build/worker-template.html")) as f:
    worker_template = f.read()

request = {}
request["UiTemplate"] = { "Content": worker_template }
request["Task"] = { "Input": json.dumps({ "text": "hello" })}
request["RoleArn"] = SM_EXECUTION_ROLE

response = sagemaker.render_ui_template(**request)

if "RenderedContent" in response:
    fn = "rendered_template.html"
    with open("rendered_template.html", "w") as f:
        f.write(response["RenderedContent"])
        print(f"Dumped rendered template to file: '{fn}'")
else:
    print("Failed to render", response)


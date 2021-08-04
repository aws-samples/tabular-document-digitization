# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import setuptools


with open('README.md') as fp:
    long_description = fp.read()


setuptools.setup(
    name='TabularDocumentDigitization',
    version='1.0.0',

    description='Tabular Document Digitization Cloud Application',
    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Human In The Loop Team @ ML Solutions Lab',

    package_dir={'': 'infra'},
    packages=setuptools.find_packages(where='infra'),

    install_requires=[
        'aws-cdk.core>=1.83.0',
        'aws-cdk.assets>=1.83.0',
        'aws-cdk.aws-cloudformation>=1.83.0',
        'aws-cdk.aws-cloudwatch>=1.83.0',
        'aws-cdk.aws-dynamodb>=1.83.0',
        'aws-cdk.aws-events>=1.83.0',
        'aws-cdk.aws-events-targets>=1.83.0',
        'aws-cdk.aws-iam>=1.83.0',
        'aws-cdk.aws-lambda>=1.83.0',
        'aws-cdk.aws-lambda-event-sources>=1.83.0',
        'aws-cdk.aws-logs>=1.83.0',
        'aws-cdk.aws-s3>=1.83.0',
        'aws-cdk.aws-s3-assets>=1.83.0',
        'aws-cdk.aws-s3-deployment>=1.83.0',
        'aws-cdk.aws-s3-notifications>=1.83.0',
        'aws-cdk.aws-sns>=1.83.0',
        'aws-cdk.aws-sns-subscriptions>=1.83.0',
        'aws-cdk.aws-sqs>=1.83.0',
        'aws-cdk.aws-cognito>=1.83.0',
        'aws-cdk.aws-sagemaker>=1.83.0',
        'aws-cdk.custom-resources>=1.83.0',
        'aws-cdk.core>=1.83.0',
        'aws-cdk.aws-stepfunctions-tasks>=1.83.0',
        'aws-cdk.aws-stepfunctions>=1.83.0',
        'boto3>=1.16.47',
        'boto3-stubs[essential]',
        'boto3-stubs[stepfunctions]',
        'boto3-stubs[sagemaker-a2i-runtime]',
        'boto3-stubs[cloudwatch]',
        'boto3-stubs[logs]',
        'jsii>=1.16.0',
        'DotMap',
        'Pillow',
        'XlsxWriter',
        'pandas'        
    ],

    python_requires='>=3.7',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: JavaScript',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',

        'Topic :: Software Development :: Code Generators',
        'Topic :: Utilities',

        'Typing :: Typed',
    ],
)

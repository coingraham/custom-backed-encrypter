# custom-backed-encrypter
Custom-backed resource for encrypting Root Drives automatically.

# Installation
1. Install [Serverless.com platform](https://serverless.com/).
2. Git pull this repo.
3. Update the profile in `serverless.yaml`.
4. Navigate to the `serverless/` folder and run `serverless deploy`.
5. If you haven't used [AWS Step Functions](https://aws.amazon.com/step-functions/) before, deploy the _Hello world_ step function so that the IAM role gets created.
5. Then review and deploy the CloudFormation Template (CFT).

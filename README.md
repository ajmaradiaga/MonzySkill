# Monzy

Monzy is an Alexa skill that lets you communicate with your [Monzo](https://monzo.com/) account.

## Requirements:
- Monzo account
- [Amazon Web Services](https://aws.amazon.com/) account
- [Amazon Developer](https://developer.amazon.com) account

### Installation

Steps needed to create an AWS Lambda function that communicates with a Custom Lambda skill - [Tutorial](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/developing-an-alexa-skill-as-a-lambda-function)

Roughly, this is what you would need to do:
  1. Sign up as a Developer in Monzo - https://developers.getmondo.co.uk/
    - Create a client and copy the details as they would be needed to configure OAuth2 in the Alexa Skill
  2. Create an AWS Lambda function
    - Zip the lambda_function.py and requests folder
    - Upload it to the AWS Lambda function
  3. Create an Alexa Skill
    - In the interaction model of the Alexa Skill - Copy and the contents of intent_schema.json and the sample_utterances.txt
    - In configuration of the Alexa Skill - Enter the Monzo Client App details
  4. Associate the Lambda function previously created

Enjoy!

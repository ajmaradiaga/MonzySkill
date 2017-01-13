# Monzy

Monzy is an Alexa skill that lets you communicate with your [Monzo](https://monzo.com/) account.

## Functionality:
Monzy will let you ask for your balance, list of transactions, and total spent. It will tell you your topups, transafer and spent.

Examples of what you are able to ask Monzy:
- Alexa, ask Monzy open Monzy
- Alexa, ask Monzy transactions for today
- Alexa, ask Monzy transactions for yesterday
- Alexa, ask Monzy transactions for the 24th of December 2016
- Alexa, ask Monzy what is my balance
- Alexa, ask Monzy total spent
- Alexa, ask Monzy total spent yesterday
- Alexa, ask Monzy total spent for December 2016
- Alexa, ask Monzy spent last month


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
    - Add account linking details - see screenshot (screenshots/AccountLinking_Example.png)
  4. Associate the Lambda function previously created

Enjoy!

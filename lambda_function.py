"""
Monzy - Beta v 0.1
"""

from __future__ import print_function
from __future__ import division
from datetime import datetime, timedelta, date
import calendar
import requests

# --------------- Helpers that build all of the responses ----------------------

monzoAPIURL = "https://api.monzo.com/"
monzoAccessToken = ""

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

def build_link_account_response():
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': 'Please go to your Alexa app and link your Monzo account.'
        },
        'card': {
            'type': 'LinkAccount'
        }
    }

# --------------- Monzo API ----------------------

def validate_access_token(session):
    """ Validates the access token within the session
    """

    print("Validate Access Token")
    #print(session['user'])

    if "accessToken" in session.get('user', {}):
        global monzoAccessToken
        monzoAccessToken = session['user']['accessToken']
        return True
    
    return False

def get_monzoapi(resource):
    """GET from Monzo"""
    URL = monzoAPIURL + resource
    headers = {'Authorization': 'Bearer ' + monzoAccessToken}

    response = requests.get(URL, headers=headers)

    print("GET " + resource) # + " response: " + response.text)

    return response

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response(session):
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Monzy"
    speech_output = "Welcome to Monzy. \n\n" \
                    "You are able to ask for your balance, transactions for a date or totals. \n"
    
    reprompt_text = "Let me know if you want to know your balance, transactions for a date or totals."
    should_end_session = False

    session_attributes = {}

    """monzoAccount = validate_session_account(session)

    if monzoAccount == None:
        return build_response({}, build_link_account_response())

    session_attributes = create_monzoAccount_attributes(get_monzo_account()) """

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using Monzy. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_monzoAccount_attributes(account_id):
    return {"monzoAccount": account_id}


def get_current_balance(intent, session):
    """ Get Monzo Balance.
    """
    print(session)

    monzoAccount = validate_session_account(session)

    if monzoAccount == None:
        return build_response({}, build_link_account_response())

    r = get_monzoapi("balance?account_id=" + monzoAccount)

    rJson = r.json()

    balance = rJson['balance']
    currency = rJson['currency']

    session_attributes = create_monzoAccount_attributes(monzoAccount)
    should_end_session = False

    card_title = "Monzo Balance"
    speech_output = "Your balance is " + str(balance / 100) + " " + currency
    reprompt_text = None

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def validate_session_account(session):
    """ 
    Validates the account set in the session
    """

    print("Validate Session - account - " + str(session))
    
    if "attributes" in session:
        attributes = session["attributes"]
        if "monzoAccount" in attributes:
            monzoAccount = attributes['monzoAccount']
            print("Monzo Account found in session attributes")
            return monzoAccount
    
    print("Monzo Account NOT found in session attributes")
    monzoAccount = get_monzo_account()
    
    return monzoAccount

def validate_intent_slot(intent, slot, slot_name):
    """ 
    Validates the slot set in the intent and returns its value if found, else None
    """

    print("Validate Intent - " + slot + " - " + str(intent))
    
    if "slots" in intent:
        slots = intent["slots"]
        if slot in slots:
            slot_node = slots[slot]
            print(slot + " found in intent slots" + str(slot_node))
            if slot_node["name"] == slot_name:
                if "value" in slot_node:
                    return slot_node["value"]
                else:
                    return None
    
    print(slot + " NOT found in intent slots")
    
    return None

def get_monzo_account():
    """
    GET the accounts of the user.
    """

    r = get_monzoapi("accounts")

    rJson = r.json()

    if "code" in rJson:
        code = rJson["code"]
        return None

    account = rJson['accounts'][0]

    return account['id']

def query_monzo_transactions(intent, session, monzoAccount, since = None, before = None):
    
    query = "transactions?expand[]=merchant&account_id=" + monzoAccount

    if since != None:
        query = query + "&since=" + since.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    if before != None:
        query = query + "&before=" + before.strftime("%Y-%m-%dT%H:%M:%SZ")

    return get_monzoapi(query)

def process_date_value(aux_date, delta):
    today = date.today()
    yesterday = today - timedelta(days=1)
    since = today - timedelta(days=delta)
    
    date_prompt = "in the last " + str(delta) + " days"
    specific_date = False

    if aux_date != None and aux_date != "":
        since = datetime.strptime(aux_date, '%Y-%m-%d')
    
    if aux_date == str(yesterday):
        date_prompt = "for yesterday"
        specific_date = True
    elif aux_date == str(today):
        date_prompt = "for today"
        specific_date = True
    elif aux_date != None and aux_date != "":
        date_prompt = "for " + aux_date
        specific_date = True

    print("Query date: " + str(aux_date))

    return  since, date_prompt, specific_date

def get_totals(intent, session):
    
    #Validate session and intent variables
    monzoAccount = validate_session_account(session)

    if monzoAccount == None:
        return build_response({}, build_link_account_response())
    
    aux_date = validate_intent_slot(intent, "Date", "Date")

    card_title = "Monzo Totals"
    session_attributes = create_monzoAccount_attributes(monzoAccount)
    should_end_session = False

    prompt_aux_date = aux_date

    try:
        today = date.today()
        yesterday = today - timedelta(days=1)
        if aux_date == None or aux_date == "":
            aux_date = today.strftime("%Y-%m")

        if len(aux_date) == 4:
            #Handle a year - Not handling as the processing can take quite a bit of time
            #since = datetime.strptime(aux_date, '%Y')
            #before = datetime.strptime(aux_date + "-12", '%Y-%m') + timedelta(days=31, hours=23, minutes=59, seconds=59)
            return build_response(session_attributes, build_speechlet_response(card_title, "Sorry, I'm unable to retrieve totals for a year at the moment.", None, should_end_session))
        elif len(aux_date) == 7:
            #Handle year with month
            since = datetime.strptime(aux_date, '%Y-%m')
            print("Dates for " + aux_date + " calculated: " + str(calendar.monthrange(since.year, since.month)[1]))
            #before = datetime.strptime(aux_date + "-"  + str(calendar.monthrange(since.year, since.month)[1]) + "T23:59:59", "%Y-%m-%dT%H:%M:%SZ")
            before = since + timedelta(days=calendar.monthrange(since.year, since.month)[1], hours=23, minutes=59, seconds=59)
            prompt_aux_date = since.strftime("%B %Y")
        else:
            #Handle full date
            since = datetime.strptime(aux_date, '%Y-%m-%d')
            before = since + timedelta(hours=23, minutes=59, seconds=59)
            if aux_date == str(today):
                prompt_aux_date = "today"
            elif aux_date == str(yesterday):
                prompt_aux_date = "yesterday"
            else:
                prompt_aux_date = since.strftime("%d %B, %Y")
    except ValueError:
        return build_response(session_attributes, build_speechlet_response(
        card_title, "Sorry, I didn't get the date correctly: " + aux_date + ". Please ask again.", None, should_end_session))
    
    r = query_monzo_transactions(intent, session, monzoAccount, since, before)
    
    """
    if aux_date == "" or aux_date == None:
        #Last Transactions
        tomorrow = date.today() + timedelta(days=1)
        r = query_monzo_transactions(intent, session, monzoAccount, since, tomorrow)
    else:
        #Specific Date
        before = since + timedelta(hours=23, minutes=59, seconds=59)
        r = query_monzo_transactions(intent, session, monzoAccount, since, before) 
    """
        

    rJson = r.json()

    transactions = rJson['transactions']
    totalTransactions = len(transactions)

    if totalTransactions == 0:
        speech_output = "No transactions found for " + prompt_aux_date + " to calculate totals.\n\n"
        reprompt_text = None
        return build_response({}, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
    else:
        speech_output = "Your total for " + prompt_aux_date + " is: \n\n"
        
    topup = 0
    spent = {'GBP': 0}
    transfer = 0
    grand_total = 0
    for index in range(totalTransactions):
        tx_output = ""
        transaction = transactions[totalTransactions - index - 1]
        metadata = transaction['metadata']
        amount = transaction['amount']
        grand_total = grand_total + amount
        local_amount = transaction['local_amount']
        local_currency = transaction['local_currency']
        is_load = False
        if "is_load" in transaction:
            is_load = transaction['is_load']

        if "is_topup" in metadata:
            topup = topup + local_amount
        elif is_load == True:
            transfer = transfer + local_amount
        else:
            if local_currency in spent:
                spent[local_currency] = spent[local_currency] + local_amount
            else:
                spent[local_currency] = local_amount

    if topup != 0:
        speech_output = speech_output + " Top Up: " + str(topup / 100) + " GBP. \n"

    if transfer != 0:
        speech_output = speech_output + " Transfer: " + str(transfer / 100) + " GBP. \n"

    speech_output = speech_output + " Spent: "
    for curr in spent.keys():
        amount = spent[curr]
        if amount != 0:
            speech_output = speech_output + str(amount / 100) + " " + curr + ". \n"
        elif curr == "GBP":
            speech_output = speech_output + "0 GBP. \n"

    if topup != 0 and transfer != 0:
        speech_output = speech_output + "For a Grand Total of: " + str(grand_total / 100) + " GBP."
    reprompt_text = None

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_list_transactions(intent, session):
    
    #Validate session and intent variables
    monzoAccount = validate_session_account(session)
    
    if monzoAccount == None:
        return build_response({}, build_link_account_response())

    aux_date = validate_intent_slot(intent, "Date", "Date")

    card_title = "Monzo Transactions"
    session_attributes = create_monzoAccount_attributes(monzoAccount)
    should_end_session = False

    try:
        if aux_date != None and aux_date != "":
            validate = datetime.strptime(aux_date, '%Y-%m-%d')
    except ValueError:
        return build_response(session_attributes, build_speechlet_response(
        card_title, "Sorry, I didn't get the date correctly: " + aux_date + ". Please ask again.", None, should_end_session))
    
    since, date_prompt, specific_date = process_date_value(aux_date, 7)

    if aux_date == "" or aux_date == None:
        #Last Transactions
        tomorrow = date.today() + timedelta(days=1)
        r = query_monzo_transactions(intent, session, monzoAccount, since, tomorrow)
    else:
        #Specific Date
        before = since + timedelta(hours=23, minutes=59, seconds=59)
        r = query_monzo_transactions(intent, session, monzoAccount, since, before)
    
    rJson = r.json()

    transactions = rJson['transactions']
    totalTransactions = len(transactions)

    if totalTransactions == 0:
        speech_output = "No transactions found " + date_prompt + "."
        reprompt_text = None
        return build_response({}, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
    elif totalTransactions == 1:
        speech_output = "Your transaction " + date_prompt + ": \n\n"
    elif totalTransactions < 5:
        speech_output = "Your transactions " + date_prompt + " are: \n\n"
    elif specific_date == True:
        speech_output = "Your transactions " + date_prompt + " are: \n\n"
    else:
        speech_output = "Your last " + str(totalTransactions) + " transactions " + date_prompt + " are: \n\n"
        
    for index in range(totalTransactions):
        #print("Total: " + str(totalTransactions) + " - Index: " + str(index) + " Calc: " + str(totalTransactions - index - 1))
        speech_output = speech_output + get_transaction_speech_output(transactions[totalTransactions - index - 1]) + "\n"
        if specific_date == False and index >= 5:
            break

    reprompt_text = None

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_transaction_speech_output(transaction):
    
    tx_output = ""

    metadata = transaction['metadata']
    amount = transaction['local_amount'] / 100
    currency = transaction['local_currency']
    
    transaction_amount = str(amount) + " " + currency + ". "

    if "is_topup" in metadata:
        return "Top up for " + transaction_amount

    is_load = False

    if "is_load" in transaction:
        is_load = transaction['is_load']

    if is_load == True:
        originator = transaction['originator']
        counterparty = transaction['counterparty']
        counterparty_desc = ""
        if "prefered_name" in counterparty:
            counterparty_desc = counterparty["prefered_name"].strip()
        elif "name" in counterparty:
            counterparty_desc = counterparty["name"].strip()
        elif "number" in counterparty:
            counterparty_desc = "contact"
        else:
            counterparty_desc = transaction["description"].strip()

        tx_output = "Transfer "
        if originator:
            tx_output = tx_output + "to " + counterparty_desc + " " + transaction_amount
        else:
            tx_output = tx_output + "from " + counterparty_desc + " " + transaction_amount

        return tx_output

    desc = ""
    merchant = transaction['merchant']
    if "name" in merchant:
        desc = merchant["name"].strip() + " "
    elif "category" in merchant:
        desc = merchant["category"].strip() + " "
    else:
        desc = "Transaction for "

    tx_output = tx_output + desc + str(amount) + " " + currency + ". "

    return tx_output

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response(session)


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'] + ", intent_name=" + intent_name)

    if validate_access_token(session) == False:
        return build_response({}, build_link_account_response())

    # Dispatch to your skill's intent handlers
    if intent_name == "GetCurrentBalance":
        return get_current_balance(intent, session)
    elif intent_name == "ListTransactions":
        return get_list_transactions(intent, session)
    elif intent_name == "Totals":
        return get_totals(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response(session)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'] + " - Data: " + str(event))

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

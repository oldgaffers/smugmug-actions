import boto3
from requests_oauthlib import OAuth1Session

ssm = boto3.client('ssm')

apiKey = ''

def get_secret_ssm():
    global apiKey
    if apiKey == '':
        r = ssm.get_parameter(Name='/SMUGMUG/API_KEY/KEY', WithDecryption=True)
        apiKey = r['Parameter']['Value']
    r = ssm.get_parameter(Name='/SMUGMUG/API_KEY/SECRET', WithDecryption=True)
    apiKeySecret = r['Parameter']['Value']
    r = ssm.get_parameter(Name='/SMUGMUG/ACCESS_TOKEN/TOKEN', WithDecryption=True)
    access_token = r['Parameter']['Value']
    r = ssm.get_parameter(Name='/SMUGMUG/ACCESS_TOKEN/SECRET', WithDecryption=True)
    access_token_secret = r['Parameter']['Value']
    return {
        'api-key': apiKey,
        'api-key-secret': apiKeySecret,
        'access_token': access_token,
        'access_token_secret': access_token_secret,
    }

def getRequestsHandler():
    secrets = get_secret_ssm()
    return OAuth1Session(secrets['api-key'],
        client_secret=secrets['api-key-secret'],
        resource_owner_key=secrets['access_token'],
        resource_owner_secret=secrets['access_token_secret']
    )

def getApiKey():
    global apiKey
    if apiKey == '':
        r = ssm.get_parameter(Name='/SMUGMUG/API_KEY/KEY', WithDecryption=True)
        return r['Parameter']['Value']
    return apiKey
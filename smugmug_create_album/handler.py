import json
import boto3
from botocore.exceptions import ClientError
from requests_oauthlib import OAuth1Session

def get_secret():

    secret_name = "boatregister/smugmug"
    region_name = "eu-west-1"
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e
    return get_secret_value_response['SecretString']

def lambda_handler(event, context):
    print(event)
    secrets = get_secret()
    smugmug = OAuth1Session(secrets['api-key'],
        client_secret=secrets['api-key-secret'],
        resource_owner_key=secrets['access_token'],
        resource_owner_secret=secrets['access_token_secret']
    )
    data = { 'UrlName': 'NCC-1701', 'Name': 'Enterprise (NCC-1701)' }
    r = smugmug.post(
        'https://www.smugmug.com/api/v2/folder/user/oga/Boats!albums',
        json.dumps(data),
        headers={'Accept':'application/json', 'Content-Type': 'application/json'}
    )
    print(r.status_code)
    print(r.text)
    print(r.json())
};


    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

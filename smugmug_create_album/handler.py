import json
import boto3
from botocore.exceptions import ClientError
from requests_oauthlib import OAuth1Session
from requests_toolbelt.multipart import decoder

def get_secret(secret_name):
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
    return json.loads(get_secret_value_response['SecretString'])

def getRequestsHandler():
    secrets = get_secret("boatregister/smugmug")
    return OAuth1Session(secrets['api-key'],
        client_secret=secrets['api-key-secret'],
        resource_owner_key=secrets['access_token'],
        resource_owner_secret=secrets['access_token_secret']
    )

def createAlbum(smugmug, name, oga_no):
    r = smugmug.post(
        'https://www.smugmug.com/api/v2/folder/user/oga/Boats!albums',
        json.dumps({ 'UrlName': f'OGA-{oga_no}', 'Name': f'{name} ({oga_no})' }),
        headers={'Accept':'application/json', 'Content-Type': 'application/json'}
    )
    print(r.status_code)
    print(r.text)
    print(r.json())

def lambda_handler(event, context):
    print(event)
    body = event['body'].encode()
    x = decoder.MultipartDecoder(body, event['headers']['content-type'])
    print(x)
    smugmug = getRequestsHandler()
    name = ''
    oga_no = ''
    createAlbum(smugmug, name, oga_no)
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

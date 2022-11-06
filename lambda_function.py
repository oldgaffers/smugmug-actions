import json
import boto3
from botocore.exceptions import ClientError

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
    print(get_secret())
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

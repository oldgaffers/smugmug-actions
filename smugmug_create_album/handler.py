import json
import boto3
from botocore.exceptions import ClientError
from requests_oauthlib import OAuth1Session
from requests_toolbelt.multipart import decoder
import base64
import werkzeug

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

def formData(body, contentType):
    form = {}
    for part in decoder.MultipartDecoder(postdata.encode('utf-8'), contentType).parts:
        postdata = base64.b64decode(body).decode('iso-8859-1')
        h = part.headers
        x = dict({k.decode():werkzeug.http.parse_options_header(h[k].decode()) for k in h.keys()})
        cd = x['Content-Disposition']
        print(cd)
        if cd[0] == 'form-data':
            fd = cd[1]
            form[fd['name']] = { 'text': part.text}
            if 'filename' in fd:
                form[fd['name']]['filename'] = fd['filename']
    return form
    
def lambda_handler(event, context):
    print(json.dumps(event))
    form = formData(event['body'], event['headers']['content-type'])
    print('oga_no', form['oga_no'])
    response = '' # s3client.put_object(  Body=lst[0].encode('iso-8859-1'),  Bucket='test',    Key='mypicturefinal.jpg')
    return {'statusCode': '200','body': 'Success', 'headers': { 'Content-Type': 'text/html' }}

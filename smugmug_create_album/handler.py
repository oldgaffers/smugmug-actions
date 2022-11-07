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

def lambda_handler(event, context):
    print(json.dumps(event))
    postdata = base64.b64decode(event['body']).decode('iso-8859-1')
    imgInput = ''
    lst = []
    content_type_header = event['headers']['content-type']
    form = {}
    for part in decoder.MultipartDecoder(postdata.encode('utf-8'), content_type_header).parts:
        h = part.headers
        x = [werkzeug.http.parse_options_header(h[k] for k in h.keys())]
        print(x)
        if b'Content-Type' in h:
            # print('content-type', h[b'Content-Type'])
            pass
        if b'Content-Disposition' in h:
            cds = h[b'Content-Disposition'].decode('utf-8')
            q = cds.split('; ')
            p = [p.split('=') for p in q if '=' in p]
            cd = dict({l[0]:l[1] for l in p})
            k = cd['name'].split('"')[1]
            form[k] = part.text
            # print('field', cd, part.text)
    for k in form.keys():
        if k != 'file':
            print(k, form[k])
    print('oga_no', form['oga_no'])
    # print(lst)
    response = '' # s3client.put_object(  Body=lst[0].encode('iso-8859-1'),  Bucket='test',    Key='mypicturefinal.jpg')
    return {'statusCode': '200','body': 'Success', 'headers': { 'Content-Type': 'text/html' }}

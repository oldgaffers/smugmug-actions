import json
import boto3
from botocore.exceptions import ClientError
from requests_oauthlib import OAuth1Session
from requests_toolbelt.multipart import decoder
import requests
import base64
import werkzeug

ssm = boto3.client('ssm')
logQueue = 'https://sqs.eu-west-1.amazonaws.com/651845762820/logging'

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

def createAlbum(smugmug, name, oga_no):
    r = smugmug.post(
        'https://www.smugmug.com/api/v2/folder/user/oga/Boats!albums',
        json.dumps({ 'UrlName': f'OGA-{oga_no}', 'Name': f'{name} ({oga_no})' }),
        headers={'Accept':'application/json', 'Content-Type': 'application/json'}
    )
    if r.status_code == 201:
        return {
            'statusCode': r.status_code,
            'headers': { 'Content-Type': 'application/json' },
            'body': { 'oga_no': oga_no, 'albumKey': r.json()['Response']['Album']['AlbumKey'] },
        }
    if r.status_code == 409:
        sqs = boto3.client('sqs')
        sqs.send_message(QueueUrl=logQueue, MessageBody=f'smugmug-create-album duplicate OGA no {oga_no}')
    
        return {
            'statusCode': r.status_code,
            'headers': { 'Content-Type': 'application/json' },
            'body': { 'oga_no': oga_no, 'albumKey': r.json()['Conflicts']['/api/v2/folder/user/oga/Boats!albums']['Album']['AlbumKey'] },
        }
    return {
        'statusCode': r.status_code,
        'body': r.text
    }

def getApiKey():
    global apiKey
    if apiKey == '':
        r = ssm.get_parameter(Name='/SMUGMUG/API_KEY/KEY', WithDecryption=True)
        return r['Parameter']['Value']
    return apiKey
    
def thumbnail(albumKey):
    apiKey = getApiKey()
    r = requests.get(f'https://api.smugmug.com/api/v2/album/{albumKey}!highlightimage',
        headers={'accept': 'application/json' },
        params={
            '_filteruri': '',
            '_filter': 'ThumbnailUrl',
            'APIKey': apiKey
        }
    )
    if r.ok:
        try:
            j = r.json()['Response']
            if 'AlbumImage' in j:
                return { 'statusCode': r.status_code, 'body': json.dumps({
                    'ThumbnailUrl': r.json()['Response']['AlbumImage']['ThumbnailUrl']
                }) }
            return { 'statusCode': r.status_code, 'body': json.dumps(j) }
        except:
            print(f"no thumbnail for album {albumKey} response was {r.text}")
            return { 'statusCode': 404, 'body': json.dumps(r.text) }
    return { 'statusCode': r.status_code, 'body': json.dumps(r.text) }
    #return {
    #    'statusCode': 301,
    #    'headers': { 'Location': r.json()['Response']['AlbumImage']['ThumbnailUrl'] },
    #    'body': json.dumps('Moved')
    #}

def getAlbumKey(oga_no):
    print('getAlbumKey', oga_no)
    r = requests.get(f'https://oga.smugmug.com/Boats/OGA-{oga_no}')
    key = r.text.split('"AlbumKey"')[1].split('"')[1];
    return { 'statusCode': r.status_code, 'body': json.dumps({'albumKey': key}) }

def newGetAlbumKey(smugmug, oga_no):
    text = f"({oga_no})"
    r = smugmug.get(f'https://api.smugmug.com/api/v2/album!search',
        headers={'accept': 'application/json' },
        params={
            'APIKey': apiKey,
            'Scope': '/folder/user/oga/Boats/',
            'SortDirection': 'Descending',
            'SortMethod': 'Rank',
            'Text': text,
        }
    )
    if r.ok:
        try:
            j = r.json()['Response']
            albums = j['Album']
            urlName = f"OGA-{oga_no}"
            matching = [a for a in albums if a['UrlName'] == urlName]
            if len(matching)>0:
              albumKey = matching[0]['AlbumKey']
              return { 'statusCode': r.status_code, 'body': json.dumps({'albumKey': albumKey}) }
            return { 'statusCode': r.status_code, 'body': json.dumps(j) }
        except:
            print(f"no album for oga_no {oga_no} response was {r.text}")
            return { 'statusCode': 404, 'body': json.dumps(r.text) }
    return { 'statusCode': r.status_code, 'body': json.dumps(r.text) }

def lambda_handler(event, context):
    # print(json.dumps(event))
    if event['requestContext']['http']['method'] == 'GET':
        n = event['requestContext']['http']['path'].split('/')
        if len(n) == 2:
            albumKey = n[1]
            return thumbnail(albumKey)
        smugmug = getRequestsHandler()
        return newGetAlbumKey(smugmug, n[2])
    body = json.loads(event['body'])
    smugmug = getRequestsHandler()
    return createAlbum(smugmug, body['name'], body['oga_no'])

import json
import boto3
from requests_oauthlib import OAuth1Session
import requests

ssm = boto3.client('ssm')
sqs = boto3.client('sqs')
logQueue = 'https://sqs.eu-west-1.amazonaws.com/651845762820/logging'

apiKey = ''

def log(message):
    sqs.send_message(QueueUrl=logQueue, MessageBody=f'smugmug-actions {message}')

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
    log(f'createAlbum {name}, {oga_no}')
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
        log(f'duplicate OGA no {oga_no}')
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

def thumbnail(albumKey, beta):
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
        if beta is not None:
            return { 'statusCode': 200, 'body': json.dumps(r.text) }
        try:
            j = r.json()['Response']
            if 'AlbumImage' in j:
                return { 'statusCode': r.status_code, 'body': json.dumps({
                    'ThumbnailUrl': r.json()['Response']['AlbumImage']['ThumbnailUrl']
                }) }
            return { 'statusCode': r.status_code, 'body': json.dumps(j) }
        except:
            log(f"no thumbnail for album {albumKey} response was {r.text}")
            return { 'statusCode': 404, 'body': json.dumps(r.text) }
    return { 'statusCode': r.status_code, 'body': json.dumps(r.text) }

def largestImage(imageKey, caption):
    apiKey = getApiKey()
    r = requests.get(f'https://api.smugmug.com/api/v2/image/{imageKey}!largestimage',
        headers={'accept': 'application/json' },
        params={
            '_filteruri': '',
            # '_filter': 'ImageKey,FormattedValues',
            'APIKey': apiKey
        }
    )
    if r.ok:
        j = r.json()['Response']
        if 'LargestImage' in j:
            resultBody = json.dumps({ 'url': j['LargestImage']['Url'], 'caption': caption }, ensure_ascii=False)
            return { 'statusCode': r.status_code, 'body': resultBody }
        return { 'statusCode': r.status_code, 'body': json.dumps(j) }
    return { 'statusCode': r.status_code, 'body': json.dumps(r.text) }

def image(albumKey):
    apiKey = getApiKey()
    r = requests.get(f'https://api.smugmug.com/api/v2/album/{albumKey}!highlightimage',
        headers={'accept': 'application/json' },
        params={
            '_filteruri': '',
            '_filter': 'ImageKey,FormattedValues',
            'APIKey': apiKey
        }
    )
    if r.ok:
        try:
            j = r.json()['Response']
            if 'AlbumImage' in j:
                return largestImage(j['AlbumImage']['ImageKey'], j['AlbumImage']['FormattedValues']['Caption']['text'])
            return { 'statusCode': r.status_code, 'body': json.dumps(j) }
        except:
            log(f"no thumbnail for album {albumKey} response was {r.text}")
            return { 'statusCode': 404, 'body': json.dumps(r.text) }
    return { 'statusCode': r.status_code, 'body': json.dumps(r.text) }

def getAlbumKey(name, oga_no):
    text = f'{name} ({oga_no})'
    smugmug = getRequestsHandler()
    r = smugmug.get(f'https://api.smugmug.com/api/v2/album!search',
        headers={'accept': 'application/json' },
        params={
            'APIKey': apiKey,
            'Scope': '/api/v2/user/oga',
            'SortDirection': 'Descending',
            'SortMethod': 'Rank',
            'Text': text,
        }
    )
    if r.ok:
        js = r.json()
        try:
            albums = js['Response']['Album']
            if len(albums)>0:
              albumKey = albums[0]['AlbumKey']
              return { 'statusCode': r.status_code, 'body': json.dumps({'albumKey': albumKey}) }
            return { 'statusCode': r.status_code, 'body': json.dumps(j) }
        except:
            log(f"no album for {text} response was {r.text}")
            return { 'statusCode': 404, 'body': json.dumps(r.text) }
    print(r.status_code, r.text, text)
    return { 'statusCode': r.status_code, 'body': json.dumps(r.text) }

def lambda_handler(event, context):
    # print(json.dumps(event))
    if event['requestContext']['http']['method'] == 'GET':
        qsp = event['queryStringParameters']
        path = event['requestContext']['http']['path']
        if path == '/thumb':
            return thumbnail(qsp['album_key'], qsp.get('beta', None))
        elif path == '/li':
            return image(qsp['album_key'])
        elif path == '/album':
            return getAlbumKey(qsp['name'], qsp['oga_no'])
        else:
            return { 'statusCode': 400, 'body': json.dumps('unknown request') }
    body = json.loads(event['body'])
    smugmug = getRequestsHandler()
    return createAlbum(smugmug, body['name'], body['oga_no'])

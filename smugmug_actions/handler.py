import json
import boto3
import os
from urllib.parse import unquote_plus
from smugmug_actions.album import createAlbum, getAlbumKey
from smugmug_actions.image import thumbnail, image
from smugmug_actions.upload import uploadToSmugMug
from smugmug_actions.mail import send_email

s3 = boto3.client('s3')

localImageBucket = 'boatregister-public'

def upload(bucket, key):
    # print('upload', bucket, key)
    o = s3.get_object(Bucket=bucket, Key=key)
    email, filename = key.split('/')
    meta = o['Metadata']
    if 'albumkey' in meta:
        albumkey = meta.get('albumkey', None)
        copyright = meta.get('copyright', 'OGA')
        url = uploadToSmugMug(filename, albumkey, copyright, o['Body'], o['ContentType'], o['ContentLength'])
        send_email(url, email, copyright)
        return
    if 'uuid' in meta:
        print('TODO, local S3 copy', meta)
        uuid = meta['uuid']
        id = meta['id']
        _, ext = os.path.splitext(filename)
        localImageKey = f"{id}/{uuid}{ext}"
        s3.copy_object(CopySource={ 'Bucket': bucket, 'Key': key}, Bucket=localImageBucket, Key=localImageKey)
        return { 'statusCode': 201, 'body': json.dumps(f"s3://{localImageBucket}/{localImageKey}") }

def lambda_handler(event, context):
    # print(json.dumps(event))
    if 'Records' in event:
        s3 = event['Records'][0]['s3']
        return upload(s3['bucket']['name'], unquote_plus(s3['object']['key']))
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
    elif event['requestContext']['http']['method'] == 'POST':
        body = json.loads(event['body'])
        return createAlbum(body['name'], body['oga_no'])
    else:
        return { 'statusCode': 400, 'body': json.dumps('unknown request') }


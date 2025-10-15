import json
from log import log
from auth import getApiKey
import requests

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
            r = r.json()['Response'].get('AlbumImage', None)
            if r is None:
                return { 'statusCode': 404, 'body': json.dumps('no image') }
            return { 'statusCode': 200, 'body': json.dumps(r)}
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

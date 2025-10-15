import json
from log import log
from auth import getRequestsHandler, getApiKey

def createAlbum(name, oga_no):
    smugmug = getRequestsHandler()
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

def getAlbumKey(name, oga_no):
    apiKey = getApiKey()
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

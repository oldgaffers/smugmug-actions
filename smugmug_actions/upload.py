import boto3
from smugmug_actions.auth import getRequestsHandler

ssm = boto3.client('ssm')

def uploadToSmugMug(filename, o):
    smugmug = getRequestsHandler()
    meta = o['Metadata']
    if 'albumkey' not in meta:
      print('missing album key')
      return
    copyright = meta.get('copyright', 'OGA')
    headers={
            'Content-Type': o['ContentType'],
            'Content-Length': f"{o['ContentLength']}",
          # 'Content-MD5': base64.b64encode(hashlib.md5(data).digest()),
           'X-Smug-AlbumUri': f"/api/v2/album/{meta['albumkey']}",
           'X-Smug-FileName': filename,
           'X-Smug-Caption': f"© {copyright}",
           'X-Smug-Hidden': 'true',
           'X-Smug-ResponseType': 'JSON',
           'X-Smug-Version': 'v2'
        }
    # print('upload', key, o['Metadata']['albumkey'])
    r=smugmug.post('https://upload.smugmug.com/', headers=headers, data=o['Body'].read())
    if r.ok:
        return r.json()['Image']['URL'], copyright
    return None, copyright

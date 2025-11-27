import boto3
from smugmug_actions.auth import getRequestsHandler

ssm = boto3.client('ssm')

def uploadToSmugMug(filename, albumkey, copyright, body, contentType, contentLength):
    smugmug = getRequestsHandler()
    headers={
            'Content-Type': contentType,
            'Content-Length': f"{contentLength}",
          # 'Content-MD5': base64.b64encode(hashlib.md5(data).digest()),
           'X-Smug-AlbumUri': f"/api/v2/album/{albumkey}",
           'X-Smug-FileName': filename,
           'X-Smug-Caption': f"© {copyright}",
           'X-Smug-Hidden': 'true',
           'X-Smug-ResponseType': 'JSON',
           'X-Smug-Version': 'v2'
        }
    # print('upload', key, albumkey)
    r=smugmug.post('https://upload.smugmug.com/', headers=headers, data=body.read())
    if r.ok:
        return r.json()['Image']['URL']

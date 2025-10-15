import smtplib
import boto3
import string

ssm = boto3.client('ssm')

def remove_non_ascii(a_str):
    ascii_chars = set(string.printable)
    return ''.join(
        filter(lambda x: x in ascii_chars, a_str)
    )

def send_email(url, email, copyright):
    boat = url.split('/')[4]
    # print('send_email', url, email, copyright, boat)
    r = ssm.get_parameter(Name='MAIL_HOST')
    host = r['Parameter']['Value']
    r = ssm.get_parameter(Name='MAIL_PORT')
    port = int(r['Parameter']['Value'])
    r = ssm.get_parameter(Name='MAIL_USER')
    user = r['Parameter']['Value']
    r = ssm.get_parameter(Name='MAIL_PASSWORD', WithDecryption=True)
    password = r['Parameter']['Value']
    server = smtplib.SMTP_SSL(host, port)
    server.login(user, password)
    fromaddr = user
    toaddrs  = [user]
    headers = [f'From: {fromaddr}']
    headers.append(f"Subject: new photo for boat {boat}")
    message = [
        f'{email} has uploaded a photo for boat {boat}.',
        f'You can see the photo here: {url}.',
        f'The copyright was claimed as {remove_non_ascii(copyright)}'
    ]
    try:
      server.sendmail(fromaddr, toaddrs, "\r\n".join(headers + message))
      # print('mail sent', json.dumps(headers))
    except:
      print('error sending email', url, email, copyright)
    server.quit()

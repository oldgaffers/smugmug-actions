import boto3

sqs = boto3.client('sqs')

logQueue = 'https://sqs.eu-west-1.amazonaws.com/651845762820/logging'

def log(message):
    sqs.send_message(QueueUrl=logQueue, MessageBody=f'smugmug-actions {message}')
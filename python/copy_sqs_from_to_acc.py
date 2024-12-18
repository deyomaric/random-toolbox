import json
import sys
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


def copy_sqs_messages(
    source_queue_url, source_access_key, source_secret_key, source_session_token,
    destination_queue_url, destination_access_key, destination_secret_key, destination_session_token
):
    try:
        # Initialize the SQS clients for source and destination
        source_sqs = boto3.client(
            'sqs',
            aws_access_key_id=source_access_key,
            aws_secret_access_key=source_secret_key,
            aws_session_token=source_session_token
        )

        destination_sqs = boto3.client(
            'sqs',
            aws_access_key_id=destination_access_key,
            aws_secret_access_key=destination_secret_key,
            aws_session_token=destination_session_token
        )

        # Receive messages from source queue and send them to destination queue
        while True:
            response = source_sqs.receive_message(
                QueueUrl=source_queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=1
            )

            messages = response.get('Messages', [])
            if not messages:
                print("No more messages to copy.")
                break

            for message in messages:
                destination_sqs.send_message(
                    QueueUrl=destination_queue_url,
                    MessageBody=message['Body'],
                    MessageAttributes=message.get('MessageAttributes', {})
                )

                # Delete the message from the source queue
                source_sqs.delete_message(
                    QueueUrl=source_queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )

            print(f"Successfully copied and deleted {len(messages)} messages.")

    except NoCredentialsError:
        print("AWS credentials not provided.")
    except PartialCredentialsError:
        print("Incomplete AWS credentials provided.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 9:
        print("Usage:")
        print("  python script.py <source_queue_url> <source_access_key> <source_secret_key> <source_session_token> <destination_queue_url> <destination_access_key> <destination_secret_key> <destination_session_token>")
    else:
        if len(sys.argv) == 9:
            source_queue_url = sys.argv[1]
            source_access_key = sys.argv[2]
            source_secret_key = sys.argv[3]
            source_session_token = sys.argv[4]
            destination_queue_url = sys.argv[5]
            destination_access_key = sys.argv[6]
            destination_secret_key = sys.argv[7]
            destination_session_token = sys.argv[8]

            copy_sqs_messages(
                source_queue_url, source_access_key, source_secret_key, source_session_token,
                destination_queue_url, destination_access_key, destination_secret_key, destination_session_token
            )

        else:
            print("Invalid arguments. Please check the usage.")
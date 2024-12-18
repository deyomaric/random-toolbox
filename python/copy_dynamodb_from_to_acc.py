import json
import sys
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def copy_dynamodb_table(
    source_table_name, source_access_key, source_secret_key, source_session_token,
    destination_table_name, destination_access_key, destination_secret_key, destination_session_token
):
    try:
        # Initialize the DynamoDB client for source
        source_dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=source_access_key,
            aws_secret_access_key=source_secret_key,
            aws_session_token=source_session_token
        )

        # Initialize the DynamoDB client for destination
        destination_dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=destination_access_key,
            aws_secret_access_key=destination_secret_key,
            aws_session_token=destination_session_token
        )

        source_table = source_dynamodb.Table(source_table_name)
        destination_table = destination_dynamodb.Table(destination_table_name)

        # Scan the source table and copy items to the destination table
        response = source_table.scan()
        items = response.get('Items', [])

        for item in items:
            destination_table.put_item(Item=item)

        print(f"Successfully copied {len(items)} items from {source_table_name} to {destination_table_name}.")

        # Handle pagination if source table has more items
        while 'LastEvaluatedKey' in response:
            response = source_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items = response.get('Items', [])

            for item in items:
                destination_table.put_item(Item=item)

            print(f"Successfully copied {len(items)} additional items from {source_table_name} to {destination_table_name}.")

    except NoCredentialsError:
        print("AWS credentials not provided.")
    except PartialCredentialsError:
        print("Incomplete AWS credentials provided.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 9:
        print("Usage: python script.py <source_table_name> <source_access_key> <source_secret_key> <source_session_token> <destination_table_name> <destination_access_key> <destination_secret_key> <destination_session_token>")
    else:
        source_table_name = sys.argv[1]
        source_access_key = sys.argv[2]
        source_secret_key = sys.argv[3]
        source_session_token = sys.argv[4]
        destination_table_name = sys.argv[5]
        destination_access_key = sys.argv[6]
        destination_secret_key = sys.argv[7]
        destination_session_token = sys.argv[8]

        copy_dynamodb_table(
            source_table_name, source_access_key, source_secret_key, source_session_token,
            destination_table_name, destination_access_key, destination_secret_key, destination_session_token
        )
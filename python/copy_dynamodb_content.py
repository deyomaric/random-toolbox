import json
import sys
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def copy_dynamodb_table(source_table_name, destination_table_name, aws_access_key, aws_secret_key, aws_session_token):
    try:
        # Initialize the DynamoDB client
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            aws_session_token=aws_session_token
        )

        source_table = dynamodb.Table(source_table_name)
        destination_table = dynamodb.Table(destination_table_name)

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
    if len(sys.argv) != 6:
        print("Usage: python script.py <source_table_name> <destination_table_name> <aws_access_key> <aws_secret_key> <aws_session_token>")
    else:
        source_table_name = sys.argv[1]
        destination_table_name = sys.argv[2]
        aws_access_key = sys.argv[3]
        aws_secret_key = sys.argv[4]
        aws_session_token = sys.argv[5]

        copy_dynamodb_table(source_table_name, destination_table_name, aws_access_key, aws_secret_key, aws_session_token)
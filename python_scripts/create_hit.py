
import boto3
from create_hit_document import create_document

REGION_NAME = 'us-east-1'
AWS_ACCESS_KEY_ID = 'AKIAIXO2I3WH7T7EJN6Q'
AWS_SECRET_ACCESS_KEY = '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'
ENDPOINT_URL = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

TITLE = "ActiveLearning"
DESCRIPTION = "External survey"
KEYWORDS = "Testing"

XML_FILE_PATH = "./xml_files/mturk.xml"


def get_client():
    client = boto3.client(
        'mturk',
        endpoint_url=ENDPOINT_URL,
        region_name=REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    return client


def get_requirement():
    local_requirements = [{
        'QualificationTypeId': '00000000000000000071',
        'Comparator': 'In',
        'LocaleValues': [{
            'Country': 'US'
        }, {
            'Country': 'CA'
        }],
        'RequiredToPreview': True
    }]
    return local_requirements


def get_xml_file():
    question_file = open(XML_FILE_PATH, "r")
    return question_file.read()


def get_hit_list(client):
    response = client.list_hits(
        MaxResults=100
    )

    hits = response['HITs']
    for hit in hits:
        if hit['HITStatus'] == 'Assignable':
            print(hit['HITId'])


def create_hit():
    client = get_client()

    requirements = get_requirement()
    question = get_xml_file()
    response = client.create_hit(
        MaxAssignments=10,
        LifetimeInSeconds=100,
        AssignmentDurationInSeconds=60,
        Reward='0.00',
        Title=TITLE,
        Keywords=KEYWORDS,
        Description=DESCRIPTION,
        Question=question,
        QualificationRequirements=requirements
    )

    hit_type_id = response['HIT']['HITTypeId']
    hit_id = response['HIT']['HITId']
    create_document(hit_id)
    print("Your HIT has been created. You can see it at this link:")
    print("https://workersandbox.mturk.com/mturk/preview?groupId={}".format(hit_type_id))
    print("Your HIT ID is: {}".format(hit_id))
    get_hit_list(client)


if __name__ == '__main__':
    create_hit()
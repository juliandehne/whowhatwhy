import boto3
from xml.dom.minidom import parseString

from delab.tw_connection_util import TwitterUtil

util = TwitterUtil()
aws_secret_access_key, aws_access_key_id = util.get_aws_secret()

region_name = 'us-east-1'
# aws_access_key_id = 'YOUR_ACCESS_ID'
# aws_secret_access_key = 'YOUR_SECRET_KEY'

endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

# Uncomment this line to use in production
# endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'

client = boto3.client(
    'mturk',
    endpoint_url=endpoint_url,
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

hit_id = "3HYV4299IG0RNBTUW5J43VNBL1E8E1"
hit = client.get_hit(HITId=hit_id)
print('Hit {} status: {}'.format(hit_id, hit['HIT']['HITStatus']))
response = client.list_assignments_for_hit(
    HITId=hit_id,
    AssignmentStatuses=['Submitted', 'Approved'],
    MaxResults=10,
)

assignments = response['Assignments']
print('The number of submitted assignments is {}'.format(len(assignments)))
for assignment in assignments:
    worker_id = assignment['WorkerId']
    assignment_id = assignment['AssignmentId']
    answer_xml = parseString(assignment['Answer'])

    # the answer is an xml document. we pull out the value of the first
    # //QuestionFormAnswers/Answer/FreeText
    answer = answer_xml.getElementsByTagName('FreeText')[0]
    # See https://stackoverflow.com/questions/317413
    only_answer = " ".join(t.nodeValue for t in answer.childNodes if t.nodeType == t.TEXT_NODE)

    print('The Worker with ID {} submitted assignment {} and gave the answer "{}"'.format(worker_id, assignment_id,
                                                                                          only_answer))

    # Approve the Assignment (if it hasn't already been approved)
    if assignment['AssignmentStatus'] == 'Submitted':
        print('Approving Assignment {}'.format(assignment_id))
        client.approve_assignment(
            AssignmentId=assignment_id,
            RequesterFeedback='good',
            OverrideRejection=False,
        )

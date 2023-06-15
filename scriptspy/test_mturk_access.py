import boto3

from delab.tw_connection_util import TwitterUtil

util = TwitterUtil()
aws_secret_access_key, aws_access_key_id = util.get_aws_secret()

region_name = 'us-east-1'
# aws_access_key_id = 'YOUR_ACCESS_ID'
# aws_secret_access_key = 'YOUR_SECRET_KEY'

endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

# Uncomment this line to use in production
# endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'

mturk = boto3.client(
    'mturk',
    endpoint_url=endpoint_url,
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

# This will return $10,000.00 in the MTurk Developer Sandbox
print(mturk.get_account_balance()['AvailableBalance'])

question = open('questions.xml').read()
new_hit = mturk.create_hit(
    Title='Is this Tweet happy, angry, excited, scared, annoyed or upset?',
    Description='Read this tweet and type out one word to describe the emotion '
                'of the person posting it: happy, angry, scared, annoyed or upset',
    Keywords='text, quick, labeling',
    Reward='0.15',
    MaxAssignments=1,
    LifetimeInSeconds=172800,
    AssignmentDurationInSeconds=600,
    AutoApprovalDelayInSeconds=14400,
    Question=question,
)
print("A new HIT has been created. You can preview it here:")
print("https://workersandbox.mturk.com/mturk/preview?groupId=" + new_hit['HIT']['HITGroupId'])
print("HITID = " + new_hit['HIT'][
    'HITId'] + " (Use to Get Results)")  # Remember to modify the URL above when you're publishing
# HITs to the live marketplace.
# Use: https://worker.mturk.com/mturk/preview?groupId=

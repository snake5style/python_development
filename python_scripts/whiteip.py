import boto3, subprocess
from awspolicy import BucketPolicy

# This script is designed to nslookup a domain, then apply those ip address to a s3 bucket policy
# created by Ray Fuller

#running the nslookup on sendingips.ongage.net to retrieve current ip addresses
process = subprocess.Popen(["nslookup", "enter-domain-here"], stdout=subprocess.PIPE, encoding='utf8')
output = process.communicate()[0].split('\n')

#creating a list of the recently discovered ip addresses
ip_arr = []
for data in output:
    if 'Address' in data:
        ip_arr.append(data.replace('Address: ',''))
ip_arr.pop(0)



#seting up connection to s3 bucket
s3_client = boto3.client('s3')
bucket_name = 'bucket-name'

# Load the bucket policy as an object
bucket_policy = BucketPolicy(serviceModule=s3_client, resourceIdentifer=bucket_name)

# Select the statement that will be modified
statement_to_modify = bucket_policy.select_statement('IPAllow')

# Insert the ods-ongage ip addresses to s3 bucket
ip_address = ip_arr
statement_to_modify.Condition['IpAddress']['aws:SourceIp'] = ip_address

# Save change of the statement
statement_to_modify.save()

# Save change of the policy. This will update the bucket policy
statement_to_modify.source_policy.save() # Or bucket_policy.save()

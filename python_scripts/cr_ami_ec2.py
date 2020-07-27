import boto3
import datetime
from dateutil.parser import parse
import time
import sys

# This Python Script is designed to create, copy and delete AMIs/associated snapshots for the ODS Infrastructure
# Created by Ray Fuller
# This script will Deregister AMIs first
# Then, delete the snapshots associated with the old AMIs
# Next, create new AMIs and snapshots associated with the new AMIs
# Last, tag the new snapshots to be ready for deletion

# Variables
SOURCE_REGION = 'us-east-1'
DEST_REGION = 'us-west-2'

EAST_REGION = 'us-east-1'
WEST_REGION = 'us-west-2'

ec2_source = boto3.client('ec2', region_name = SOURCE_REGION)
ec2_destination = boto3.client('ec2', region_name = DEST_REGION)

ec2_source_east     = boto3.client('ec2', region_name = EAST_REGION)
ec2_source_west     = boto3.client('ec2', region_name = WEST_REGION)

image_east = ec2_source.describe_images(Filters=[{'Name':'tag:Stack','Values':['Development']}])['Images']
image_west = ec2_destination.describe_images(Filters=[{'Name':'tag:Stack','Values':['Development']}])['Images']
snaps_east = ec2_source.describe_snapshots(Filters=[{'Name':'tag:Delete','Values':['30days']}])['Snapshots']
snaps_west = ec2_destination.describe_snapshots(Filters=[{'Name':'tag:Delete','Values':['30days']}])['Snapshots']



# Deregistering AMIs
print("Deregistering AMIs")

# Variable for delete_date and delete_date_west function
age = sys.argv[1]

# Parsing Date for Deregistering AMIs
def delete_date(date):
   get_date = parse(date)
   date_tz = get_date.replace(tzinfo=None)
   diff = datetime.datetime.now() - date_tz

   return diff.days

# Deregistering AMIs from the East Region
for image in image_east:
   c_date = image['CreationDate']
   day_old = delete_date(c_date)
   if day_old > age:
      print("Deregistering: ", image['ImageId'])
      response = ec2_source.deregister_image(
         ImageId=image['ImageId'],
      )
   else:
      print("There are no AMIs available with the Development tag")

# Parsing Date for Deregistering AMIs
def delete_west(date):
   get_date = parse(date)
   date_tz = get_date.replace(tzinfo=None)
   diff1 = datetime.datetime.now() - date_tz

   return diff1.days

# Deregistering AMIs from the West Region
for image in image_west:
   c_date = image['CreationDate']
   day_old = delete_west(c_date)
   if day_old > age:
      print("Deregistering: ", image['ImageId'])
      response = ec2_destination.deregister_image(
         ImageId=image['ImageId'],
      )
   else:
      print("There are no AMIs available with the Development tag out in the west region")


# Deleting Snapshots associated with AMIs
print("Deleting Snapshots")

# Deleting Snapshots from the East Region
for east in snaps_east:
   del_east = east['SnapshotId']
   print(del_east)
   east_snap = ec2_source.delete_snapshot(
      SnapshotId=del_east
   )

# Deleting Snapshots from the West Region
for west in snaps_west:
   del_west = west['SnapshotId']
   print(del_west)
   west_snap = ec2_destination.delete_snapshot(
      SnapshotId=del_west
   )


def create_ami(image_east, image_west):

   # Finding all instances with the Development tag
   reservations = ec2_source.describe_instances(Filters=[{'Name':'tag:Stack','Values':['Development']}])['Reservations']
   instances = []

   # Creating the AMIs
   for reservation in reservations:
      for instance in reservation['Instances']:
          print("Creating an AMI image from: " + instance['InstanceId'])
          response = ec2_source.create_image(
             Description='Development Ami',
             InstanceId=instance['InstanceId'],
             Name='Dev_' + instance['InstanceId'],
             NoReboot=True
          )
          # Adding Tags to AMIs
          SourceAMIID = response['ImageId']
          ec2_source.create_tags(Resources=[SourceAMIID],
             Tags=instance['Tags']
          )
          # Using a waiter to wait for AMI to become available
          waiter = ec2_source.get_waiter('image_available')
          waiter.wait(
              ImageIds=[SourceAMIID],
              DryRun=False,
              WaiterConfig={'Delay': 60,'MaxAttempts': 120}
          )
          # Copying AMIs to Oregon
          response1 = ec2_destination.copy_image(
              Description='Development Ami',
              Name='Dev_' + instance['InstanceId'],
              SourceImageId=response['ImageId'],
              SourceRegion=EAST_REGION
          )
          # Adding Tags to Oregon AMIs
          DestinationAMIID = response1['ImageId']
          ec2_destination.create_tags(Resources=[DestinationAMIID],
              Tags=instance['Tags']
          )
          # Using a waiter for AMI to become available in Oregon
          waiter = ec2_destination.get_waiter('image_available')
          waiter.wait(
              ImageIds=[DestinationAMIID],
              DryRun=False,
              WaiterConfig={'Delay': 60,'MaxAttempts': 120}
          )
   # Creating tags for Snapshots to be deleted


   # Variables for getting East Region Snapshots
   image_east = ec2_source.describe_images(Filters=[{'Name':'tag:Stack','Values':['Development']}])['Images']

   # Creating tags for East Region Snapshots
   for image in image_east:
      SnapTAG = image['BlockDeviceMappings']
      for Snap in SnapTAG:
         tagsnap = Snap['Ebs']['SnapshotId']
         response1 = ec2_source.create_tags(Resources=[tagsnap],
            Tags=[{ 'Key': 'Delete', 'Value': '30days'},],
         )

   # Variables for getting West Region Snapshots
   image_west = ec2_destination.describe_images(Filters=[{'Name':'tag:Stack','Values':['Development']}])['Images']

   # Creating tags for West Region Snapshots
   for image in image_west:
      SnapTAG = image['BlockDeviceMappings']
      for Snap in SnapTAG:
         tagsnap = Snap['Ebs']['SnapshotId']
         response1 = ec2_destination.create_tags(Resources=[tagsnap],
            Tags=[{ 'Key': 'Delete', 'Value': '30days'},],
         )

create_ami(image_east, image_west)

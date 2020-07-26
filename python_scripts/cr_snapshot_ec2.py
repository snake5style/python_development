import argparse
import boto3
from datetime import date, timedelta

# This script was designed to create, copy and delete snapshots in an AWS environment with the capabilities of setting arguments
# created by Ray Fuller and Felix


"""
Example CLI Usage: in the command line enter:
python cr_snapshot_ec2.py -c -d -r 3    'this will set copy and delete to True and retention to 3'
python cr_snapshot_ec2.py -d            'this will set copy to False, delete to True and retention to default value'
"""

# Create the parser and set name & description of the script
parser = argparse.ArgumentParser(prog='cr_snapshot_ec2.py',
                                 description='description: copy and/or delete ec2 snapshot')

# add optional copy arg to the arg parser -> true by default - can use -c or --copy
parser.add_argument('-c', '--copy', help='trigger copy function', action="store_true")

# add optional delete arg to the arg parser -> true by default - can use -d ot --delete
parser.add_argument('-d', '--delete', help='trigger delete function', action="store_true")

# add positional retention arg to the arg parser -> default = 2 - can use -r or --retention
parser.add_argument('-r', '--retention', help='# of days to retain backups for; everything before will be deleted', default='2')

# Variables
SOURCE_REGION = 'us-east-1'
DEST_REGION = 'us-west-2'

EAST_REGION = 'us-east-1'
WEST_REGION = 'us-west-2'

ec2_source = boto3.client('ec2', region_name=SOURCE_REGION)
ec2_destination = boto3.client('ec2', region_name=DEST_REGION)

ec2_source_east = boto3.client('ec2', region_name=EAST_REGION)
ec2_source_west = boto3.client('ec2', region_name=WEST_REGION)


# Creating and copying snapshots

def create_copy():
    # Getting the volumes with the tag Backup and values of Yes
    volumes = ec2_source.describe_volumes(Filters=[{'Name': 'tag:Backup', 'Values': ['Yes']}])['Volumes']

    # For loop the volumes that match the filter then create a snapshot
    # with a waiter
    for volume in volumes:
        print('Getting:', volume['VolumeId'])
        response = ec2_source.create_snapshot(
            Description='Prod_' + volume['VolumeId'],
            VolumeId=volume['VolumeId'],
        )
        # Adding Tags
        SourceVolumeID = response['SnapshotId']
        ec2_source.create_tags(Resources=[SourceVolumeID],
                               Tags=volume['Tags']
                               )
        # Deleting a tag
        SourceTagID = response['SnapshotId']
        ec2_source.delete_tags(Resources=[SourceTagID],
                               Tags=[{'Key': 'Backup', 'Value': 'Yes'}, ]
                               )
        # creating a tag
        SourceTagID = response['SnapshotId']
        ec2_source.create_tags(Resources=[SourceTagID],
                               Tags=[{'Key': 'Backup', 'Value': 'Complete'}, ]
                               )
        # creating a tag
        SourceTagID = response['SnapshotId']
        ec2_source.create_tags(Resources=[SourceTagID],
                               Tags=[{'Key': 'Done', 'Value': 'Copied'}, ]
                               )
        # Using a waiter
        waiter = ec2_source.get_waiter('snapshot_completed')
        waiter.wait(
            SnapshotIds=[SourceTagID],
            DryRun=False,
            WaiterConfig={'Delay': 60, 'MaxAttempts': 120}
        )
    # Getting the snapshots with the tag Backup and values of Complete
    snaps = ec2_source.describe_snapshots(OwnerIds=['self'], Filters=[{'Name': 'tag:Backup', 'Values': ['Complete']}])[
        'Snapshots']

    # Setting up date
    Tday = date.today()
    Tday_snaps = [s for s in snaps if s['StartTime'].date() == Tday]
    len_Tdaysnaps = len(Tday_snaps)
    mid_index = len_Tdaysnaps // 2
    first_Tday = Tday_snaps[:mid_index]
    second_Tday = Tday_snaps[mid_index:]

    # for loop to copy only snapshots from the date above ot Oregon
    for first_T in first_Tday:
        print('Copying:', first_T['SnapshotId'])
        DestinationSnapshot = ec2_destination.copy_snapshot(
            SourceSnapshotId=first_T['SnapshotId'],
            SourceRegion=SOURCE_REGION,
            Description=first_T['VolumeId']
        )
        # Adding Tags
        DestinationSnapshotID = DestinationSnapshot['SnapshotId']
        ec2_destination.create_tags(Resources=[DestinationSnapshotID],
                                    Tags=first_T['Tags']
                                    )
        # Deleting a tag
        DestinationSnapshotID = DestinationSnapshot['SnapshotId']
        ec2_destination.delete_tags(Resources=[DestinationSnapshotID],
                                    Tags=[{'Key': 'Backup', 'Value': 'Complete'}, ]
                                    )
        # Using a waiter
        waiter = ec2_destination.get_waiter('snapshot_completed')
        waiter.wait(
            SnapshotIds=[DestinationSnapshotID],
            DryRun=False,
            WaiterConfig={'Delay': 60, 'MaxAttempts': 120}
        )

    # for loop to copy only snapshots from the date above ot Oregon
    for second_T in second_Tday:
        print('Copying:', second_T['SnapshotId'])
        DestinationSnapshot = ec2_destination.copy_snapshot(
            SourceSnapshotId=first_T['SnapshotId'],
            SourceRegion=SOURCE_REGION,
            Description=second_T['VolumeId']
        )
        # Adding Tags
        DestinationSnapshotID = DestinationSnapshot['SnapshotId']
        ec2_destination.create_tags(Resources=[DestinationSnapshotID],
                                    Tags=second_T['Tags']
                                    )
        # Deleting a tag
        DestinationSnapshotID = DestinationSnapshot['SnapshotId']
        ec2_destination.delete_tags(Resources=[DestinationSnapshotID],
                                    Tags=[{'Key': 'Backup', 'Value': 'Complete'}, ]
                                    )


# Deleting snapshots parameters set by cron

def del_east_west(args):
    del_east_snaps = \
        ec2_source_east.describe_snapshots(OwnerIds=['self'], Filters=[{'Name': 'tag:Backup', 'Values': ['Complete']}])[
            'Snapshots']

    today = date.today()

    retention = timedelta(days=int(args.retention))

    # delete_after_date format is yyyy-mm-dd (2020-04-27)
    delete_after_date = today - retention

    east_del = [d for d in del_east_snaps if d['StartTime'].date() < delete_after_date]

    for today in east_del:
        print('Deleting:', today['SnapshotId'])
        response = ec2_source_east.delete_snapshot(
            SnapshotId=today['SnapshotId'],
        )

    del_west_snaps = \
        ec2_source_west.describe_snapshots(OwnerIds=['self'], Filters=[{'Name': 'tag:Done', 'Values': ['Copied']}])[
            'Snapshots']
    # west = date.today()
    west_del = [d for d in del_west_snaps if d['StartTime'].date() < delete_after_date]

    for west in west_del:
        print('Deleting:', west['SnapshotId'])
        response = ec2_source_west.delete_snapshot(
            SnapshotId=west['SnapshotId'],
        )


# create_copy()
# del_east_west()


if __name__ == '__main__':
    # parsing arguments
    args = parser.parse_args()
    # we can now access the arguments using dot method (args.copy, args.delete and args.retention)

    # since one of the two (copy or delete) arg MUST be provided, we generate an error when NONE are provided
    if not (args.copy or args.delete):
        parser.error('No action requested, add --copy and/or --delete')

    # Logic based on arguments passed
    if args.copy and args.delete:
        create_copy()
        del_east_west(args)

    elif args.copy:
        create_copy()

    elif args.delete:
        del_east_west(args)

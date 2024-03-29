import boto3
import botocore
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')


def has_pending_snapshot(volume):
	snapshots = list(volume.snapshots.all())
	return snapshot and snapshots[0].state == 'pending'


def filter_instances(project):
	"Filter instances by project"
	instances =[]

	if project:
		filters =[{'Name':'tag:Project','Values':[project]}]
		instances =ec2.instances.filter(Filters=filters)
	else:
		instances =ec2.instances.all()
	return instances

@click.group()
def cli():
	""" Shotty manages instances"""



@cli.group('Volumes')
def Volumes():
		"""Command for Volumes"""
@Volumes.command('list')
@click.option('--project', default=None, help="Only instances for project (tag Project:<name>)")
def list_Volumes(project):
	"List Volumes"
	instances = filter_instances(project)

	for i in instances:
		for v in i.volumes.all():
			print("," .join((
				v.id,
				i.id,
				v.state,
				str(v.size) + "GiB",
				v.encrypted and "encrypted" or "Not encrypted"
				)))
	return

@cli.group('snapshots')
def snapshots():
		"""Command for snapshots"""
@snapshots.command('list')
@click.option('--project', default=None, help="Only instances for project (tag Project:<name>)")
@click.option('--all','list_all',default=False, is_flag=True,help='List all snapshots for each volume, not just the most recent')
def list_snapshots(project,list_all):
	"List snapshots"
	instances = filter_instances(project)

	for i in instances:
		for v in i.volumes.all():
			for s in v.snapshots.all():
				print(",".join((
					s.id,
					v.id,
					i.id,
					s.state,
					s.progress,
					s.start_time.strftime("%c")


					)) )
				if s.state == 'completed' and not list_all:
					break
	return


@cli.group('instances')
def instances():
	""" Command for instances """
@instances.command('list')
@click.option('--project', default=None, help="Only instances for project (tag Project:<name>)")
def list_instances(project):
	"List EC2 instances"

	instances = filter_instances(project)
	

	for i in instances:
	    print(', '.join((
	    	i.id,
	    	i.instance_type,
	    	i.placement['AvailabilityZone'],
	    	i.state['Name'],
	    	i.public_dns_name,
	    	)))
	return 


@instances.command('stop')
@click.option('--project',default=None,help='Only instances for project(tag project)')

def stop_instances(project):
	"Stop EC2 instances"
	
	instances = filter_instances(project)


	for i in instances:
		print(f"Stopping {i.id}")
		try:
			i.stop()
		except botocore.exceptions.ClientError as e:
			print(f"Couldnt stop {i.id}" + str(e))
			continue
	return

@instances.command('start')
@click.option('--project',default=None,help='Only instances for project(tag project)')

def start_instances(project):
	"start EC2 instances"
	
	instances = filter_instances(project)


	for i in instances:
		print(f"Starting {i.id}")
		try:
			i.start()
		except botocore.exceptions.ClientError as e:
			print(f"Couldnt start {i.id}" + str(e))
			continue
	return

@instances.command('snapshot', help="Create snapshot for Volumes")
@click.option('--project',default=None,help='Only instances for project(tag project)')

def create_snapshots(project):
	""" Create snapshots for EC2 instances"""

	instances= filter_instances(project)

	for i in instances:
		print(f"stopping ...{i.id}")
		i.stop()
		i.wait_until_stopped()
		for v in i.volumes.all():
			if has_pending_snapshot(v):
				print(f"skipping..{v.id}")
			print(f"Creating snapshot of {v.id}")
			v.create_snapshot(Description='created by snapshotAnalyzer30K')

		print(f"Starting ...{i.id}")
		i.start()
		i.wait_until_running()

	print("Job's done")	
	return



if __name__ == '__main__':
	cli()
	
from setuptools import setup

setup(
	name='snapshotanalyzer30k',
	version='1.0',
	author ='RKS',
	author_email ='rks@amazon.com',
	description ='This is a tool to manage AWS EC2 Snapshots',
	license= 'GPLv3+',
	packages=['shotty'],
	url='https://github.com/gitrks/snapshotanalyzer30k',
	install_requires=['click','boto3'],
	entry_points='''
		[console_scripts]
		shotty=shotty.shotty:cli
		''',

	)
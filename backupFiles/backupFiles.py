#!/usr/bin/python3

import argparse
import sys
import os
from distutils.dir_util import copy_tree
from distutils.file_util import copy_file
import warnings
from datetime import datetime as dt

__version__ = '0.0.1'
__prog__ = 'backupFiles'
__name_version__ = __prog__ + ' ' + __version__

def output_log(log_file, processed, ignored):
	log_string = __name_version__ + '\n' + \
				dt.today().strftime('%Y-%m-%d-%H:%M:%S') + '\n\n' + \
				'Processed :\n' + \
				'\n'.join(elem for elem in processed) + \
				'\n\nIgnored :\n' + \
				'\n'.join(elem for elem in ignored) + '\n'
	print(log_string)
	if log_file is not None:
		log_file.write(log_string)
		log_file.close()

def main(args):
	with open(args.input_file, 'r') as f:
		files_to_bkp = [line.rstrip('\n') for line in f]

	print('Files/directories to backup :')
	print('\n'.join(elem for elem in files_to_bkp))
	print('')

	ignored = []
	processed = []

	for f in files_to_bkp:
		if not os.path.isabs(f):
			warnings.warn('File or directory ' + f + ' is not absolute')
			ignored.append(f)
			continue

		if not os.path.exists(f):
			warnings.warn('File or directory ' + f + ' does not exist, skipping...')
			ignored.append(f)
			continue

		destination = os.path.join(args.dest_folder, *f.split(os.sep))

		if os.path.isfile(f):
			os.makedirs(os.path.dirname(destination), exist_ok=True)
			(dest_name, _) = copy_file(f, destination,
									   preserve_mode=True, update=True)
			processed.append('{} -> {}'.format(f, dest_name))
		elif os.path.isdir(f):
			dest_names = copy_tree(f, destination,
								   preserve_mode=True, update=True)
			for i in dest_names:
				processed.append('{} -> {}'.format(i.replace(args.dest_folder, ''), i))
		else:
			warnings.warn(f + ' is neither a file or directory')
			ignored.append(f)
			continue

	output_log(args.log_file, processed, ignored)
	sys.exit(0)

def create_dir(string):
	if os.path.exists(string) and not os.path.isdir(string):
		raise argparse.ArgumentTypeError(repr(string) + ' exist but is not a directory.')
	if not os.path.exists(string):
		os.makedirs(string)
	return os.path.abspath(string)

def existing_file(string):
    if not os.path.isfile(string):
        raise argparse.ArgumentTypeError(repr(string) + " not found.")
    return os.path.abspath(string)

def parse_args():
	parser = argparse.ArgumentParser(description='Takes a list of files and directoried to backup' \
												 ' and copy them with folder structure in' \
												 ' destination folder')
	parser.add_argument('input_file', type=existing_file,
						help='Input file containing folders/files to backup')
	parser.add_argument('dest_folder', type=create_dir,
						help='Destination folder where to save the backup files')
	parser.add_argument('-v', '--version', action='version', version=__name_version__)
	parser.add_argument('-l', '--log_file', type=argparse.FileType('w'),
						help='Log file to store processed and ignored files lists')
	args = parser.parse_args()

	if args.log_file is not None:
		print('Log file : {}\n'.format(args.log_file.name))

	return args

if __name__ == '__main__':
	args = parse_args()
	main(args)

#!/usr/bin/env python3 

import shutil
import glob
import time
import sys
import os

def move():

	file_extension = 'md' #sys.argv[1]
	output_directory = '/home/joona/Documents/Notes' # sys.argv[2]
	
	while True:
		files = glob.glob(f'/home/joona/Downloads/*.{file_extension}')
		for file in files:

			shutil.move(file, output_directory)
			print(f'{os.path.basename(file)} moved to {output_directory}')

		time.sleep(5)

def print_help():
	print('Usage:')
	print('python3 move_files.py <file_extension> <output_directory>')


'''
if sys.argv[1] in ['--help', '-help', '-h'] or len(sys.argv) < 3:
	print_help()

else:
	move()

'''

move()
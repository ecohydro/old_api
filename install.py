import os
import pip

'''Intended to pip install the prerequesites (from requirements.txt) on a developer machine.

additionally for windows platforms this might be required to compile:
http://www.microsoft.com/en-us/download/details.aspx?id=44266
and git and python should be in the path

'''
f = open('requirements.txt','r')

for line in f:
	if 0 >= len(line.strip()) or '#' == line[0]:
		continue
	pip.main(['install', line])
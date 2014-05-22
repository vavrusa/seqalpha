#!/usr/bin/env python
import urllib2
import sys, os

PDB_PATH = "http://www.rcsb.org/pdb/files/%s"

def help():
    ''' Print help and exit. '''
    print('Usage: %s <directory>' % sys.argv[0])
    print('Parameters:')
    print('\t<directory> pointing to a path with \'list\' file of PDB structure names')
    print('Example:')
    print('"%s 3_plus_1" ... fetch PDB files for names in 3_plus_1/list' % sys.argv[0])
    sys.exit(1)

if len(sys.argv) < 2:
    help()
if '-h' in sys.argv or '--help' in sys.argv:
    help()

for local_dir in sys.argv[1:]:
    print '> updating "%s"' % local_dir
    basedir = os.getcwd()
    os.chdir(local_dir)

    ''' Read PDB file list '''
    with open('list') as listfile:
	for pdbname in listfile:
		pdbname = '%s.pdb' % (pdbname.strip())
		if os.path.isfile(pdbname):
			print '>  exists "%s"' % pdbname
			continue
		print '>  fetching "%s"' % pdbname
		remote_file = urllib2.urlopen(PDB_PATH % pdbname)
		output = open(pdbname,'w')
		output.write(remote_file.read())
		output.close()

    os.chdir(basedir)

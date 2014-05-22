#!/usr/bin/env python
import sys, os, glob, getopt
import tetrad
from Bio.PDB import *

def analyze_model(name, model, qclass, result_file):
    ''' Spatial analysis of model chains. '''
    # Analyze guanine tetrads
    result = tetrad.analyze(model)
    if result is None:
        return
    if result_file:
        (planarity, planarity_std, twist, twist_std, chains, topology, loops) = result
        result_file.write('%s\t%s\t%.02f\t%.02f\t%.02f\t%.02f\t%d\t%s\t%s\n' % \
                          (name, qclass, planarity, planarity_std, twist, twist_std, chains, topology, loops))


def process_file(pdbfile, qclass = None, result_file = None):
    ''' Process and analyze models found in given PDB file. '''
    print('> processing "%s"' % pdbfile)
    parser = PDBParser()
    try:
        name = os.path.splitext(os.path.basename(pdbfile))[0]
        structure = parser.get_structure(name, pdbfile)
        # Analyze each model separately
        for model in structure:
            analyze_model(structure.get_id(), model, qclass, result_file)
        # Return success
        return 0
    # Failed to open PDB file for reading
    except IOError:
        print('> could not open file "%s"' % pdbfile)
        return 1

def process_path(dirname, result_file = None):
    ''' Process PDB files in a path. '''
    return_code = 0
    if os.path.isdir(dirname):
        for filename in glob.glob(dirname + '/*.pdb'):
            return_code = process_file(filename, qclass = dirname, result_file = result_file)
            if return_code != 0:
                break
    else:
        process_file(sys.argv[1])
    return return_code

def class_description(dirname):
    ''' Read DESCRIPTION file for given quadruplex class. '''
    with open(dirname + '/DESCRIPTION') as description:
        return description.readlines()

def help():
    ''' Print help and exit. '''
    print('Usage: %s [-o] [directory]' % sys.argv[0])
    print('Parameters:')
    print('\t-o <output>, --output=<output>\tOutput for the analysis results (TSV) (default: gqclass.tsv)')
    print('\t[directory]\tOptional path to a GQ family directory.')
    print('Notes:')
    print('\tIf the directory is not set, all monomeric GQ families are processed and the result')
    print('\tis written to the <output>/"gqclass.tsv" file.')
    print('Example:')
    print('"%s"                 ... process all monomeric GQ families' % sys.argv[0])
    print('"%s 3_plus_1 basket" ... process 3+1 and basket-type families' % sys.argv[0])
    sys.exit(1)

if __name__ == '__main__':

    return_code = 0

    # Process parameters
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:", ["help", "output="])
    except getopt.GetoptError as err:
        print str(err)
        help()
    output = 'gqclass.tsv'
    for o, a in opts:
        if o in ('-h', '--help'):
            help()
        elif o in ('-o', '--output'):
            output = a
        else:
            help()

    # Process predefined GQ classes or set/single PDB files
    with open(output, 'w') as result_file:
        # Write header
        result_file.write(';Planarity[A]\tPlanarity std[A]\tTwist[deg]\tTwist std[deg]\tChains\tTopology\tLoops\n')
        # Process parameters
        if len(args) > 0:
            for arg in args:
                process_path(arg, result_file)
        else:
            # Write results
            for qclass in ['basket', 'chair_type', '3_plus_1', '2_plus_2', 'propeller', 'pdl', 'ppl', 'pplp']:
                process_path(qclass, result_file)

    # Return proper code
    sys.exit(return_code)

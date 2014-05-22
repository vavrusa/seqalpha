#!/usr/bin/env python

import sys
from Bio import SeqIO, SeqRecord
import random
import runnable
import os
import string

class Runnable(runnable.Runnable):
    ''' Generic runnable that accepts any data input and produces random scored
        sequences. '''

    @staticmethod
    def info():
        ''' Compulsory method to return runnable name and parameters. '''
        return {'name': 'Dummy', 'accepts': '*'}

    def __init__(self, data_in, param):
        ''' Set up runnable data input, set output type and result fields. '''
        runnable.Runnable.__init__(self, data_in)
        self.type = runnable.ResultScore
        self.fields = ['Accession', 'Score', 'Sequence']

    def run(self, data_out = None):
        ''' Process the input data and write both results and a result file. '''
        out = self.out_stream(data_out)
        self.result = []
        # Generate 10 random results
        for record in xrange(0, 10):
            randstr = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            accession = random.choice(['5HSA', '3HSA', 'NR_', 'NC_']) + randstr
            seq = ''.join(random.choice('acgt') for x in range(20))
            # Write the triple into the results
            self.result.append( ( accession, random.random(), seq) )
            # Store the output file in FASTA
            out.write('>%s\n%s\n' % (accession, seq))
            self.processed += 1
        # Finalize data
        self.planned = self.processed

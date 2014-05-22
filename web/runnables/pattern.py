#!/usr/bin/env python

import re
import sys
from Bio import SeqIO, SeqRecord
import runnable

class Runnable(runnable.Runnable):
    ''' Basic RegEx pattern matching. '''

    data = None
    pattern = None
    matched_records = 0

    @staticmethod
    def info():
        return {'name': 'RegEx',
                'accepts': 'fasta',
                'param': {
                    'RegEx to search':'text|query|g{3,}[acgtu]{1,7}g{3,}[acgtu]{1,7}g{3,}[acgtu]{1,7}g{3,}'
                }}

    def __init__(self, data_in, param):
        runnable.Runnable.__init__(self, data_in)
        self.type = runnable.ResultFasta
        self.fields = ['Rule', 'Matched', 'Total']
        self.pattern = param['query']

    def sequence_match(self, record, regex, fasta_out):
        match_list = regex.findall(str(record.seq))
        for match in match_list: 
            fasta_out.write('>%s\n' % record.id)
            fasta_out.write(match + '\n')
            self.matched_records += 1

    def run(self, data_out = None):
        self.result = []
        self.planned = 0
        self.procesed = 0
        
        # Open source / destination files
	fasta_in = self.in_stream()
	fasta_out = self.out_stream(data_out)
	regex = re.compile(self.pattern)

        # Parse FASTA data
	for record in SeqIO.parse(fasta_in, 'fasta'):
	    self.sequence_match(record, regex, fasta_out)
	    self.processed += 1

	# Finalize data
	self.result.append([ self.pattern, self.matched_records, self.processed ])
	self.planned = self.processed


def main():
	if len(sys.argv) != 3:
		print('%s <pattern> <fasta>' % sys.argv[0])
		sys.exit(1)

	matcher = Runnable(sys.argv[2], sys.argv[1])
	matcher.run(data_out = '-')

if __name__ == '__main__':
    main()

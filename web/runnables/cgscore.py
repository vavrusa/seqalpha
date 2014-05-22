#!/usr/bin/env python

import re
import sys
from operator import itemgetter
from Bio import SeqIO, SeqRecord
import runnable

class Runnable(runnable.Runnable):
        ''' Calculate cG/cC score on the sequences in FASTA. '''

        @staticmethod
        def info():
            return {'name': 'Quadruplex cG/cC', 'accepts': 'fasta', 'param': {'cG/cC score limit':'text|limit|100'} }

	def __init__(self, data_in, param):
            runnable.Runnable.__init__(self, data_in)
            self.type = runnable.ResultScore
            self.fields = ['Accession', 'cG/cC Score', 'Sequence']
            self.score_limit = None
            if 'limit' in param:
                self.score_limit = float(param['limit'])

        def conseq_score(self, seq_str, nucleotide):
            """ Scoring is described in http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3902908/ """
            score = 0
            length = 1
            while length < len(seq_str):
                nlet_count = seq_str.count(nucleotide * length)
                if nlet_count == 0:
                    break
                score += length * 10 * nlet_count
                length += 1
            return score

	def eval_sequence(self, record, out):
                cg_score = self.conseq_score(str(record.seq), 'g')
                cc_score = self.conseq_score(str(record.seq), 'c')
                if cc_score == 0: # PMC3902908 doesn't specify, assume 1C
                    cc_score = 1
                score = cg_score / float(cc_score)
                # Cut off sequences below score
                if self.score_limit is not None and score < self.score_limit:
                    return
                # TODO: This should be GFF or something
                self.result.append( (record.id, score, str(record.seq)) )
                out.write('>%s\n%s\n' % (record.id, str(record.seq)))

	def run(self, data_out = None):
            self.planned = 0
            self.processed = 0
            self.result = []

            fasta_in = self.in_stream()
            score_out = self.out_stream(data_out)
	    for record in SeqIO.parse(fasta_in, 'fasta'):
		self.eval_sequence(record, score_out)
                self.processed += 1

            self.planned = self.processed
            self.result.sort(key = itemgetter(1), reverse = True)

def main():
        params = {}
	if len(sys.argv) < 2:
		print('%s <fasta> [limit]' % sys.argv[0])
		sys.exit(1)
        if len(sys.argv) == 3:
                params['limit'] = float(sys.argv[2])

	matcher = Runnable(sys.argv[1], params)
	matcher.run(data_out = '-')

if __name__ == '__main__':
    main()

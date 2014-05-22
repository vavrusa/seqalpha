#!/usr/bin/env python

import re
import sys
import subprocess
import tempfile
from operator import itemgetter
import runnable

class Runnable(runnable.Runnable):
    ''' ViennaRNA Package RNAfold wrapper, predict structure stability. '''

    @staticmethod
    def info():
        return {'name': 'RNAfold score', 'accepts': 'fasta', 'param': {'Mfe[kcal/mol] limit':'text|limit|-20.0'} }

    def __init__(self, data_in, param):
        runnable.Runnable.__init__(self, data_in)
        self.type = runnable.ResultScore
        self.mfe_limit = 100.0
        self.fields = ['Accession', 'Mfe [kcal/mol]', 'Fold', 'Sequence']
        if 'limit' in param:
            self.mfe_limit = float(param['limit'])

    def parse_rnafold_triple(self, accession, sequence, score):
        accession = accession[1:] # >ACCESSION
        score = score.split(' ')  # fold energy
        if len(score) != 2:
            return # parse error

        # Format result line
        # TODO: This should be GFF or something
        mfe = float(score[1].strip('()'))
        if mfe < self.mfe_limit:
            self.result.append( (accession, mfe, score[0], sequence)  )
            self.processed += 1

    def parse_rnafold_result(self, result_file, data_out):

        self.planned = 0
        self.processed = 0
        self.result = []
        score_out = self.out_stream(data_out)

        # Process triples in output file
        lines = []
        for line in result_file:
            lines.append(line.strip())
            if len(lines) == 3:
                self.parse_rnafold_triple(lines[0], lines[1], lines[2])
                lines = []

        # Sort by score
        self.planned = self.processed
        self.result.sort(key = itemgetter(1))

        # Write to file
        for (accession, mfe, fold, seq) in self.result:
            score_out.write('>%s\n%s\n' % (accession, seq))

        score_out.flush()


    def run(self, data_out = None):
        rnafold_cmd = ['RNAfold', '--noPS', '-g']
        fasta_in = self.in_stream()
        rnafold_out = tempfile.NamedTemporaryFile()

        # Process RNAfold
        proc = subprocess.Popen(rnafold_cmd, stdout = rnafold_out, stdin = fasta_in)
        if proc.wait() != 0:
            return 1

        # Process output
        rnafold_out.flush()
        rnafold_out.seek(0)
        self.parse_rnafold_result(rnafold_out, data_out)

def main():
    if len(sys.argv) < 2:
        print('%s <fasta> [params]' % sys.argv[0])
        sys.exit(1)
    params = None
    if len(sys.argv) > 2:
        params = ' '.join(sys.argv[3:])

    matcher = Runnable(sys.argv[1], params)
    matcher.run(data_out = '-')

if __name__ == '__main__':
    main()

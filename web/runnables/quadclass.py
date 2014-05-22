#!/usr/bin/env python

import sys
from Bio import SeqIO
import markdown
import runnable
from quadclasslib import seqlearn, quadclass

class Runnable(runnable.Runnable):
    ''' Quadclass wrapper for GQ structure prediction. '''

    @staticmethod
    def info():
        return {'name': 'Quadclass', 'accepts': 'fasta'}

    def __init__(self, data_in, param):
        runnable.Runnable.__init__(self, data_in)
        self.type = runnable.ResultGFF
        self.fields = ['Accession', 'Sequence', 'Topology']

    def eval_sequence(self, id, seq, out):
        # Load class list
        gq_classlist = seqlearn.load_classlist('runnables/quadclasslib/gqclass.tsv')
        pval_table = seqlearn.calc_pval(gq_classlist)
        candidates = seqlearn.fit(gq_classlist, seq.upper(), pval_table)
        configurations = []
        for key in candidates:
            configurations.append('%s:%s/%s' % (key[1], key[0], ','.join(candidates[key])))
        self.result.append( (id, seq, ' '.join(configurations)) )
        out.write('%s %s %s\n' % self.result[-1][0:3])

    def run(self, data_out = None):
        self.planned = 0
        self.processed = 0
        self.result = []

        in_type = runnable.file_type(self.data_in)
        score_out = self.out_stream(data_out)
        file_in = self.in_stream()

        if in_type == runnable.ResultFasta or in_type == runnable.ResultScore:
            for record in SeqIO.parse(file_in, 'fasta'):
                self.eval_sequence(record.id, str(record.seq), score_out)
                self.processed += 1
        if in_type == runnable.ResultGFF:
            pass

        self.planned = self.processed

    @staticmethod
    def get_info(param):
        ''' Get GQ class information. '''
        topo = param[0]
        name = param[1].lower()
        info = {}
        # Read description file
        description = quadclass.class_description('runnables/quadclasslib/' + name)
        # First line contains prettified name
        info['name'] = description.pop(0).strip() + ' (%s)' % topo
        info['image'] = topo.lower()
        # Markdown
        info['description'] = markdown.markdown(''.join(description).strip())
        return info

def main():
    if len(sys.argv) != 2:
        print('%s <fasta>' % sys.argv[0])
        sys.exit(1)

    matcher = Runnable(sys.argv[1], {})
    matcher.run(data_out = '-')

if __name__ == '__main__':
    main()

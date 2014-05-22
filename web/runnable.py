import sys
import uuid
import tempfile

RESULT_PATH = 'results'

''' These constants define result type and are used as a hint for.
    Plotting the data.
'''
ResultNone =  'result_none'
ResultFasta = 'result_fasta' 
ResultScore = 'result_score' 
ResultGFF   = 'result_gff' 

def result_suffix(result_type):
    if result_type == ResultNone:  return ''
    if result_type == ResultFasta: return '.fasta'
    if result_type == ResultScore: return '.score'
    if result_type == ResultGFF:   return '.gff'

def file_type(filename):
    if filename.endswith('.fasta'): return ResultFasta
    if filename.endswith('.score'): return ResultScore
    if filename.endswith('.gff'): return ResultGFF
    return ResultNone

class Runnable:
    ''' Generic runnable interface. '''

    uid = None
    type = ResultNone
    fields = {}
    result = []
    processed = 0
    planned = 0
    data_in = None
    data_out = None
    persistent = False

    def __init__(self, data_in):
        self.data_in = data_in
        self.uid = str(uuid.uuid1())
        pass

    def progress(self):
        if self.planned == 0:
            return -1 
        return self.processed / self.planned

    def in_stream(self):
        return open(self.data_in)

    def out_stream(self, data_out = None):
        out = None
        self.data_out = data_out
        if data_out is None:
            out = tempfile.NamedTemporaryFile(delete = False, prefix = 'result', suffix = result_suffix(self.type), dir = RESULT_PATH)
            self.data_out = out.name
        elif data_out is "-":
            out = sys.stdout
        else:
            out = open(data_out, 'r')
        return out

    def pickle(self):
        ''' Pickle the runnable object with the results. '''
        return dict(
                uuid      = self.uid,
                type      = self.type,
                fields    = self.fields,
                result    = self.result,
                processed = self.processed,
                data_in   = self.data_in,
                data_out  = self.data_out);

class Search:
    ''' Single search representation. '''

    def __init__(self, uid):
        self.uid = uid
        self.persistent = False
        self.task_list = []

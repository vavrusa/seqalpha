#!/usr/bin/env python
import re
import sys, getopt
import pylab as pl
from sklearn.metrics import roc_curve, auc
from matplotlib.lines import Line2D

def load_classlist(source = 'gqclass.tsv'):
    ''' Load sequence classlist. '''
    gq_classlist = dict()
    with open(source) as datafile:
        for line in datafile:
            # Skip header
            if line.startswith(';'):
                continue
            # Unpack rows of data
            (name, qclass, planarity, planarity_std, twist, twist_std, chains, topology, loops) = line.strip().split('\t')
            if not qclass in gq_classlist:
                gq_classlist[qclass] = {'id': qclass, 'topology': set([])}
            # Inosine -> Guanine ambiguity
            loops = '|'.join(loops.replace('I', 'G').split('|')[0:3])
            gq_classlist[qclass]['topology'].add((topology, loops))
    return gq_classlist

def loop_len_config(loops):
    ''' Return length configuration for L{1,2,3} loops. '''
    try:
        shortest = min([re.match(r'^G+', loop).end(0) for loop in loops])
    except ValueError:
        return ''
    return ''.join([str(len(loop) - shortest) for loop in loops])

def loop_len_dt(loops):
    ''' Return length derivation for L{1,2,3} loops. '''
    config = loop_len_config(loops)
    if len(config) < 1:
        return '?'
    result = config[0]
    for i in range(1, len(config)):
        if config[0] < config[i]:
            result += '+'
        elif config[0] == config[i]:
            result += '='
        else:
            result += '-'
    return result

def loop_composition(loops):
    ''' Calculate loop sequences nucleotide composition expressed as nucleotide relative frequency. '''
    composition = {'A':0, 'C':0, 'G':0, 'T':0, 'U':0}
    if len(loops) < 1:
        return composition
    n_sum = 0
    for loop in loops:
        for n in loop:
            composition[n] += 1
            n_sum += 1
    # Normalize nucleotide frequency
    norm = 1.0 / n_sum
    return {n: round(composition[n] * norm, 2) for n in composition}

def find_fragments(seq):
    ''' Identify L{1,2,3} loops in sequence. '''
    loops = []
    loop = ''
    in_loop = False
    seq = seq[seq.find('G'):]
    for n in seq:
        loop += n
        if not in_loop:
            # Find loop opening
            if n != 'G' and len(loop) > 0:
                in_loop = True
        else:
            # G2 is a loop closure
            if loop.endswith('GG'):
                loops.append(loop[:-2])
                loop = loop[-2:]
                in_loop = False
    # Join shortest G-tracts until L1-L3 are identified
    while len(loops) > 3:
        shortest = min(enumerate(loops), key = lambda x: x[1].count('G'))[0]
        # Merge with previous loop
        if shortest > 0:
            loops[shortest - 1] += loops[shortest]
        loops.pop(shortest)

    return loops

def fit_candidate(candidates, qclass, topology, reason, val, pval):
    reason_str = '%s:%s:%.02f' % (reason, val, pval)
    key = (qclass, topology)
    if key in candidates:
        candidates[key].add(reason_str)
    else:
        candidates[key] = set([reason_str])

def get_pval(pval, ptype, qclass):
    ''' Return p-value for given class. '''
    n = 0
    clslist = pval[ptype]
    for cls in clslist.keys():
        n += clslist[cls]
    return 1 - clslist[qclass] / float(n)

def ins_pval(clslist, obs, qclass):
    ''' Insert observation of an occurence in the qclass. '''
    if obs not in clslist:
        clslist[obs] = dict()
    if qclass not in clslist[obs]:
        clslist[obs][qclass] = 0
    clslist[obs][qclass] += 1

def calc_pval(clslist):
        ''' Calculate p-values for predictors. '''
        pval = { 'dt': dict(), 'config': dict() }
        for qclass, info in clslist.items():
            for (topology, loops) in info['topology']:
                ins_pval(pval['dt'], loop_len_dt(loops.split('|')), qclass)
                ins_pval(pval['config'], loop_len_config(loops.split('|')), qclass)
        return pval

def fit(gq_classlist, loops, pval_table):
    ''' Decompose input sequence and attempt to fit it to the identified GQ classes. '''
    if len(loops) == 0:
        return set([])
    config = loop_len_config(loops)
    len_dt = loop_len_dt(loops)
    n_freq = loop_composition(loops)
    candidates = dict()

    # Calculate least error composition
    k3best = 1.0
    k3best_match = (None, None, None)

    for qclass, info in gq_classlist.items():
        for (gq_topology, gq_loops) in info['topology']:
            # Match based on L1-L3 length configuration
            candidate_config = loop_len_config(gq_loops.split('|'))
            if config == candidate_config:
                pval = get_pval(pval_table['config'], config, qclass)
                fit_candidate(candidates, qclass, gq_topology, 'length_match', config, pval)
            # Match based on length sequence derivation
            gq_len_dt = loop_len_dt(gq_loops.split('|'))
            if len_dt == gq_len_dt:
                pval = get_pval(pval_table['dt'], len_dt, qclass)
                fit_candidate(candidates, qclass, gq_topology, 'length_dt', len_dt, pval)
            # Match based on sequence composition
            gq_n_freq = loop_composition(gq_loops.split('|'))
            k3err = sum([abs(n_freq[n] - gq_n_freq[n]) for n in gq_n_freq.keys()]) / 5.0
            if k3err < k3best:
                k3best = k3err
                k3best_match = (qclass, gq_topology, gq_loops)

    # Pick least sequence composition error match
    if k3best < 1.0:
        (qclass, gq_topology, gq_loops) = k3best_match
        fit_candidate(candidates, qclass, gq_topology, 'composition', 'match', k3best)

    return candidates

def evaluate_k(qclass, pred, y_pred, y_true, why = None):
    best = [None, 1.0]
    for key in pred:
        for reason_str in pred[key]:
            reason = reason_str.split(':')
            pval = float(reason[2])
            if why is None:
                if pval < best[1]:
                    best = (key[0], pval)
            else:
                if pval < best[1] and reason[0] == why:
                    best = (key[0], pval)

    y_true.append(best[0] == qclass)
    y_pred.append(1 - best[1])
    return best

def evaluate_show(name, y_pred, y_true, pl, style):
    print '%s accuracy: %f' % (name, y_true.count(True)/float(len(y_true)))
    fpr, tpr, thresholds = roc_curve(y_true, y_pred)
    # Plot ROC curve
    pl.plot(fpr, tpr, marker=style, label=name)

def validate(gq_classlist, input_file, pval_table, graph = True):
    k_style = [ '^', 'o', 's' ]
    k_name = [ 'length_match', 'length_dt', 'composition' ]
    y_pred = [ [], [], [] ]
    y_true = [ [], [], [] ]
    for line in input_file:
        line = line.strip().split('\t')
        qclass, loops = (line[1], line[8].replace('I', 'G').split('|'))
        pred = fit(gq_classlist, loops, pval_table)
        for k in range(len(k_name)):
            evaluate_k(qclass, pred, y_pred[k], y_true[k], k_name[k])
    # Plot ROC curve
    pl.clf()
    dpi = 96.0
    fig = pl.figure(1, figsize=(round(1000/dpi), round(600/dpi)))
    for k in range(0, len(k_name)):
        evaluate_show(k_name[k], y_pred[k], y_true[k], pl, k_style[k])
    pl.xlim([0.0, 1.0])
    pl.ylim([0.0, 1.0])
    pl.xlabel('False Positive Rate')
    pl.ylabel('True Positive Rate')
    pl.title('Receiver operating characteristic')
    pl.plot([0, 1], [0, 1], 'k--')
    pl.legend(loc="lower right")
    pl.show()
    fig.savefig('seqlearn-roc.pdf')

def help():
    ''' Print help and exit. '''
    print('Usage: %s [-t <path>] [-v <path>] [-g] [sequences] ' % sys.argv[0])
    print('Parameters:')
    print('\t-t <path>, --training=<path>\tTraining dataset (TSV file).')
    print('\t-v <path>, --validate=<path>\tValidation dataset (TSV file).')
    print('\t-g, --graph\tPrint ROC curve.')
    print('\t[directory]\tDirectories with GQ class families.')
    print('Notes:')
    print('\tThe "-t" default is "gqclass.tsv".')
    print('Example:')
    print('"%s"                                  ... print all predictors and p-values' % sys.argv[0])
    print('"%s -t classes.tsv GGGTGGGTTAGGGTGGG" ... predict the topology for given sequence' % sys.argv[0])
    sys.exit(1)

if __name__ == '__main__':

    # Process parameters
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:v:g", ["help", "training=", "validate=", "graph"])
    except getopt.GetoptError as err:
        print str(err)
        help()

    class_file = 'gqclass.tsv'
    validate_file = None
    show_graph = False
    for o, a in opts:
        if o in ('-h', '--help'):
            help()
        elif o in ('-t', '--training'):
            class_file = a
        elif o in ('-v', '--validate'):
            validate_file = a
        elif o in ('-g', '--graph'):
            show_graph = True
        else:
            help()

    gq_classlist = load_classlist(class_file)
    pval = calc_pval(gq_classlist)

    # Accept sequences as parameters
    if len(args) > 0:
        for seq in args:
            seq = seq.trim()
            print('> %s ...' % seq)
            loops = find_fragments(seq)
            print('%s %s %s %s' % (loop_len_config(loops), loop_len_dt(loops), '|'.join(loops), loop_composition(loops).values()))
            candidates = fit(gq_classlist, loops, pval)
            for key in candidates:
                print '%s (%s)' % (key[0], key[1])
                for reason_str in candidates[key]:
                    reason = reason_str.split(':')
                    print(' * %s..\'%s\' p-value=%s' % (reason[0], reason[1], reason[2]))

    # Validate file if presented
    elif validate_file != None:
            validate(gq_classlist, open(validate_file), pval)

    # No parameters, just print out current fitting info
    else:  
        print('; Loop lenghts, Loop lengths dt, p-val(lengths), p-val(dt), topology, loops, composition')
        for qclass, info in gq_classlist.items():
            print('; ---- %s ----' % qclass)
            for (topology, loops) in info['topology']:
                dt = loop_len_dt(loops.split('|'))
                config = loop_len_config(loops.split('|'))
                dt_pval = get_pval(pval['dt'], dt, qclass)
                dt_config = get_pval(pval['config'], config, qclass)
                print config, dt, "%.03f %.03f" % (dt_config, dt_pval), topology, loops, \
                        loop_composition(loops.split('|')).values()

#!/usr/bin/env python
import sys, getopt
import numpy as np
import pylab as pl
from sklearn import datasets, preprocessing, metrics, svm, neighbors
from sklearn.tree import DecisionTreeClassifier
import matplotlib.pyplot as plt

X = []
Y = []
weights = []
class_weights = dict()
class_ids = dict()
class_names = dict()
show_graph = False

def get_line_marker(line):
    # Unpack rows of data
    (name, qclass, planarity, planarity_std, twist, twist_std, chains, config, loops) = line.strip().split('\t')

    # Separate structures by strand count
    planarity_coeff = float(planarity) + int(chains)*2.0
    twist_coeff = float(twist_std)**2 + int(chains)*10.0

    return (qclass, [twist_coeff, planarity_coeff])

def register_class(qclass):
        # Calculate class weights
        if qclass not in class_names:
            class_names[qclass] = len(class_names)
            class_ids[class_names[qclass]] = qclass
            class_weights[class_names[qclass]] = 0
        class_weights[class_names[qclass]] += 1

def help():
    ''' Print help and exit. '''
    print('Usage: %s [-t <path>] [-g] [directory] ' % sys.argv[0])
    print('Parameters:')
    print('\t-t <path>, --training=<path>\tTraining dataset (TSV file).')
    print('\t-g, --graph\tShow decision surface plot.')
    print('\t[directory]\tDirectories with GQ class families.')
    print('Notes:')
    print('\tThe "-t" default is "gqclass.tsv".')
    print('Example:')
    print('"%s -t training.tsv newset" ... process spatial data from quadclass results' % sys.argv[0])
    sys.exit(1)

# Process parameters
try:
    opts, args = getopt.getopt(sys.argv[1:], "hgt:", ["help", "graph", "training="])
except getopt.GetoptError as err:
    print str(err)
    help()

training_file = 'gqclass.tsv'
for o, a in opts:
    if o in ('-h', '--help'):
        help()
    elif o in ('-g', '--graph'):
        show_graph = True 
    elif o in ('-t', '--training'):
        training_file = a
    else:
        help()

# Load classification markers
with open(training_file) as datafile:
    for line in datafile:

        # Skip header
        if line.startswith(';'):
            continue
        # Get geometric properties from the TSV line
        qclass, marker = get_line_marker(line)
        register_class(qclass)

        X.append(marker)
        Y.append(class_names[qclass])

# Recalculate weights
for i in xrange(0, len(Y)):
    weights.append( class_weights[ Y[i] ] )

# Normalize data
h = .01  # step size in the mesh
X = preprocessing.scale(np.array(X))
Y = np.array(Y)

# Fit the models
clf = DecisionTreeClassifier()
#clf = neighbors.KNeighborsClassifier()
#clf = svm.SVC(C=1.0, kernel='linear')
clf.fit(X, Y)

x_min, x_max = X[:, 0].min() - .5, X[:, 0].max() + .5
y_min, y_max = X[:, 1].min() - .5, X[:, 1].max() + .5

# Prediction
for input_set in args:
    print '> predicting', input_set
    with open(input_set) as fit_data:
        pred_X = []
        expect_Y = []
        for line in fit_data:
            # Skip header
            if line.startswith(';'):
                continue
            # Get geometric properties from the TSV line
            qclass, marker = get_line_marker(line)
            if qclass not in class_names:
                continue
            pred_X.append(marker)
            expect_Y.append(class_names[qclass])
        # Predict
        expect_Y = np.array(expect_Y)
        pred_X = preprocessing.scale(np.array(pred_X))
        pred_Y = clf.predict(pred_X)
        # Print metrics
        print 'Accuracy: %d/%d' % (metrics.accuracy_score(expect_Y, pred_Y, normalize=False), len(pred_Y))
        print 'Accuracy: %f (normalized)' % metrics.accuracy_score(expect_Y, pred_Y)


# Plot the decision boundary
if show_graph:
    dpi = 96.0
    colors = pl.cm.Paired(np.linspace(0,1,len(class_names)))
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    fig = pl.figure(1, figsize=(round(1000/dpi), round(600/dpi)))
    pl.pcolormesh(xx, yy, Z, cmap = pl.cm.Paired)

    # Plot also the training points
    for i in range(len(class_names)):
        idx = np.where(Y == i)
        pl.scatter(X[idx, 0], X[idx, 1], c = colors[i], label = class_ids[i])
    pl.xlabel('Twist')
    pl.ylabel('Planarity')
    pl.xlim(xx.min(), xx.max())
    pl.ylim(yy.min(), yy.max())
    pl.xticks(())
    pl.yticks(())
    pl.legend()
    pl.show()
    fig.savefig('decision-surface.png')

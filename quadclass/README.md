# Quadclass library and CLI tools

The library requires a Python with a BioPython module to handle I/O formats.
The quadlearn tool additionally requires an sklearn module for machine learning.

## Requirements

The library requires Python and addditionally a BioPython library for the FASTA/PDB reading and writing:

 	$ pip install biopython
	$ pip install markdown 
	$ pip install sklearn

Each of the utilities supports the `-h` or `--help` parameter with an example usage and a short overview
of what the tool does.

## Tools

### pdbfetch

This pdbfetch is a helper tool to fetch PDB files from a remote RCSB PDB servers. The only parameter is directory, that
contains a `list`  file with PDB structure names. The tool checks the existence of the PDB files in that folder and
downloads only missing files. The source code does not include PDB files, but only lists, therefore populating the directories
with PDB files is required before the structure analysis.

	$ ./pdbfetch.py 3_plus_1

### quadclass

This tool is an interface for the `tetrad.py` PDB structure analysis library. Similarly to the pdbfetch tool, the tool accepts an optional
directory name (or list of directories) as a parameter. However, if no parameter is supplied, all known intramolecular GQ families are evaluated, and the metrics are written
to the `gqclass.tsv` TSV file for further processing.

	$ ./quadclass.py unknown 
	> processing "unknown/1EAM.pdb"
 	[!!] less than 8 DGs found, ignoring
	> processing "unknown/1EVM.pdb"
 	* scanning model <Model id=0>, 12 DGs
  	  - assembly: 3 tetrads
	  - mean planarity: 0.65 A, stddev 0.17 A
	  - twist angle: 0.44 rad (25.32 deg), stddev 0.07
	  - chains: 4, consensus: AGGGT
	  - topology: O, fragments: GGGT

### quadlearn

The tool for learning and fitting, using the the PDB structure spatial metrics. The input is a training and test sets, both in form of a TSV file produced by the
quadclass tool. The ML learning algorithm is trained on the twist angle and planarity metrics parameters from the
training set and plots a decision surface along with the estimated GQ family predictions for each entry in the test set.

	$ ./quadlearn.py -t train90.tsv control.tsv

### seqlearn


The tool for prediction of the GQ topologies from the sequences. The input of the program is a sequence (or list of sequences) as parameters, and optionally a training TSV data set.
If no sequence is passed to the tool, the whole training set is processed and the overview of all predictors including the p-values is printed to the standard output.

	$ ./seqlearn.py GGGTTGGGTTAGGGTTGGG
	> GGGTTGGGTTAGGGTTGGG ...
	232 2+= GGGTT|GGGTTA|GGGTT
	propeller (PPPD)
 	 * length_match..'232' p-value=0.50
 	 * length_dt..'2+=' p-value=0.67

## Evaluating the performance of the predictors

The training and testing sets can be found in the `test` subdirectory. Both quadlearn and seqlearn tools
support a performance evaluation and custom data set splits. There are test data sets included, which are derived
from the quadclass analysis of all available structures and randomized.

### Structure classification

The quadlearn tool supports a `-t` parameter for a training set:

	$ ./quadlearn.py -g -t train80.tsv test20.tsv # 80-20 split

### Structure prediction

The `-g`  parameter shows the ROC curves, which is also saved in the `seqlearn-roc.pdf` file:

	$ ./seqlearn.py -g -t train80.tsv -v test20.tsv # 80-20 split



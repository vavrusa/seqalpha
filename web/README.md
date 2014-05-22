# Web interface

The Flask-based web interface supporting the filtering of the input dataset and visualization of the results.
There are three main components to the website:

* Datasets - user-uploadable data, often in an interchangeable format
* Runnables - specific operations over the datasets with given parameters
* Visualizations - the interpretation of the results, currently several plots are available
                   and a GQ-specific interpretation 

## Dependencies

* Python 2.6+
* Flask (http://flask.pocoo.org/)
* Jinja2 (http://jinja.pocoo.org/docs/)
* BioPython (http://biopython.org)
* Python-Markdown (http://pythonhosted.org//Markdown/)
* ViennaRNA Package (https://www.tbi.univie.ac.at/~ronny/RNA) for the RNAfold runnable

### ViennaRNA Package

The ViennaRNA installation instructions can be found [here](http://www.tbi.univie.ac.at/RNA/documentation.html#install).

## Installation

No installation is neccessary, the default host is '0.0.0.0' and port 5000.
You can change the configuration in the `seqalpha.py` file config and run it:

	$ vim seqalpha.py # Edit configuration
	$ python ./seqalpha.py
	* Running on http://0.0.0.0:5000/
	* Restarting with reloader

### Deployment as WSGI containers

Depends on the server, there is a good tutorial on the [Flask webpage](http://flask.pocoo.org/docs/deploying/uwsgi/)
on uWSGI deployment.

### Executing runnables from CLI

It is possible (although inconvenient) to execute runnables from CLI as well:

	$ python runner.py cgscore data/5UTRaspic_small.fasta 10
	>5HSAA000316
	agaagggagtgaagataaga

## Exploring

The user interface presents a header in the top of the page, which allows:

* To select or upload a custom data set
* To execute a filtering operation with given parameters
* To resume a previous search

### Custom data sets

That depends on what you're looking for! For example human untranslated regions
can be found at the [ASPicDB](http://ebi.edu.au/ftp/databases/UTR/data/).
Note that the web interface accepts uncompressed FASTA only.

### Search results

The search results are presented as a sequence of filtering operations. Each filtering operation works with the results
from the previous operations. Each search result may be discarded or saved for future continuation.
A single result is represented by a short header containing the name of the operation, results, links to FASTA/GFF data
and the button to hide/remove the result.

### The data table

The filtered data is often presented in form of a table and charts to provide a visual cue of the filtering.
Some charts like the quartile split are interactive. The table itself is often interactive as well,
for example the `quadclass` runnable makes the rows interactive, so that they expand upon click and show a
detailed breakdown on the predictions. The accession ids are often clickable as well, leading to an external page
with the description.

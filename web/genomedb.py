import glob
import os

class Genome:
    """ Genome representation """

    id = ""
    resource = None

    def __init__(self, resource):
        self.resource = resource

    def __cmp__(self, other):
        return cmp(self.id, other.id)

    def __hash__(self):
        return self.id

class GenomeDB:
    """ Currently a file-based database of genomes. """

    path = None

    def __init__(self, path):
        self.path = path

    def list(self):
        genome_list = []
        for resource in glob.glob(self.path + "/*"):
            genome = Genome(resource)
            genome.id = os.path.basename(resource)
            genome_list.append(genome)
        genome_list.sort()
        return genome_list

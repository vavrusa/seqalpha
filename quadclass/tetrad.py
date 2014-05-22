#!/usr/bin/env python
import sys
import numpy
import math
from Bio.PDB import *
from Bio import pairwise2

# Allowed nucleotides in a loop
NUCLEOTIDE = set([ 'DA', 'DC', 'DG', 'DT', 'DI' ])

def nucleotide_translate(name):
    # Subtitute 8-bromoguanosines for normal DG (see 2E4I)
    if name == 'BGM':
        return 'DG'
    # Modified DG compound (see 2M53)
    if name == 'LCG':
        return 'DG'
    return name

def resi_name(resi):
    ''' Get residue nucleotide name. '''
    return nucleotide_translate(resi.get_resname().strip(' ')).strip('D')

def point_rmsd(a, b):
    ''' Calculate RMSD between two points. '''
    sub = a - b
    sub = (sub[0], sub[1], sub[2]) # Python3 compatibility
    return numpy.sqrt(numpy.dot(sub, sub))

def tetragon_cog(atoms):
    ''' Calculate center of gravity for given tetragon.
    @note This only works for non self-intersecting tetragons. '''
    vectors = [atom.get_vector() for atom in atoms]
    cog1 = (vectors[0] + vectors[3]) / 2.0
    cog2 = (vectors[1] + vectors[2]) / 2.0
    return (cog1 + cog2) / 2.0

def analyze_planarity(tetrads):
    ''' Analyze tetrads planarity. An ideal tetrad consists of an outer and
        inner tetragon. Outer tetragon is formed by N9 atoms where the DG
        connects to the backbone and the inner angle is formed by O6 atoms
        which are formed around the metal ion in the center.
        Planarity is represented by a standard deviation between the
        centers of gravity of the outer and inner tetragon. '''
    deviation = []
    for tetrad in tetrads:
        outer_cog = tetragon_cog([resi['N9'] for resi in tetrad])
        inner_cog = tetragon_cog([resi['O6'] for resi in tetrad])
        # @TODO maximum deviaton is probably the best, but need to verify later
        dist = point_rmsd(outer_cog, inner_cog)
        deviation.append(dist)
    return deviation

def analyze_twist(tetrads):
    ''' Analyze C1' twist angle. '''
    twist_angles = []
    visited = []
    for tetrad in tetrads:
        # Select first N guanines' C1' atoms
        level1 = [resi['C1\''].get_vector() for resi in tetrad]
        level2 = [None, None, None, None]
        # Find closest tetrad, this is hard to guess as the C1' distance is fairly varied
        # mean value is around 4-6A, too low produces false negative and too high hopscotchs
        # a level
        min_rmsd = 7.0 # Max 7A
        closest = None
        visited.append((tetrad, tetrad))
        for adjacent in tetrads:
            # Omit visisted pairs
            if ((tetrad, adjacent) in visited) or ((adjacent, tetrad) in visited):
                continue
            # Find closest C1' complete mapping
            adjacent_level = [None, None, None, None]
            adjacent_rmsd = []
            for i in range(0, len(level1)):
                local_rmsd = 7.0 # Max 7A
                for resi in adjacent:
                    # Ignore already mapped atoms
                    if resi in adjacent_level:
                        continue
                    paired = resi['C1\''].get_vector()
                    rmsd = point_rmsd(level1[i], paired)
                    if rmsd < local_rmsd:
                        local_rmsd = rmsd
                        adjacent_level[i] = paired
                # Identify incomplete mapping
                if adjacent_level[i] is None:
                    # print('pair for',i,'at',local_rmsd)
                    # print('incomplete mapping of',tetrads.index(adjacent),tetrads.index(tetrad))
                    break
                adjacent_rmsd.append(local_rmsd)
            # Pair closest, completely mapped tetrads
            if len(adjacent_rmsd) != len(level1):
                continue
            # We are guaranteed that it does not exceed local RMSD constraint, try to minimize mean value now
            adjacent_rmsd_mean = numpy.mean(adjacent_rmsd)
            if adjacent_rmsd_mean < min_rmsd:
                min_rmsd = adjacent_rmsd_mean
                closest = adjacent
                level2 = adjacent_level

        # Orphan tetrad or an outlier
        if closest is None:
            continue

        # Mark closest tetrad pair as visited
        visited.append((tetrad, closest))
        # Calculate dihedral twist angle
        # Since we don't know which level is higher or lower, absolute value of
        # the angle has to stay within the <0, 60>deg
        twist = 0.0
        for side in [(0,1), (1,2), (2,3), (3,0)]:
            (a, b) = side
            pair_twist = abs(calc_dihedral(level1[a], level1[b], level2[b], level2[a]))
            twist += abs(pair_twist)
        twist /= 4.0
        twist_angles.append(twist)

    # Return mean twist angle
    return twist_angles

def closest_guanine(target, guanines, paired_from = 'N7', paired_to = 'N2', rmsd_min = 5.0, same_level = False):
    ''' Find closest guanine to target form the list. Attempts to find a shortest RMSD between two
        connected atoms. H21/N7 is closer, but not always present in the structure, so N2/N7 is selected. '''
    adjacent = None
    # No remaining guanines
    if len(guanines) == 0:
        return None
    # Find minimal N7 - H21/N2 identifying adjacent DG
    for resi in guanines:
        # Ignore guanine residues without N7 - H21/N2 bonds
        if paired_to not in resi:
            continue
        rmsd = target[paired_from] - resi[paired_to]
        rmsd_o6 = 0.0
        # Same level guanines have the close inner O6-N1 core
        if same_level:
            rmsd_o6 = target['O6'] - resi['N1']
        # @todo We shouldn't pair to the closest DG which isn't connected to the GQ core
        # @note Disabled by default, as some GQs have really twisted tetrads (f.e. 1OZ8)
        if rmsd < rmsd_min and rmsd_o6 < rmsd_min:
            rmsd_min = rmsd
            adjacent = resi
    return adjacent

def sort_tetrads(tetrads):
    ''' We don't know how the tetrads stack yet, but we know the first tetrad is eith top or bottom.
        With that we find the next closest tetrad and align it so the first DG in the tetrad is the next
        one attached to the same P backbone. '''
    unsorted = tetrads[1:]
    stack = [tetrads[0]]
    while len(unsorted) > 0:
        # Align to first element of the last sorted level
        lead = stack[-1][0]
        guanines = reduce(lambda t1, t2: t1 + t2, unsorted)
        closest = closest_guanine(lead, guanines, "C1'", "C1'", rmsd_min = 15.0, same_level = False)
        # Identify originating level and align
        for tetrad in unsorted:
            if closest in tetrad:
                offset = tetrad.index(closest)
                # Rotate tetrad so the closest DG is first
                unsorted.remove(tetrad)
                stack.append(tetrad[offset:] + tetrad[:offset])
                break
        # Odd, couldn't find a closest guanine pair
        if closest is None:
            # This can happen for disconnected GQ levels like in 3CDM
            # @todo We can't solve two interconnected GQs here, return the partial result
            break
    return stack

def group_tetrads(guanines):
    ''' Identify guanine tetrads by N7-H21/N2 shortest RMSD distances. '''
    tetrads = []
    visited = set([])

    while len(guanines) != 0:
        tetrad = [guanines.pop(0)]
        if tetrad[0] in visited:
            break
        while len(tetrad) != 4:
            adjacent = closest_guanine(tetrad[-1], guanines)
            # No N2 in range, discard incomplete tetrad
            if adjacent is None:
                break
            # Append adjacent DG to tetrad list
            tetrad.append(adjacent)
            guanines.remove(adjacent)
        # Check if tetrad forms a closed loop
        pin = closest_guanine(tetrad[-1], tetrad[0:3] + guanines)
        # Form complete interconnected tetrad
        if len(tetrad) == 4 and pin == tetrad[0]:
            tetrads.append(tetrad)
        else:
            # Reinsert other guanines before visited guanines
            split = len(guanines) - len(visited)
            for resi in tetrad[1:]:
                guanines.insert(split, resi)
            # Mark guanine as visited and append, so we know
            # when to stop trying to match them
            guanines.append(tetrad[0])
            visited.add(tetrad[0])

    # Not enough tetrads identified
    if len(tetrads) < 2:
        return tetrads

    # Sort tetrads into adjacent floors
    return sort_tetrads(tetrads)

def tetrad_pos(target, tetrads):
    ''' Identify DG molecule position in tetrad stack. '''
    for i in range(0, len(tetrads)):
        for k in range(0, len(tetrads[i])):
            if tetrads[i][k] is target:
                return (i, k)
    return None

def loop_type(entry, closure, tetrads):
    ''' Analyze loop type. '''
    entry_pos = tetrad_pos(entry, tetrads)
    closure_pos = tetrad_pos(closure, tetrads)
    level_dist = abs(entry_pos[0] - closure_pos[0])
    strand_dist = abs(entry_pos[1] - closure_pos[1])
    # Loop connects G on the same level.
    if level_dist == 0:
        # Loop connects edge-wise to the neighbouring strand
        if strand_dist % 2 == 1:
            return 'L'
        else:
            # Diagonal loop
            return 'D'
    else:
        # Propeller-type loop
        # @todo Identify diagonal/edge-wise ?
        return 'P'

    # Unidentified loop type
    return 'X'

def analyze_loops(tetrads, strands):
    ''' Analyze backbone direction. '''
    core = reduce(lambda t1, t2: t1 + t2, tetrads)
    loop_list = []
    topology = []

    # Strands are symmetric for dimolecular GQs
    for strand in [strands[0]]:
        loop = []
        loop_entry = None
        for resi in strand:
            if loop_entry is not None:
                # Find loop closure
                if resi in core:
                    topology.append(loop_type(loop_entry, resi, tetrads))
                    loop_list.append(''.join([resi_name(r) for r in loop]))
                    loop_entry = None
                    loop = [resi]
                    # # Final loop
                    # if len(loop_list) == 3:
                    #     break
                else:
                    loop.append(resi)
            else:
                # If next residue is not part of the DG core, start loop with the last
                # identified core DG on the strand
                if resi not in core:
                    # Cutoff leading nucleotides
                    if len(loop) == 0:
                        continue
                    loop_entry = loop[-1]
                # @todo Nucleotide-less loop in advanced structures
                #       We could detect it by comparing the direction of previous step with current that could hint
                #       strand reversal.
                loop.append(resi)

    # No closed loop (therefore not connected)
    if len(topology) == 0:
        loop_list = [''.join([resi_name(r) for r in loop])]
        topology = 'O'

    return (''.join(topology), '|'.join(loop_list))

def analyze(model, output = None):
    ''' Assemble guanine tetrads and analyze properties. '''
    guanines = []
    strands = []
    chain_count = 0
    for chain in model:
        strand = []
        chain_dg = []
        for residue in chain:
            residue_name = nucleotide_translate(residue.get_resname().strip())
            # Allow Inosine to substitute for Guanine,
            if residue_name == 'DG' or residue_name == 'DI':
                chain_dg.append(residue)
            # Build input sequence chain
            if residue_name.startswith('D'):
                # Filter out only nucleotide chains
                if residue_name in NUCLEOTIDE:
                    strand.append(residue)
        # Ignore chains without DG
        if len(chain_dg) > 0:
            chain_count += 1
            guanines += chain_dg
            strands.append(strand)
    # Must have at least 8 guanines to form a tetrad
    if len(guanines) < 8:
        sys.stderr.write(' [!!] less than 8 DGs found, ignoring\n')
        return None
    # Group tetrads from guanine list
    print(' * scanning model %s, %d DGs' % (model.__repr__(), len(guanines)))
    tetrads = group_tetrads(guanines)
    print('  - assembly: %d tetrads' % len(tetrads))
    if len(tetrads) < 2:
        sys.stderr.write(' [!!] at least 2 tetrads are required\n')
        return None
    planarity = analyze_planarity(tetrads)
    planarity_mean = numpy.mean(planarity)
    planarity_std = numpy.std(planarity)
    print('  - mean planarity: %.02f A, stddev %.02f A' % (planarity_mean, planarity_std))
    twist_angles = analyze_twist(tetrads)
    if len(twist_angles) == 0:
        sys.stderr.write(' [!!] can\'t calculate twist angles\n')
        return None
    twist = numpy.mean(twist_angles)
    twist_dev = numpy.std(twist_angles)
    print('  - twist angle: %.02f rad (%.02f deg), stddev %.02f rad' % (twist, math.degrees(twist), twist_dev))

    # Calculate consensus loop
    consensus = ''.join([resi_name(resi) for resi in strands[0]])
    print('  - chains: %d, consensus: %s' % (chain_count, consensus))
    (topology, loops) = analyze_loops(tetrads, strands)
    print('  - topology: %s, fragments: %s' % (topology, loops))

    return [planarity_mean, planarity_std, math.degrees(twist), math.degrees(twist_dev), chain_count, topology, loops]

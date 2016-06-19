#!/usr/bin/env python

"""
Project_Name: main, File_name: stage0_evfold.py
Aufthor: kalabharath, Email: kalabharath@gmail.com
Date: 14/06/2016

prepare data to run with BOSS-Evo

"""

import utility.evfold as evfold
import utility.io_util    as io
import utility.ss_util    as ss

data = io.readInputDataFiles('input_data.txt')
aa_seq, ss_seq = evfold.parseSS(data['evfold_ss'])
database_cutoff = data['database_cutoff']
rmsd = data['rmsd']
clash_distance = data['clash_distance']
ss_seq = 'CCHHHHHHHHHHHHHHHHHHHHHHHHHCCCCCCCCHHHHHHHHHHHHHHHHHHHHCCCCCCCCCHHHHHHHHHHCCCCHHHHHHHHHHHHHHHHHHHHHHHHCCCCCCCCCCCCCCCCCCCCHHHHHHHHHHHHHHHHHCCCCCCCCCCCCCCCCHHHHHHHHHHHHHHHCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCHHHHHHHHHHHHHCCCCCCCCCCHHHHHHHHCC'

ss_def, ss_combi = ss.genSSCombinations(ss_seq)
native_pdbs = evfold.parseNatives(data['native_pdbs'])
contact_matrix, plm_score_matrix = evfold.parseContacts(data['evfold_plm'], ss_combi, len(ss_seq))
map_route = evfold.getRoute(ss_def, contact_matrix)
data_dict = {'ss_seq': ss_seq, 'contact_matrix': contact_matrix, 'plm_scores': plm_score_matrix, 'aa_seq': aa_seq,
             'natives': native_pdbs, 'database_cutoff': database_cutoff, 'rmsd': float(rmsd),
             'clash_distance': float(clash_distance)}

"""
Dump all of the data in relavant pickle foiles
however, have to streamline this to a much better way of doing it
"""
io.dumpPickle("exp_data.pickle", data_dict)
io.dumpPickle("ss_profiles.pickle", ss_combi)
io.dumpPickle("contacts_route.pickle", map_route)
io.dumpPickle('contacts.matrix', contact_matrix)
io.dumpPickle('plm_scores.matrix', plm_score_matrix)
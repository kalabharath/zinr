from numpy import sum
from numpy import zeros

import io_util as io


def parseSS(filename):
    """
    Parse the Secondary Structure assignment file for Amino acid sequence and Secondary structure seq
    :param filename:
    :return: aa_seq, ss_seq
    """

    data = io.readFile(filename)
    aa_seq = ''
    ss_seq = ''

    # up_index, up_residue, ss_pred ss_conf msa_index, msa_cons%, msa_cons, in_construct
    # ['232', 'I', 'H', '3', '232', '2', '~', '*\n']

    for i in range(1, len(data)):
        line = data[i].split('\t')
        aa_seq = aa_seq + line[1]
        ss_seq = ss_seq + line[2]

    return aa_seq, ss_seq


def parseNatives(native_pdbs):
    """
    Parse native pdb files into an array that can be used in BOSS
    :param native_pdbs:
    :return:
    """
    native_pdbs = native_pdbs.lower()
    return native_pdbs.split()


def parseContacts(filename, ss_combi, nor, cutoff_score=0.25):
    """
    Parse the ev_couplings generated using plm method into contact data arrays
    :param filename, ss_combi:
    :return contact_matrix, plm_score_matrix:
    """
    data = io.readFile(filename)
    """
    list of all-by-all residue pairings, and score computed by chosen method
    MI_DI column headers:
    - 1stResidueNum
    - 1stResidueCode
    - 2ndResidueNum
    - 2ndResidueCode
    - mutual information score
    - DI score
    PLM columns are the same, replacing DI score with PLM score, and
    omitting MI scores (always 0)
    """
    from collections import defaultdict
    from operator import itemgetter
    from itertools import combinations

    plm_contacts = defaultdict(list)

    for line in data:
        r1, a1, r2, a2, pl, score = line.split()

        if round(float(score), 1) > cutoff_score:
            plm_contacts[int(r1)].append([int(r2), float(score)])

    for resi in plm_contacts.keys():
        plm_contacts[resi] = sorted(plm_contacts[resi], key=itemgetter(1), reverse=True)

    contact_matrix = zeros((nor, nor + 2))
    plm_score_matrix = zeros((nor, nor + 2))
    for pair in list(combinations(ss_combi.keys(), 2)):
        sse1 = ss_combi[pair[0]]
        sse2 = ss_combi[pair[1]]
        for i in range(0, len(sse1)):
            for j in range(0, len(sse2)):
                for k in range(sse1[i][4], sse1[i][5] + 1):
                    for l in range(sse2[j][4], sse2[j][5] + 1):
                        for entry in plm_contacts[k]:
                            if entry[0] == l:
                                contact_matrix[k, l] = 1.0
                                contact_matrix[l, k] = 1.0
                                plm_score_matrix[k, l] = entry[1]
                                plm_score_matrix[l, k] = entry[1]
    """
    print plm_contacts[8]
    print contact_matrix[8][49], len(contact_matrix[8])
    print plm_score_matrix[8][49], len(plm_score_matrix[8])

    print contact_matrix[8], len(contact_matrix[8])
    print plm_score_matrix[8], len(plm_score_matrix[8])
    """

    return contact_matrix, plm_score_matrix


def extractContacts(ss_def, contact_matrix):
    conatacts_def = []
    for ss in ss_def:
        start, end = ss[3], ss[4]
        temp = 0
        for i in range(start, end + 1):
            temp = temp + sum(contact_matrix[i])
        conatacts_def.append(temp)
    return conatacts_def


def get_ij(contacts_perss):
    """
        return the index of SS carrying largest PCSs/SS
    """
    # TODO this is a duplicate from PCSmap
    ntpcs = 0

    for i in xrange(0, len(contacts_perss) - 1):
        if i == 0:
            tpcs = contacts_perss[i] + contacts_perss[i + 1]

            ti = i
            tj = i + 1
        else:
            ntpcs = contacts_perss[i] + contacts_perss[i + 1]
        if tpcs >= ntpcs:
            pass
        else:
            tpcs = ntpcs
            ti = i
            tj = i + 1
    return ti, tj


def getRoute(ss_def, contact_matrix):
    """

    :param ss_def:
    :param contact_matrix:
    :return:
    """

    map_route = []
    contacts_perss = extractContacts(ss_def, contact_matrix)
    map_route = []
    control, i, j = 0, 0, 0

    # TODO this part is also a duplicate from the file PCSmap
    # TODO should try a common func or use classes and inherit

    while not (control == len(ss_def) - 1):

        if control == 0:
            control += 1
            i, j = get_ij(contacts_perss)  # get the largest PCS smotif
            map_route.append([i, j, 'start'])

        else:
            if i == 0:
                ti = j
                j = j + 1
                control += 1
                direction = 'right'
                map_route.append([ti, j, direction])
            elif j == len(contacts_perss) - 1:
                tj = i
                i = i - 1
                control += 1
                direction = 'left'
                map_route.append([i, tj, direction])
            else:
                if contacts_perss[i - 1] >= contacts_perss[j + 1]:
                    tj = i
                    i = i - 1
                    direction = 'left'
                    control += 1
                    map_route.append([i, tj, direction])
                else:
                    ti = j
                    j = j + 1
                    control += 1
                    direction = 'right'
    return map_route

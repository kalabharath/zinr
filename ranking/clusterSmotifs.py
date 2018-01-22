"""
Clustering based on RMSD with a cluster radius of user defined RMSD

"""
from filters.rmsd.clusterRMSD import clusterRMSD


def getSeq(smotif_def, aa_seq):

    smotif_seq = ''

    for entry in smotif_def[1]:
        start = entry[-2]-1
        end = entry[-1]
        tseq = aa_seq[start:end]
        smotif_seq = smotif_seq+tseq

    return smotif_seq


def getAlignment(seq1, seq2):

    from Bio import pairwise2
    from Bio.SubsMat import MatrixInfo as matlist

    matrix = matlist.blosum62
    gap_open = -0
    gap_extend = -0
    alns = pairwise2.align.globalds(seq1, seq2, matrix, gap_open, gap_extend)

    return alns[0]


def get_equivalent_atoms(top_aln):

    equivalent1 = []
    equivalent2 = []

    # Compute teh sequence identity
    seqa, qseqa, score, begin, end = top_aln
    j, k = 0.0, 0.0
    offset1 = 0
    offset2 = 0
    for i in range(0, len(qseqa)):
        if qseqa[i] == '-' and seqa[i] == '-':
            offset1 -=1
            offset2 -=1
        elif seqa[i] == '-' and qseqa[i] != '-':
            offset1 -=1
        elif qseqa[i] == '-' and seqa[i] != '-':
            offset2 -= 1
        elif qseqa[i] == seqa[i]:
            equivalent1.append(i + offset1)
            equivalent2.append(i + offset2)
        elif qseqa[i] != seqa[i]:
            pass
        else:
            print i, seqa[i], qseqa[i]
            print seqa
            print qseqa
            print "Fatal flaw in the logic"
            return False, False

    return equivalent1, equivalent2


def parse_from_equivalent(aa1, aa2, eq1, eq2):

    taa1 = ''
    taa2 = ''
    for res in eq1:
        taa1 = taa1 + aa1[res]
    for res in eq2:
        taa2 = taa2 + aa2[res]
    if taa1 == taa2:
        return taa1, taa2
    else:
        print "Could be a fatal flaw in this whole assumption"
        return False, False


def clusterSmotifs(all_entries, aa_seq, rmsd_cutoff):


    pos = 0
    total_entries = len(all_entries)
    counter = 0

    while pos < total_entries:
        non_redundant = []
        smotif_1 = all_entries[pos]
        smotif_seq1 = getSeq(smotif_1[1], aa_seq)

        for i in range(0, total_entries):
            smotif_2 = all_entries[i]
            smotif_seq2 = getSeq(smotif_2[1], aa_seq)
            top_align = getAlignment(smotif_seq1, smotif_seq2)
            eq1, eq2 = get_equivalent_atoms(top_align)
            if eq1 and eq2:
                seq1, seq2 = parse_from_equivalent(smotif_seq1, smotif_seq2, eq1, eq2)
            else:
                continue

            if seq1 and seq2:
                coors1 = smotif_1[2][1]
                coors2 = smotif_2[2][1]
                rmsd = clusterRMSD(coors1, coors2, eq1, eq2)
                rmsd = round(rmsd, 2)

            if i == pos:
                non_redundant.append(all_entries[i])
            elif rmsd >= rmsd_cutoff:
                non_redundant.append(all_entries[i])
            else:
                counter += 1
                pass
        all_entries = non_redundant[:]
        total_entries = len(all_entries)
        if pos >= len(all_entries)-1:
            break
        else:
            pos += 1

    return all_entries, counter
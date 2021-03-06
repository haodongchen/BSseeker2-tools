#!/usr/bin/env python
# Copyright (c) 2014 UCLA
# Modified from a script provided by Dr. Pellegrini's lab
#
# This software is distributable under the terms of the GNU General
# Public License (GPL) v2, the text of which can be found at
# http://www.gnu.org/copyleft/gpl.html. Installing, importing or
# otherwise using this module constitutes acceptance of the terms of
# this License.
#
# Disclaimer
# 
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# Comments and/or additions are welcome (send e-mail to:
# hdchen@ucla.edu).

import sys
import os
import os.path
import re, gzip

# Define the Dictionary & the Reverse Dictionary for barcode

Dict = {  '1': 'ATCACG',  '2': 'CGATGT',  '3': 'TTAGGC',  '4': 'TGACCA',
          '5': 'ACAGTG',  '6': 'GCCAAT',  '7': 'CAGATC',  '8': 'ACTTGA',
          '9': 'GATCAG', '10': 'TAGCTT', '11': 'GGCTAC', '12': 'CTTGTA',
         '13': 'AGTCAA', '14': 'AGTTCC', '15': 'ATGTCA', '16': 'CCGTCC',
         '17': 'GTAGAG', '18': 'GTCCGC', '19': 'GTGAAA', '20': 'GTGGCC',
         '21': 'GTTTCG', '22': 'CGTACG', '23': 'GAGTGG', '24': 'GGTAGC',
         '25': 'ACTGAT', '26': 'ATGAGC', '27': 'ATTCCT', '28': 'CAAAAG',
         '29': 'CAACTA', '30': 'CACCGG', '31': 'CACGAT', '32': 'CACTCA',
         '33': 'CAGGCG', '34': 'CATGGC', '35': 'CATTTT', '36': 'CCAACA',
         '37': 'CGGAAT', '38': 'CTAGCT', '39': 'CTATAC', '40': 'CTCAGA',
         '41': 'GACGAC', '42': 'TAATCG', '43': 'TACAGC', '44': 'TATAAT',
         '45': 'TCATTC', '46': 'TCCCGA', '47': 'TCGAAG', '48': 'TCGGCA' } 

RevDict = dict((v,k) for k,v in Dict.iteritems())
# ===========================================
# Find Hamming Distance between two patterns

def hamming_distance(s1, s2):
    #print s1, s2
    assert len(s1) == len(s2)
    return sum(ch1 != ch2 for ch1, ch2 in zip(s1, s2))


# ===========================================
# 

def process_input_file( qseqfn, bcdfn, bcdstr, mismatch):
    try :
        if qseqfn.endswith(".gz") : # support input file ending with ".gz"
            qseqF = gzip.open(qseqfn, "r")
            qseqfn = qseqfn.rstrip(".gz")
        else :
            qseqF = open(qseqfn, 'r')
    except IOError :
        print "\n[Error]:\n\t File cannot be open: ", qseqfn;
        exit(-1)

    try :
        if bcdfn.endswith(".gz") : # support input file ending with ".gz"
            bcdF = gzip.open(bcdfn, "r")
        else :
            bcdF = open(bcdfn, 'r')
    except IOError :
        print "\n[Error]:\n\t File cannot be open: ", bcdfn;
        exit(-1)

    if bcdstr == "" :
        print "No barcode in the list"
        return

    bcdlist = bcdstr.split(',')
    n = len(bcdlist)

    bcdseq = range(n)
    outfile = range(n)
    count = [0] * n
    count_null = total = 0
    # open files for different barcodes

    for i in range(n):
        bcdseq[i] = Dict[bcdlist[i]]
        try:
            os.mkdir('./BC%s' % bcdlist[i])
        except:
            pass
        outfile[i] = open('./BC%s/BC%s_%s' % (bcdlist[i],bcdlist[i], os.path.basename(qseqfn)), 'w')
    #    print i,'\n'
    try:
        os.mkdir('./BCN')
    except:
        pass
    nullfile = open('./BCN/BCN_%s' % os.path.basename(qseqfn), 'w')

    for line in qseqF:
        total = total + 1
        line  = line.strip().split()            #data with read
        line2 = bcdF.next().strip().split()  #data with barcode
        barcode = line2[8]

        # allow one mismatch from exact barcode sequence
        id = -1; min = 7; min_c = 1 # count of the min
        mmc = range(n)
        #print ">", barcode[:-1]
        for i in range(n):
            mmc[i] = hamming_distance(bcdseq[i], barcode[:-1])
            #print 'mis=',mmc[i], '; min=', min
            if mmc[i] < min:
                min = mmc[i]
                id = i 
                min_c = 1
            elif mmc[i] == min:
                min_c = min_c + 1
            #print ':mis=', mmc[i], '; min=', min

        #print "mmc:", mmc;
        # Only the unique min mismatch will be allowed
        if (min_c==1) & (min <= mismatch):
            outfile[id].write('%s\r\n' % '\t'.join(map(str, line)))
            count[id] = count[id] + 1
            #print "match to ", id
        else:
            nullfile.write('%s\r\n' % '\t'.join(map(str, line)))
            count_null = count_null + 1
            #print "not matched", "id=", id, "min=", min

    for i in range(n):
        outfile[i].close()
    nullfile.close()

    qseqF.close()
    bcdF.close()
    # summary
    print "Total reads:", total
    for i in range(n):
        print "Barcode ID:\t", bcdlist[i], "\tSequence:\t", bcdseq[i], \
              "\tCount:\t", count[i]
    print "NOT MAPPED READS:\t", count_null
    print "MAPPABILITY:\t%.2f" % (float(total - count_null) / total * 100), "%"


# ===========================================
# Learn the main barcodes from barcode file

def GetBarcodeList (bcdfn):
    try :
        if bcdfn.endswith(".gz") : # support input file ending with ".gz"
            bcdF = gzip.open(bcdfn, "r")
        else :
            bcdF = open(bcdfn, 'r')
    except IOError :
        print "\n[Error]:\n\t File cannot be open: ", bcdfn;
        exit(-1)
    i = 0
    bcdDict = {}
    # Count the numbers of barcodes in first 10000 lines
    for line in bcdF:
        line = line.strip().split()
        if i >= 10000:
            break
        w = line[8][:-1]
        if w not in bcdDict:
            bcdDict[w] = 1
        else:
            bcdDict[w] = bcdDict[w] + 1
        i = i + 1
    bcdF.close()

    bcdseqs = "";
    bcdlist = "";
    # Rank barcodes by counts
    Rank = sorted(bcdDict.iteritems(), key=lambda d:d[1], reverse = True )
    print "Top ten enriched patterns:"
    print Rank[0:10]
    print "=========================================="
    n = len(Rank)
    j = 0 # start of valid index
    # find the first valid barcode, avoid "..AC..." etc ...
    while ( (j < n) and (Rank[j][0] not in RevDict.keys()) ) :
        j += 1 
    if j < n :
        bcdseqs = Rank[j][0]
        bcdlist = RevDict[bcdseqs]
        pre = Rank[j][1]; #print "pre=", pre;
        #print len(Rank)
        #print Rank
        for i in range(j+1,n) :
            if pre > Rank[i][1] * 2 :
                 #print "pre:", pre, "\tRank i", Rank[i][1]
                 break
            elif Rank[i][0] in RevDict.keys() : # check for valid barcode
                bcdseqs += (',%s' % Rank[i][0])
                bcdlist += (',%s' % RevDict[Rank[i][0]])
                pre = Rank[i][1]; #print "pre<=", pre

    # Making a summary
    print "These are barcodes learned for you:"
    print "\tSequence :\t", bcdseqs
    print "\t      ID :\t", bcdlist, "\n"

    return bcdlist



from optparse import OptionParser
# ===========================================
def main():
    usage = "Usage: %prog -I <input directory> -i | -s <seq_file> -b <barcode_file> [-l <barcode_id_list>][-m <int>]\n" \
            "Date : 2012-11-25"
    parser = OptionParser(usage)
    parser.add_option("-s", dest="qseqfile", 
                  help="Name of the input qseq file", metavar="FILE")
    parser.add_option("-b", dest="barcodefile",
                  help="Name of the input barcode file", metavar="FILE")
    parser.add_option("-l", dest="list", metavar="STRING", type='string',
                  help="list of barcode id: 13,14,15.\n We'll learn it from barcode file if not provided")
    parser.add_option("-i", action="store_true", dest="interactive", help="Interactive input mode when specified", default=False)
    parser.add_option("-m", type="int", dest="mismatch", help="Number of mismatch allowed, [Default: 2]", default=2)
    parser.add_option("-I", dest="INdir", metavar="STRING", type='string', 
                  help="Name of the input directory")
    (options, args) = parser.parse_args()
    os.chdir(options.INdir)

    if options.interactive :
        options.qseqfile = raw_input('Please enter the qseq file:\n')
    #    print options.qseqfile;
        options.barcodefile = raw_input('Please enter the barcode file:\n')
    #    print options.barcodefile;
        options.list = raw_input('Please enter the list of barcode id:\n(Ex: 13,14,15 or nothing)\n')
    #    print options.list;						
    elif (options.qseqfile is None) or (options.barcodefile is None) :
        print parser.print_help()
        return 

    if not options.list:
        print "Our program will choose barcode id for you"
        print "=========================================="
        options.list = GetBarcodeList(options.barcodefile)
        print "=========================================="
        print "The barcode list we choose for you are:\n", options.list;
        print "=========================================="

    process_input_file(options.qseqfile, options.barcodefile, options.list, options.mismatch)


# ===========================================
if __name__ == "__main__":
    main()

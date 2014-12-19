import json
import os
import sys
from churnhash2 import ChurnHash

list = ['aurora-25', 'aurora-26','aurora-27', 'aurora-28', 'aurora-29', 'aurora-30',
        'aurora-31', 'aurora-32', 'aurora-33', 'aurora-34',
        'beta-25', 'beta-26','beta-27', 'beta-28', 'beta-29', 'beta-30',
        'beta-31', 'beta-32', 'beta-33']

output = {}
for release in list:

    fp = open('%s.json' % release, "r")

    history = json.load(fp)
    fp.close()
    ch = ChurnHash()

    for i in history:
        for j in history[i]["files"]:
            if "filename" in j:
                ch.add_file_path(j["filename"], j["added"], j["removed"])

    h = ch.get_hash()

    for i in h:
        if (h[i]['file'].count('/') == 0 and (h[i]['file'].count('.') == 0)):
            if h[i]['file'] not in output:
                output[h[i]['file']] = {}

            output[h[i]['file']][release + "-a"] = h[i]['lines_added']
            output[h[i]['file']][release + "-r"] = h[i]['lines_removed']


# Output in csv format
afp = open('aurora-0.csv', "w")
afp.write('filepath, aurora-25 added, aurora-25 removed, aurora-26 added, aurora-26 removed, aurora-27 added, aurora-27 removed, aurora-28 added, aurora-28 removed,\
    aurora-29 added, aurora-29 removed, aurora-30 added, aurora-30 removed, aurora-31 added, aurora-31 removed, aurora-32 added, aurora-32 removed,\
    aurora-33 added, aurora-33 removed, aurora-34 added, aurora-34 removed\n')
bfp = open('beta-0.csv', 'w')
bfp.write('filepath, beta-25 added, beta-25 removed, beta-26 added, beta-26 removed, beta-27 added, beta-27 removed, beta-28 added, beta-28 removed,\
    beta-29 added, beta-29 removed, beta-30 added, beta-30 removed, beta-31 added, beta-31 removed, beta-32 added, beta-32 removed,\
    beta-33 added, beta-33 removed, beta-34 added, beta-34 removed\n')
for i in output:
    afp.write("%s," % i)
    bfp.write("%s," % i)
    for n in range(25,35):
        relname = "aurora-" + str(n)
        if (relname + "-a") not in output[i]:
            afp.write("0,")
        else:
            afp.write("%d," % output[i][relname+"-a"])
        if (relname + "-r") not in output[i]:
            afp.write("0,")
        else:
            afp.write("%d," % output[i][relname+"-r"])
        
        relname = "beta-" + str(n)
        if (relname + "-a") not in output[i]:
            bfp.write("0,")
        else:
            bfp.write("%d," % output[i][relname+"-a"])
        if (relname + "-r") not in output[i]:
            bfp.write("0,")
        else:
            bfp.write("%d," % output[i][relname+"-r"])
    afp.write("\n")
    bfp.write("\n")

afp.close()
bfp.close()
#for i in h:
#    if (h[i]['file'].count('/') <=3 and (h[i]['file'].count('.') == 0)):
#        ofp.write("%s,%d,%d\n" % (h[i]['file'], h[i]['lines_added'], h[i]['lines_removed']))

#    fp.close()
#    ofp.close()

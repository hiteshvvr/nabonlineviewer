def removecomments(fname):
    f = open(fname)
    nf = open("tmp_" + fname, 'w')
    for line in f:
        tline = line.lstrip(' ')
        if tline.startswith("#"):
            continue
        else:
            nf.write(line)


for i in range(9):
    fname = input("give me filename\n")
    removecomments(fname)
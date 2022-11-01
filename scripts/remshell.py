import os, sys, readline, getopt

user = ""

opts, args = getopt.getopt(sys.argv[1:], "u:")

for opt, val in opts:
    if opt == '-u': user = val + "@"

nodes = []
for a in args:
    words = a.split("+", 1)
    if len(words) > 1:
        root = words[0]
        tails = words[1].split(",")
        for t in tails:
            words = t.split(":", 1)
            if len(words) > 1:
                i1 = int(words[0])
                i2 = int(words[1])
                for i in range(i1, i2+1):
                    fmt = "%d"
                    if len(words[0]) == len(words[1]):
                        fmt = "%%0%dd" % (len(words[0]),)
                    nodes.append(root + (fmt % (i,)))
            else:
                nodes.append(root + t)
    else:
        nodes.append(a)

print(' '.join(nodes))



while True:
    try:    cmd = input("> ")
    except EOFError:    
        print("")
        break
    cmd = cmd.strip()
    if cmd:
        for n in nodes:
            #print "ssh %s%s %s" % (user, n, cmd)
            print("[%s]" % (n,))
            os.system("ssh %s%s %s" % (user, n, cmd))

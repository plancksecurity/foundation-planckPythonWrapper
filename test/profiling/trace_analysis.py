import sys
first = True
funcs = {}
prevfs = [0,0,0,[0]]
prevtime = 0

for line in sys.stdin:
    if first:
        first = False
        continue
    try:
        _cpu, _id, probe, time = line.split() 
    except:
        break
    time = int(time)
    func,point = probe.split(':')
    entry = point == "entry"
    fs = funcs.setdefault(func,[0,0,0,[]])
    if entry:
        prevfs[2] = prevfs[2] + time - prevtime  
        fs[0] = fs[0] + 1
        fs[3].append(time)
    else:
        prevfs[2] = prevfs[2] + time - prevtime  
        fs[1] = fs[1] + time - fs[3].pop()
    prevfs = fs
    prevtime = time

    #print(_cpu, _id, func,point, time)

for func in sorted(funcs.items(), key=lambda fs: fs[1][1]):
    name,(count, totaltime, insidetime, entries) = func

    print("{:<40} {:<6} {:<4} {:>6.2f} {:>6.2f}".format( name, count, len(entries), totaltime/1000000000, insidetime/1000000000))

    

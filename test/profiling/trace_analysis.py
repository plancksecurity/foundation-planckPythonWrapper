import sys
first = True
funcs = {}
prevtime = 0
stack=[]

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
        if len(stack) > 0:
            prevfunc, prevfs = stack[-1]
            prevfs[2] = prevfs[2] + time - prevtime  
        fs[0] = fs[0] + 1
        fs[3].append(time)
        stack.append((func,fs))
    else:
        while len(stack) > 0 :
            prevfunc, prevfs=stack.pop()
            if func != prevfunc:
                print(prevfunc, ": NO RETURN, unwinded in", func, file=sys.stderr)
                # in case unwinding from non returning func, cannot guess time spent
                # spent time is then (abusively) added to all unwinded, worst case.
                prevfs[2] = prevfs[2] + time - prevtime  
                prevfs[1] = prevfs[1] + time - prevfs[3].pop()
            else:
                break

        fs[2] = fs[2] + time - prevtime  
        fs[1] = fs[1] + time - fs[3].pop()
        
    prevtime = time

    #print(_cpu, _id, func,point, time)

for func in sorted(funcs.items(), key=lambda fs: fs[1][1]):
    name,(count, totaltime, insidetime, entries) = func

    print("{:<40} {:<6} {:>6.2f} {:>6.2f}".format( name, count, totaltime/1000000000, insidetime/1000000000))

    

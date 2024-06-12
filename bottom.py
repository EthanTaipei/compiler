import copy

GRAMMAR = 'ex1'
if GRAMMAR == 'ex1':
    grammar = {
    'Start': [['S', '$']],
    'S': [['A', 'B'], ['a', 'c'], ['x', 'A', 'c']],
    'A': [['a']],
    'B': [['b'], []]
    };
else:
    grammar = {
    'S': [['E', '$']],
    'E': [['E', '+', 'T'], ['E', '-', 'T'], ['T']],
    'T': [['T', '*', 'F'], ['T', '/', 'F'], ['F']],
    'F': [['id'], ['num'], ['(', 'E', ')']],
    };

nstate = 0
acc = 0
nt = { nt for nt in grammar }
rules = []
count = 0
for i in grammar:
    for j in grammar[i]:
        rules += [[i, j, count]]
        count += 1
print(nt)
print(rules)

def closure(state):
    ans = state
    while True:
        prev = copy.copy(ans)
        new = set()
        for (i, j, *k) in ans:
            #print("closure: ({0}, {1})".format(i, j))
            if j == len(rules[i][1]):   # inferring to empty
                continue
            sym = rules[i][1][j]
            if sym in nt:
                new |= {(rule[2], 0, -1) for rule in rules if sym == rule[0]}
        ans |= new
        if ans == prev:
            break
    ans = list(state)
    ans.sort()
    return ans
                
def add_state(n, sym):
    global nstate, states, base, acc
    state = states[n]
    #print('add_state: n =', n, ', state =', state)
    items = []      # the list record all possible indexes of given symbol "x" in the "state".
    for idx, i in enumerate(state):
        rhs = rules[i[0]][1]
        if i[1] == len(rhs):
            continue
        if sym == rhs[i[1]]:
            items.append(idx)

    # filter out the same configuration
    new = {(state[i][0], state[i][1]+1, -1) for i in items}
    new = closure(new)
    new = [(i, j) for (i, j, *k) in new]
    conf = {}
    for key in states:
        rhs = [(i, j) for (i, j, *k) in states[key]]
        conf[key] = rhs
    goto = 0
    hit = False
    for k in conf:
        if new == conf[k]:
            goto = k
            hit = True
            break

    if not hit:
        new = {(state[i][0], state[i][1]+1, -1) for i in items}
        nstate += 1
        goto = nstate
        states[nstate] = closure(new) 
        base[nstate] = acc
        acc += len(states[nstate])
    for i in items:
        states[n][i] = (*states[n][i][:2], goto)
    return -1 if hit else nstate

def compute_goto(n):
    global nstate, acc, states
    state = states[n]
    print('compute_goto: n =', n, ', state =', state)

    next_sym = []
    for (i, j, *k) in states[nstate]:
        rhs = rules[i][1]
        if len(rhs) == j:
            continue
        next_sym.append(rhs[j])

    if next_sym == []:
        return -1
    next_sym = list(dict.fromkeys(next_sym))      # remove duplicates from list
    for i in next_sym:
        next_state = add_state(n, i)
        if next_state == -1:
            continue
        compute_goto(next_state) 
    return n

def print_state(n, states):
    global pedge
    print("State {0}".format(n))
    for idx, (i, j, g) in enumerate(states[n]):
        print("{0} {1}:".format(base[n]+idx, rules[i][0]), end='')
        rule = rules[i][1]
        front = [k for k in range(0, j)]
        rear = [k for k in range(j, len(rule))]
        for k in front:
            print(' ', rule[k], sep='', end='')
        print(' .', end='')
        for k in rear:
            print(' ', rule[k], sep='', end='')
        print("\t({0}, {1})".format(g, pedge[base[n]+idx]))

states = {}
base = { 0:0 }
states[0] = closure({ (0, 0, -1) })
acc += len(states[0])

# calculate goto state
compute_goto(nstate) 

# the elmt of lr0: (rule number, dot position, goto state)
lr0 = []
for i in states:
    lr0 += [j for j in states[i]]
print(lr0)

# calculate propagation edge
pedge = [-1 for i in range(len(lr0))]   # propagation edge
for idx, (i, j, k) in enumerate(lr0):
    rule = rules[i]
    if k == -1:
        continue
    for state_idx, (p, q, r) in enumerate(states[k]):
        if i == p and j + 1 == q:
            pedge[idx] = base[k] + state_idx
            break
print(pedge)
    
k = [k for k in states]
for i in k:
    print_state(i, states)
    print()
#print(base, ', acc =', acc)

import json,collections,re
A=json.load(open('atlas.json'));G=json.load(open('graph.json'));P=json.load(open('pages.json'))
T={o['i']:o for o in A}
edges=G['edges']
ind=collections.Counter(e['d'] for e in edges);outd=collections.Counter(e['s'] for e in edges)
conn=sorted(set(ind)|set(outd))
# components
par={i:i for i in conn}
def f(x):
    while par[x]!=x: par[x]=par[par[x]]; x=par[x]
    return x
for e in edges: par[f(e['s'])]=f(e['d'])
comp=collections.defaultdict(list)
for i in conn: comp[f(i)].append(i)
cs=sorted(comp.values(),key=len,reverse=True)
print('components',len(cs),[len(c) for c in cs[:15]])
print('cat of connected',collections.Counter(T[i]['cat'] for i in conn))
print('cat of numbered',collections.Counter(o['cat'] for o in A if o['ids']))
cross=collections.Counter(tuple(sorted((T[e['s']]['cat'],T[e['d']]['cat']))) for e in edges)
print('edge cats',cross.most_common(20))
for c in cs[1:12]: print('  comp:',[T[i]['t'][:45] for i in c])
print('examiner-only direct edges',sum(1 for e in edges if e['direct'] and e['ex']),'direct',sum(e['direct'] for e in edges))
for cat in ['fork','drive','wheel','comp','emtb','frame','transport','tech']:
    top=[(n,T[i]['t'][:60]) for i,n in ind.most_common() if T[i]['cat']==cat][:4]; print(cat,top)
# surprising cross-cat direct edges
for e in edges:
    a,b=T[e['s']],T[e['d']]
    if a['cat']!=b['cat'] and e['direct'] and {a['cat'],b['cat']}&{'transport','tech','comp','wheel'} : print('X',a['cat'],a['t'][:45],'->',b['cat'],b['t'][:45])
unfetched=[o['t'] for o in A if o['ids'] and all(P.get(p) is None for p in o['ids'])]
nocit=[o['t'][:60] for o in A if o['ids'] and all((P.get(p) is None) or (not P[p]['back'] and not P[p]['fwd']) for p in o['ids'])]
print('cards w/ no citation data at all',len(nocit),nocit)
idx={i:k for k,i in enumerate(conn)}
def short(t):
    s=re.sub(r'\s*\([^)]*\)','',t); s=re.split(r' — | - ',s)[0].strip()
    return s if len(s)<=34 else s[:32].rstrip()+'…'
nodes=[dict(ref=T[i]['ref'],t=T[i]['t'],s=short(T[i]['t']),cat=T[i]['cat'],y=T[i]['y'],st=T[i]['st'],gp=T[i]['ids'][0]) for i in conn]
E2=[[idx[e['s']],idx[e['d']],0 if e['direct'] else 1,1 if (e['direct'] and e['ex']) else 0] for e in edges]
MIN=10
ext=[]
seen={}
def addx(x,kind):
    key=(x['t'].lower().strip(),x['pd']) if x['t'] and x['pd'] else x['b']
    cards=[idx[c] for c in x['cards'] if c in idx]
    if key in seen:
        k=seen[key]
        if ext[k]['k']==kind: ext[k]['c']=sorted(set(ext[k]['c'])|set(cards)); return
    seen[key]=len(ext)
    ext.append(dict(pn=x['pn'],t=x['t'].rstrip('. '),a=x['asg'],y=int(x['pd'][:4]) if x['pd'][:4].isdigit() else None,k=kind,c=cards))
for x in G['eb']:
    if x['n']>=MIN: addx(x,'cited')
for x in G['ef']:
    if x['n']>=MIN: addx(x,'citing')
ext=[x for x in ext if len(x['c'])>=MIN and x['y']]
print('ext',len(ext),collections.Counter(x['k'] for x in ext))
meta=dict(cards=len(A),numbered=sum(1 for o in A if o['ids']),numbers=len(P),fetched=sum(1 for p in P.values() if p),connected=len(conn),edges=len(E2),direct=sum(1 for e in E2 if e[2]==0),nocit=len(nocit),extMin=MIN,date='2026-11-13')
json.dump(dict(nodes=nodes,edges=E2,ext=ext,meta=meta),open('data.json','w'),ensure_ascii=False,separators=(',',':'))
print(meta, len(open('data.json').read()))

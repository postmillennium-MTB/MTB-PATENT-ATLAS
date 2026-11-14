import json,re,collections
from parse import base
A=json.load(open('atlas.json')); P=json.load(open('pages.json'))
own={};fam={}
for o in A:
    for pid in o['ids']:
        p=P.get(pid)
        if not p: continue
        for b in p['own']: own.setdefault(b,set()).add(o['i'])
        for b in p['fam']: fam.setdefault(b,set()).add(o['i'])
E={}  # (src,dst)->dict
def add(s,d,direct,ex,via,a,b):
    if s==d: return
    e=E.setdefault((s,d),dict(direct=False,ex=None,via=set(),pairs=set()))
    e['direct']|=direct; e['via'].add(via); e['pairs'].add((a,b,direct))
    if direct: e['ex']=ex if e['ex'] is None else (e['ex'] and ex)
ext_back=collections.defaultdict(lambda:dict(by=set(),t='',pd='',asg='',pn=''))
ext_fwd=collections.defaultdict(lambda:dict(of=set(),t='',pd='',asg='',pn=''))
for o in A:
    for pid in o['ids']:
        p=P.get(pid)
        if not p: continue
        for r in p['back']:
            b=base(r['pn'])
            if b in own:
                for d in own[b]: add(o['i'],d,not r['fam'],r['ex'],'back',base(pid),b)
            elif b in fam:
                for d in fam[b]: add(o['i'],d,False,r['ex'],'back',base(pid),b)
            elif not r['fam']:
                x=ext_back[b]; x['by'].add(o['i']); x.update(t=r['t'] or x['t'],pd=r['pd'] or r['pub'] or x['pd'],asg=r['asg'] or x['asg'],pn=r['pn'])
        for r in p['fwd']:
            b=base(r['pn'])
            if b in own:
                for s in own[b]: add(s,o['i'],not r['fam'],r['ex'],'fwd',b,base(pid))
            elif b in fam:
                for s in fam[b]: add(s,o['i'],False,r['ex'],'fwd',b,base(pid))
            elif not r['fam']:
                x=ext_fwd[b]; x['of'].add(o['i']); x.update(t=r['t'] or x['t'],pd=r['pd'] or r['pub'] or x['pd'],asg=r['asg'] or x['asg'],pn=r['pn'])
# same-card family edges (both directions exist between siblings) fine.
edges=[dict(s=s,d=d,direct=e['direct'],ex=bool(e['ex']),via=sorted(e['via']),pairs=sorted(e['pairs'])) for (s,d),e in E.items()]
print('edges',len(edges),'direct',sum(e['direct'] for e in edges))
both=sum(1 for e in edges if len(e['via'])==2);print('seen both ways',both,'back only',sum(1 for e in edges if e['via']==['back']),'fwd only',sum(1 for e in edges if e['via']==['fwd']))
mutual=[(s,d) for (s,d) in E if (d,s) in E and s<d];print('mutual pairs',len(mutual))
T={o['i']:o for o in A}
for s_,d_ in mutual[:30]: print('  ',T[s_]['t'][:50],'<->',T[d_]['t'][:50],E[(s_,d_)]['direct'],E[(d_,s_)]['direct'])
def merge(X,key):
    out=[]
    for b,x in X.items():
        out.append(dict(pn=x['pn'],b=b,t=x['t'],pd=x['pd'],asg=x['asg'],n=len(x[key]),cards=sorted(x[key])))
    out.sort(key=lambda x:-x['n']); return out
eb=merge(ext_back,'by');ef=merge(ext_fwd,'of')
print('--ext cited by many atlas');[print(x['n'],x['pn'],x['pd'],x['asg'][:25],x['t'][:60]) for x in eb[:25]]
print('--ext citing many atlas');[print(x['n'],x['pn'],x['pd'],x['asg'][:25],x['t'][:60]) for x in ef[:25]]
json.dump(dict(edges=edges,eb=eb[:400],ef=ef[:400]),open('graph.json','w'))

import re,json,os,html as H,collections
A=json.load(open('atlas.json'))
FIX={'US102017116754':'DE102017116754B4','US202017104416U1':'DE202017104416U1'}
def base(p):
    m=re.match(r'^([A-Z]{2}(?:D|RE|PP|H)?\d+)([A-Z]\d?)?$',p)
    if m: return m.group(1)
    m=re.match(r'^(TWI\d+)',p)
    return m.group(1) if m else p
def clean(s): return re.sub(r'\s+',' ',H.unescape(re.sub(r'<[^>]+>','',s))).strip()
def rows(h,prop):
    out=[]
    for m in re.finditer(r'<tr itemprop="%s" itemscope repeat>(.*?)</tr>'%prop,h,re.S):
        r=m.group(1)
        pn=re.search(r'itemprop="(?:publicationNumber|representativePublication)">([^<]+)<',r)
        if not pn: continue
        g=lambda k:(lambda x: clean(x.group(1)) if x else '')(re.search(r'itemprop="%s"[^>]*>(.*?)</(?:td|span)>'%k,r,re.S))
        out.append(dict(pn=pn.group(1).strip(),ex='examinerCited' in r,pd=g('priorityDate'),pub=g('publicationDate'),asg=g('assigneeOriginal'),t=g('title')))
    return out
pages={}
for o in A:
    for pid in o['ids']:
        f='raw/%s.html'%FIX.get(pid,pid)
        if not os.path.exists(f): pages[pid]=None; continue
        h=open(f,errors='replace').read()
        own={base(r['pn']) for r in rows(h,'pubs')}
        own.add(base(FIX.get(pid,pid)))
        fam={base(r['pn']) for r in rows(h,'docdbFamily')}|{base(r['pn']) for r in rows(h,'applications')}
        back=[dict(r,fam=False) for r in rows(h,'backwardReferencesOrig')] or [dict(r,fam=False) for r in rows(h,'backwardReferences')]
        back+=[dict(r,fam=True) for r in rows(h,'backwardReferencesFamily')]
        fwd=[dict(r,fam=False) for r in rows(h,'forwardReferencesOrig')] or [dict(r,fam=False) for r in rows(h,'forwardReferences')]
        fwd+=[dict(r,fam=True) for r in rows(h,'forwardReferencesFamily')]
        def meta(k):
            m=re.search(r'itemprop="%s"[^>]*>(.*?)</'%k,h,re.S); return clean(m.group(1)) if m else ''
        t=re.search(r'<meta name="DC.title" content="([^"]*)"',h)
        pages[pid]=dict(own=sorted(own),fam=sorted(fam-own),back=back,fwd=fwd,title=clean(t.group(1)) if t else '',prio=meta('priorityDate'))
json.dump(pages,open('pages.json','w'))
ok=[p for p in pages if pages[p]]
print('ids',len(pages),'fetched',len(ok),'missing',[p for p in pages if not pages[p]])
print('with back',sum(1 for p in ok if pages[p]['back']),'with fwd',sum(1 for p in ok if pages[p]['fwd']))
print('none either',[p for p in ok if not pages[p]['back'] and not pages[p]['fwd']])

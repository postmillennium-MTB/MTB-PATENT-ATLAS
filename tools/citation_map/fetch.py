import json,subprocess,os,sys,time
from concurrent.futures import ThreadPoolExecutor
A=json.load(open('atlas.json'))
ids=sorted({i for o in A for i in o['ids']})
def get(u,path):
    r=subprocess.run(['curl','-sSL','-m','120','-o',path,'-w','%{http_code}',u],capture_output=True,text=True)
    return r.stdout
def one(pid):
    p=f'raw/{pid}.html'
    if os.path.exists(p) and os.path.getsize(p)>20000: return pid,'cached'
    tries=[pid]
    import re
    if not re.search(r'[A-Z]\d?$',pid[2:]): tries+= [pid+k for k in ['A','B1','B2','A1','A2','E','S','U1','B']]
    for t in tries:
        c=get(f'https://patents.google.com/patent/{t}/en',p)
        if c=='200' and os.path.getsize(p)>20000: return pid,'ok:'+t
        time.sleep(0.5)
    if os.path.exists(p): os.remove(p)
    return pid,'fail:'+c
with ThreadPoolExecutor(2) as ex:
    res=dict(ex.map(one,ids))
json.dump(res,open('fetchlog.json','w'),indent=0)
print(sum(1 for v in res.values() if not v.startswith('fail')),len(res))
print([k for k,v in res.items() if v.startswith('fail')])

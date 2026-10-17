import json,numpy as np,collections
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
R=json.load(open('/home/claude/data/oppfeat.json'))
def n_of(r): return 5 if r['W']*r['H']>=2400 else 4
X=[];keep=[]
for r in R:
    if r['rounds']<200: continue
    ts=n_of(r)
    x=[(r['e200']-r['o200'])/(r['e200']+r['o200']+50), r['d200']/ts]
    X.append(x);keep.append(r)
X=np.array(X);mu=X.mean(0);sd=X.std(0)+1e-9;Z=(X-mu)/sd
for k in (3,4,5,6):
    km=KMeans(k,n_init=20,random_state=0).fit(Z);print(k,round(silhouette_score(Z,km.labels_),3))
K=int(__import__('sys').argv[1]) if len(__import__('sys').argv)>1 else 4
km=KMeans(K,n_init=50,random_state=0).fit(Z)
C=km.cluster_centers_*sd+mu
for c in range(K):
    idx=[i for i in range(len(keep)) if km.labels_[i]==c]
    us=[keep[i] for i in idx if keep[i]['label'].startswith('US')]
    print(f"cluster {c}: n={len(idx)} race={C[c][0]:+.2f} deaths/ch={C[c][1]:.2f} | our games {len(us)} win {np.mean([u['win'] for u in us]) if us else float('nan'):.2f} margin {np.mean([u['margin'] for u in us]) if us else float('nan'):+.0f}")
    print('   maps',collections.Counter(keep[i]['map'] for i in idx).most_common(6))
json.dump({'mu':mu.tolist(),'sd':sd.tolist(),'centers':km.cluster_centers_.tolist(),'raw':C.tolist()},open('/home/claude/data/clusters.json','w'))
lab={keep[i]['file']+keep[i]['label']:int(km.labels_[i]) for i in range(len(keep))}
json.dump(lab,open('/home/claude/data/cluster_labels.json','w'))

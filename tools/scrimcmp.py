"""scrimcmp.py CACHE_A CACHE_B -> compare our stats (and opponent stats) between two scrim caches."""
import json,sys,statistics as st
def summ(p):
    G=list(json.load(open(p)).values());m=lambda f:round(st.mean(f(g) for g in G),1)
    return {'games':len(G),'wins':sum(g['result']=='win' for g in G),'our gems':m(lambda g:g['gems'][0]),'their gems':m(lambda g:g['gems'][1]),
      'our deaths':m(lambda g:g['deaths'][0]),'their deaths':m(lambda g:g['deaths'][1]),'our gold400':m(lambda g:g['gold']['400'][0]),
      'their gold400':m(lambda g:g['gold']['400'][1]),'our gold800':m(lambda g:g['gold']['800'][0]),'our banks':m(lambda g:g['banks'][0]),'our camp deaths':m(lambda g:g['camp_deaths'][0])}
A,B=summ(sys.argv[1]),summ(sys.argv[2])
for k in A:print(k.ljust(16),str(A[k]).rjust(8),str(B[k]).rjust(8))

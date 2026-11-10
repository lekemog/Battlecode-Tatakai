import sys
b=open(sys.argv[1],'rb').read(); want=sys.argv[2:]
p=8
def leb():
    global p
    r=s=0
    while True:
        x=b[p];p+=1;r|=(x&0x7f)<<s;s+=7
        if x<0x80:return r
T={0x7f:'i32',0x7e:'i64',0x7d:'f32',0x7c:'f64'}
types=[];funcs=[];nimp=0;exps={}
while p<len(b):
    sid=b[p];p+=1;sz=leb();end=p+sz
    if sid==1:
        for _ in range(leb()):
            p+=1;pa=[T.get(b[p+i]) for i in range(leb())] if False else None
            n=leb();pa=[T.get(b[p+i]) for i in range(n)];p+=n
            n=leb();re_=[T.get(b[p+i]) for i in range(n)];p+=n
            types.append((pa,re_))
    elif sid==2:
        for _ in range(leb()):
            l=leb();p+=l;l=leb();p+=l;k=b[p];p+=1
            if k==0: funcs.append(leb());nimp+=1
            elif k==1: p+=1;f=leb();leb() if f&1 else None;
            elif k==2: f=leb();leb();leb() if f&1 else None
            elif k==3: p+=2
    elif sid==3:
        for _ in range(leb()): funcs.append(leb())
    elif sid==7:
        for _ in range(leb()):
            l=leb();nm=b[p:p+l].decode();p+=l;k=b[p];p+=1;i=leb()
            if k==0: exps[nm]=i
    p=end
for nm in want:
    for k,i in exps.items():
        if nm in k: print(k,types[funcs[i]])

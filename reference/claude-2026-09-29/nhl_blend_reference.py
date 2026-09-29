# Reference implementation: NHL DK blended projections (Sim Savant + DFF + props). Inputs: ss.csv, dff.csv, props.csv (player,market[G|P],over,under), saves.csv (player,line,over,under). See DFS-Blended-Projection-Playbook.md
# NOT production. v3 does not equal-weight Savant or a DFS site into a Vegas number. Kept as a worked example of the conversion math.
import pandas as pd, numpy as np
from scipy.stats import poisson
from scipy.optimize import brentq
ss=pd.read_csv('ss.csv',dtype={'DFS ID':str}); dff=pd.read_csv('dff.csv')
df=ss.merge(dff[['Player','Team','Pos','Projection']].rename(columns={'Player':'Name','Projection':'DFF'}),on='Name',how='left').rename(columns={'Proj':'SS'})
for n,(t,p) in {'Kirill Marchenko':('TOR','W'),'Elias-Nils Pettersson':('VAN','D'),'Zack Bolduc':('MTL','W'),'Max Jones':('VAN','W')}.items():
    df.loc[df.Name==n,['Team','Pos']]=[t,p]
def imp(ml): ml=float(ml); return 100/(ml+100) if ml>0 else -ml/(-ml+100)
# game lines
games=[('TOR','MTL',-104,-112,6.4),('BOS','NYR',-112,-104,5.75),('EDM','VAN',-285,235,6.55),('VGK','CHI',-258,220,5.8)]
def split(T,pw):
    best=None
    for s in np.linspace(.3,.75,901):
        M=np.outer(poisson.pmf(np.arange(15),T*s),poisson.pmf(np.arange(15),T*(1-s)))
        w=np.tril(M,-1).sum()+.5*np.trace(M)
        if best is None or abs(w-pw)<best[0]: best=(abs(w-pw),T*s,T*(1-s))
    return best[1:]
team={}
for h,a,mh,ma,T in games:
    ph,pa=imp(mh),imp(ma); pw=ph/(ph+pa); lh,la=split(T,pw)
    team[h]=dict(goals=lh,win=pw,oppg=la); team[a]=dict(goals=la,win=1-pw,oppg=lh)

df['Base']=np.where(df.SS==0,0.0,np.where(df.DFF.isna(),df.SS,(df.SS+df.DFF)/2))
df.loc[df.Name=='Ryan Nugent-Hopkins','Base']=0.0   # OUT

# ---- props -> probabilities ----
pr=pd.read_csv('props.csv',dtype=str)
def prob(r):
    po=imp(r.over)
    if isinstance(r.under,str) and r.under.strip(): pu=imp(r.under); return po/(po+pu)
    return po*(0.87 if r.market=='G' else 0.92)
pr['p']=pr.apply(prob,axis=1)
P=pr.pivot_table(index='player',columns='market',values='p',aggfunc='mean')
df=df.join(P,on='Name')
df=df.rename(columns={'G':'pGoal','P':'pPoint'})

def dk_skater(r):
    D = r.Pos=='D'
    pg,pp=r.pGoal,r.pPoint
    if pd.isna(pg) and pd.isna(pp): return np.nan
    if not pd.isna(pg): lg=-np.log(1-pg)
    if not pd.isna(pp): lp=-np.log(1-pp)
    if pd.isna(pp): la=lg*(3.0 if D else 1.4)
    elif pd.isna(pg): lg=lp*(0.2 if D else 0.42); la=lp-lg
    else: la=max(lp-lg,0.25*lg)
    sh=(0.045+0.03*min(lg/0.2,1)) if D else (0.08+0.06*min(lg/0.5,1))
    sog=lg/sh; blk=1.4 if D else 0.5
    pts=lg+la
    return (8.5*lg+5*la+1.5*sog+1.3*blk+3*(1-poisson.cdf(2,lg))+3*(1-poisson.cdf(2,pts))
            +3*(1-poisson.cdf(4,sog))+3*(1-poisson.cdf(2,blk)))
sk=(df.Pos!='G')
df['VegasRaw']=np.nan
df.loc[sk,'VegasRaw']=df[sk].apply(dk_skater,axis=1)
df.loc[df.Base==0,'VegasRaw']=np.nan
df.loc[(df.Pos=='D')&df.pPoint.isna(),'VegasRaw']=np.nan   # D with goal odds only: too little info
m=df.VegasRaw.notna()&sk
vr,bs=df.loc[m,'VegasRaw'],df.loc[m,'Base']
scale=bs.std()/vr.std()
df.loc[m,'Vegas']=(vr-vr.mean())*scale+bs.mean()   # match level & spread of the services, keep prop-based ordering
print('skater props matched:',m.sum(),' scale',round(scale,3), ' corr w/ base', round(df.loc[m,['Base','VegasRaw']].corr().iloc[0,1],3))

# ---- goalies from saves O/U + game lines ----
sv=pd.read_csv('saves.csv',dtype=str)
for _,r in sv.iterrows():
    po,pu=imp(r.over),imp(r.under); p=po/(po+pu); L=float(r.line)
    mu=brentq(lambda x:(1-poisson.cdf(np.floor(L),x))-p,5,60)
    i=df.index[df.Name==r.player][0]; t=team[df.at[i,'Team']]
    ga=t['oppg']*0.93
    val=0.7*mu+6*t['win']-3.5*ga+4*np.exp(-ga)+2*0.115*(1-t['win'])*2*0.5+3*(1-poisson.cdf(34,mu))
    df.at[i,'VegasRaw']=val; df.at[i,'SavesMean']=mu
g=df.SavesMean.notna()
df.loc[g,'Vegas']=df.loc[g,'VegasRaw']-df.loc[g,'VegasRaw'].mean()+df.loc[g,'Base'].mean()
print('goalie raw vs base mean',round(df.loc[g,'VegasRaw'].mean(),2),round(df.loc[g,'Base'].mean(),2))

def final(r):
    if r.Base==0: return 0.0
    if pd.isna(r.Vegas): return r.Base
    ins=[r.SS,r.Vegas]+([] if pd.isna(r.DFF) else [r.DFF])
    return float(np.mean(ins))
df['Blend']=df.apply(final,axis=1).round(2)

out=df[['Name','DFS ID','Blend','Own']].rename(columns={'Blend':'Proj'})
out['Proj']=out.Proj.map(lambda x:f'{x:.2f}')
out.to_csv('/mnt/user-data/outputs/Blended-Projections-09-29-2026-DraftKings-Main.csv',index=False)
aud=df[['Name','Team','Pos','SS','DFF','pGoal','pPoint','SavesMean','Vegas','Blend','Own']].copy()
aud['Delta_vs_SS']=(aud.Blend-aud.SS).round(2)
aud=aud.sort_values('Blend',ascending=False); aud.round(3).to_csv('/mnt/user-data/outputs/Blend-Audit-09-29-2026.csv',index=False)
pd.set_option('display.width',200)
print(aud[aud.Blend>0].head(30).round(2).to_string(index=False))
print(aud.reindex(aud.Delta_vs_SS.abs().sort_values(ascending=False).index).head(18).round(2).to_string(index=False))
print('slate skaters w/ Base>0 and no props:', df[sk&(df.Base>0)&df.Vegas.isna()].Name.tolist())

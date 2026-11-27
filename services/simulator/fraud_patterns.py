import config as cfg
import numpy as np
import pandas as pd


def mark_fraud_customers(rng,customers):
    df=customers.copy()
    df['fraud_type']="none"
    n=len(df)
    perm=rng.permutation(n)
    
    cutoff=pd.Timestamp(cfg.SIM_END)-pd.Timedelta(days=200)
    early=perm[(df["signup_date"]<=cutoff).to_numpy()[perm]]
    bust=early[: int(n*cfg.FRAUD_BUSTOUT_SHARE)]
    
    rest=perm[~np.isin(perm,bust)]
    n_ring=int(n*cfg.FRAUD_RINGS_SHARE)
    n_synth=int(n*cfg.FRAUD_SYNTHETIC_SHARE)
    ring=rest[:n_ring]
    synth=rest[n_ring:n_ring+n_synth]
    
    df.loc[bust,"fraud_type"]="bust_out"
    df.loc[synth,"fraud_type"]="synthetic"
    df.loc[ring,"fraud_type"]="ring"
    
    pos,ring_no=0,0
    while pos< len(ring):
        size=int(rng.integers(cfg.RING_SIZE_MIN,cfg.RING_SIZE_MAX+1))
        members=ring[pos:pos+size]
        
        df.loc[members,"device_id"]=f"dev_ring_{ring_no:04d}"
        if rng.random()<0.5:
            df.loc[members,"phone_id"]=f"phone_id_{ring_no:04d}"
        
        pos+=size
        ring_no+=1
        
    df.loc[synth,"age"]=rng.integers(18,25,len(synth))
    df.loc[synth,"bureau_score"]=np.nan
    df.loc[synth,["kyc_verified","phone_verified"]]=True
    
    df["is_fraud_profile"]=(df["fraud_type"]!="none").astype(int)
    
    return df

def _build(rng,cust_ids,dates,merchants):
    n=len(cust_ids)
    
    risky=merchants[merchants["risk_tier"] == "high"].reset_index(drop=True)
    m=risky.iloc[rng.integers(0,len(risky),n)].reset_index(drop=True)
    plan=rng.choice(["pay in 3","pay in 4"],size=n)
    hi=pd.Series(plan).map({k:v["max"] for k,v in cfg.PLANS.items()})
    
    amount=np.clip(m["avg_ticket"]*rng.uniform(1.0,2.0,n),500,hi)
    
    return pd.DataFrame({
        "customer_id": cust_ids,
        "merchant_id": m["merchant_id"].to_numpy(),
        "category": m["category"].to_numpy(),
        "plan": plan,
        "amount_sar": amount,
        "order_date": dates,
        "tenor_days": pd.Series(plan).map(
            {k: v["tenor_days"] for k, v in cfg.PLANS.items()}).to_numpy(),
        "is_fraud_order": True,
    })  

def inject_fraud_orders(rng,orders,customers,merchants):
    ftype=customers.set_index("customer_id")["fraud_type"]
    
    keep=~orders["customer_id"].map(ftype).isin(["ring","synthetic"])
    base=orders[keep].copy()
    base["is_fraud_order"]=False
    
    parts= [base]
    end=pd.Timestamp(cfg.SIM_END)
    
    for kind,lo,hi in [("synthetic",1,1),("ring",2,4),("bust_out",6,10)]:
        c=customers[customers["fraud_type"]==kind].reset_index(drop=True)
        
        if c.empty:
            continue
        
        counts=rng.integers(lo,hi+1,len(c))
        idx=np.repeat(np.arange(len(c)),counts)
        n=len(idx)
        signup=c["signup_date"].iloc[idx].reset_index(drop=True)
        
        if kind=="synthetic":
            dates=signup+pd.to_timedelta(rng.uniform(1, 20,n),unit="h")
        
        elif kind == "ring":
            dates=signup + pd.to_timedelta(rng.uniform(1, 10,n),unit="D")
        
        else: 
            avail=(end-pd.Timedelta(days=130)-c['signup_date']).dt.days.to_numpy()
            start_days= 60 + rng.random(len(c)) * (avail-60)
            start=c["signup_date"]+pd.to_timedelta(start_days,unit="D")
            dates=(start.iloc[idx].reset_index(drop=True)+ pd.to_timedelta(rng.uniform(0, 72,n),unit="h"))
        dates=dates.clip(upper=end)
        
        parts.append(_build(rng,c["customer_id"].iloc[idx].to_numpy(),dates,merchants))
        
    out=pd.concat(parts,ignore_index=True).drop(columns="order_id")
    out=out.sort_values("order_date").reset_index(drop=True)
    out.insert(0,"order_id",[f"O{i:08d}" for i in range(len(out))])
    
    return out
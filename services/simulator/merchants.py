import config as cfg
import numpy as np
import pandas as pd


def generate_merchants(rng,n=cfg.N_MERCHANTS):
    
    names=list(cfg.CATEGORIES)
    weights=[cfg.CATEGORIES[k]["weight"] for k in names]
    category=rng.choice(names,size=n,p=weights)


    typical=np.array([cfg.CATEGORIES[c]["avg_ticket"] for c in category])
    avg_ticket=(typical * rng.lognormal(0,0.25,n)).round(2)


    return pd.DataFrame({
        "merchant_id":[f"M{i:05d}"for i in range(n)],
        "category":category,
        "risk_tier":[cfg.CATEGORIES[c]["risk_tier"] for c in category],
        "avg_ticket":avg_ticket
    })

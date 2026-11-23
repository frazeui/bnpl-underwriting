import config as cfg
import numpy as np
import pandas as pd
from merchants import generate_merchants


def draw_order_counts(rng,customers):
    end=pd.Timestamp(cfg.SIM_END)
    days_active=(end - customers["signup_date"]).dt.days.to_numpy()
    expected=cfg.ORDERS_PER_MONTH * days_active / 30

    return rng.poisson(expected),days_active


def generate_orders(rng,customers,merchants):
    _n_orders,days_active=draw_order_counts(rng,customers)

    cust_idx=np.repeat(np.arange(len(customers)),repeats=_n_orders)
    total=len(cust_idx)
    
    offset=rng.random(total)*days_active[cust_idx]
    signup=customers["signup_date"].iloc[cust_idx].reset_index(drop=True)
    order_date=signup + pd.to_timedelta(offset,unit="D")
    
    merchant_idx=rng.integers(0,len(merchants),size=total)
    plan_names=list(cfg.PLANS)
    plan=rng.choice(plan_names,size=total,p=[cfg.PLANS[k]["share"] for k in plan_names])
    
    
    typical=merchants['avg_ticket'].to_numpy()[merchant_idx]
    amount=typical * rng.lognormal(0,cfg.BASKET_SIGMA,total)
    lo=pd.Series(plan).map({k:v["min"] for k ,v in cfg.PLANS.items()}).to_numpy()
    hi=pd.Series(plan).map({k:v["max"] for k,v in cfg.PLANS.items()}).to_numpy()
    
    amount=np.clip(amount,lo,hi).round()
    
    
    orders=pd.DataFrame({
        "customer_id":customers['customer_id'].to_numpy()[cust_idx],
        "merchant_id":merchants['merchant_id'].to_numpy()[merchant_idx],
        "category":merchants['category'].to_numpy()[merchant_idx],
        "plan":plan,
        "amount_sar":amount,
        "order_date":order_date,
        "tenor_days":pd.Series(plan).map({
            k:v['tenor_days'] for k,v in cfg.PLANS.items()
        }).to_numpy()
    })
    
    orders=orders.sort_values("order_date").reset_index(drop=True)
    orders.insert(0,"order_id",[f"O{i:08d}" for i in range(len(orders))])
    
    return orders


if __name__=="__main__":
    from pathlib import Path
    
    customers=pd.read_parquet("data/raw/customers.parquet")
    merchants=generate_merchants(np.random.default_rng(cfg.SEED+1))
    orders=generate_orders(np.random.default_rng(cfg.SEED+2),customers,merchants)
    
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    merchants.to_parquet("data/raw/merchants.parquet",index=False)
    orders.to_parquet("data/raw/orders.parquet",index=False)
    
    print(orders.head())
    print(f"\n{len(merchants)} merchants, {len(orders):,} orders saved")
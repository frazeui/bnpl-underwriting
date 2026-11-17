import config as cfg
import numpy as np
import pandas as pd


def make_ids(n):
        return [f"C{i:07d}" for i in range(n)]


def draw_age(rng,n):
        age=rng.normal(cfg.AGE_MEAN,cfg.AGE_SD,n)
        return np.clip(age,cfg.AGE_MIN,cfg.AGE_MAX).round().astype(int)


def draw_from_share(rng,shares:dict,n):
        return rng.choice(list(shares),size=n,p=list(shares.values()))

def draw_employment(rng,n):
        names=list(cfg.EMPLOYMENT)
        shares=[cfg.EMPLOYMENT[k]["share"]for k in names]

        return rng.choice(names,size=n,p=shares)

def draw_income(rng,employment):

        medians=pd.Series(employment).map({k:v['income_median'] for k,v in cfg.EMPLOYMENT.items()}).to_numpy()

        income=medians*rng.lognormal(0,cfg.INCOME_SIGMA,len(employment))

        return np.clip(income,cfg.INCOME_MIN,cfg.INCOME_MAX).round()

def draw_obligation(rng,income):
        a,b=cfg.OBLIGATION_BETA
        share=rng.beta(a,b,len(income))

        obligations= (income*share).round()
        dti=(obligations/income).round(3)

        return obligations,dti

def draw_bureau(rng,age,income):
        n=len(age)
        
        score=(
            rng.normal(cfg.BUREAU_MEAN,cfg.BUREAU_SD,n) +
            cfg.BUREAU_PER_LOG_INCOME * np.log(income / 7_000) +
            cfg.BUREAU_PER_AGE_YEAR * (age-33)
            )
        
        score=np.clip(score,cfg.BUREAU_MIN,cfg.BUREAU_MAX).round()

        thin_prob=np.where(age<24,cfg.THIN_FILE_PROB_YOUNG,cfg.THIN_FILE_PROB_ADULT)
        is_thin=rng.random(n)<thin_prob

        score[is_thin]=np.nan

        return score

def draw_signup_dates(rng,n):
        span=(cfg.SIM_END-cfg.SIM_START).days
        days=rng.integers(0,span,n)
        return pd.to_datetime(cfg.SIM_START)+pd.to_timedelta(days,unit="D")

def generate_customers(rng,n=cfg.N_CUSTOMERS):
        age=draw_age(rng,n)
        employment=draw_employment(rng,n)
        income=draw_income(rng,employment)
        obligations,dti=draw_obligation(rng,income)

        return pd.DataFrame({
            "customer_id":make_ids(n),
            "age":age,
            "city":draw_from_share(rng,cfg.CITIES,n),
            "employment_type":employment,
            "monthly_income_sar":income,
            "monthly_obligations_sar":obligations,
            "dti":dti,
            "bureau_score":draw_bureau(rng,age,income),
            "kyc_verified":rng.random(n) < cfg.KYC_VERIFIED_PROB,
            "phone_verified":rng.random(n) < cfg.PHONE_VERIFIED_PROB,
            "signup_date":draw_signup_dates(rng,n),
            "device_id":[f"dev_{i:07d}" for i in range(n)],
            "phone_id":[f"ph_{i:07d}" for i in range(n)],
            "gender":draw_from_share(rng,cfg.GENDER,n),
            "nationality":draw_from_share(rng,cfg.NATIONALITY,n),
            "is_fraud_profile":0,
        })

if __name__=='__main__':
        from pathlib import Path
        rng=np.random.default_rng(cfg.SEED)
        df=generate_customers(rng)
        Path("data/raw").mkdir(parents=True,exist_ok=True)
        df.to_parquet("data/raw/customers.parquet",index=False)
        print(df.head())
        print(f"\n{len(df):,} customers saved")
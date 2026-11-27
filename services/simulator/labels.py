import config as cfg
import numpy as np
import pandas as pd


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def build_risk_score(rng, orders, customers):
    df = orders.merge(customers, on="customer_id", how="left")

    emp_shift = df["employment_type"].map(
        {k: v["risk_shift"] for k, v in cfg.EMPLOYMENT.items()}
    )
    cat_shift = df["category"].map(
        {k: v["risk_shift"] for k, v in cfg.CATEGORIES.items()}
    )

    bureau = df["bureau_score"].fillna(cfg.BUREAU_MEAN)
    thin = df["bureau_score"].isna().astype(float)
    ratio = np.minimum(df["amount_sar"] / df["monthly_income_sar"], 2.0)

    risk = (
        cfg.RISK_BASE
        + emp_shift
        + cat_shift
        + cfg.RISK_PER_DTI * (df["dti"])
        + cfg.RISK_PER_BUREAU_100 * (bureau - cfg.BUREAU_MEAN) / 100 
        + cfg.RISK_THIN_FILE * thin
        + cfg.RISK_PER_BASKET_RATIO * ratio
        + rng.normal(0, cfg.RISK_NOISE_SD, len(df))
    )

    return risk.to_numpy()


def add_labels(rng, orders, customers):

    risk = build_risk_score(rng, orders, customers)
    true_pd = sigmoid(risk)
    is_fraud=(orders["is_fraud_order"].to_numpy() if "is_fraud_order" in orders else np.zeros(len(orders),dtype=bool))
    defaulted = (rng.random(len(orders)) < true_pd) | is_fraud

    labels = pd.DataFrame(
        {
            "order_id": orders["order_id"],
            "default_flag": defaulted.astype(int),
            "label_known_date": orders["order_date"]
            + pd.Timedelta(days=cfg.LABEL_WINDOWS_DAYS),
            "true_pd": true_pd,
            "is_fraud_order":is_fraud
        }
    )

    labels["is_labeled"] = labels["label_known_date"] <= pd.Timestamp(cfg.SIM_END)
    labels["default_flag"] = labels["default_flag"].astype("Int8")
    labels.loc[~labels["is_labeled"], "default_flag"] = pd.NA

    return labels


if __name__ == "__main__":
    customers = pd.read_parquet("data/raw/customers.parquet")
    orders = pd.read_parquet("data/raw/orders.parquet")

    labels = add_labels(np.random.default_rng(cfg.SEED + 3), orders, customers)
    labels.to_parquet("data/raw/labels.parquet", index=False)

    known = labels[labels["is_labeled"]]
    print(labels.head())
    print(f"\n{len(labels):,} orders, {len(known):,} labeled")
    print(
        f"default rate among labeled: {known['default_flag'].astype(float).mean():.3f}"
    )

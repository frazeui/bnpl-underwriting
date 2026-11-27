from pathlib import Path

import config as cfg
import numpy as np
from customers import generate_customers
from fraud_patterns import inject_fraud_orders, mark_fraud_customers
from labels import add_labels
from merchants import generate_merchants
from orders import generate_orders


def build():
    customers = generate_customers(np.random.default_rng(cfg.SEED))
    customers = mark_fraud_customers(np.random.default_rng(cfg.SEED + 4), customers)

    merchants = generate_merchants(np.random.default_rng(cfg.SEED + 1))

    orders = generate_orders(np.random.default_rng(cfg.SEED + 2), customers, merchants)
    orders = inject_fraud_orders(
        np.random.default_rng(cfg.SEED + 5), orders, customers, merchants
    )
    labels = add_labels(np.random.default_rng(cfg.SEED + 3), orders, customers)

    orders = orders.drop(columns="is_fraud_order")

    return customers, merchants, orders, labels


if __name__ == "__main__":
    out = Path("data/raw")
    out.mkdir(parents=True, exist_ok=True)

    customers, merchants, orders, labels = build()

    for name, table in [
        ("customers", customers),
        ("merchants", merchants),
        ("orders", orders),
        ("labels", labels),
    ]:
        table.to_parquet(out / f"{name}.parquet", index=False)
        print(f"{name}: {len(table):,} rows")

    print(customers["fraud_type"].value_counts().to_string())

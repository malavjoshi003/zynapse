"""Load products from MongoDB, with a CSV fallback."""

import pandas as pd
from pymongo.errors import PyMongoError

from app.core.database import products_col

_df = None


def _load_csv():
    global _df

    from app.core.loader import load_data as csv_load
    from app.core.loader import get_df as csv_get_df

    csv_load()
    _df = csv_get_df().copy()
    print(f"[CSV] Loaded {len(_df):,} products")


def load_data():
    global _df

    if _df is not None:
        return

    try:
        documents = list(
            products_col().find({}, {"_id": 0})
        )
    except PyMongoError:
        print("[MongoDB] Unavailable; loading CSV")
        _load_csv()
        return

    if not documents:
        print("[MongoDB] No products found; loading CSV")
        _load_csv()
        return

    dataframe = pd.DataFrame(documents)
    dataframe["asin"] = dataframe["asin"].astype("int64")
    dataframe["price"] = dataframe["price"].astype("float32")
    dataframe["stars"] = dataframe["stars"].astype("float32")
    dataframe["boughtInLastMonth"] = (
        dataframe["boughtInLastMonth"].astype("int32")
    )

    _df = dataframe
    print(f"[MongoDB] Loaded {len(_df):,} products")


def get_df():
    if _df is None:
        raise RuntimeError(
            "Product data is not loaded. Call load_data() first."
        )

    return _df
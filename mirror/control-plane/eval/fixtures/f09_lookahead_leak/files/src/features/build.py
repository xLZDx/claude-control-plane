import pandas as pd


def make_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("ts")
    df["ret_next"] = df["close"].pct_change().shift(-1)
    df["feat_vol"] = df["close"].pct_change().rolling(20).std()
    df["feat_mean_ret"] = df["ret_next"].rolling(20).mean()
    df["label"] = (df["ret_next"] > 0).astype(int)
    return df.dropna()

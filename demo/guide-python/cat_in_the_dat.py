"""A simple demo for categorical data support using dataset from Kaggle categorical data
tutorial.

The excellent tutorial is at:
https://www.kaggle.com/shahules/an-overview-of-encoding-techniques

And the data can be found at:
https://www.kaggle.com/shahules/an-overview-of-encoding-techniques/data

Also, see the tutorial for using XGBoost with categorical data:
https://xgboost.readthedocs.io/en/latest/tutorials/categorical.html

    .. versionadded 1.6.0

"""

from __future__ import annotations
from time import time
import os
from tempfile import TemporaryDirectory

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

import xgboost as xgb


def load_cat_in_the_dat() -> tuple[pd.DataFrame, pd.Series]:
    """Assuming you have already downloaded the data into `input` directory."""

    df_train = pd.read_csv("./input/cat-in-the-dat/train.csv")

    print(
        "train data set has got {} rows and {} columns".format(
            df_train.shape[0], df_train.shape[1]
        )
    )
    X = df_train.drop(["target"], axis=1)
    y = df_train["target"]

    for i in range(0, 5):
        X["bin_" + str(i)] = X["bin_" + str(i)].astype("category")

    for i in range(0, 5):
        X["nom_" + str(i)] = X["nom_" + str(i)].astype("category")

    for i in range(5, 10):
        X["nom_" + str(i)] = X["nom_" + str(i)].apply(int, base=16)

    for i in range(0, 6):
        X["ord_" + str(i)] = X["ord_" + str(i)].astype("category")

    print(
        "train data set has got {} rows and {} columns".format(X.shape[0], X.shape[1])
    )
    return X, y


params = {"tree_method": "gpu_hist", "use_label_encoder": False, "n_estimators": 32}


def categorical_model(X: pd.DataFrame, y: pd.Series, output_dir: str) -> None:
    """Train using builtin categorical data support from XGBoost"""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, random_state=1994, test_size=0.2
    )
    # Specify `enable_categorical`.
    clf = xgb.XGBClassifier(**params, enable_categorical=True)
    clf.fit(
        X_train,
        y_train,
        eval_set=[(X_test, y_test), (X_train, y_train)],
        eval_metric="auc",
    )
    clf.save_model(os.path.join(output_dir, "categorical.json"))

    y_score = clf.predict_proba(X_test)[:, 1]  # proba of positive samples
    auc = roc_auc_score(y_test, y_score)
    print("AUC of using builtin categorical data support:", auc)


def onehot_encoding_model(X: pd.DataFrame, y: pd.Series, output_dir: str) -> None:
    """Train using one-hot encoded data."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, random_state=42, test_size=0.2
    )
    # Specify `enable_categorical`.
    clf = xgb.XGBClassifier(**params, enable_categorical=False)
    clf.fit(
        X_train,
        y_train,
        eval_set=[(X_test, y_test), (X_train, y_train)],
        eval_metric="auc",
    )
    clf.save_model(os.path.join(output_dir, "one-hot.json"))

    y_score = clf.predict_proba(X_test)[:, 1]  # proba of positive samples
    auc = roc_auc_score(y_test, y_score)
    print("AUC of using onehot encoding:", auc)


if __name__ == "__main__":
    X, y = load_cat_in_the_dat()

    with TemporaryDirectory() as tmpdir:
        start = time()
        categorical_model(X, y, tmpdir)
        end = time()
        print("Duration:categorical", end - start)

        X = pd.get_dummies(X)
        start = time()
        onehot_encoding_model(X, y, tmpdir)
        end = time()
        print("Duration:onehot", end - start)

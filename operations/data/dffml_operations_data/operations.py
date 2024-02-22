import numpy as np
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import f_classif, SelectKBest, SelectPercentile

from dffml.df.base import op

from .definitions import (
    n_iter,
    strategy,
    input_data,
    categories,
    output_data,
    random_state,
    n_components,
    missing_values,
    target_data,
    k,
    percentile,
    score_func
)


@op(
    inputs={"data": input_data, "n_components": n_components},
    outputs={"result": output_data},
)
async def principal_component_analysis(
    data, n_components=None,
):
    """
    Decomposes the data into (n_samples, n_components)
    using PCA method

    Parameters
    ----------
    data : List[List[int]]
        data to be decomposed.

    n_components : int
        number of colums the data should have after decomposition.

    Returns
    -------
    result: Data having dimensions (n_samples, n_components)
    """
    pca = PCA(n_components=n_components)
    new_data = pca.fit_transform(data)
    return {"result": new_data}


@op(
    inputs={
        "data": input_data,
        "n_components": n_components,
        "n_iter": n_iter,
        "random_state": random_state,
    },
    outputs={"result": output_data},
)
async def singular_value_decomposition(
    data, n_components=2, n_iter=5, random_state=None,
):
    """
    Decomposes the data into (n_samples, n_components)
    using SVD method.

    Parameters
    ----------
    data : List[List[int]]
        data to be decomposed.

    n_components : int
        number of colums the data should have after decomposition.

    Returns
    -------
    result: Data having dimensions (n_samples, n_components)
    """
    svd = TruncatedSVD(
        n_components=n_components, n_iter=n_iter, random_state=random_state
    )
    new_data = svd.fit_transform(data)
    return {"result": new_data}


@op(
    inputs={
        "data": input_data,
        "missing_values": missing_values,
        "strategy": strategy,
    },
    outputs={"result": output_data},
)
async def simple_imputer(data, missing_values=np.nan, strategy="mean"):
    """
    Imputation method for missing values

    Parameters
    ----------
    data : List[List[int]]
        data in which missing values are present

    missing_values : Any str, int, float, None default = np.nan
        The value present in place of missing value

    strategy : str "mean", "median", "constant", "most_frequent" default = "mean"
        The value present in place of missing value

    Returns
    -------
    result: Dataset having missing values imputed with the strategy
    """
    if missing_values not in (int, float, str, None, np.nan):
        raise Exception(
            f"Missing values should be one of: str, float, int, None, np.nan got {missing_values}"
        )

    if strategy not in ("mean", "median", "constant", "most_frequent"):
        raise Exception(
            f"Strategy should be one of mean, median, constant, most_frequent got {strategy}"
        )

    imp = SimpleImputer(missing_values=missing_values, strategy=strategy)
    new_data = imp.fit_transform(data)
    return {"result": new_data}


@op(
    inputs={"data": input_data, "categories": categories},
    outputs={"result": output_data},
)
async def one_hot_encoder(data, categories):
    """
    One hot encoding for categorical data columns

    Parameters
    ----------
    data : List[List[int]]
        data to be encoded.

    categories : List[List[str]]
        Categorical values which needs to be encoded

    Returns
    -------
    result: Encoded data for categorical values
    """
    enc = OneHotEncoder(categories=categories)
    enc.fit(data)
    new_data = enc.transform(data).toarray()
    return {"result": new_data}


@op(inputs={"data": input_data}, outputs={"result": output_data})
async def standard_scaler(data):
    """
    Standardize features by removing the mean and
    scaling to unit variance.

    Parameters
    ----------
    data: List[List[int]]
        data that needs to be standardized
    
    Returns
    -------
    result: Standardized data
    """
    scaler = StandardScaler()
    new_data = scaler.fit_transform(data)
    return {"result": new_data.tolist()}


@op(
    inputs={"data": input_data}, outputs={"result": output_data},
)
async def remove_whitespaces(data):
    """
    Removes white-spaces from the dataset

    Parameters
    ----------
    data : List[List[int]]
        dataset.

    Returns
    -------
    result: dataset having whitespaces removed
    """
    new_data = np.char.strip(data)
    return {"result": new_data}


@op(
    inputs={"data": input_data}, outputs={"result": output_data},
)
async def ordinal_encoder(data):
    """
    One hot encoding for categorical data columns

    Parameters
    ----------
    data : List[List[int]]
        data to be encoded.

    categories : List[List[str]]
        Categorical values which needs to be encoded

    Returns
    -------
    result: Encoded data for categorical values

    References:

        - https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.SelectKBest.html
    
    """
    enc = OneHotEncoder()
    enc.fit(data)
    new_data = enc.transform(data).toarray()
    return {"result": new_data}

@op(
    inputs={"data": input_data, "target_data": target_data, "k": k, "score_func": score_func},
    outputs={"result": output_data}
)
async def select_k_best(data, target_data, score_func=f_classif, k=10):
    """
    Select the top k features, based on the score function.

    Parameters
    ----------
    data : List[List[int]]
        Input data, excluding the target column
    target_data : List[int]
        1D list containing values for the target column.
    score_func : function
        Function that takes in data and target_data, and returns 
        a pair of arrays (scores, pvalues) or a single array with
        scores.
    k : int
        Number of top features to select.

    Returns
    -------
    result: Encoded data for categorical values
    """

    selector = SelectKBest(score_func, k=k)
    new_data = selector.fit_transform(data, target_data)
    return {"result": new_data}

@op(
    inputs={"data": input_data, "target_data": target_data, "percentile": percentile, "score_func": score_func},
    outputs={"result": output_data}
)
async def select_percentile(data, target_data, score_func=f_classif, percentile=10):
    """
    Select a certain top percentile of features, based on the score function.

    Parameters
    ----------
    data : List[List[int]]
        Input data, excluding the target column
    target_data : List[int]
        1D list containing values for the target column.
    score_func : function
        Function that takes in data and target_data, and returns 
        a pair of arrays (scores, pvalues) or a single array with
        scores.
    percentile : int
        Percentile of top features to select.

    Returns
    -------
    result: Encoded data for categorical values

    References:

        - https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.SelectPercentile.html

    """

    selector = SelectPercentile(score_func, percentile=percentile)
    new_data = selector.fit_transform(data, target_data)
    return {"result": new_data}

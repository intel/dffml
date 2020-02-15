import numbers
import numpy as np

from sagaopt import row_norms, sag_solver

async def _handle_zeros_in_scale(scale, copy=True):
    ''' Makes sure that whenever scale is zero, we handle it correctly.

    This happens in most scalers when we have constant features.'''

    # if we are fitting on 1D arrays, scale might be a scalar
    if np.isscalar(scale):
        if scale == .0:
            scale = 1.
        return scale
    elif isinstance(scale, np.ndarray):
        if copy:
            # New array to avoid side-effects
            scale = scale.copy()
        scale[scale == 0.0] = 1.0
        return scale

async def f_normalize(X, norm='l2', axis=1, copy=True, return_norm=False):
    if norm not in ('l1', 'l2', 'max'):
        raise ValueError("'%s' is not a supported norm" % norm)


    if axis == 0:
        X = X.T

    if norm == 'l1':
        norms = np.abs(X).sum(axis=1)
    elif norm == 'l2':
        norms = await row_norms(X)
    elif norm == 'max':
        norms = np.max(X, axis=1)
    norms = await _handle_zeros_in_scale(norms, copy=False)
    X /= norms[:, np.newaxis]

    if axis == 0:
        X = X.T

    if return_norm:
        return X, norms
    else:
        return X


async def _ridge_regression(X, y, alpha, sample_weight=None,
                      max_iter=None, tol=1e-3, verbose=0, random_state=None,
                      return_n_iter=False, return_intercept=False,
                      X_scale=None, X_offset=None, check_input=True):
    has_sw = sample_weight is not None

    n_samples, n_features = X.shape

    if y.ndim > 2:
        raise ValueError("Target y has the wrong shape %s" % str(y.shape))

    ravel = False
    if y.ndim == 1:
        y = y.reshape(-1, 1)
        ravel = True

    n_samples_, n_targets = y.shape

    if n_samples != n_samples_:
        raise ValueError("Number of samples in X and y does not correspond:"
                        " %d != %d" % (n_samples, n_samples_))

    if has_sw:
        if np.atleast_1d(sample_weight).ndim > 1:
            raise ValueError("Sample weights must be 1D array or scalar")
        # There should be either 1 or n_targets penalties
    alpha = np.asarray(alpha, dtype=X.dtype).ravel()
    if alpha.size not in [1, n_targets]:
        raise ValueError("Number of targets and number of penalties "
                         "do not correspond: %d != %d"
                         % (alpha.size, n_targets))
    if alpha.size == 1 and n_targets > 1:
        alpha = np.repeat(alpha, n_targets)
    n_iter = None

    # precompute max_squared_sum for all targets
    squared_sum = await row_norms(X, squared=True)
    max_squared_sum = squared_sum.max()
    coef = np.empty((y.shape[1], n_features), dtype=X.dtype)
    n_iter = np.empty(y.shape[1], dtype=np.int32)
    intercept = np.zeros((y.shape[1], ), dtype=X.dtype)
    for i, (alpha_i, target) in enumerate(zip(alpha, y.T)):
            init = {'coef': np.zeros((n_features + int(return_intercept), 1),
                                     dtype=X.dtype)}
            coef_, n_iter_, _ = await sag_solver(
                X, target.ravel(), sample_weight, 'squared', alpha_i, 0,
                max_iter, tol, verbose, random_state, False, max_squared_sum,
                init,
                is_saga=True)
            if return_intercept:
                coef[i] = coef_[:-1]
                intercept[i] = coef_[-1]
            else:
                coef[i] = coef_
            n_iter[i] = n_iter_

    if intercept.shape[0] == 1:
            intercept = intercept[0]
    coef = np.asarray(coef)

    if ravel:
        # When y was passed as a 1d-array, we flatten the coefficients.
        coef = coef.ravel()

    if return_n_iter and return_intercept:
        return coef, n_iter, intercept
    elif return_intercept:
        return coef, intercept
    elif return_n_iter:
        return coef, n_iter
    else:
        return coef
    


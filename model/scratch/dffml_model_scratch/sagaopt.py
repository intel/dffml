import numpy as np
import warnings
from sklearn.linear_model.sag_fast import sag32, sag64
from sklearn.utils.seq_dataset import ArrayDataset32, ArrayDataset64
import numbers

async def row_norms(X, squared=False):
    norms = np.einsum('ij,ij->i', X, X)
    if not squared:
        np.sqrt(norms, norms)
    return norms

async def check_random_state(seed):
    if seed is None or seed is np.random:
        return np.random.mtrand._rand
    if isinstance(seed, (numbers.Integral, np.integer)):
        return np.random.RandomState(seed)
    if isinstance(seed, np.random.RandomState):
        return seed
    raise ValueError('%r cannot be used to seed a numpy.random.RandomState'
                     ' instance' % seed)


async def make_dataset(X, y, sample_weight, random_state=None):
    rng =await check_random_state(random_state)
    # seed should never be 0 in SequentialDataset64
    seed = rng.randint(1, np.iinfo(np.int32).max)

    if X.dtype == np.float32:
        ArrayData = ArrayDataset32
    else:
        ArrayData = ArrayDataset64

    dataset = ArrayData(X, y, sample_weight, seed=seed)
    intercept_decay = 1.0

    return dataset, intercept_decay


async def get_auto_step_size(max_squared_sum, alpha_scaled, loss, fit_intercept,
                       n_samples=None,
                       is_saga=False):
    if loss in ('log', 'multinomial'):
        L = (0.25 * (max_squared_sum + int(fit_intercept)) + alpha_scaled)
    elif loss == 'squared':
        # inverse Lipschitz constant for squared loss
        L = max_squared_sum + int(fit_intercept) + alpha_scaled
    else:
        raise ValueError("Unknown loss function for SAG solver, got %s "
                         "instead of 'log' or 'squared'" % loss)
    if is_saga:
        # SAGA theoretical step size is 1/3L or 1 / (2 * (L + mu n))
        # See async defazio et al. 2014
        mun = min(2 * n_samples * alpha_scaled, L)
        step = 1. / (2 * L + mun)
    else:
        # SAG theoretical step size is 1/16L but it is recommended to use 1 / L
        # see http://www.birs.ca//workshops//2014/14w5003/files/schmidt.pdf,
        # slide 65
        step = 1. / L
    return step



async def sag_solver(X, y, sample_weight=None, loss='log', alpha=1., beta=0.,
               max_iter=1000, tol=0.001, verbose=0, random_state=None,
               check_input=True, max_squared_sum=None,
               warm_start_mem=None,
               is_saga=False):


    if warm_start_mem is None:
        warm_start_mem = {}
    # Ridge async default max_iter is None
    if max_iter is None:
        max_iter = 1000
    
    n_samples, n_features = X.shape[0], X.shape[1]
    # As in SGD, the alpha is scaled by n_samples.
    alpha_scaled = float(alpha) / n_samples
    beta_scaled = float(beta) / n_samples

    # if loss == 'multinomial', y should be label encoded.
    n_classes = int(y.max()) + 1 if loss == 'multinomial' else 1

    # initialization
    if sample_weight is None:
        sample_weight = np.ones(n_samples, dtype=X.dtype, order='C')

    if 'coef' in warm_start_mem.keys():
        coef_init = warm_start_mem['coef']
    else:
        # assume fit_intercept is False
        coef_init = np.zeros((n_features, n_classes), dtype=X.dtype,
                             order='C')

    # coef_init contains possibly the intercept_init at the end.
    # Note that Ridge centers the data before fitting, so fit_intercept=False.
    fit_intercept = coef_init.shape[0] == (n_features + 1)
    if fit_intercept:
        intercept_init = coef_init[-1, :]
        coef_init = coef_init[:-1, :]
    else:
        intercept_init = np.zeros(n_classes, dtype=X.dtype)

    if 'intercept_sum_gradient' in warm_start_mem.keys():
        intercept_sum_gradient = warm_start_mem['intercept_sum_gradient']
    else:
        intercept_sum_gradient = np.zeros(n_classes, dtype=X.dtype)

    if 'gradient_memory' in warm_start_mem.keys():
        gradient_memory_init = warm_start_mem['gradient_memory']
    else:
        gradient_memory_init = np.zeros((n_samples, n_classes),
                                        dtype=X.dtype, order='C')
    if 'sum_gradient' in warm_start_mem.keys():
        sum_gradient_init = warm_start_mem['sum_gradient']
    else:
        sum_gradient_init = np.zeros((n_features, n_classes),
                                     dtype=X.dtype, order='C')

    if 'seen' in warm_start_mem.keys():
        seen_init = warm_start_mem['seen']
    else:
        seen_init = np.zeros(n_samples, dtype=np.int32, order='C')

    if 'num_seen' in warm_start_mem.keys():
        num_seen_init = warm_start_mem['num_seen']
    else:
        num_seen_init = 0

    dataset, intercept_decay =await make_dataset(X, y, sample_weight, random_state)

    if max_squared_sum is None:
        max_squared_sum =await row_norms(X, squared=True).max()
    step_size =await get_auto_step_size(max_squared_sum, alpha_scaled, loss,
                                   fit_intercept, n_samples=n_samples,
                                   is_saga=is_saga)
    if step_size * alpha_scaled == 1:
        raise ZeroDivisionError("Current sag implementation does not handle "
                                "the case step_size * alpha_scaled == 1")

    sag = sag64 if X.dtype == np.float64 else sag32
    num_seen, n_iter_ = sag(dataset, coef_init,
                            intercept_init, n_samples,
                            n_features, n_classes, tol,
                            max_iter,
                            loss,
                            step_size, alpha_scaled,
                            beta_scaled,
                            sum_gradient_init,
                            gradient_memory_init,
                            seen_init,
                            num_seen_init,
                            fit_intercept,
                            intercept_sum_gradient,
                            intercept_decay,
                            is_saga,
                            verbose)

    if n_iter_ == max_iter:
        warnings.warn("The max_iter was reached which means "
                      "the coef_ did not converge", BytesWarning)

    if fit_intercept:
        coef_init = np.vstack((coef_init, intercept_init))

    warm_start_mem = {'coef': coef_init, 'sum_gradient': sum_gradient_init,
                      'intercept_sum_gradient': intercept_sum_gradient,
                      'gradient_memory': gradient_memory_init,
                      'seen': seen_init, 'num_seen': num_seen}

    if loss == 'multinomial':
        coef_ = coef_init.T
    else:
        coef_ = coef_init[:, 0]

    return coef_, n_iter_, warm_start_mem
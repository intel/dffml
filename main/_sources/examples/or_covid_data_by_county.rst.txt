COVID Forecasting
=================

Stay home and stay safe folks. This is a sad application of machine learning.

This example covers the following using the Python API.

- Writing a new model. We'll be wrapping fbprophet.

  - Overwriting a :py:class:`SimpleModel <dffml.model.model.SimpleModel>`
    ``__init__()`` method.

  - Using joblib to save and load the fbprophet model class.

- Creating Pandas DataFrames from DFFML :py:class:`Record <dffml.record.Record>`
  objects.

- Downloading dataset files with hash verification.

- Loading data from files using the high level API.

- Using multiple models. Model predictions will be used as feature data for
  another model. This problem can be approached many ways we have implemented it
  the way it is to show how one models prediction can be used as the input to
  another model as a feature.

Plan
----

The dataset we'll be working with is the state of Oregon's COVID case and death
numbers by county.

Our goal is to forecast the number of cases and deaths in each county on any
given day.

The dataset has already been divided into two files, training and test. We'll
download them using the
:py:func:`cached_download() <dffml.util.net.cached_download>`
function.

fbprophet is great at forecasting int or float values given a date. Therefore,
we're going to wrap it using a model class (for more explanation first read the
:ref:`model_tutorial_slr` tutorial).

Setup
-----

We need to install dependencies we'll be importing.

See the https://facebook.github.io/prophet/docs/installation.html#python for
more details

.. code-block:: console
    :test:

    $ python -m pip install joblib pandas "pystan==2.19.1.1"
    $ python -m pip install fbprophet

Code
----

There are lots of comments in the following code so we're not going to explain
everything in this documentation page. Please open an issue or ask on Gitter if
there is anything that is unclear or you think could be changed / improved.

**or_covid_data_by_county.py**

.. literalinclude:: /../examples/or_covid_data_by_county.py
    :test:

Run the file to see the predictions for the test data along with today plus the
next four days.

.. code-block:: console
    :test:

    $ python or_covid_data_by_county.py
    INFO:fbprophet:Disabling yearly seasonality. Run prophet with yearly_seasonality=True to override this.
    INFO:fbprophet:Disabling daily seasonality. Run prophet with daily_seasonality=True to override this.
    Initial log joint probability = -4.48963
        Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes
          99       470.387     0.0198861       992.252       0.934       0.934      117
        Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes
         195       493.794   0.000557792       208.725   1.765e-06       0.001      272  LS failed, Hessian reset
         199       494.869     0.0142908       273.213           1           1      276
        Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes
         274       506.305    0.00034089       135.527   1.069e-06       0.001      410  LS failed, Hessian reset
         299       512.079     0.0479183       140.335           1           1      443
        Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes
         399       523.789   0.000554393       243.109   3.188e-06       0.001      599  LS failed, Hessian reset
        Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes
         499       530.926     0.0021352       316.262      0.4123      0.4123      721
        Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes
         597       537.419   0.000436284       246.382   7.017e-07       0.001      876  LS failed, Hessian reset
         599       537.634    0.00161266       87.1624           1           1      878
        Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes
         699       541.955   0.000221894       75.1759      0.8981      0.8981     1009
        Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes
         799       542.227     0.0031715       187.747           1           1     1137
        Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes
         899       542.449   0.000102382       70.2315      0.6954      0.6954     1257
        Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes
         999       544.304    0.00911989       138.497           1           1     1379
        Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes
        1099       546.541   2.90923e-06       78.8871      0.2538      0.2538     1509
        Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes
        1199       546.616    0.00152174       144.315           1           1     1627
        Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes
        1274       547.735   0.000108332       104.365   7.121e-07       0.001     1759  LS failed, Hessian reset
        1299       547.759   8.21456e-06       72.6784      0.6158      0.6158     1794
        Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes
        1317       547.761   5.74449e-06       68.9362   6.756e-08       0.001     1853  LS failed, Hessian reset
        1399       547.886    0.00178702       80.0121           1           1     1949
        Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes
        1403       547.901   9.98032e-05       107.405   1.012e-06       0.001     1996  LS failed, Hessian reset
        1471       548.011    8.6135e-09        74.944      0.3285      0.3285     2085
    Optimization terminated normally:
      Convergence detected: absolute parameter change was below tolerance
    ---------------------------------------
    county:           : Lincoln
    date:             : 2020-10-25
    predicted_cases   : 510.5316275788172
    actual_cases      : 517
    predicted_deaths  : 9
    actual_deaths     : 13
    ---------------------------------------
    county:           : Lincoln
    date:             : 2020-10-26
    predicted_cases   : 512.1564675524057
    actual_cases      : 517
    predicted_deaths  : 9
    actual_deaths     : 13
    ---------------------------------------
    county:           : Lincoln
    date:             : 2020-10-27
    predicted_cases   : 511.7605249084097
    actual_cases      : 517
    predicted_deaths  : 9
    actual_deaths     : 13
    ---------------------------------------
    county:           : Lincoln
    date:             : 2020-10-28
    predicted_cases   : 512.410408061449
    actual_cases      : 518
    predicted_deaths  : 9
    actual_deaths     : 13
    ---------------------------------------
    county:           : Lincoln
    date:             : 2020-10-29
    predicted_cases   : 512.9605657720964
    actual_cases      : 518
    predicted_deaths  : 9
    actual_deaths     : 13
    ---------------------------------------
    county:           : Lincoln
    date:             : 2020-10-30
    predicted_cases   : 514.5428400672448
    actual_cases      : 519
    predicted_deaths  : 9
    actual_deaths     : 13
    ---------------------------------------
    county:           : Lincoln
    date:             : 2020-10-31
    predicted_cases   : 514.999483186029
    actual_cases      : 519
    predicted_deaths  : 9
    actual_deaths     : 13
    INFO:dffml.record:Evaluated 2021-01-05 {'county': 'Lincoln', 'date': '2021-01-05', 'cases': 576.0638433267727}
    ---------------------------------------
    county:           : Lincoln
    date:             : 2021-01-05
    predicted_cases   : 576.0638433267727
    actual_cases      : Actual Cases Unknown
    predicted_deaths  : 10
    actual_deaths     : Actual Deaths Unknown
    INFO:dffml.record:Evaluated 2021-01-06 {'county': 'Lincoln', 'date': '2021-01-06', 'cases': 576.7137264798116}
    ---------------------------------------
    county:           : Lincoln
    date:             : 2021-01-06
    predicted_cases   : 576.7137264798116
    actual_cases      : Actual Cases Unknown
    predicted_deaths  : 10
    actual_deaths     : Actual Deaths Unknown
    INFO:dffml.record:Evaluated 2021-01-07 {'county': 'Lincoln', 'date': '2021-01-07', 'cases': 577.2638841904583}
    ---------------------------------------
    county:           : Lincoln
    date:             : 2021-01-07
    predicted_cases   : 577.2638841904583
    actual_cases      : Actual Cases Unknown
    predicted_deaths  : 10
    actual_deaths     : Actual Deaths Unknown
    INFO:dffml.record:Evaluated 2021-01-08 {'county': 'Lincoln', 'date': '2021-01-08', 'cases': 578.8461584856071}
    ---------------------------------------
    county:           : Lincoln
    date:             : 2021-01-08
    predicted_cases   : 578.8461584856071
    actual_cases      : Actual Cases Unknown
    predicted_deaths  : 10
    actual_deaths     : Actual Deaths Unknown
    INFO:dffml.record:Evaluated 2021-01-09 {'county': 'Lincoln', 'date': '2021-01-09', 'cases': 579.3028016043917}
    ---------------------------------------
    county:           : Lincoln
    date:             : 2021-01-09
    predicted_cases   : 579.3028016043917
    actual_cases      : Actual Cases Unknown
    predicted_deaths  : 10
    actual_deaths     : Actual Deaths Unknown

# -*- coding: utf-8 -*-
"""
Functions and Plots relating to Closure Test
Statistical Estimators.
"""

import logging

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from reportengine.figure import figure
from reportengine.checks import make_argcheck
from reportengine.table import table
from reportengine import collect

from validphys.results import experiment_results, total_experiments_chi2data
from validphys.dataplots import plot_phi_scatter_dataspecs
from validphys.checks import check_pdf_is_montecarlo
from validphys import plotutils
from validphys.calcutils import calc_chi2, bootstrap_values

log = logging.getLogger(__name__)

exp_result_underlying = collect(experiment_results, ('fitunderlyinglaw',))

def bias_experiment(experiment_results,
                    exp_result_underlying):
    """Calculates the bias for a given fit and experiment. The bias is the chi2
    between the level zero closure replica and the level zero of the PDF used to
    generate the data. The underlying law is taken from the fit runcard.
    """
    dt_ct, th_ct = experiment_results
    #does collect need to collect a list even with one element?
    _, th_ul = exp_result_underlying[0]
    central_diff = th_ct.central_value - th_ul.central_value
    bias_out = calc_chi2(dt_ct.sqrtcovmat, central_diff)/len(dt_ct)
    return bias_out

experiments_bias = collect('bias_experiment', ('experiments',))
fits_experiments_bias = collect('experiments_bias', ('fits', 'fitcontext',))

@table
def biases_table(fits_experiments, fits_experiments_bias, fits):
    """Creates a table with fits as the columns and the experiments from both
    fits as the row index.
    """
    col = ['bias']
    dfs = []
    for fit, experiments, biases in zip(fits, fits_experiments, fits_experiments_bias):
        records = []
        for biasres, experiment in zip(biases, experiments):
            records.append(dict(
                    experiment=str(experiment),
                    bias=biasres
            ))
        df = pd.DataFrame.from_records(records,
                 columns=('experiment','bias'),
                 index = ('experiment')
             )
        df.columns = pd.MultiIndex.from_product(([str(fit)], col))
        dfs.append(df)
    return pd.concat(dfs, axis=1, sort=True)

@figure
def plot_biases(biases_table):
    """
    Plot the bias of each experiment for all fits with bars. For information on
    how biases is calculated see `bias_experiment`
    """
    fig, ax = plotutils.barplot(biases_table.values.T,
                        collabels=biases_table.index.values,
                        datalabels=biases_table.columns.droplevel(1).values
              )
    ax.set_title("Biases for experiments")
    ax.legend()
    return fig

@check_pdf_is_montecarlo
def bootstrap_bias_experiment(
        experiment_results, exp_result_underlying, bootstrap_samples=500):
    """Bootstrap `bias_experiment` across replicas"""
    dt_ct, th_ct = experiment_results
    _, th_ul = exp_result_underlying[0]
    th_ct_boot_cv = bootstrap_values(th_ct._rawdata, bootstrap_samples)
    boot_diffs = th_ct_boot_cv - th_ul.central_value[:, np.newaxis]
    boot_bias = calc_chi2(dt_ct.sqrtcovmat, boot_diffs)/len(dt_ct)
    return boot_bias

experiments_bootstrap_bias = collect('bootstrap_bias_experiment', ('experiments',))
fits_experiments_bootstrap_bias = collect('experiments_bootstrap_bias', ('fits', 'fitcontext',))

@figure
def plot_fits_bootstrap_bias(
    fits_experiments_bootstrap_bias, fits_name_with_covmat_label, fits_experiments):
    """Plot the bias for each experiment for all `fits` as a scatter point with an error bar,
    where the error bar is given by bootstrapping the bias across replicas

    The number of bootstrap samples can be controlled by the parameter `bootstrap_samples`
    """
    # plot_phi_scatter_dataspecs gets an input of the same type and gives what we want
    fig = plot_phi_scatter_dataspecs(
        fits_experiments, fits_name_with_covmat_label, fits_experiments_bootstrap_bias)
    return fig


fits_exps_bootstrap_chi2_central = collect('experiments_bootstrap_chi2_central',
                                           ('fits', 'fitcontext',))
fits_chi2_t0_pseudodata = collect(total_experiments_chi2data, ('fits', 'fitinputcontext', 'fitunderlyinglaw'))

def delta_chi2_bootstrap(fits_chi2_t0_pseudodata,
                         fits_exps_bootstrap_chi2_central):
    """Bootstraps delta chi2 for specified fits.
    Delta chi2 measures whether the level one data is fitted better by
    the underlying law or the specified fit, it is a measure of overfitting.

    delta chi2 = (chi2(T[<f>], D_1) - chi2(T[f_in], D_1))/chi2(T[f_in], D_1)

    where T[<f>] is central theory prediction from fit, T[f_in] is theory
    prediction from t0 pdf (input) and D_1 is level 1 closure data

    Exact details on delta chi2 can be found in 1410.8849 eq (28).
    """
    closure_total_chi2_boot = np.sum(fits_exps_bootstrap_chi2_central, axis=1)
    t0_pseudodata_chi2 = np.array([chi2.central_result for chi2 in fits_chi2_t0_pseudodata])
    deltachi2boot = (closure_total_chi2_boot -
                     t0_pseudodata_chi2[:, np.newaxis])\
                     /t0_pseudodata_chi2[:, np.newaxis]
    return deltachi2boot

@make_argcheck
def check_use_fitcommondata(use_fitcommondata):
    if not use_fitcommondata:
        log.warning("Delta chi2 should be calculated on a closure test, "
                    "`use_fitcommondata` should be True.")

@check_use_fitcommondata
@figure
def plot_delta_chi2(delta_chi2_bootstrap, fits, use_fitcommondata):
    """Plots distributions of delta chi2 for each fit in `fits`.
    Distribution is generated by bootstrapping. For more information
    on delta chi2 see `delta_chi2_bootstrap`
    """
    delta_chi2 = delta_chi2_bootstrap.T
    labels= [fit.label for fit in fits]
    fig, ax = plt.subplots()
    for i, label in enumerate(labels):
        ax.hist(delta_chi2[:, i], alpha=0.3, label=label, zorder=100)
    plt.xlabel(r'$\Delta_{\chi^{2}}$')
    l = ax.legend()
    l.set_zorder(1000)
    return fig

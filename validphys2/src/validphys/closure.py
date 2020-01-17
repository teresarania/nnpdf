# -*- coding: utf-8 -*-
"""
Functions and Plots relating to Closure Test
Statistical Estimators.
"""

import logging
from collections import namedtuple

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
from validphys.calcutils import calc_chi2, bootstrap_values, calc_phi

log = logging.getLogger(__name__)

exp_result_underlying = collect(experiment_results, ('fitunderlyinglaw',))

BiasData = namedtuple('BiasData', ('bias', 'ndata'))

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
    return BiasData(bias_out, len(dt_ct))

experiments_bias = collect('bias_experiment', ('experiments',))
fits_experiments_bias = collect('experiments_bias', ('fits', 'fitcontext',))

@table
def biases_table(
        fits_experiments, fits_experiments_bias, fits, show_total:bool=False):
    """Creates a table with fits as the columns and the experiments from both
    fits as the row index.
    """
    col = ['bias']
    dfs = []
    for fit, experiments, biases in zip(fits, fits_experiments, fits_experiments_bias):
        total= 0
        total_points= 0
        records = []
        for biasres, experiment in zip(biases, experiments):
            records.append(dict(
                    experiment=str(experiment),
                    bias=biasres.bias
            ))
            if show_total:
                total += biasres.bias*biasres.ndata
                total_points += biasres.ndata
        if show_total:
            total /= total_points
            records.append(dict(
                    experiment="Total",
                    bias=total))

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
    ax.set_title("Biases per experiment for each fit")
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
    ax = fig.gca()
    ax.set_title("Bias for each fit with errorbars from bootstrap")
    return fig

@table
def fits_bootstrap_bias_table(
    fits_experiments_bootstrap_bias,
    fits_name_with_covmat_label,
    fits_experiments,
):
    """Produce a table with bias for each experiment for each fit, along with
    variance calculated from doing a bootstrap sample
    """
    col = ['bias', 'bias std. dev.']
    dfs = []
    for fit, experiments, biases in zip(
            fits_name_with_covmat_label,
            fits_experiments,
            fits_experiments_bootstrap_bias,
            ):
        records = []
        for biasres, experiment in zip(biases, experiments):
            records.append(dict(
                    experiment=str(experiment),
                    bias=biasres.mean(),
                    bias_std=biasres.std()
            ))
        df = pd.DataFrame.from_records(records,
                 columns=('experiment','bias', 'bias_std'),
                 index = ('experiment')
             )
        df.columns = pd.MultiIndex.from_product(([str(fit)], col))
        dfs.append(df)
    return pd.concat(dfs, axis=1, sort=True)


fits_bs_phi_exps = collect('experiments_bootstrap_phi', ('fits', 'fitcontext'))

@table
def fits_bootstrap_phi_table(
    fits_bs_phi_exps,
    fits_name_with_covmat_label,
    fits_experiments,
):
    """Produce a table with variance
    """
    col = ['variance', 'variance std. dev.']
    dfs = []
    for fit, experiments, phis in zip(
            fits_name_with_covmat_label,
            fits_experiments,
            fits_bs_phi_exps,
            ):
        records = []
        for phires, experiment in zip(phis, experiments):
            varres = phires**2
            records.append(dict(
                    experiment=str(experiment),
                    variance=varres.mean(),
                    variance_std=varres.std()
            ))
        df = pd.DataFrame.from_records(records,
                 columns=('experiment','variance', 'variance_std'),
                 index = ('experiment')
             )
        df.columns = pd.MultiIndex.from_product(([str(fit)], col))
        dfs.append(df)
    return pd.concat(dfs, axis=1, sort=True)

def bootstrap_bias_variance_ratio(
    experiment_results, exp_result_underlying, bootstrap_samples=30,
):
    """Calculate the ratio of bias over variance with a bootstrap resample"""
    seed_state = np.random.RandomState(None)
    seed = seed_state.randint(np.iinfo(np.int32).max, dtype=np.int32)

    dt_ct, th_ct = experiment_results
    _, th_ul = exp_result_underlying[0]

    diff = np.array(th_ct._rawdata - dt_ct.central_value[:, np.newaxis])
    phi_resample = bootstrap_values(
        diff, bootstrap_samples, boot_seed=seed,
        apply_func=(lambda x, y: calc_phi(y, x)),
        args=[dt_ct.sqrtcovmat]
    )
    var_resample = phi_resample**2
    dt_ct, th_ct = experiment_results

    th_ct_boot_cv = bootstrap_values(th_ct._rawdata, bootstrap_samples, boot_seed=seed)
    boot_diffs = th_ct_boot_cv - th_ul.central_value[:, np.newaxis]
    boot_bias = calc_chi2(dt_ct.sqrtcovmat, boot_diffs)/len(dt_ct)
    return boot_bias/var_resample

fits_bs_ratio = collect('bootstrap_bias_variance_ratio', ('fits', 'fitpdf'))
exps_fits_bs_ratio = collect('fits_bs_ratio', ('fits', 'fitcontext', 'experiments'))

@table
def boot_fits_ratio_exp(
    fits_bs_ratio,
    experiment,
):
    """bootstrap over level 1 and replicas"""
    ratios_np = np.array(fits_bs_ratio)
    ratio_bs = ratios_np[:, np.random.randint(ratios_np.shape[1], size=50)].mean(axis=0)
    res = np.array([ratio_bs.mean(), ratio_bs.std()])[np.newaxis, :]
    del ratio_bs, ratios_np
    df = pd.DataFrame(
        res,
        columns=["ratio", "ratio error"],
        index=[str(experiment)]
    )
    return df

def bias_variance(
    experiment_results, exp_result_underlying):
    """Calculate the ratio of bias over variance"""

    dt_ct, th_ct = experiment_results
    _, th_ul = exp_result_underlying[0]

    diff = np.array(th_ct._rawdata - dt_ct.central_value[:, np.newaxis])

    phi = calc_phi(dt_ct.sqrtcovmat, diff)
    var = phi**2

    bias_diff = th_ct.central_value - th_ul.central_value
    bias = calc_chi2(dt_ct.sqrtcovmat, bias_diff)/len(dt_ct)
    return bias, var

fits_b_v = collect('bias_variance', ('fits', 'fitpdf'))

@table
def fits_ratio_exp(
    fits_b_v,
    experiment,
):
    """no bootstrap - check result"""
    ratios_np = np.array(fits_b_v)
    means = ratios_np.mean(axis=0)
    df = pd.DataFrame(
        means[0]/means[1],
        columns=["ratio"],
        index=[str(experiment)]
    )
    return df

@table
def boot_fits_ratio_table(
    exps_fits_bs_ratio,
    fits_experiments,
):
    """bootstrap over level 1 and replicas"""
    records = []
    cols = ['ratio', 'ratio std. dev']
    for exp, fits_ratios in zip(fits_experiments[0], exps_fits_bs_ratio):
        ratios_np = np.array(fits_ratios)
        ratio_bs = ratios_np[:, np.random.randint(ratios_np.shape[1], size=50)].mean(axis=0)
        records.append(dict(
                    experiment=str(exp),
                    ratio=ratio_bs.mean(),
                    ratio_std=ratio_bs.std()
            ))
    df = pd.DataFrame.from_records(records,
        columns=('experiment','ratio', 'ratio_std'),
        index = ('experiment')
    )
    df.columns = cols
    print(df)
    return df


fits_exps_bootstrap_chi2_central = collect('experiments_bootstrap_chi2_central',
                                           ('fits', 'fitcontext',))
fits_chi2_t0_pseudodata = collect(
    total_experiments_chi2data, ('fits', 'fitinputcontext', 'fitunderlyinglaw'))

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
    ax.set_title(r'Total $\Delta_{\chi^{2}}$ for each fit')
    return fig

fits_exps_noise = collect(
    'experiments_chi2', ('fits', 'fitinputcontext', 'fitunderlyinglaw')
)
fits_exps_chi2 = collect(
    'experiments_chi2', ('fits', 'fitcontext',)
)
#Want this to account for TEST set
fit_specified_experiments = collect(
    'experiments', ('fits', 'fitcontext',)
)

@table
@check_use_fitcommondata
def delta_chi2_table(
    fits_exps_chi2,
    fits_exps_noise,
    fits_name_with_covmat_label,
    fit_specified_experiments):
    """Calculated delta chi2 per experiment and put in table
    Here delta chi2 is just normalised by ndata and is equal to

    delta_chi2 = (chi2(T[<f>], D_1) - chi2(T[f_in], D_1))/ndata
    """
    dfs = []
    cols = ('ndata', r'$\Delta_{chi^2}$ (normalised by ndata)')
    for label, experiments, exps_chi2, exps_noise in zip(
            fits_name_with_covmat_label,
            fit_specified_experiments,
            fits_exps_chi2,
            fits_exps_noise):
        records = []
        for experiment, exp_chi2, exp_noise in zip(experiments, exps_chi2, exps_noise):
            delta_chi2 = (exp_chi2.central_result - exp_noise.central_result)/exp_chi2.ndata
            npoints = exp_chi2.ndata
            records.append(dict(
                experiment=str(experiment),
                npoints=npoints,
                delta_chi2 = delta_chi2

            ))
        df = pd.DataFrame.from_records(records,
                 columns=('experiment', 'npoints', 'delta_chi2'),
                 index = ('experiment', )
             )
        df.columns = pd.MultiIndex.from_product(([label], cols))
        dfs.append(df)
    res =  pd.concat(dfs, axis=1)
    return res

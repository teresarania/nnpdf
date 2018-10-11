# -*- coding: utf-8 -*-
"""
Functions and Plots relating to Closure Test 
Statistical Estimators.
"""

import logging

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm, colors as mcolors, ticker as mticker

from reportengine.figure import figure
from reportengine.checks import make_argcheck
from reportengine import collect

from validphys.results import experiment_results, total_experiments_chi2data
from validphys import plotutils
from validphys.calcutils import calc_chi2

log = logging.getLogger(__name__)

exp_result_closure = collect(experiment_results, ('closures',))
exp_result_t0 = collect(experiment_results, ('closures', 'fitunderlyinglaw',))

def bias_experiment(exp_result_closure,
                    exp_result_t0):
    """Calculates the bias for all closure fit specified in runcard for
    one experiment. The bias is the chi2 between the level zero closure
    replica and the level zero of the PDF used to generate the data.
    The underlying law is taken to be the same as the PDF used to generate
    the t0 covariance matrix
    """
    bias_out = np.zeros(len(exp_result_closure))
    for i, (ct, ul) in enumerate(zip(exp_result_closure,
                                       exp_result_t0)):
        ((dt_ct, th_ct), (_, th_ul)) = ct, ul
        central_diff = th_ct.central_value - th_ul.central_value
        bias_out[i] = calc_chi2(dt_ct.sqrtcovmat, central_diff)/len(dt_ct)
    return bias_out

closures_speclabel = collect('speclabel', ('closures',), element_default=None)
bias_experiments = collect(bias_experiment, ('experiments',))

@figure
def plot_biases(experiments, bias_experiments, closures_speclabel):
    """Plot the biases of all experiments with bars."""
    biases = np.array(bias_experiments).T
    labels = closures_speclabel
    xticks = [experiment.name for experiment in experiments]
    fig, ax = plotutils.barplot(biases, collabels=xticks, datalabels=labels)
    ax.set_title("biases for experiments")
    ax.legend()
    return fig

fits_exps_bootstrap_chi2_central = collect('experiments_bootstrap_chi2_central',
                                           ('fits', 'fitpdf',))
fits_chi2_t0_pseudodata = collect(total_experiments_chi2data, ('fits', 'fitunderlyinglaw'))

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
    labels= [fit.name for fit in fits]
    fig, ax = plt.subplots()
    for i, label in enumerate(labels):
        ax.hist(delta_chi2[:, i], alpha=0.3, label=label, zorder=100)
    plt.xlabel(r'$\Delta_{\chi^{2}}$')
    l = ax.legend()
    l.set_zorder(1000)
    return fig

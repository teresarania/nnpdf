    # -*- coding: utf-8 -*-
"""
Utilities for reweighting studies

Implements utilities for calculating the NNPDF weights and unweighted PDF sets.
It also allows for some basic statistics.

Created on Mon May 30 12:50:16 2016

@author: Zahari Kassabov
"""
import logging


import numpy as np
import pandas as pd

from reportengine.table import table
from reportengine.checks import make_check
from reportengine.formattingtools import spec_to_nice_name


from validphys.results import abs_chi2_data, results
from validphys.checks import check_pdf_is_montecarlo, check_not_empty, CheckError
from validphys.lhio import new_pdf_from_indexes

log = logging.getLogger(__name__)

#TODO: implement this using reportengine expand when available
#use_t0 is to request that parameter to be set explicitly
@check_pdf_is_montecarlo
def chi2_data_for_reweighting_experiments(reweighting_experiments, pdf, use_t0, t0set=None):
    return [abs_chi2_data(results(exp,pdf,t0set)) for exp in reweighting_experiments]

@table
#will call list[0]
@check_not_empty('reweighting_experiments')
def nnpdf_weights(chi2_data_for_reweighting_experiments):
    total_ndata = 0
    chi2s = np.zeros_like(chi2_data_for_reweighting_experiments[0][0].data)
    for data in chi2_data_for_reweighting_experiments:
        res, central, ndata = data
        total_ndata += ndata
        chi2s += res.data

    chi2s = np.ravel(chi2s)

    logw = ((total_ndata - 1)/2)*np.log(chi2s) - 0.5*chi2s
    logw -= np.max(logw)
    w = np.exp(logw)
    w /= sum(w)
    return pd.DataFrame(w, index=np.arange(1, len(w) + 1))

def reweighting_stats():...

@table
def unweighted_index(nnpdf_weights, nreplicas:int=100):
    nnpdf_weights = np.ravel(nnpdf_weights)
    res = 1 + np.random.choice(len(nnpdf_weights), size=nreplicas, p=nnpdf_weights)
    return pd.DataFrame(res, index=np.arange(1,nreplicas+1))



@make_check
def prepare_pdf_name(*, callspec, ns, environment, **kwargs):
    #TODO: Does this make any sense?
    if ns['output_path'] is not None:
        raise CheckError("Output folder is not meant to be overwritten")
    output_path = environment.output_path / 'pdfsets'
    output_path.mkdir(exist_ok=True)
    ns['output_path'] = output_path

    set_name = ns['set_name']
    rootns = ns.maps[-1]
    if set_name is None:

        nreplicas = ns['nreplicas']
        set_name = spec_to_nice_name(rootns, callspec, str(nreplicas))
        ns['set_name'] = set_name

    if '_future_pdfs' not in rootns:
        rootns['_future_pdfs'] = {}

    future_pdfs = rootns['_future_pdfs']

    if set_name in future_pdfs:
        raise CheckError("PDF set with name %s would already be "
                         "generated by another action and would be overwritten"
                         % set_name)
    future_pdfs[set_name] = callspec



@prepare_pdf_name
def make_unweighted_pdf(pdf, unweighted_index,
                        set_name:(str, type(None))=None, output_path=None):
    new_pdf_from_indexes(pdf=pdf, indexes=np.ravel(unweighted_index),
                         set_name=set_name, folder=output_path)


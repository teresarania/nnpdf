"""
conftest.py

Pytest fixtures.
"""
import pathlib
import sys

import pytest
from hypothesis import settings

# Adding this here to change the time of deadline from default (200ms) to 1500ms
settings.register_profile("extratime", deadline=1500)
settings.load_profile("extratime")

#Fortunately py.test works much like reportengine and providers are
#connected by argument names.
@pytest.fixture
def tmp(tmpdir):
    """A tempdir that is manipulated like pathlib Paths"""
    return pathlib.Path(tmpdir)

# Here define the default config items like the PDF, theory and experiment specs

EXPERIMENTS = [
    {
        'experiment': 'NMC',
        'datasets': [{'dataset': 'NMC'}]},
    {
        'experiment': 'ATLASTTBARTOT',
        'datasets': [{'dataset': 'ATLASTTBARTOT', 'cfac':['QCD']}]},
    {
        'experiment': 'CMSZDIFF12',
        'datasets': [{'dataset': 'CMSZDIFF12', 'cfac':('QCD', 'NRM'), 'sys':10}]}
    ]

SINGLE_EXP = [
    {
        'experiment': 'pseudo experiment',
        'datasets': [
            {'dataset': 'NMC'},
            {'dataset': 'ATLASTTBARTOT', 'cfac':['QCD']},
            {'dataset': 'CMSZDIFF12', 'cfac':('QCD', 'NRM'), 'sys':10}]}]

WEIGHTED_DATA = [
    {
        'experiment': 'NMC Experiment',
        'datasets': [{'dataset': 'NMC'}]},
    {
        'experiment': 'Weighted',
        'datasets': [{'dataset': 'NMC', 'weight': 100}]},
    ]

PDF = "NNPDF31_nnlo_as_0118"
THEORYID = 162

base_config = dict(
        pdf=PDF,
        use_cuts='nocuts',
        experiments=EXPERIMENTS,
        theoryid=THEORYID,
        use_fitthcovmat=False
    )

@pytest.fixture(scope='module')
def data_config():
    return base_config

@pytest.fixture(scope='module')
def data_witht0_config():
    config_dict = dict(
        **base_config,
        use_t0=True,
        t0pdfset=PDF)
    return config_dict

@pytest.fixture(scope='module')
def data_singleexp_witht0_config(data_witht0_config):
    config_dict = dict(data_witht0_config)
    config_dict.update({'experiments': SINGLE_EXP})
    return config_dict

@pytest.fixture(scope='module')
def weighted_data_witht0_config(data_witht0_config):
    config_dict = dict(data_witht0_config)
    config_dict.update({'experiments': WEIGHTED_DATA})
    return config_dict

def pytest_runtest_setup(item):
    ALL = {"darwin", "linux"}
    supported_platforms = ALL.intersection(mark.name for mark in item.iter_markers())
    plat = sys.platform
    if supported_platforms and plat not in supported_platforms:
        pytest.skip("cannot run on platform {}".format(plat))

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "linux: mark test to run only on linux"
    )
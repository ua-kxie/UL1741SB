from pyUL1741SB.UL1741SB import UL1741SB
from EpriEnv import EpriEnv
from EpriEut import EpriEut
import pandas as pd
pd.options.plotting.backend = "plotly"

std = UL1741SB()
eut = EpriEut()
env = EpriEnv(eut)

def test_cpf():
    std.cpf_proc(env=env, eut=eut)
    results = env.cpf_results
    df = pd.concat(env.cpf_results.loc[:, 'data'].values)
    assert env.cpf_results.loc[:, 'ss_valid'].all()
    assert env.cpf_results.loc[:, 'olrt_valid'].all()

def test_crp():
    std.crp_proc(env=env, eut=eut)
    results = env.crp_results
    df = pd.concat(env.crp_results.loc[:, 'data'].values)
    assert env.crp_results.loc[:, 'ss_valid'].all()
    assert env.crp_results.loc[:, 'olrt_valid'].all()

def test_vv():
    std.vv_proc(env=env, eut=eut)
    results = env.vv_results
    df = pd.concat(env.vv_results.loc[:, 'data'].values)
    assert env.vv_results.loc[:, 'ss_valid'].all()
    assert env.vv_results.loc[:, 'olrt_valid'].all()

def test_vv_vref():
    std.vv_vref_proc(env=env, eut=eut)
    results = env.wv_results
    df = pd.concat(env.vv_vref_results.loc[:, 'data'].values)
    assert env.vv_vref_results.loc[:, 'valid'].all()

def test_wv():
    std.wv_proc(env=env, eut=eut)
    results = env.wv_results
    df = pd.concat(env.wv_results.loc[:, 'data'].values)
    assert env.wv_results.loc[:, 'ss_valid'].all()
    assert env.wv_results.loc[:, 'olrt_valid'].all()

def test_vw():
    # TODO should meet criteria with 1.5 * tMRA accounted for for olrt validation
    std.vw_proc(env=env, eut=eut)
    results = env.vw_results
    df = pd.concat(env.vw_results.loc[:, 'data'].values)
    assert env.vw_results.loc[:, 'ss_valid'].all()
    assert env.vw_results.loc[:, 'olrt_valid'].all()

# def test_fwo():
#     # TODO deltaPlarge, wait for ss between traversals
#     std.fwo_proc(env=env, eut=eut)
#     assert env.fwo_results.loc[:, 'ss_valid'].all()
#     assert env.fwo_results.loc[:, 'olrt_valid'].all()
#     # results = env.fwo_results
#     # df = pd.concat(env.fwo_results.loc[:, 'data'].values)

def test_uvt():
    std.uvt_proc(env=env, eut=eut)
    results = env.uvt_results
    assert env.uvt_results.loc[:, 'ceased'].all()
    assert env.uvt_results.loc[:, 'tripped'].all()

def test_ovt():
    std.ovt_proc(env=env, eut=eut)
    results = env.uvt_results
    assert env.ovt_results.loc[:, 'ceased'].all()
    assert env.ovt_results.loc[:, 'tripped'].all()

def test_uft():
    std.uft_proc(env=env, eut=eut)
    results = env.uft_results
    assert env.uft_results.loc[:, 'ceased'].all()
    assert env.uft_results.loc[:, 'tripped'].all()

def test_oft():
    std.oft_proc(env=env, eut=eut)
    results = env.uft_results
    assert env.oft_results.loc[:, 'ceased'].all()
    assert env.oft_results.loc[:, 'tripped'].all()


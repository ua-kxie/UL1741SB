import pytest
from pyUL1741SB import UL1741SB, Post
from DercEnv import DercEnv
from DercEut import DercEut
import plotly
from plotly.subplots import make_subplots
import datetime as dt
import os

class DercStd(UL1741SB):
    def __init__(self, env: DercEnv, eut: DercEut):
        super().__init__(env, eut)

        self.mra_scale = 1.5  # 1.5 in standard
        self.trip_rpt = 5  # 5 in standard

    def conn_to_grid(self):
        self.c_env.ac_config(Vac=self.c_eut.VN, freq=self.c_eut.fN, rocof=self.c_eut.rocof())
        self.c_env.sleep(dt.timedelta(seconds=10.0))

    def trip_rst(self):
        self.conn_to_grid()
        self.c_env.log(msg='waiting for re-energization...')
        while self.c_env.meas_single('P').iloc[0, 0] < self.c_eut.Prated * 0.5:
            self.c_env.sleep(dt.timedelta(seconds=1))
        return None

post = Post('tests/derc/results/')

@pytest.fixture
def std():
    eut = DercEut()
    env = DercEnv(eut)
    std = DercStd(env, eut)
    return std

class TestVoltreg:
    def test_cpf(self, std):
        std.cpf_proc()
        proc = 'cpf'
        post.post(proc, std.c_env.results[proc], proc)
        pfcols = ['ss_valid', 'olrt_valid']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

    def test_crp(self, std):
        std.crp_proc()
        proc = 'crp'
        post.post(proc, std.c_env.results[proc], proc)
        pfcols = ['ss_valid', 'olrt_valid']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

    def test_vv(self, std):
        std.vv_proc()
        proc = 'vv'
        post.post(proc, std.c_env.results[proc], proc)
        pfcols = ['ss_valid', 'olrt_valid']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

    def test_vv_vref(self, std):
        std.vv_vref_proc()
        proc = 'vv-vref'
        post.post(proc, std.c_env.results[proc], proc)
        pfcols = ['valid']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

    def test_wv(self, std):
        std.wv_proc()
        proc = 'wv'
        post.post(proc, std.c_env.results[proc], proc)
        pfcols = ['ss_valid', 'olrt_valid']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

    def stest_vw_fast(self, std):
        std.vw_proc(pwr_pus=(0.66,), crvs=(1,))
        proc = 'vw'
        post.post(proc, std.c_env.results[proc], 'vw-fast')
        pfcols = ['ss_valid', 'olrt_valid']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

    def test_vw_1pu(self, std):
        std.vw_proc(pwr_pus=(1,))
        proc = 'vw'
        post.post(proc, std.c_env.results[proc], 'vw-1pu')
        pfcols = ['ss_valid', 'olrt_valid']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

    def test_vw_p66pu(self, std):
        std.vw_proc(pwr_pus=(0.66,))
        proc = 'vw'
        post.post(proc, std.c_env.results[proc], 'vw-p66pu')
        pfcols = ['ss_valid', 'olrt_valid']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

    def test_vw_p20pu(self, std):
        std.vw_proc(pwr_pus=(0.2,))
        proc = 'vw'
        post.post(proc, std.c_env.results[proc], 'vw-p20pu')
        pfcols = ['ss_valid', 'olrt_valid']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

class TestFreqsupp:
    def test_fwo(self, std):
        std.fwo_proc()
        proc = 'fwo'
        post.post(proc, std.c_env.results[proc], proc)
        pfcols = ['ss_valid', 'olrt_valid']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

    def test_fwu(self, std):
        std.fwu_proc()
        proc = 'fwu'
        post.post(proc, std.c_env.results[proc], proc)
        pfcols = ['ss_valid', 'olrt_valid']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

class TestMisc:
    def test_pri(self, std):
        std.pri_proc()
        proc = 'pri'
        post.post(proc, std.c_env.results[proc], proc)
        pfcols = ['p_valid', 'q_valid']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

    def test_lap(self, std):
        std.lap_proc()
        proc = 'lap'
        post.post(proc, std.c_env.results[proc], proc)
        pfcols = ['ss_valid', 'olrt_valid']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

    def test_es_ramp(self, std):
        std.es_ramp_proc()
        proc = 'es-ramp'
        post.post(proc, std.c_env.results[proc], proc)
        pfcols = ['valid']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

class TestTrip:
    def test_uvt(self, std):
        std.uvt_proc()
        proc = 'uvt'
        post.post(proc, std.c_env.results[proc], proc)
        pfcols = ['ceased']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

    def test_ovt(self, std):
        std.ovt_proc()
        proc = 'ovt'
        post.post(proc, std.c_env.results[proc], proc)
        pfcols = ['ceased']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

    def test_uft(self, std):
        std.uft_proc()
        proc = 'uft'
        post.post(proc, std.c_env.results[proc], proc)
        pfcols = ['ceased']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

    def test_oft(self, std):
        std.oft_proc()
        proc = 'oft'
        post.post(proc, std.c_env.results[proc], proc)
        pfcols = ['ceased']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

class TestRidethrough:
    def test_lvrt(self, std):
        std.lvrt_proc()
        proc = 'lvrt'
        post.post(proc, std.c_env.results[proc], proc)
        pfcols = ['valid']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

    def test_hvrt(self, std):
        std.hvrt_proc()
        proc = 'hvrt'
        post.post(proc, std.c_env.results[proc], proc)
        pfcols = ['valid']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

    def test_lfrt(self, std):
        std.lfrt_proc()
        proc = 'lfrt'
        post.post(proc, std.c_env.results[proc], proc)
        pfcols = ['valid']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()

    def test_hfrt(self, std):
        std.hfrt_proc()
        proc = 'hfrt'
        post.post(proc, std.c_env.results[proc], proc)
        pfcols = ['valid']
        for pfcol in pfcols:
            assert std.c_env.results[proc].loc[:, pfcol].all()


def rtest_pri_corruption(std):
    std.vv_vref_proc()
    std.vw_proc()
    std.pri_proc()
    proc = 'pri'
    post.post(proc, std.c_env.results[proc], proc)
    pfcols = ['p_valid', 'q_valid']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def rtest_uvt_nrst(std):
    std.lap_proc()
    ts = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d %H:%M:%S")
    print('\n')
    print(ts)
    std.uvt_proc()
    proc = 'uvt'
    post.post(proc, std.c_env.results[proc], proc)
    pfcols = ['ceased']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()
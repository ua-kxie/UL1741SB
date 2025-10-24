import pytest
from pyUL1741SB import UL1741SB, Plotting
from EpriEnv import EpriEnv
from EpriEut import EpriEut
import plotly
from plotly.subplots import make_subplots
import datetime as dt

class EpriStd(UL1741SB):
    def __init__(self, env: EpriEnv, eut: EpriEut):
        super().__init__(env, eut)

        self.mra_scale = 1.5  # 1.5 in standard
        self.trip_rpt = 5  # 5 in standard

    def conn_to_grid(self):
        # vdc to nom
        # vgrid to std
        pass

    def trip_rst(self):
        # return to continuous op after tripping
        # set VDC, (Vg) to 0
        self.c_env.ac_config(Vac=self.c_eut.VN, freq=self.c_eut.fN, rocof=self.c_eut.rocof())
        self.c_eut.dc_config(Vdc=0)
        # wait 1 second
        self.c_env.sleep(dt.timedelta(seconds=1))
        # set VDC to nominal
        self.c_eut.dc_config(Vdc=self.c_eut.Vin_nom)
        self.c_env.log(msg='waiting for re-energization...')
        while self.c_env.meas_single('P').iloc[0, 0] < self.c_eut.Prated * 0.5:
            self.c_env.sleep(dt.timedelta(seconds=1))
        return None

pltng = Plotting('tests/epri/results/')

@pytest.fixture
def std():
    eut = EpriEut()
    env = EpriEnv(eut)
    std = EpriStd(env, eut)
    return std

def test_cpf(std):
    std.cpf_proc()
    proc = 'cpf'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['ss_valid', 'olrt_valid']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_crp(std):
    std.crp_proc()
    proc = 'crp'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['ss_valid', 'olrt_valid']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_vv(std):
    std.vv_proc()
    proc = 'vv'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['ss_valid', 'olrt_valid']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_vv_vref(std):
    std.vv_vref_proc()
    proc = 'vv-vref'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['valid']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_wv(std):
    std.wv_proc()
    proc = 'wv'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['ss_valid', 'olrt_valid']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_vw(std):
    std.vw_proc()
    proc = 'vw'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['ss_valid', 'olrt_valid']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_fwo(std):
    std.fwo_proc()
    proc = 'fwo'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['ss_valid', 'olrt_valid']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_fwu(std):
    std.fwu_proc()
    proc = 'fwu'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['ss_valid', 'olrt_valid']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_pri(std):
    std.pri_proc()
    proc = 'pri'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['p_valid', 'q_valid']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_lap(std):
    std.lap_proc()
    proc = 'lap'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['ss_valid', 'olrt_valid']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_es_ramp(std):
    std.es_ramp_proc()
    proc = 'es-ramp'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['valid']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_uvt(std):
    std.uvt_proc()
    proc = 'uvt'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['ceased']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_ovt(std):
    std.ovt_proc()
    proc = 'ovt'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['ceased']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_uft(std):
    std.uft_proc()
    proc = 'uft'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['ceased']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_oft(std):
    std.oft_proc()
    proc = 'oft'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['ceased']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_lvrt(std):
    std.lvrt_proc()
    proc = 'lvrt'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['valid']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_hvrt(std):
    std.hvrt_proc()
    proc = 'hvrt'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['valid']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_lfrt(std):
    std.lfrt_proc()
    proc = 'lfrt'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['valid']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

def test_hfrt(std):
    std.hfrt_proc()
    proc = 'hfrt'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['valid']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()


def rtest_pri_corruption(std):
    std.vv_vref_proc()
    std.vw_proc()
    std.pri_proc()
    proc = 'pri'

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

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

    pltng.plot(proc, std.c_env.results[proc])
    results = std.c_env.results[proc].iloc[:, :-1]
    results.to_csv(f'tests/epri/results/{proc}.csv')

    pfcols = ['ceased']
    for pfcol in pfcols:
        assert std.c_env.results[proc].loc[:, pfcol].all()

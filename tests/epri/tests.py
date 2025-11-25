import pytest
from pyUL1741SB import UL1741SB, Post
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
        self.c_env.ac_config(
            Vac=self.c_eut.VN, freq=self.c_eut.fN, rocof=self.c_eut.rocof())
        self.c_eut.dc_config(Vdc=0)
        # wait 1 second
        self.c_env.sleep(dt.timedelta(seconds=1))
        # set VDC to nominal
        self.c_eut.dc_config(Vdc=self.c_eut.Vin_nom)
        self.c_env.log(msg='waiting for re-energization...')
        while self.c_env.meas_single('P').iloc[0, 0] < self.c_eut.Prated * 0.5:
            self.c_env.sleep(dt.timedelta(seconds=1))
        return None


outdir = 'tests/epri/results/'
post = Post(outdir)


@pytest.fixture
def std():
    eut = EpriEut()
    env = EpriEnv(eut)
    std = EpriStd(env, eut)
    return std


class TestVoltreg:
    def test_cpf(self, std):
        std.cpf(outdir, lambda: None)

    def test_crp(self, std):
        std.crp(outdir, lambda: None)

    def test_vv(self, std):
        std.vv(outdir, lambda: None)

    def test_vv_vref(self, std):
        std.vv_vref(outdir, lambda: None)

    def test_wv(self, std):
        std.wv(outdir, lambda: None)

    def test_vw_1pu(self, std):
        std.vw(outdir, lambda: None, pwr_pus=(1.0,))

    def test_vw_p66pu(self, std):
        std.vw(outdir, lambda: None, pwr_pus=(0.66,))

    def test_vw_p20pu(self, std):
        std.vw(outdir, lambda: None, pwr_pus=(0.2,))


class TestFreqsupp:
    def test_fwo(self, std):
        std.fwo(outdir, lambda: None)

    def test_fwu(self, std):
        std.fwu(outdir, lambda: None)


class TestMisc:
    def test_pri(self, std):
        std.pri(outdir, lambda: None)

    def test_lap(self, std):
        std.lap(outdir, lambda: None)

    def test_es_ramp(self, std):
        std.es_ramp(outdir, lambda: None)


class TestTrip:
    def test_uvt(self, std):
        std.uvt(outdir, lambda: None)

    def test_ovt(self, std):
        std.ovt(outdir, lambda: None)

    def test_uft(self, std):
        std.uft(outdir, lambda: None)

    def test_oft(self, std):
        std.oft(outdir, lambda: None)


class TestRidethrough:
    def test_lvrt(self, std):
        std.lvrt(outdir, lambda: None)

    def test_hvrt(self, std):
        std.hvrt(outdir, lambda: None)

    def test_lfrt(self, std):
        std.lfrt(outdir, lambda: None)

    def test_hfrt(self, std):
        std.hfrt(outdir, lambda: None)

import pytest
from pyUL1741SB import UL1741SB
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
        self.c_env.ac_config(
            Vac=self.c_eut.VN, freq=self.c_eut.fN, rocof=self.c_eut.rocof())
        self.c_env.sleep(dt.timedelta(seconds=10.0))

    def trip_rst(self):
        self.conn_to_grid()
        self.c_env.log(msg='waiting for re-energization...')
        while self.c_env.meas_single('P').iloc[0, 0] < self.c_eut.Prated * 0.5:
            self.c_env.sleep(dt.timedelta(seconds=1))
        return None

eut = DercEut()
@pytest.fixture
def std():
    env = DercEnv(eut)
    std = DercStd(env, eut)
    return std

outdir = 'tests/derc/results/'
def final():
    pass

class TestVoltreg:
    def test_cpf(self, std):
        std.cpf(outdir, final)

    def test_crp(self, std):
        std.crp(outdir, final)

    def test_vv_char1(self, std):
        std.vv_char1(outdir, final)

    def test_vv_char23(self, std):
        std.vv_char23(outdir, final)

    def test_vv_vref(self, std):
        std.vv_vref(outdir, final)

    def test_wv(self, std):
        std.wv(outdir, final)

    def test_vw_1pu(self, std):
        std.vw_1pu(outdir, final)

    def test_vw_p66pu(self, std):
        std.vw_pu66(outdir, final)

    def test_vw_p20pu(self, std):
        std.vw_pu20(outdir, final)


class TestFreqsupp:
    def test_fwo(self, std):
        std.fwo(outdir, final)

    def test_fwu(self, std):
        std.fwu(outdir, final)


class TestMisc:
    def test_pri(self, std):
        std.pri(outdir, final)

    def test_lap(self, std):
        std.lap(outdir, final)

    def test_es_ramp(self, std):
        std.es_ramp(outdir, final)


class TestTrip:
    def test_uvt(self, std):
        std.uvt(outdir, final)

    def test_ovt(self, std):
        std.ovt(outdir, final)

    def test_uft(self, std):
        std.uft(outdir, final)

    def test_oft(self, std):
        std.oft(outdir, final)


class TestRidethrough:
    def test_lvrt(self, std):
        std.lvrt(outdir, final)

    def test_hvrt(self, std):
        std.hvrt(outdir, final)

    def test_lfrt(self, std):
        std.lfrt(outdir, final)

    def test_hfrt(self, std):
        std.hfrt(outdir, final)

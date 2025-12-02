import os
import datetime as dt
import sys
_ = os.path.dirname
sys.path.append(_(_(_(__file__))))
from pyUL1741SB import UL1741SB
from DercEnv import DercEnv
from DercEut import DercEut

pid = os.getpid()
print(f"Process PID: {pid}") 

class DercStd(UL1741SB):
    def __init__(self, env: DercEnv, eut: DercEut):
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
# import time
# time.sleep(5.0)
eut = DercEut()
env = DercEnv(eut)
std = DercStd(env, eut)

std.cpf('', lambda: None)

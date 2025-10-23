"""
IEEE 1547.1-2020 5.13
"""
from typing import Callable
from datetime import timedelta
import pandas as pd
from pyUL1741SB import Eut, Env

class IEEE1547:
    def __init__(self, env: Env, eut: Eut):
        self.c_env = env
        self.c_eut = eut

        self.mra_scale = 1.5  # 1.5 in standard
        self.trip_rpt = 2  # 5 in standard

    def range_4p2(self, y_of_x, x, xMRA, yMRA):
        """"""
        '''
        IEEE 1547.1-2020 4.2
        '''
        s1p5 = self.mra_scale
        y_min = min(y_of_x(x - s1p5 * xMRA), y_of_x(x + s1p5 * xMRA)) - s1p5 * yMRA
        y_max = max(y_of_x(x - s1p5 * xMRA), y_of_x(x + s1p5 * xMRA)) + s1p5 * yMRA
        return y_min, y_max

    def meas_perturb(self, perturb: Callable, olrt: timedelta, interval: timedelta, meas_args: tuple):
        # tMRA is 1% of measured duration
        # the smallest measured duration is olrt (90% resp at olrt)
        t_step = self.c_eut.mra.static.T(olrt.total_seconds())
        init = self.c_env.meas_single(*meas_args)
        perturb()
        resp = self.c_env.meas_for(interval, timedelta(seconds=t_step), *meas_args)
        df = pd.concat([init, resp])
        return df

    def cease_energize(self):
        """"""
        df_meas = self.c_env.meas_single('P', 'Q')
        zipped = zip(df_meas.iloc[0, :].values, [self.c_eut.mra.static.P, self.c_eut.mra.static.Q])
        return all([v < thresh for v, thresh in zipped])

    def trip_validate(self, dur, ts, tMRA):
        """"""
        '''
        5.4.2.4 Criteria - freq trip similar
        The EUT shall be considered in compliance if it ceases to energize the ac test source and trips within
        respective clearing times for each overvoltage range specified in IEEE Std 1547. The evaluated ranges of
        adjustment for tripping magnitude and duration shall be greater than or equal to the allowable ranges of
        adjustment for each overvoltage tripping range specified in IEEE Std 1547.
        '''
        while not self.c_env.elapsed_since(dur, ts):
            self.c_env.sleep(timedelta(seconds=tMRA))
            if self.c_eut.has_tripped():
                return True
        return False

    def trip_rst(self):
        # TODO reset the inverter for next test
        # set VDC, (Vg) to 0
        self.c_env.ac_config(Vac=self.c_eut.VN, freq=self.c_eut.fN, rocof=self.c_eut.rocof())
        self.c_eut.dc_config(Vdc=0)
        # wait 1 second
        self.c_env.sleep(timedelta(seconds=1))
        # set VDC to nominal
        self.c_eut.dc_config(Vdc=self.c_eut.Vin_nom)
        self.c_env.log(msg='waiting for re-energization...')
        while self.c_env.meas_single('P').iloc[0, 0] < self.c_eut.Prated * 0.5:
            self.c_env.sleep(timedelta(seconds=1))

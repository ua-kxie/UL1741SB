"""
IEEE 1547.1-2020 5.13
"""
from typing import Callable
from datetime import timedelta
import pandas as pd
from pyUL1741SB import Eut, Env
import math

class IEEE1547:
    def __init__(self, env: Env, eut: Eut):
        self.c_env = env
        self.c_eut = eut

        self.mra_scale = 1.5  # 1.5 in standard
        self.trip_rpt = 2  # 5 in standard

    def ts_of_interest(self, index, olrt):
        t_init = index[0]
        t_olrt = index.asof(index[1] + olrt)
        t_ss0 = index.asof(index[1] + 2 * olrt)
        t_ss1 = index[-1]
        return t_init, t_olrt, t_ss0, t_ss1

    def expapp(self, olrt, t, y0, y1):
        return (y0-y1) * math.exp(math.log(0.1)*t/olrt) + y1

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

    def cease_energize(self, df_meas_single):
        """"""
        '''
        IEEE 1547.1-2018 
        4.5 Cease to energize performance requirement
        In the cease to energize state, the DER shall not deliver active power during steady-state or transient
        conditions. The requirements for cease to energize shall apply to the point of DER connection (PoC).
        For Local EPS with aggregate DER rating less than 500 kVA, the reactive power exchange in the cease to
        energize state shall be less than 10% of nameplate DER rating and shall exclusively result from passive
        devices. For Local EPS with aggregate DER rating 500 kVA and greater, the reactive power exchange in
        the cease to energize state shall be less than 3% of nameplate DER rating and shall exclusively result from
        passive devices.40
        If requested by the Area EPS operator, the DER operator shall provide the reactive susceptance that
        remains connected to the Area EPS in the cease to energize state.
        Import of active power and reactive power exchange in the cease to energize state is permitted only for
        continuation of supply to DER housekeeping and auxiliary loads.
        Alternatively, the requirements for cease to energize may be met by disconnecting41 the local EPS, or the
        portion of the local EPS to which the DER is connected from the Area EPS. The DER may continue to
        deliver power to the portion of the Local EPS that is disconnected from the Area EPS.42
        '''
        if self.c_eut.Srated < 500e3:
            Qlim = self.c_eut.Srated * 0.1
        else:
            Qlim = self.c_eut.Srated * 0.03
        lst_PQlims = [self.c_eut.mra.static.P * self.mra_scale, Qlim + self.c_eut.mra.static.Q * self.mra_scale]
        zipped = zip(df_meas_single.iloc[0, :].values, lst_PQlims)
        return all([v < thresh for v, thresh in zipped])

    def trip_step(self, dct_label, dur: timedelta, tstep_s, step0, step1, meas_args):
        # reset eut input
        dfs = []
        self.c_env.ac_config(Vac=self.c_eut.VN, freq=self.c_eut.fN, rocof=self.c_eut.rocof())
        dfs.append(self.c_env.meas_single(*meas_args))
        step0()
        dfs.append(self.c_env.meas_for(dur, timedelta(seconds=tstep_s), *meas_args))

        ts = self.c_env.time_now()
        step1()

        ceased = False
        while not self.c_env.elapsed_since(dur, ts):
            df_meas = self.c_env.meas_single(*meas_args)
            dfs.append(df_meas)
            if self.cease_energize(df_meas):
                ceased = True
                break
            self.c_env.sleep(timedelta(seconds=tstep_s))
        dfs.append(self.c_env.meas_single(*meas_args))
        self.c_env.validate({**dct_label, 'ceased': ceased, 'data': pd.concat(dfs)})

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
        return None

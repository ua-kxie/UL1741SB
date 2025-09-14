from typing import Callable
from datetime import timedelta
import pandas as pd
from pyUL1741SB import Eut, Env


class IEEE1547Common:
    def range_4p2(self, y_of_x, x_ss, xMRA, yMRA):
        """"""
        '''
        IEEE 1547.1-2020 4.2
        '''
        y_min = min(y_of_x(x_ss - 1.5 * xMRA), y_of_x(x_ss + 1.5 * xMRA)) - 1.5 * yMRA
        y_max = max(y_of_x(x_ss - 1.5 * xMRA), y_of_x(x_ss + 1.5 * xMRA)) + 1.5 * yMRA
        return y_min, y_max

    def meas_perturb(self, env: Env, eut:Eut, perturb: Callable, olrt: timedelta, interval: timedelta, meas_args: tuple):
        # tMRA is 1% of measured duration
        # the smallest measured duration is olrt (90% resp at olrt)
        t_step = eut.mra.static.T(olrt.total_seconds())
        init = env.meas_single(*meas_args)
        perturb()
        resp = env.meas_for(interval, timedelta(seconds=t_step), *meas_args)
        df = pd.concat([init, resp])
        return df

    def trip_rst(self, env: Env, eut: Eut):
        # TODO reset the inverter for next test
        # set VDC, (Vg) to 0
        env.ac_config(Vac=eut.VN)
        env.dc_config(Vdc=0)
        # wait 1 second
        env.sleep(timedelta(seconds=1))
        # set VDC to nominal
        env.dc_config(Vdc=eut.Vin_nom)
        env.log(msg='waiting for re-energization...')
        while env.meas_single('P').iloc[0, 0] < eut.Prated * 0.5:
            env.sleep(timedelta(seconds=1))
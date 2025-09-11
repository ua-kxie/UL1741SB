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

    def meas_for(self, env: Env, perturb: Callable, olrt: timedelta, interval: timedelta, meas_args: tuple):
        # tMRA is 1% of measured duration
        # the smallest measured duration is olrt (90% resp at olrt)
        # t_step = tMRA * olrt
        vals = []
        vals.append(env.meas('time', *meas_args))
        t_init = vals[0][0]
        perturb()
        vals.append(env.meas('time', *meas_args))
        i = 0
        t_step = olrt.total_seconds() * 0.01
        while not env.elapsed_since(interval, t_init):
            i += 1
            env.sleep(t_init + timedelta(seconds=i * t_step) - env.time_now())
            vals.append(env.meas('time', *meas_args))
        df = pd.DataFrame(data=vals, columns=['time'] + list(meas_args))
        df = df.set_index('time')
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
        while env.meas('P')[0] < eut.Prated * 0.5:
            env.sleep(timedelta(seconds=1))
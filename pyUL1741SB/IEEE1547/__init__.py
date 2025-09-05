from typing import Callable
from datetime import timedelta
import pandas as pd

from pyUL1741SB.IEEE1547.VoltReg import VoltReg
from pyUL1741SB.eut import Eut
from pyUL1741SB.env import Env
from pyUL1741SB.IEEE1547.VoltReg.vv import VVCurve

class IEEE1547(VoltReg):
    pass

    def ss_eval_4p2(self, env, label, y_of_x, x_ss, y_ss, xMRA, yMRA):
        y_min = min(y_of_x(x_ss - 1.5 * xMRA), y_of_x(x_ss + 1.5 * xMRA)) - 1.5 * yMRA
        y_max = max(y_of_x(x_ss - 1.5 * xMRA), y_of_x(x_ss + 1.5 * xMRA)) + 1.5 * yMRA
        # y_targ = y_of_x(x_ss)
        if y_min <= y_ss <= y_max:
            # steady state value is good
            passfail = 'passed'
        else:
            passfail = 'failed'
        env.log(msg=f"{label} steady state {passfail} (y_min [{y_min:.1f}VAR], y_ss [{y_ss:.1f}VAR], y_max [{y_max:.1f}VAR])")

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

from src import Eut, Env
from src.IEEE1547 import IEEE1547
from datetime import datetime, timedelta
from typing import Callable
import statistics as stats

class UL1741SB(IEEE1547):
    def cpf_validate_step(self, env: Env, label: str, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float], yMRA, xMRA):
        print("1741 cpf vali")
        # measure initial
        x_init, y_init = env.meas('P', 'Q')
        # note initial time -
        t_init_pre = datetime.now()
        # step
        perturb()
        # note initial time +
        t_init_post = datetime.now()
        # wait 1x olrt since t_init_pre
        env.sleep(t_init_pre + olrt - datetime.now())
        # measure y_olrt - this value has to be within 10% of y_ss
        x_olrt, y_olrt = env.meas('P', 'Q')
        # wait for steady state - at least 1x olrt since t_init_post
        env.sleep(t_init_post + olrt - datetime.now())

        # measure y_ss as the average over the next 3x olrt
        lst_xy_ss = []
        t_ss_init = datetime.now()
        x, y = env.meas('P', 'Q')
        lst_xy_ss.append((x, y))
        while datetime.now() - t_ss_init < olrt * 3:
            env.sleep(timedelta(seconds=1))
            x, y = env.meas('P', 'Q')
            lst_xy_ss.append((x, y))
        lst_xy_ss = list(zip(*lst_xy_ss))
        x_ss, y_ss = stats.mean(lst_xy_ss[0]), stats.mean(lst_xy_ss[1])

        # meas. complete
        y_olrt_thresh = y_ss + 0.1 * (y_init - y_ss)
        if min(y_init, y_olrt) <= y_olrt_thresh <= max(y_init, y_olrt):
            # response time is good
            passfail = 'passed'
        else:
            passfail = 'failed'
        env.log_result(msg=f"{label} response time {passfail} (y_init [{y_init:.1f}VAR], y_olrt [{y_olrt:.1f}VAR], y_90% [{y_olrt_thresh:.1f}VAR])")

        # ss eval with 1741SB amendment
        y_min = y_of_x(x_ss) - 1.5 * yMRA
        y_max = y_of_x(x_ss) + 1.5 * yMRA
        if y_min <= y_ss <= y_max:
            # steady state value is good
            passfail = 'passed'
        else:
            passfail = 'failed'
        env.log_result(msg=f"{label} steady state {passfail} (y_min [{y_min:.1f}VAR], y_ss [{y_ss:.1f}VAR], y_max [{y_max:.1f}VAR])")
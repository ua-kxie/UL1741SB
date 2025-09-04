from datetime import timedelta
from typing import Callable
import statistics as stats
import logging
import numpy as np

from pyUL1741SB.eut import Eut
from pyUL1741SB.env import Env
from pyUL1741SB.IEEE1547 import IEEE1547
from pyUL1741SB.IEEE1547.VoltReg.vv import VVCurve

class UL1741SB(IEEE1547):
    def olrt_resp_range(self, env, label, y_init, y_olrt, y_ss, yMRA):
        y_olrt_targ = y_ss + 0.1 * (y_init - y_ss)
        y_olrt_min = y_olrt_targ - 1.5 * yMRA
        y_olrt_max = y_olrt_targ + 1.5 * yMRA
        if y_olrt_min <= y_olrt <= y_olrt_max:
            # response time is good
            passfail = 'passed'
        else:
            passfail = 'failed'
        env.log(msg=f"{label} response time {passfail} (y_olrt_min [{y_olrt_min:.1f}VAR], y_olrt [{y_olrt:.1f}VAR], y_olrt_max [{y_olrt_max:.1f}VAR])")

    def vv_proc(self, env: Env, eut: Eut):
        """
        """
        VH, VN, VL, Pmin, Prated = eut.VH, eut.VN, eut.VL, eut.Pmin, eut.Prated
        av = 1.5 * eut.mra.static.V
        if eut.Cat == Eut.Category.A:
            vv_crvs = [VVCurve.Crv_1A(eut.Prated, eut.VN)]  # just char1 curve, UL1741 amendment
        elif eut.Cat == Eut.Category.B:
            vv_crvs = [VVCurve.Crv_1B(eut.Prated, eut.VN)]
        else:
            raise TypeError(f'unknown category {eut.Cat}')
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all voltage trip parameters to the widest range of adjustability. Disable all reactive/active power
        control functions.
        c) Set all ac test source parameters to the nominal operating voltage and frequency.
        d) Adjust the EUT’s available active power to Prated. For an EUT with an electrical input, set the input
        voltage to Vin_nom. The EUT may limit active power throughout the test to meet reactive power
        requirements.
        '''
        '''
        ee) Repeat test steps e) through dd) with VRef set to 1.05 × VN and 0.95 × VN, respectively.
        '''
        for vref in [VN]:  # 1741SB amendment
            '''
            ff) Repeat test steps d) through ee) at EUT power set at 20% and 66% of rated power.
            '''
            for pwr in [Prated]:  # 1741SB amendment
                '''
                gg) Repeat steps e) through ee) for characteristics 2 and 3.
                '''
                for vv_crv in vv_crvs:
                    '''
                    e) Set EUT volt-var parameters to the values specified by Characteristic 1. All other function should
                    be turned off. Turn off the autonomously adjusting reference voltage.
                    f) Verify volt-var mode is reported as active and that the correct characteristic is reported.
                    '''
                    dct_vvsteps = self.vv_traverse_steps(env, vv_crv, VL, VH, av)
                    for stepname, perturbation in dct_vvsteps.items():
                        self.vv_validate_step(
                            env,
                            label=f'vv vref: {vref:.0f} pwr: {pwr:.0f} crv{vv_crv.name} step {stepname}',
                            perturb=perturbation,
                            olrt=timedelta(seconds=vv_crv.Tr),
                            y_of_x=vv_crv.y_of_x,
                            yMRA=eut.mra.static.Q,
                            xMRA=eut.mra.static.V,
                        )

    def vv_validate_step(self, env: Env, label: str, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float], yMRA, xMRA):
        env.log(msg="vv validate step against 1741SB")
        meas_args = ('V', 'Q')
        # measure initial
        x_init, y_init = env.meas(*meas_args)
        # note initial time -
        t_init_pre = env.time_now()
        # step
        perturb()
        # note initial time +
        t_init_post = env.time_now()
        # wait 1x olrt since t_init_pre
        env.sleep(t_init_pre + olrt - env.time_now())
        # measure y_olrt - this value has to be 90% within 1.5 MRA
        x_olrt, y_olrt = env.meas(*meas_args)
        # wait for steady state - at least 1x olrt since t_init_post
        env.sleep(t_init_post + olrt - env.time_now())

        # measure y_ss as the average over the next 3x olrt
        lst_xy_ss = []
        t_ss_init = env.time_now()
        x, y = env.meas(*meas_args)
        lst_xy_ss.append((x, y))
        while not env.elapsed_since(olrt * 3, t_ss_init):
            env.sleep(timedelta(seconds=1))
            x, y = env.meas(*meas_args)
            lst_xy_ss.append((x, y))
        lst_xy_ss = list(zip(*lst_xy_ss))
        x_ss, y_ss = stats.mean(lst_xy_ss[0]), stats.mean(lst_xy_ss[1])

        # meas. complete
        self.olrt_resp_range(env, label, y_init, y_olrt, y_ss, yMRA)

        # ss eval with 1741SB amendment
        self.ss_eval_4p2(env, label, y_of_x, x_ss, y_ss, xMRA, yMRA)

    def cpf_validate_step(self, env: Env, label: str, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float], yMRA, xMRA):
        env.log(msg=f"1741SB {label}")
        meas_args = ('P', 'Q')
        # measure initial
        x_init, y_init = env.meas(*meas_args)
        # note initial time -
        t_init_pre = env.time_now()
        # step
        perturb()
        # note initial time +
        t_init_post = env.time_now()
        # wait 1x olrt since t_init_pre
        env.sleep(t_init_pre + olrt - env.time_now())
        # measure y_olrt - this value has to be within 10% of y_ss
        x_olrt, y_olrt = env.meas(*meas_args)
        # wait for steady state - at least 1x olrt since t_init_post
        env.sleep(t_init_post + olrt - env.time_now())

        # measure y_ss as the average over the next 3x olrt
        lst_xy_ss = []
        t_ss_init = env.time_now()
        x, y = env.meas(*meas_args)
        lst_xy_ss.append((x, y))
        while not env.elapsed_since(olrt * 3, t_ss_init):
            env.sleep(timedelta(seconds=1))
            x, y = env.meas(*meas_args)
            lst_xy_ss.append((x, y))
        lst_xy_ss = list(zip(*lst_xy_ss))
        x_ss, y_ss = stats.mean(lst_xy_ss[0]), stats.mean(lst_xy_ss[1])

        # meas. complete
        '''
        init olrt_thresh olrt ss - 90% response at 1 olrt
        '''
        y_olrt_thresh = y_ss + 0.1 * (y_init - y_ss)
        # # interpreted: olrt measurement should also get accuracy allowance
        # y_olrt_thresh = y_olrt_thresh + np.sign(y_init - y_olrt_thresh) * yMRA
        # if y_init < y_ss:
        #     passfail = 'passed' if y_olrt_thresh <= y_olrt else 'failed'
        # else:
        #     passfail = 'passed' if y_olrt_thresh >= y_olrt else 'failed'
        if min(y_init, y_olrt) <= y_olrt_thresh <= max(y_init, y_olrt):
            # response time is good
            passfail = 'passed'
        else:
            passfail = 'failed'
        env.log(msg=f"response time {passfail} (y_init [{y_init:.1f}VAR], y_90% [{y_olrt_thresh:.1f}VAR], y_olrt [{y_olrt:.1f}VAR])")

        # ss eval with 1741SB amendment
        y_min = y_of_x(x_ss) - 1.5 * yMRA
        y_max = y_of_x(x_ss) + 1.5 * yMRA
        if y_min <= y_ss <= y_max:
            # steady state value is good
            passfail = 'passed'
        else:
            passfail = 'failed'
        env.log(msg=f"steady state {passfail} (y_min [{y_min:.1f}VAR], y_ss [{y_ss:.1f}VAR], y_max [{y_max:.1f}VAR])")

    def crp_validate_step(self, env: Env, label: str, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float], yMRA, xMRA):
        env.log(msg="cpf validate step against 1741SB")
        meas_args = ('P', 'Q')
        # measure initial
        x_init, y_init = env.meas(*meas_args)
        # note initial time -
        t_init_pre = env.time_now()
        # step
        perturb()
        # note initial time +
        t_init_post = env.time_now()
        # wait 1x olrt since t_init_pre
        env.sleep(t_init_pre + olrt - env.time_now())
        # measure y_olrt - this value has to be within 10% of y_ss
        x_olrt, y_olrt = env.meas(*meas_args)
        # wait for steady state - at least 1x olrt since t_init_post
        env.sleep(t_init_post + olrt - env.time_now())

        # measure y_ss as the average over the next 3x olrt
        lst_xy_ss = []
        t_ss_init = env.time_now()
        x, y = env.meas(*meas_args)
        lst_xy_ss.append((x, y))
        while not env.elapsed_since(olrt * 3, t_ss_init):
            env.sleep(timedelta(seconds=1))
            x, y = env.meas(*meas_args)
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
        env.log(msg=f"{label} response time {passfail} (y_init [{y_init:.1f}VAR], y_olrt [{y_olrt:.1f}VAR], y_90% [{y_olrt_thresh:.1f}VAR])")

        # ss eval with 1741SB amendment
        y_min = y_of_x(x_ss) - 1.5 * yMRA
        y_max = y_of_x(x_ss) + 1.5 * yMRA
        if y_min <= y_ss <= y_max:
            # steady state value is good
            passfail = 'passed'
        else:
            passfail = 'failed'
        env.log(msg=f"{label} steady state {passfail} (y_min [{y_min:.1f}VAR], y_ss [{y_ss:.1f}VAR], y_max [{y_max:.1f}VAR])")

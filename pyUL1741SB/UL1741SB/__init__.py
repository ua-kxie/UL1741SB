from datetime import timedelta
from typing import Callable
import statistics as stats
import logging
import numpy as np

from pyUL1741SB import Eut, Env

from pyUL1741SB.IEEE1547 import IEEE1547
from pyUL1741SB.IEEE1547.base import IEEE1547Common
from pyUL1741SB.IEEE1547.VoltReg.vv import VVCurve

class UL1741SB(IEEE1547, IEEE1547Common):
    def vv_proc(self, env: Env, eut: Eut, pre_cbk=None, post_cbk=None):
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
                        dct_label = {'vref': f'{vref:.0f}', 'pwr': f'{pwr:.0f}', 'crv': f'{vv_crv.name}', 'step': f'{stepname}'}
                        slabel = ''.join([f'{k}: {v}; ' for k, v in dct_label.items()])
                        if pre_cbk is not None:
                            pre_cbk(**dct_label)
                        self.vv_validate_step(
                            env,
                            eut,
                            label=slabel,
                            perturb=perturbation,
                            olrt=timedelta(seconds=vv_crv.Tr),
                            y_of_x=vv_crv.y_of_x,
                        )
                        if post_cbk is not None:
                            post_cbk(**dct_label)

    def vv_validate_step(self, env: Env, eut: Eut, label: str, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
        """"""
        '''
        IEEE 1547.1-2020 5.14.3.3
        '''
        xMRA = eut.mra.static.V
        yMRA = eut.mra.static.Q
        env.log(msg=f"1741SB {label}")
        xarg, yarg = 'V', 'Q'
        meas_args = (xarg, yarg)
        df_meas = self.meas_perturb(env, eut, perturb, olrt, 4 * olrt, meas_args)

        # get y_init
        y_init = df_meas.loc[df_meas.index[0], yarg]
        y_olrt = df_meas.loc[df_meas.index.asof(df_meas.index[1] + olrt), yarg]
        # determine y_ss by average after olrt
        x_ss = df_meas.loc[df_meas.index[1] + olrt:, xarg].mean()
        y_ss = df_meas.loc[df_meas.index[1] + olrt:, yarg].mean()
        '''
        [...] the EUT shall reach 90% × (Qfinal – Qinitial) + Qinitial within 1.5*MRA at olrt within 1.5*MRA 
        '''
        y_thresh = y_init + 0.9 * (y_ss - y_init)
        y_min, y_max = y_thresh - 1.5 * yMRA, y_thresh + 1.5 * yMRA
        valid = y_min <= y_olrt <= y_max
        env.validate(
            is_valid=valid,
            msg=f"response time {'passed' if valid else 'failed'} (y_min [{y_min:.1f}VAR], y_olrt [{y_olrt:.1f}VAR], y_max [{y_max:.1f}VAR])"
        )

        '''
        shall meet 4.2
        '''
        # ss eval with 1741SB amendment
        y_min, y_max = self.range_4p2(y_of_x, x_ss, xMRA, yMRA)
        valid = y_min <= y_ss <= y_max
        env.validate(
            is_valid=valid,
            msg=f"steady state {'passed' if valid else 'failed'} (y_min [{y_min:.1f}VAR], y_ss [{y_ss:.1f}VAR], y_max [{y_max:.1f}VAR])"
        )

    def cpf_crp_validate_common(self, env: Env, eut: Eut, label: str, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
        """"""
        '''
        IEEE 1547.1-2020 5.14.3.3
        '''
        env.log(msg=f"1741SB {label}")
        yMRA = eut.mra.static.Q
        xarg, yarg = 'P', 'Q'
        meas_args = (xarg, yarg)
        df_meas = self.meas_perturb(env, eut, perturb, olrt, 4 * olrt, meas_args)

        # get y_init
        y_init = df_meas.loc[df_meas.index[0], yarg]
        # determine y_ss by average after olrt
        x_ss = df_meas.loc[df_meas.index[0] + olrt:, xarg].mean()
        y_ss = df_meas.loc[df_meas.index[0] + olrt:, yarg].mean()
        '''
        [...] the EUT shall reach 90% × (Qfinal – Qinitial) + Qinitial within 10 s after a voltage or power step.
         - olrt validate as: any y meas within 10% of y_ss before olrt, then pass
         
         Q shall reach Qini + 0.9 * (Qfin - Qini) in a time of 10s or less
        '''
        y_thresh = y_init + (y_ss - y_init) * 0.9
        y_olrt = df_meas.loc[df_meas.index.asof(df_meas.index[1] + olrt), yarg]
        valid = y_olrt > y_thresh
        env.validate(
            is_valid=valid,
            msg=f"response time {'passed' if valid else 'failed'} (y_init [{y_init:.1f}VAR], y_90% [{y_thresh:.1f}VAR], y_olrt [{y_olrt:.1f}VAR])"
        )

        '''
        Qfinal shall meet the test result accuracy
        requirements specified in 4.2 where Qfinal is the Y parameter and Pfinal is the X parameter. The relationship
        between active and reactive power for constant power factor is given by the following equation: [...]
        SB amendment: Qfinal shall be within 150% of the MRA for VArs of the Q value calculated using the following 
        equation and entering Pfinal and the PF setting under test: [...]
        
        crp:
        Qfin shall equal Qset +/- 1.5 * qMRA
        '''
        # ss eval with 1741SB amendment
        y_min = y_of_x(x_ss) - 1.5 * yMRA
        y_max = y_of_x(x_ss) + 1.5 * yMRA
        valid = y_min <= y_ss <= y_max
        env.validate(
            is_valid=valid,
            msg=f"steady state {'passed' if valid else 'failed'} (y_min [{y_min:.1f}VAR], y_ss [{y_ss:.1f}VAR], y_max [{y_max:.1f}VAR])"
        )

    def crp_validate_step(self, env: Env, eut: Eut, label: str, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
        self.cpf_crp_validate_common(env, eut, label, perturb, olrt, y_of_x)

    def cpf_validate_step(self, env: Env, eut: Eut, label: str, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
        self.cpf_crp_validate_common(env, eut, label, perturb, olrt, y_of_x)

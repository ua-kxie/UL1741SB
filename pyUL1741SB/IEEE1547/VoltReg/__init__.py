from datetime import timedelta
from typing import Callable
from pyUL1741SB import Eut, Env
from pyUL1741SB.IEEE1547 import IEEE1547
import pandas as pd

class VoltReg(IEEE1547):
    def vv_wv_step_validate(self, dct_label: dict, perturb: Callable, xarg, yarg, y_of_x: Callable,
                            olrt: timedelta, xMRA, yMRA):
        df_meas = self.meas_perturb(perturb, olrt, 4 * olrt, ('P', 'Q', 'V', 'F'))
        self.vv_wv_validate(dct_label, df_meas, olrt, y_of_x, xarg, yarg, xMRA, yMRA)

    def vv_wv_validate(self, dct_label: dict, df_meas, olrt: timedelta, y_of_x: Callable, xarg, yarg, xMRA, yMRA):
        # get y_init
        tMRA = self.c_eut.mra.static.T(olrt.total_seconds())
        t_init, t_olrt, t_ss0, t_ss1 = self.ts_of_interest(df_meas.index, olrt)

        y_init = df_meas.loc[t_init, yarg]
        y_olrt = df_meas.loc[t_olrt, yarg]
        # determine y_ss by average after olrt
        x_ss = df_meas.loc[t_ss0:, xarg].mean()
        y_ss = df_meas.loc[t_ss0:, yarg].mean()
        '''
        [...] the EUT shall reach 90% × (Qfinal – Qinitial) + Qinitial within 1.5*MRA at olrt within 1.5*MRA 
        '''
        olrt_s = olrt.total_seconds()
        y_of_t = lambda t: self.expapp(olrt_s, t, y_init, y_ss)
        y_olrt_min, y_olrt_max = self.range_4p2(y_of_t, olrt_s, tMRA, yMRA)
        y_olrt_target = y_of_t(olrt_s)
        olrt_valid = y_olrt_min <= y_olrt <= y_olrt_max

        '''
        shall meet 4.2
        '''
        # ss eval with 1741SB amendment
        y_ss_target = y_of_x(x_ss)
        y_ss_min, y_ss_max = self.range_4p2(y_of_x, x_ss, xMRA, yMRA)
        ss_valid = y_ss_min <= y_ss <= y_ss_max

        self.validator.record_epoch(
            df_meas=df_meas,
            dct_crits={
                'Q': pd.DataFrame({
                    'ts': [t_init, t_olrt, t_ss0, t_ss1],
                    'min': [y_init, y_olrt_min, y_ss_min, y_ss_min],
                    'targ': [y_init, y_olrt_target, y_ss_target, y_ss_target],
                    'max': [y_init, y_olrt_max, y_ss_max, y_ss_max],
                }).set_index('ts'),
            },
            start=t_init,
            end=t_ss1,
            label=''.join(f"{k}: {v}; " for k, v in {**dct_label, 'olrt_valid': olrt_valid, 'ss_valid': ss_valid}.items()),
            passed=olrt_valid and ss_valid
        )

    def cpf_crp_validate(self, dct_label: dict, df_meas, olrt: timedelta, y_of_x: Callable[[float], float]):
        xarg, yarg = 'P', 'Q'
        yMRA = self.c_eut.mra.static.Q
        t_init, t_olrt, t_ss0, t_ss1 = self.ts_of_interest(df_meas.index, olrt)

        y_init = df_meas.loc[t_init, yarg]
        y_olrt = df_meas.loc[t_olrt, yarg]
        x_ss = df_meas.loc[t_ss0:, xarg].mean()
        y_ss = df_meas.loc[t_ss0:, yarg].mean()
        '''
        [...] the EUT shall reach 90% × (Qfinal – Qinitial) + Qinitial within 10 s after a voltage or power step.
         Q shall reach Qini + 0.9 * (Qfin - Qini) in a time of 10s or less
        '''
        y_ss_target = y_of_x(x_ss)
        y_ss_min, y_ss_max = self.range_4p2(y_of_x, x_ss, 0, yMRA)

        olrt_s = olrt.total_seconds()
        y_of_t = lambda t: self.expapp(olrt_s, t, y_init, y_ss)

        y_olrt_min, y_olrt_max = self.range_4p2(y_of_t, olrt_s, 0, yMRA)
        y_olrt_min = min(y_olrt_min, y_ss_min)
        y_olrt_max = max(y_olrt_max, y_ss_max)

        y_olrt_target = y_of_t(olrt_s)
        olrt_valid = y_olrt_min <= y_olrt <= y_olrt_max
        '''
        Qfinal shall meet the test result accuracy
        requirements specified in 4.2 where Qfinal is the Y parameter and Pfinal is the X parameter. The relationship
        between active and reactive power for constant power factor is given by the following equation: [...]
        SB amendment: Qfinal shall be within 150% of the MRA for VArs of the Q value calculated using the following 
        equation and entering Pfinal and the PF setting under test: [...]

        crp:
        Qfin shall equal Qset +/- 1.5 * qMRA
        '''
        ss_valid = y_ss_min <= y_ss <= y_ss_max

        self.validator.record_epoch(
            df_meas=df_meas,
            dct_crits={
                'Q': pd.DataFrame({
                    'ts': [t_init, t_olrt, t_ss0, t_ss1],
                    'min': [y_init, y_olrt_min, y_ss_min, y_ss_min],
                    'targ': [y_init, y_olrt_target, y_ss_target, y_ss_target],
                    'max': [y_init, y_olrt_max, y_ss_max, y_ss_max],
                }).set_index('ts'),
            },
            start=t_init,
            end=t_ss1,
            label=''.join(f"{k}: {v}; " for k, v in {**dct_label, 'olrt_valid': olrt_valid, 'ss_valid': ss_valid}.items()),
            passed=olrt_valid and ss_valid
        )

    def cpf_crp_meas_validate(self, dct_label: dict, perturb: Callable, olrt: timedelta,
                              y_of_x: Callable[[float], float]):
        """"""
        '''
        IEEE 1547.1-2020 5.14.3.3
        '''
        slabel = ''.join([f'{k}: {v}; ' for k, v in dct_label.items()])
        self.c_env.log(msg=f"1741SB {slabel}")
        df_meas = self.meas_perturb(perturb, olrt, 4 * olrt, ('P', 'Q', 'V', 'F'))
        self.cpf_crp_validate(dct_label, df_meas, olrt, y_of_x)

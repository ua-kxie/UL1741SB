from datetime import timedelta
from typing import Callable
from pyUL1741SB import Eut, Env
from pyUL1741SB.IEEE1547 import IEEE1547

class VoltReg(IEEE1547):
    def vv_wv_step_validate(self, dct_label: dict, perturb: Callable, xarg, yarg, y_of_x: Callable,
                            olrt: timedelta, xMRA, yMRA):
        df_meas = self.meas_perturb(perturb, olrt, 4 * olrt, (xarg, yarg))
        self.vv_wv_validate(dct_label, df_meas, olrt, y_of_x, xarg, yarg, xMRA, yMRA)

    def vv_wv_validate(self, dct_label: dict, df_meas, olrt: timedelta, y_of_x: Callable, xarg,
                       yarg, xMRA, yMRA):
        # get y_init
        y_init = df_meas.loc[df_meas.index[0], yarg]
        y_olrt = df_meas.loc[df_meas.index.asof(df_meas.index[0] + olrt), yarg]
        # determine y_ss by average after olrt
        x_ss = df_meas.loc[df_meas.index[0] + olrt:, xarg].mean()
        y_ss = df_meas.loc[df_meas.index[0] + olrt:, yarg].mean()
        '''
        [...] the EUT shall reach 90% × (Qfinal – Qinitial) + Qinitial within 1.5*MRA at olrt within 1.5*MRA 
        '''
        y_thresh = y_init + 0.9 * (y_ss - y_init)
        y_min, y_max = y_thresh - 1.5 * yMRA, y_thresh + 1.5 * yMRA
        olrt_valid = y_min <= y_olrt <= y_max

        '''
        shall meet 4.2
        '''
        # ss eval with 1741SB amendment
        y_targ = y_of_x(x_ss)
        y_min, y_max = self.range_4p2(y_of_x, x_ss, xMRA, yMRA)
        ss_valid = y_min <= y_ss <= y_max

        df_meas['y_target'] = y_targ
        self.c_env.validate(dct_label={
            **dct_label,
            'y_init': y_init,
            'y_olrt': y_olrt,
            'y_ss': y_ss,
            'y_olrt_target': y_thresh,
            'y_ss_target': y_targ,
            'olrt_valid': olrt_valid,
            'ss_valid': ss_valid,
            'data': df_meas
        })

    def cpf_crp_validate(self, dct_label: dict, df_meas, olrt: timedelta,
                         y_of_x: Callable[[float], float]):
        xarg, yarg = 'P', 'Q'
        yMRA = self.c_eut.mra.static.Q

        # # get y_init as furthest from y_ss in the first 10% of olrt (interpreted)
        # y_init = df_meas.loc[df_meas.index[0]:df_meas.index[0] + olrt/10, yarg]
        # y_init = max(y_init, key=lambda x: abs(x - y_ss))
        y_init = df_meas.loc[df_meas.index[0], yarg]
        y_olrt = df_meas.loc[df_meas.index.asof(df_meas.index[0] + olrt), yarg]
        # determine y_ss by average after olrt
        x_ss = df_meas.loc[df_meas.index[0] + olrt:, xarg].mean()
        y_ss = df_meas.loc[df_meas.index[0] + olrt:, yarg].mean()
        '''
        [...] the EUT shall reach 90% × (Qfinal – Qinitial) + Qinitial within 10 s after a voltage or power step.
         - olrt validate as: any y meas within 10% of y_ss before olrt, then pass

         Q shall reach Qini + 0.9 * (Qfin - Qini) in a time of 10s or less
        '''
        # interpret as require y within 10% of y_ss after olrt, or 1.5*MRA, whichever is greater
        # y_thresh = y_init + (y_ss - y_init) * 0.9  # direct interpretation
        y_thresh = max(abs(y_ss - y_init) * 0.1, 1.5 * yMRA)
        olrt_valid = (abs(df_meas.loc[df_meas.index[0] + olrt:, yarg] - y_ss) < y_thresh).all()

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
        y_targ = y_of_x(x_ss)
        y_min = y_targ - 1.5 * yMRA
        y_max = y_targ + 1.5 * yMRA
        ss_valid = y_min <= y_ss <= y_max

        df_meas['y_target'] = y_targ
        self.c_env.validate(dct_label={
            **dct_label,
            'y_init': y_init,
            'y_olrt': y_olrt,
            'y_ss': y_ss,
            'y_olrt_target': y_thresh,
            'y_ss_target': y_targ,
            'olrt_valid': olrt_valid,
            'ss_valid': ss_valid,
            'data': df_meas
        })

    def cpf_crp_meas_validate(self, dct_label: dict, perturb: Callable, olrt: timedelta,
                              y_of_x: Callable[[float], float]):
        """"""
        '''
        IEEE 1547.1-2020 5.14.3.3
        '''
        slabel = ''.join([f'{k}: {v}; ' for k, v in dct_label.items()])
        self.c_env.log(msg=f"1741SB {slabel}")
        xarg, yarg = 'P', 'Q'
        meas_args = (xarg, yarg)
        df_meas = self.meas_perturb(perturb, olrt, 4 * olrt, meas_args)
        self.cpf_crp_validate(dct_label, df_meas, olrt, y_of_x)

from datetime import timedelta
from typing import Callable
import pandas as pd

from pyUL1741SB import Eut, Env

from pyUL1741SB.IEEE1547 import IEEE1547
from pyUL1741SB.IEEE1547.base import IEEE1547Common
from pyUL1741SB.IEEE1547.VoltReg.vv import VVCurve
from pyUL1741SB.IEEE1547.VoltReg.wv import WVCurve
from pyUL1741SB.IEEE1547.VoltReg.vw import VWCurve

class UL1741SB(IEEE1547, IEEE1547Common):
    def await_ss(self):
        # for tests without a well-defined olrt, detect ss. Specifically SB correction for vv-vref

        # get target range
        # detect measurement is within range and not moving

        # how to detect not moving in presence of noise? stationarity tests like augmented dickey-fuller
        pass

    def wv_proc(self, env: Env, eut: Eut):
        """
        """
        env.log(msg="cpf proc against 1547")
        if eut.Cat == Eut.Category.A:
            wv_crvs = [
                ('1A', WVCurve.Crv_1A(eut.Prated, eut.Pmin, eut.Prated_prime, eut.Pmin_prime)),
                ('2A', WVCurve.Crv_2A(eut.Prated, eut.Pmin, eut.Prated_prime, eut.Pmin_prime)),
                ('3A', WVCurve.Crv_3A(eut.Prated, eut.Pmin, eut.Prated_prime, eut.Pmin_prime)),
            ]
        elif eut.Cat == Eut.Category.B:
            wv_crvs = [
                ('1B', WVCurve.Crv_1B(eut.Prated, eut.Pmin, eut.Prated_prime, eut.Pmin_prime)),
                ('2B', WVCurve.Crv_2B(eut.Prated, eut.Pmin, eut.Prated_prime, eut.Pmin_prime)),
                ('3B', WVCurve.Crv_3B(eut.Prated, eut.Pmin, eut.Prated_prime, eut.Pmin_prime)),
            ]
        else:
            raise TypeError(f'unknown eut category {eut.Cat}')
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all ac test source parameters to the nominal operating voltage and frequency.
        c) Set all EUT parameters to the rated active power conditions for the EUT.
        d) Set all voltage trip parameters to default settings.
        e) Set EUT watt-var parameters to the values specified by Characteristic 1. All other functions should
        be turned off.
        '''
        '''
        bb) Repeat steps f) through aa) for characteristics 2 and 3.
        '''
        for crv_key, wv_crv in wv_crvs:
            eut.set_wv(Ena=True, crv=wv_crv)
            lst_dct_steps = [('inj', self.wv_traverse_steps_inj(env, eut, wv_crv))]
            '''
            z) If this EUT can absorb active power, repeat steps g) through y) using PN' values instead of PN.
            '''
            if eut.Prated_prime < 0:
                lst_dct_steps.append(('abs', self.wv_traverse_steps_abs(env, eut, wv_crv)))

            # validate for all steps
            for direction, dct_steps in lst_dct_steps:
                for k, step in dct_steps.items():
                    dct_label = {'proc': 'wv', 'crv': crv_key, 'dir': direction, 'step': k}
                    self.wv_validate_step(
                        env, eut, dct_label, lambda: eut.active_power(pu=step), timedelta(seconds=5),
                        lambda x: wv_crv.y_of_x(x / eut.Prated) * eut.Prated)

    def vw_traverse_steps(self, env: Env, eut: Eut, vw_crv: VWCurve):
        """
        """
        '''
        g) Begin the adjustment towards VH. Step the ac test source voltage to av above VL.
        h) Step the ac test source voltage to av below V1
        i) Step the ac test source voltage to av above V1.
        j) Step the ac test source voltage to (V1 + V2)/2.
        k) Step the ac test source voltage to av below V2.
        l) Step the ac test source voltage to av above V2.
        m) Step the ac test source voltage to av below VH.
        n) Step the ac test source voltage to av above V2.
        o) Step the ac test source voltage to av below V2.
        p) Step the ac test source voltage to (V1 + V2)/2.
        q) Step the ac test source voltage to av above V1. 
        r) Step the ac test source voltage to av below V1.
        s) Step the ac test source voltage to av above VL.
        '''
        aV = eut.mra.static.V * 1.5
        ret = {
            'g': eut.VL + aV,
            'h': vw_crv.V1 * eut.VN - aV,
            'i': vw_crv.V1 * eut.VN + aV,
            'j': (vw_crv.V1 + vw_crv.V2) * eut.VN / 2.,
            'k': vw_crv.V2 * eut.VN - aV,
            'm': eut.VH - aV,
            'o': vw_crv.V2 * eut.VN - aV,
            'p': (vw_crv.V1 + vw_crv.V2) * eut.VN / 2.,
            'q': vw_crv.V1 * eut.VN + aV,
            'r': vw_crv.V1 * eut.VN - aV,
            's': eut.VL + aV
        }
        return ret

    def vw_validate(self, env: Env, eut: Eut, dct_label: dict, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
        """"""
        '''
        IEEE 1547.1-2020 5.14.9.3, +SB amendments
        Data from the test is used to confirm the manufacturer’s stated ratings. After each voltage or power step, a
        new steady-state active power, Pfinal, and steady-state voltage Vfinal is measured. To obtain a steady-state
        value, measurements shall be taken at a time period much larger than the open loop response, Tr, setting of
        the volt-watt function. As a guideline, at 2 times the open loop response time setting, the steady-state state
        error is 1%. In addition, instrumentation filtering may be used to reject any variation in ac test source
        voltage during steady-state measurement.
        
        After each voltage or power step, the open loop response time, Tr, is evaluated. The expected active power
        output, P(Tr), at one times the open loop response time, is calculated as 90% × (Pfinal – Pinitial) + Pinitial.
        Pfinal shall meet the test result accuracy requirements specified in 4.2 where Pfinal is the Y parameter and
        Vfinal is the X parameter.
        
        P(Tr) shall meet the test result accuracy requirements specified in 4.2 where P(Tr) is the Y parameter and Tr
        is the X parameter.
        
        SB amendments:
        The measured Pfinal shall be not more than P(Vfinal) + 1.5 * pMRA, where P(Vfinal) is the target power at 
        Vfinal calculated according to the piecewise linear characteristic under test. There is no tolerance on the 
        low side: Pfinal may be less than P(Vfinal) without limit.
        
        After each voltage or power step, the open loop response time Tr is evaluated. The measured active power output 
        P(tr) at olrt +/- 1.5 tMRA shall be not more than 0.9 * (Pfinal - Pinitial) + Pinitial + 1.5 * pMRA.
        '''
        xMRA = eut.mra.static.V
        yMRA = eut.mra.static.P
        slabel = ''.join([f'{k}: {v}; ' for k, v in dct_label.items()])
        env.log(msg=f"1741SB {slabel}")
        xarg, yarg = 'V', 'P'

        df_meas = self.meas_perturb(env, eut, perturb, olrt, 4 * olrt, (xarg, yarg))

        # get y_init
        y_init = df_meas.loc[df_meas.index[0], yarg]
        y_olrt = df_meas.loc[df_meas.index.asof(df_meas.index[1] + olrt), yarg]
        # determine y_ss by average after olrt
        x_ss = df_meas.loc[df_meas.index[1] + olrt:, xarg].mean()
        y_ss = df_meas.loc[df_meas.index[1] + olrt:, yarg].mean()
        '''
        P(tr) at olrt +/- 1.5 tMRA [...] shall be not more than 0.9 * (Pfinal - Pinitial) + Pinitial + 1.5 * pMRA
        '''
        y_thresh = y_init + 0.9 * (y_ss - y_init) + 1.5 * yMRA
        olrt_valid = y_olrt <= y_thresh

        '''
        Pfinal shall be not more than P(Vfinal) + 1.5 * pMRA
        '''
        # ss eval with 1741SB amendment
        y_targ = y_of_x(x_ss)
        y_min, y_max = self.range_4p2(y_of_x, x_ss, xMRA, yMRA)
        ss_valid = y_ss <= y_max
        env.validate(dct_label={
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

    def wv_validate_step(self, env: Env, eut: Eut, dct_label: dict, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
        """"""
        '''
        IEEE 1547.1-2020 5.14.3.3
        '''
        xMRA = eut.mra.static.P
        yMRA = eut.mra.static.Q
        slabel = ''.join([f'{k}: {v}; ' for k, v in dct_label.items()])
        env.log(msg=f"1741SB {slabel}")
        xarg, yarg = 'P', 'Q'

        self.vv_wv_common_validate(env, eut, dct_label, perturb, xarg, yarg, y_of_x, olrt, xMRA, yMRA)

    def vv_proc(self, env: Env, eut: Eut):
        """
        """
        VH, VN, VL, Pmin, Prated = eut.VH, eut.VN, eut.VL, eut.Pmin, eut.Prated
        av = 1.5 * eut.mra.static.V
        if eut.Cat == Eut.Category.A:
            vv_crvs = [('1A', VVCurve.Crv_1A())]  # just char1 curve, UL1741 amendment
        elif eut.Cat == Eut.Category.B:
            vv_crvs = [('1B', VVCurve.Crv_1B())]
        else:
            raise TypeError(f'unknown eut category {eut.Cat}')
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all voltage trip parameters to the widest range of adjustability. Disable all reactive/active power
        control functions.
        c) Set all ac test source parameters to the nominal operating voltage and frequency.
        d) Adjust the EUT’s available active power to Prated. For an EUT with an electrical input, set the input
        voltage to Vin_nom. The EUT may limit active power throughout the test to meet reactive power
        requirements.
        '''
        eut.wlim(Ena=False, pu=1)
        eut.reactive_power(Ena=False)
        eut.fixed_pf(Ena=False)
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
                for crv_name, vv_crv in vv_crvs:
                    '''
                    e) Set EUT volt-var parameters to the values specified by Characteristic 1. All other function should
                    be turned off. Turn off the autonomously adjusting reference voltage.
                    f) Verify volt-var mode is reported as active and that the correct characteristic is reported.
                    '''
                    eut.set_vv(Ena=True, crv=vv_crv)
                    dct_vvsteps = self.vv_traverse_steps(env, vv_crv, VL, VH, av)
                    for stepname, perturbation in dct_vvsteps.items():
                        dct_label = {'proc': 'vv', 'vref': f'{vref:.0f}', 'pwr': f'{pwr:.0f}', 'crv': f'{crv_name}', 'step': f'{stepname}'}
                        env.pre_cbk(**dct_label)
                        self.vv_validate_step(
                            env,
                            eut,
                            dct_label=dct_label,
                            perturb=perturbation,
                            olrt=timedelta(seconds=vv_crv.Tr),
                            y_of_x=vv_crv.y_of_x,
                        )
                        env.post_cbk(**dct_label)

    def vv_wv_common_validate(self, env: Env, eut: Eut, dct_label: dict, perturb:Callable, xarg, yarg, y_of_x: Callable, olrt: timedelta, xMRA, yMRA):
        df_meas = self.meas_perturb(env, eut, perturb, olrt, 4 * olrt, (xarg, yarg))

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
        olrt_valid = y_min <= y_olrt <= y_max

        '''
        shall meet 4.2
        '''
        # ss eval with 1741SB amendment
        y_targ = y_of_x(x_ss)
        y_min, y_max = self.range_4p2(y_of_x, x_ss, xMRA, yMRA)
        ss_valid = y_min <= y_ss <= y_max
        env.validate(dct_label={
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

    def vv_validate_step(self, env: Env, eut: Eut, dct_label: dict, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
        """"""
        '''
        IEEE 1547.1-2020 5.14.3.3
        '''
        xMRA = eut.mra.static.V
        yMRA = eut.mra.static.Q
        slabel = ''.join([f'{k}: {v}; ' for k, v in dct_label.items()])
        env.log(msg=f"1741SB {slabel}")
        xarg, yarg = 'V', 'Q'

        self.vv_wv_common_validate(env, eut, dct_label, perturb, xarg, yarg, y_of_x, olrt, xMRA, yMRA)

    def vv_vref_proc(self, env: Env, eut: Eut):
        """
        """
        if eut.Cat == Eut.Category.A:
            crv = VVCurve.Crv_1A()  # just char1 curve, UL1741 amendment
        elif eut.Cat == Eut.Category.B:
            crv = VVCurve.Crv_1B()
        else:
            raise TypeError(f'unknown eut category {eut.Cat}')
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        '''
        '''
        j) Repeat test steps b) through i) with Tref set at 5000 s.
        '''
        for Tref_s in [300, 5000]:
            '''
            b) Set all voltage trip parameters to the widest range of adjustability. Disable all reactive/active power
            control functions.
            c) Set all ac test source parameters to the nominal operating voltage and frequency.
            d) Adjust the EUT’s available active power to Prated. For an EUT with an electrical input, set the input
            voltage to Vin_nom. The EUT may limit active power throughout the test to meet reactive power
            requirements.
            e) Set EUT volt-var parameters to the values specified by Characteristic 1. All other functions should
            be turned off. Enable the autonomously adjusting VRef and set Tref to 300 s.
            f) Verify volt-var mode is reported as active and that the correct characteristic is reported. Verify Tref
            is reported back correctly.
            g) Once steady state is reached, read and record the EUT’s active power, reactive power, voltage, and
            current measurements.
            '''
            eut.set_vv(Ena=True, crv=crv)
            eut.set_vv_vref(Ena=True, Tref_s=Tref_s)
            '''
            h) Step the ac test source voltage to (V3 + V4)/2.
            i) Step the ac test source voltage to (V2 + V1)/2.
            '''
            for step, perturbation, is_valid in [
                ('h', lambda: env.ac_config(Vac=eut.VN * (crv.V3 + crv.V4) / 2), lambda x: abs(x) < abs(crv.Q4 * 0.1)),
                ('i', lambda: env.ac_config(Vac=eut.VN * (crv.V2 + crv.V1) / 2), lambda x: abs(x) < abs(crv.Q1 * 0.1)),
            ]:
                dct_label = {'proc': 'vv-vref', 'Tref': Tref_s, 'step': step}
                self.vv_vref_validate(env, eut, dct_label, perturbation, timedelta(seconds=Tref_s), is_valid)

    def vv_vref_validate(self, env: Env, eut: Eut, dct_label: dict, perturb: Callable, olrt: timedelta, is_valid: Callable[[float], bool]):
        """"""
        '''
        IEEE 1547-2020 5.14.5.3
        Data from the test is used to confirm the manufacturer’s stated ratings. After each voltage or power step, a
        new steady-state reactive power, Qfinal, shall be determined. To obtain a steady-state value, Qfinal may be
        measured at a time period much larger than the voltage reference low-pass filter time constant, Tref, setting
        of the volt-var function. As a guideline, at 2 times the open loop response time setting, the steady-state
        error is 1%. In addition, filtering may be used to reject any variation in ac test source voltage during
        steady-state measurement.

        The reactive power output at 1 times the voltage reference low-pass filter time constant, Tref, Q(Tref), shall
        be less than 10% of Q4 for increasing voltage and shall be less than 10% of Q1 for decreasing voltage.
        '''
        '''
        SB Correction:
        In IEEE 1547.1-2020 5.14.5.2, the procedure requires measuring for at least 4 times Tref. 
        As the test settings for Tref are 300 and 5000s, the requirement to measure for 4 times that long greatly 
        extends testing time, and is not necessary in all cases. It is acceptable to stop measuring sooner, 
        if Q has reached steady state at a value compliant with the magnitude criteria, in a shorter time.
        
        In IEEE 1547.1-2020 5.14.5.3, revise the criteria as follows:
            a) it is not required to measure Qfinal at a "time period much larger than ... Tref". Disregard the 
            statement that "at 2 times the open loop response time setting, the steady-state error is 1%". It is 
            acceptable to stop measuring sooner if Q has reached steady state faster
            
            b) After each step (h) and (i), Qfinal shall have an absolute value:
                - Less than 10% of the absolute value of Q1 for decreasing voltage, or
                - Less than 10% of the absolute value of Q4 for increasing voltage,
                in a time not more than 4x Tref
        
        For this test, it is acceptable for the AC source to require longer than 1 cycle requirement stated in 
        IEEE 15476.1-2020 to produce the required test voltage at the EUT terminals, but not more than 1s. This 
        allowance is based on the time constants used in this test, and on some potential difficulties AC sources will 
        face when performing this test with some EUT's (e.g. very large EUT's with external transformers). An 
        alternative is to use signal injection for this test, as allowed by IEEE 1547.1-2020 Section 5.14.2.
        '''
        # measure init
        # perturb
        # measure until Q is valid, up to 1x Tr (4x Tr looks like an error)
        slabel = ''.join([f'{k}: {v}; ' for k, v in dct_label.items()])
        env.log(msg=f"1741SB {slabel}")
        yarg = 'Q'
        meas_args = (yarg,)

        t_step = timedelta(seconds=eut.mra.static.T(olrt.total_seconds()))
        resp, valids = [], []
        resp.append(env.meas_single(*meas_args))
        ts = env.time_now()
        perturb()
        while not env.elapsed_since(4 * olrt, ts):
            env.sleep(t_step)
            meas = env.meas_single(*meas_args)
            if is_valid(meas.loc[meas.index[0], 'Q']):
                valids.append(True)
            else:
                valids = []
            resp.append(meas)
            if len(valids) > 10:  # 30 seconds at 300s Tr, 60 seconds at 5000s Tr
                break
        df_meas = pd.concat(resp)

        crit1 = df_meas.loc[df_meas.index[-10]:, 'Q'].apply(is_valid).all()
        crit2 = (df_meas.index[-10] - df_meas.index[0]).total_seconds() < olrt.total_seconds() * 4
        # get last 10 meas, check all values in last 10 meas are valid
        # get first of last 10 meas, check time is not more than olrt
        # seem dubious, validation similar to vv test would make more sense

        env.validate(dct_label={
            **dct_label,
            'olrt_valid': crit1 and crit2,
            'data': df_meas
        })

    def cpf_crp_validate_common(self, env: Env, eut: Eut, dct_label: dict, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
        """"""
        '''
        IEEE 1547.1-2020 5.14.3.3
        '''
        slabel = ''.join([f'{k}: {v}; ' for k, v in dct_label.items()])
        env.log(msg=f"1741SB {slabel}")
        yMRA = eut.mra.static.Q
        xarg, yarg = 'P', 'Q'
        meas_args = (xarg, yarg)
        df_meas = self.meas_perturb(env, eut, perturb, olrt, 4 * olrt, meas_args)

        # determine y_ss by average after olrt
        x_ss = df_meas.loc[df_meas.index[0] + olrt:, xarg].mean()
        y_ss = df_meas.loc[df_meas.index[0] + olrt:, yarg].mean()

        # # get y_init as furthest from y_ss in the first 10% of olrt (interpreted)
        # y_init = df_meas.loc[df_meas.index[0]:df_meas.index[0] + olrt/10, yarg]
        # y_init = max(y_init, key=lambda x: abs(x - y_ss))
        y_init = df_meas.loc[df_meas.index[0], yarg]
        '''
        [...] the EUT shall reach 90% × (Qfinal – Qinitial) + Qinitial within 10 s after a voltage or power step.
         - olrt validate as: any y meas within 10% of y_ss before olrt, then pass
         
         Q shall reach Qini + 0.9 * (Qfin - Qini) in a time of 10s or less
        '''
        # interpret as require y within 10% of y_ss after olrt, or 1.5*MRA, whichever is greater
        # y_thresh = y_init + (y_ss - y_init) * 0.9  # direct interpretation
        y_thresh = max(abs(y_ss - y_init) * 0.1, 1.5 * yMRA)
        y_olrt = df_meas.loc[df_meas.index.asof(df_meas.index[0] + olrt), yarg]
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
        env.validate(dct_label={
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

    def crp_validate_step(self, env: Env, eut: Eut, dct_label: dict, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
        self.cpf_crp_validate_common(env, eut, dct_label, perturb, olrt, y_of_x)

    def cpf_validate_step(self, env: Env, eut: Eut, dct_label: dict, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
        self.cpf_crp_validate_common(env, eut, dct_label, perturb, olrt, y_of_x)

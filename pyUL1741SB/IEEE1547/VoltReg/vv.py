from datetime import timedelta
from typing import Callable
from pyUL1741SB import Eut, Env
import numpy as np
import pandas as pd

from pyUL1741SB.IEEE1547.VoltReg import VoltReg


class VVCurve:
    '''IEEE 1547.1-2020 Tables 25-27'''
    def __init__(self, **kwargs):
        self.VRef = kwargs['VRef']
        self.V2 = kwargs['V2']
        self.Q2 = kwargs['Q2']
        self.V3 = kwargs['V3']
        self.Q3 = kwargs['Q3']
        self.V1 = kwargs['V1']
        self.Q1 = kwargs['Q1']
        self.V4 = kwargs['V4']
        self.Q4 = kwargs['Q4']
        self.Tr = kwargs['Tr']

    def __str__(self):
        str(self.__dict__)

    def y_of_x(self, x):
        return np.interp(
            x,
            [self.V1, self.V2, self.V3, self.V4],
            [self.Q1, self.Q2, self.Q3, self.Q4],
        )

    @staticmethod
    def Crv_1A():
        return VVCurve(VRef=1.0,
                       V2=1.0, Q2=0, V3=1.0, Q3=0,
                       V1=0.9, Q1=0.25, V4=1.1, Q4=-0.25,
                       Tr=10)

    @staticmethod
    def Crv_1B():
        return VVCurve(VRef=1.0,
                       V2=0.98, Q2=0, V3=1.02, Q3=0,
                       V1=0.92, Q1=0.44, V4=1.08, Q4=-0.44,
                       Tr=5)

    @staticmethod
    def Crv_2A(eut: Eut):
        # defined around NP_Q_ABS / INJ
        inj_scale = self.c_eut.Qrated_inj / self.c_eut.Srated
        abs_scale = self.c_eut.Qrated_abs / self.c_eut.Srated
        return VVCurve(VRef=1.05,
                       V2=1.04, Q2=0.5 * inj_scale, V3=1.07, Q3=0.5 * inj_scale,
                       V1=0.88, Q1=1.0 * inj_scale, V4=1.1, Q4=-1.0 * abs_scale,
                       Tr=1)

    @staticmethod
    def Crv_2B(eut: Eut):
        # defined around NP_Q_ABS / INJ
        inj_scale = self.c_eut.Qrated_inj / self.c_eut.Srated
        abs_scale = self.c_eut.Qrated_abs / self.c_eut.Srated
        return VVCurve(VRef=1.05,
                       V2=1.04, Q2=0.5 * inj_scale, V3=1.07, Q3=0.5 * inj_scale,
                       V1=0.88, Q1=1.0 * inj_scale, V4=1.1, Q4=-1.0 * abs_scale,
                       Tr=1)

    @staticmethod
    def Crv_3A(eut: Eut):
        # defined around NP_Q_ABS / INJ
        inj_scale = self.c_eut.Qrated_inj / self.c_eut.Srated
        abs_scale = self.c_eut.Qrated_abs / self.c_eut.Srated
        return VVCurve(VRef=0.95,
                       V2=0.93, Q2=-0.5 * abs_scale, V3=0.96, Q3=-0.5 * abs_scale,
                       V1=0.9, Q1=1.0 * inj_scale, V4=1.1, Q4=-1.0 * abs_scale,
                       Tr=90)

    @staticmethod
    def Crv_3B(eut: Eut):
        # defined around NP_Q_ABS / INJ
        inj_scale = self.c_eut.Qrated_inj / self.c_eut.Srated
        abs_scale = self.c_eut.Qrated_abs / self.c_eut.Srated
        return VVCurve(VRef=0.95,
                       V2=0.93, Q2=-0.5 * abs_scale, V3=0.96, Q3=-0.5 * abs_scale,
                       V1=0.9, Q1=1.0 * inj_scale, V4=1.1, Q4=-1.0 * abs_scale,
                       Tr=90)

class VV(VoltReg):
    def vv_step_validate(self, env: Env, label: str, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
        '''
        Data from the test is used to confirm the manufacturer’s stated ratings. After each voltage, a new steady
        state reactive power, Qfinal, and steady-state voltage Vfinal is measured. To obtain a steady-state value,
        measurements shall be taken at a time period much larger than the open loop response, Tr, setting of the
        volt-var function. As a guideline, at 2 times the open loop response time setting, the steady-state error is
        1%. In addition, instrumentation filtering may be used to reject any variation in ac test source voltage
        during steady-state measurement.
        After each voltage, the open loop response time, Tr, is evaluated. The expected reactive power output,
        Q(Tr), at one times the open loop response time, is calculated as 90% × (Qfinal – Qinitial) + Qinitial.
        Qfinal shall meet the test result accuracy requirements specified in 4.2, where Qfinal is the Y parameter and
        Vfinal is the X parameter.
        Q(Tr) shall meet the test result accuracy requirements specified in 4.2, where Q(Tr) is the Y parameter and
        Tr is the X parameter.
        Where EUT is DER equipment that does not produce power, such as a plant controller, the DER’s
        commanded power factor or commanded reactive power may be used to verify compliance at the DER
        design evaluation stage. Because the unit does not produce power, signal injection may be used.
        '''
        raise NotImplementedError

    def vv_traverse_steps(self, vv_crv: VVCurve, VL, VH, av):
        """
        """
        '''
        g) Once steady state is reached, Begin the adjustment to VH. Step the ac test source voltage av below V3.
        h) Step the ac test source voltage to av above V3.
        i) Step the ac test source voltage to (V3 + V4)/2.
        j) If V4 is less than VH, step the ac test source voltage to av below V4, else skip to step l).
        k) Step the ac test source voltage to av above V4.
        l) Step the ac test source voltage to av below VH.
        m) Begin the return to VRef. If V4 is less than VH, step the ac test source voltage to av above V4, else skip to step o).
        n) Step the ac test source voltage to av below V4.
        o) Step the ac test source voltage to (V3 + V4)/2.
        p) Step the ac test source voltage to av above V3.
        q) Step the ac test source voltage to av below V3.
        r) Step the ac test source voltage to VRef.
        s) Begin the adjustment to VL. Step the ac test source voltage to av above V2 (Vb).
        t) Step the ac test source voltage to av below V2 (Vb).
        u) Step the ac test source voltage to (V2 + V1)/2.
        v) If V1 is greater than VL, step the ac test source voltage to av above V1, else skip to step x).
        w) Step the ac test source voltage to av below V1.
        x) Step the ac test source voltage to av above VL.
        y) Begin the return to VRef. If V1 is greater than VL, step the ac test source voltage to av below V1, else skip to step z).
        z) Step the ac test source voltage to av above V1.
        aa) Step the ac test source voltage to (V2 + V1)/2.
        bb) Step the ac test source voltage to av below V2.
        cc) Step the ac test source voltage to av above V2.
        dd) Step the ac test source voltage to VRef.
        '''
        ret = {
            'g': lambda: self.c_env.ac_config(Vac=vv_crv.V3 * self.c_eut.VN - av),
            'h': lambda: self.c_env.ac_config(Vac=vv_crv.V3 * self.c_eut.VN + av),
            'i': lambda: self.c_env.ac_config(Vac=(vv_crv.V3 + vv_crv.V4) / 2. * self.c_eut.VN),
            'j': lambda: self.c_env.ac_config(Vac=vv_crv.V4 * self.c_eut.VN - av),
            'k': lambda: self.c_env.ac_config(Vac=vv_crv.V4 * self.c_eut.VN + av),
            'l': lambda: self.c_env.ac_config(Vac=VH - av),
            'm': lambda: self.c_env.ac_config(Vac=vv_crv.V4 * self.c_eut.VN + av),
            'n': lambda: self.c_env.ac_config(Vac=vv_crv.V4 * self.c_eut.VN - av),
            'o': lambda: self.c_env.ac_config(Vac=(vv_crv.V3 + vv_crv.V4) / 2. * self.c_eut.VN),
            'p': lambda: self.c_env.ac_config(Vac=vv_crv.V3 * self.c_eut.VN + av),
            'q': lambda: self.c_env.ac_config(Vac=vv_crv.V3 * self.c_eut.VN - av),
            'r': lambda: self.c_env.ac_config(Vac=vv_crv.VRef * self.c_eut.VN),
            's': lambda: self.c_env.ac_config(Vac=vv_crv.V2 * self.c_eut.VN + av),
            't': lambda: self.c_env.ac_config(Vac=vv_crv.V2 * self.c_eut.VN - av),
            'u': lambda: self.c_env.ac_config(Vac=(vv_crv.V2 + vv_crv.V1) / 2. * self.c_eut.VN),
            'v': lambda: self.c_env.ac_config(Vac=vv_crv.V1 * self.c_eut.VN + av),
            'w': lambda: self.c_env.ac_config(Vac=vv_crv.V1 * self.c_eut.VN - av),
            'x': lambda: self.c_env.ac_config(Vac=VL + av),
            'y': lambda: self.c_env.ac_config(Vac=vv_crv.V1 * self.c_eut.VN - av),
            'z': lambda: self.c_env.ac_config(Vac=vv_crv.V1 * self.c_eut.VN + av),
            'aa': lambda: self.c_env.ac_config(Vac=(vv_crv.V2 + vv_crv.V1) / 2. * self.c_eut.VN),
            'bb': lambda: self.c_env.ac_config(Vac=vv_crv.V2 * self.c_eut.VN - av),
            'cc': lambda: self.c_env.ac_config(Vac=vv_crv.V2 * self.c_eut.VN + av),
            'dd': lambda: self.c_env.ac_config(Vac=vv_crv.VRef * self.c_eut.VN)
        }
        if VH < vv_crv.V4 * self.c_eut.VN:
            self.c_env.log(msg=f'steps j, k, m, n will be skipped since VH [{VH}] < V4 [{vv_crv.V4 * self.c_eut.VN}]')
            for step in ['j', 'k', 'm', 'n']:
                ret.pop(step)
        if VL > vv_crv.V1 * self.c_eut.VN:
            self.c_env.log(msg=f'steps v, w, y, z will be skipped since VH [{VL}] > V1 [{vv_crv.V1 * self.c_eut.VN}]')
            for step in ['v', 'w', 'y', 'z']:
                ret.pop(step)
        return ret

    def vv_proc(self):
        """
        """
        VH, VN, VL, Pmin, Prated = self.c_eut.VH, self.c_eut.VN, self.c_eut.VL, self.c_eut.Pmin, self.c_eut.Prated
        av = 1.5 * self.c_eut.mra.static.V
        if self.c_eut.Cat == self.c_eut.Category.A:
            vv_crvs = [('1A', VVCurve.Crv_1A())]  # just char1 curve, UL1741 amendment. NP_VA as base. Other curves use NP_Q as base
        elif self.c_eut.Cat == self.c_eut.Category.B:
            vv_crvs = [('1B', VVCurve.Crv_1B())]
        else:
            raise TypeError(f'unknown eut category {self.c_eut.Cat}')
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all voltage trip parameters to the widest range of adjustability. Disable all reactive/active power
        control functions.
        c) Set all ac test source parameters to the nominal operating voltage and frequency.
        d) Adjust the EUT’s available active power to Prated. For an EUT with an electrical input, set the input
        voltage to Vin_nom. The EUT may limit active power throughout the test to meet reactive power
        requirements.
        '''
        self.c_eut.set_cpf(Ena=False)
        self.c_eut.set_crp(Ena=False)
        self.c_eut.set_wv(Ena=False)
        self.c_eut.set_vv(Ena=False)
        self.c_eut.set_vw(Ena=False)
        self.c_eut.set_lap(Ena=False, pu=1)
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
                    g) Once steady state is reached, Begin the adjustment to VH. Step the ac test source voltage av below V3.
                    '''
                    self.c_eut.set_vv(Ena=True, crv=vv_crv)
                    dct_vvsteps = self.vv_traverse_steps(vv_crv, VL, VH, av)
                    self.c_env.sleep(timedelta(seconds=vv_crv.Tr * 2))
                    for stepname, perturbation in dct_vvsteps.items():
                        dct_label = {'proc': 'vv', 'vref': f'{vref:.0f}', 'pwr': f'{pwr:.0f}', 'crv': f'{crv_name}', 'step': f'{stepname}'}
                        self.vv_step_validate(
                            dct_label=dct_label,
                            perturb=perturbation,
                            olrt=timedelta(seconds=vv_crv.Tr),
                            y_of_x=lambda x: vv_crv.y_of_x(x / self.c_eut.VN) * self.c_eut.Srated,
                        )

    def vv_step_validate(self, dct_label: dict, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
        """"""
        '''
        IEEE 1547.1-2020 5.14.3.3
        '''
        xMRA = self.c_eut.mra.static.V
        yMRA = self.c_eut.mra.static.Q
        slabel = ''.join([f'{k}: {v}; ' for k, v in dct_label.items()])
        self.c_env.log(msg=f"1741SB {slabel}")
        xarg, yarg = 'V', 'Q'

        self.vv_wv_step_validate(dct_label, perturb, xarg, yarg, y_of_x, olrt, xMRA, yMRA)

    def vv_vref_proc(self):
        """
        """
        if self.c_eut.Cat == self.c_eut.Category.A:
            crv = VVCurve.Crv_1A()  # just char1 curve, UL1741 amendment
        elif self.c_eut.Cat == self.c_eut.Category.B:
            crv = VVCurve.Crv_1B()
        else:
            raise TypeError(f'unknown eut category {self.c_eut.Cat}')
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        '''
        self.c_eut.set_cpf(Ena=False)
        self.c_eut.set_crp(Ena=False)
        self.c_eut.set_wv(Ena=False)
        self.c_eut.set_vv(Ena=False)
        self.c_eut.set_vw(Ena=False)
        self.c_eut.set_lap(Ena=False, pu=1)
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
            self.c_eut.set_vv(Ena=True, crv=crv)
            self.c_eut.set_vv_vref(Ena=True, Tref_s=Tref_s)
            self.c_env.sleep(timedelta(seconds=10))
            '''
            h) Step the ac test source voltage to (V3 + V4)/2.
            i) Step the ac test source voltage to (V2 + V1)/2.
            '''
            for step, perturbation, is_valid in [
                ('h', lambda: self.c_env.ac_config(Vac=self.c_eut.VN * (crv.V3 + crv.V4) / 2), lambda x: abs(x) < abs(crv.Q4 * 0.1)),
                ('i', lambda: self.c_env.ac_config(Vac=self.c_eut.VN * (crv.V2 + crv.V1) / 2), lambda x: abs(x) < abs(crv.Q1 * 0.1)),
            ]:
                dct_label = {'proc': 'vv-vref', 'Tref': Tref_s, 'step': step}
                self.vv_vref_validate(dct_label, perturbation, timedelta(seconds=Tref_s), is_valid)

    def vv_vref_validate(self, dct_label: dict, perturb: Callable, olrt: timedelta,
                         is_valid: Callable[[float], bool]):
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
        self.c_env.log(msg=f"1741SB {slabel}")
        yarg = 'Q'
        meas_args = (yarg,)

        t_step = timedelta(seconds=self.c_eut.mra.static.T(olrt.total_seconds()))
        resp, valids = [], []
        resp.append(self.c_env.meas_single(*meas_args))
        ts = self.c_env.time_now()
        perturb()
        while not self.c_env.elapsed_since(4 * olrt, ts):
            self.c_env.sleep(t_step)
            meas = self.c_env.meas_single(*meas_args)
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

        self.c_env.validate(dct_label={
            **dct_label,
            'valid': crit1 and crit2,
            'data': df_meas
        })

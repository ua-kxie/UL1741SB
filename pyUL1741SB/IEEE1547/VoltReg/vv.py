
from pyUL1741SB import Eut, Env
import numpy as np

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
        self.name = kwargs['name']

    def y_of_x(self, x):
        return np.interp(
            x,
            [self.V1, self.V2, self.V3, self.V4],
            [self.Q1, self.Q2, self.Q3, self.Q4],
        )

    @staticmethod
    def Crv_1A(Prated, VN):
        return VVCurve(
            VRef=VN,
            V2=VN,
            Q2=0,
            V3=VN,
            Q3=0,
            V1=0.9 * VN,
            Q1=0.25 * Prated,
            V4=1.1 * VN,
            Q4=-0.25 * Prated,
            Tr=10,
            name='1a'
        )

    @staticmethod
    def Crv_1B(Prated, VN):
        return VVCurve(
            VRef=VN,
            V2=0.98 * VN,
            Q2=0,
            V3=1.02 * VN,
            Q3=0,
            V1=0.92 * VN,
            Q1=0.44 * Prated,
            V4=1.08 * VN,
            Q4=-0.44 * Prated,
            Tr=5,
            name='1b'
        )

    @staticmethod
    def Crv_2A(Prated, VN):
        return VVCurve(
            VRef=1.05 * VN,
            V2=1.04 * VN,
            Q2=0.5 * Prated,
            V3=1.07 * VN,
            Q3=0.5 * Prated,
            V1=0.88 * VN,
            Q1=1.0 * Prated,
            V4=1.1 * VN,
            Q4=-1.0 * Prated,
            Tr=1,
            name='2a'
        )

    @staticmethod
    def Crv_2B(Prated, VN):
        return VVCurve(
            VRef=1.05 * VN,
            V2=1.04 * VN,
            Q2=0.5 * Prated,
            V3=1.07 * VN,
            Q3=0.5 * Prated,
            V1=0.88 * VN,
            Q1=1.0 * Prated,
            V4=1.1 * VN,
            Q4=-1.0 * Prated,
            Tr=1,
            name='2b'
        )

    @staticmethod
    def Crv_3A(Prated, VN):
        return VVCurve(
            VRef=0.95 * VN,
            V2=0.93 * VN,
            Q2=-0.5 * Prated,
            V3=0.96 * VN,
            Q3=-0.5 * Prated,
            V1=0.9 * VN,
            Q1=1.0 * Prated,
            V4=1.1 * VN,
            Q4=-1.0 * Prated,
            Tr=90,
            name='3a'
        )

    @staticmethod
    def Crv_3B(Prated, VN):
        return VVCurve(
            VRef=0.95 * VN,
            V2=0.93 * VN,
            Q2=-0.5 * Prated,
            V3=0.96 * VN,
            Q3=-0.5 * Prated,
            V1=0.9 * VN,
            Q1=1.0 * Prated,
            V4=1.1 * VN,
            Q4=-1.0 * Prated,
            Tr=90,
            name='3b'
        )

class VV:
    def vv_validate_step(self):
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

    def vv_traverse_steps(self, env: Env, vv_crv: VVCurve, VL, VH, av):
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
            'g': lambda: env.ac_config(Vac=vv_crv.V3 - av),
            'h': lambda: env.ac_config(Vac=vv_crv.V3 + av),
            'i': lambda: env.ac_config(Vac=(vv_crv.V3 + vv_crv.V4) / 2.),
            'j': lambda: env.ac_config(Vac=vv_crv.V4 - av),
            'k': lambda: env.ac_config(Vac=vv_crv.V4 + av),
            'l': lambda: env.ac_config(Vac=VH - av),
            'm': lambda: env.ac_config(Vac=vv_crv.V4 + av),
            'n': lambda: env.ac_config(Vac=vv_crv.V4 - av),
            'o': lambda: env.ac_config(Vac=(vv_crv.V3 + vv_crv.V4) / 2.),
            'p': lambda: env.ac_config(Vac=vv_crv.V3 + av),
            'q': lambda: env.ac_config(Vac=vv_crv.V3 - av),
            'r': lambda: env.ac_config(Vac=vv_crv.VRef),
            's': lambda: env.ac_config(Vac=vv_crv.V2 + av),
            't': lambda: env.ac_config(Vac=vv_crv.V2 - av),
            'u': lambda: env.ac_config(Vac=(vv_crv.V2 + vv_crv.V1) / 2.),
            'v': lambda: env.ac_config(Vac=vv_crv.V1 + av),
            'w': lambda: env.ac_config(Vac=vv_crv.V1 - av),
            'x': lambda: env.ac_config(Vac=VL + av),
            'y': lambda: env.ac_config(Vac=vv_crv.V1 - av),
            'z': lambda: env.ac_config(Vac=vv_crv.V1 + av),
            'aa': lambda: env.ac_config(Vac=(vv_crv.V2 + vv_crv.V1) / 2.),
            'bb': lambda: env.ac_config(Vac=vv_crv.V2 - av),
            'cc': lambda: env.ac_config(Vac=vv_crv.V2 + av),
            'dd': lambda: env.ac_config(Vac=vv_crv.VRef)
        }
        if VH < vv_crv.V4:
            env.log(msg=f'steps j, k, m, n will be skipped since VH [{VH}] < V4 [{vv_crv.V4}]')
            for step in ['j', 'k', 'm', 'n']:
                ret.pop(step)
        if VL > vv_crv.V1:
            env.log(msg=f'steps v, w, y, z will be skipped since VH [{VL}] > V1 [{vv_crv.V1}]')
            for step in ['v', 'w', 'y', 'z']:
                ret.pop(step)
        return ret

    def vv_proc(self, env: Env, eut: Eut):
        """
        """
        raise NotImplementedError
        VH, VN, VL, Pmin, Prated = eut.VH, eut.VN, eut.VL, eut.Pmin, eut.Prated
        av = 1.5 * eut.mra.static.V
        if eut.Cat == Eut.Category.A:
            vv_crvs = [VVCurve.Crv_1A(eut.Prated, eut.VN), VVCurve.Crv_2A(eut.Prated, eut.VN), VVCurve.Crv_3A(eut.Prated, eut.VN)]
        elif eut.Cat == Eut.Category.B:
            vv_crvs = [VVCurve.Crv_1B(eut.Prated, eut.VN), VVCurve.Crv_2B(eut.Prated, eut.VN), VVCurve.Crv_3B(eut.Prated, eut.VN)]
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
        for vref in [VN, 1.05 * VN, 0.95 * VN]:
        # for vref in [VN]:  # 1741SB amendment
            '''
            ff) Repeat test steps d) through ee) at EUT power set at 20% and 66% of rated power.
            '''
            for pwr in [Prated, 0.2 * Prated, 0.66 * Prated]:
            # for pwr in [Prated]:  # 1741SB amendment
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

    def vv_vref(self):
        """
        """
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        '''
        '''
        j) Repeat test steps b) through i) with Tref set at 5000 s.
        '''
        raise NotImplementedError("IEEE 1547 vv_vref")
        for Tref in [300, 5000]:
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
            h) Step the ac test source voltage to (V3 + V4)/2.
            i) Step the ac test source voltage to (V2 + V1)/2.
            '''

    def vv_imbal(self):
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all voltage trip parameters to the widest range of adjustability. Disable all reactive/active power
        control functions.
        c) Set all ac test source parameters to the nominal operating voltage and frequency.
        d) Adjust the EUT’s available active power to Prated. For an EUT with an electrical input, set the input
        voltage to Vin_nom. The EUT may limit active power throughout the test to meet reactive power
        requirements.
        e) Set EUT volt-var parameters to the values specified by the default volt-var settings in Characteristic
        1. All other function should be turned off. Turn off the autonomously adjusting reference voltage.
        f) Verify volt-var mode is reported as active and that the correct characteristic is reported.
        g) Once steady state is reached, begin the adjustment of phase voltages.
        h) For multiphase units, step the ac test source voltage to Case A from Table 24.
        i) For multiphase units, step the ac test source voltage to VN.
        j) For multiphase units, step the ac test source voltage to Case B from Table 24.
        k) For multiphase units, step the ac test source voltage to VN.
        l) Where an EUT has more than one setting for the response to unbalanced voltages, repeat steps a)
        through k) to verify each setting.
        '''
        raise NotImplementedError("IEEE 1547 vv_imbal")

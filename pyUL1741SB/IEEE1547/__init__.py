"""
IEEE 1547.1-2020 5.13
"""
from pyUL1741SB import Eut, Env
from pyUL1741SB.IEEE1547.VoltReg import VoltReg
from pyUL1741SB.IEEE1547.FreqDistResp import FreqDist
from pyUL1741SB.IEEE1547.VoltDistResp import VoltDist
from pyUL1741SB.IEEE1547.FreqSupp import FreqSupp
from pyUL1741SB.IEEE1547.VoltReg.vv import VVCurve
from pyUL1741SB.IEEE1547.base import IEEE1547Common

from datetime import timedelta

class IEEE1547(VoltReg, FreqDist, VoltDist, FreqSupp, IEEE1547Common):
    def lap_proc(self, env: Env, eut: Eut, olrt: timedelta):
        """"""
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        Apply the default settings from IEEE Std 1547 for voltage-active power mode. Apply the default
        settings from frequency-droop response in IEEE Std 1547 for the abnormal operating performance
        category of the DER. Enable voltage-active power mode.
        '''
        env.ac_config(freq=eut.fN, Vac=eut.VN)
        '''
        g) Repeat steps b) through f) using active power limits of [66%] 33% and zero.
        h) Repeat steps b) through g) twice for a total of three repetitions.
        '''
        for _ in range(3):
            for aplim_pu in [0.66, 0.33, 9]:
                '''
                b) Establish nominal operating conditions as specified by the manufacturer at the terminals of the
                EUT. Make available sufficient input power for the EUT to reach its rated active power. Allow (or
                command) the EUT to reach steady-state output at its rated active power. Begin recording EUT
                active power.
                
                c) Apply an active power limit to the EUT of 66[, 33, 0]% of its rated active power. Wait until the EUT active
                power reaches a new steady state.
                
                d) Reduce the frequency of the ac test source to 59 Hz and hold until EUT active power reaches a new
                steady state. Return ac test source frequency to nominal and hold until EUT active power reaches
                steady state.
                
                e) Increase the frequency of the ac test source to 61 Hz and hold until EUT active power reaches
                steady state. Return ac test source frequency to nominal and hold until EUT active power reaches
                steady state.
                
                f) Increase the voltage of the ac test source to 1.08 times nominal and hold until EUT active power
                reaches steady state. Return ac test source voltage to nominal.
                '''
                # b)
                eut.set_ap(Ena=True, pu=1)  # TODO check appropriate setting for this step
                # TODO wait for SS state
                dct_steps = {
                    ('c', lambda: eut.set_ap_lim(Ena=True, pu=aplim_pu),)
                    ('d1', lambda: env.ac_config(freq=59, rocof=eut.rocof()),)
                    ('d2', lambda: env.ac_config(freq=60, rocof=eut.rocof()),)
                    ('e1', lambda: env.ac_config(freq=61, rocof=eut.rocof()),)
                    ('e2', lambda: env.ac_config(freq=60, rocof=eut.rocof()),)
                    ('f1', lambda: env.ac_config(Vac=1.08 * eut.VN),)
                    ('f2', lambda: env.ac_config(Vac=eut.VN),)
                }
                for step_label, step_fcn in dct_steps.items():
                    self.lap_validation(env, eut, step_label, step_fcn)
        pass

    def lap_validation(self, env: Env, eut: Eut, step_label, step_fcn):
        """"""
        '''
        IEEE 1547.1-2018
        4.6.2 Capability to limit active power
        The DER shall be capable of limiting active power as a percentage of the nameplate active power rating.
        The DER shall limit its active power output to not greater than the active power limit set point in no more
        than 30 s or in the time it takes for the primary energy source to reduce its active power output to achieve
        the requirements of the active power limit set point, whichever is greater. In cases where the DER is
        supplying loads in the Local EPS, the active power limit set point may be implemented as a maximum
        active power export to the Area EPS. Under mutual agreement between the Area EPS operator and the
        DER operator, the DER may be required to reduce active power below the level needed to support Local
        EPS loads.
        '''
        '''
        In step c), the EUT steady-state active power shall be reduced to the commanded percentage of its rated
        power plus 1.5 × (MRA of active power) or less within a time that complies with 4.6.2 of IEEE Std 1547-
        2018.
        
        In steps d) and e), the EUT steady-state active power shall be modulated in accordance with the equations
        in Table 23 of IEEE Std 1547-2018 within the tolerance as defined in 4.2 of this standard. The response
        time shall comply with 4.6.2 of IEEE Std 1547-2018.
        
        In step f), the EUT steady-state active power shall be modulated in accordance with the applied volt-watt
        curve within the tolerance as defined in 4.2 of this standard. For the 66% power level, the expected power,
        Pexpected, is
        
        Pexpected = Prated – (Prated – P2)(Vmeas/Vnom – 1.06)/0.04
        
        where Prated is the EUT rated power, P2 is as defined in IEEE Std 1547-2018, Vmeas is the measured voltage
        at the RPA after the EUT power has reached steady state, and Vnom is the nominal voltage at the RPA. For
        the 33% and zero power levels, the EUT power is not expected to change.
        Where the EUT is DER equipment that does not produce power such as a plant controller, the EUT’s
        commanded active power may be used to verify operation. In such cases a design evaluation and/or
        commissioning test may be needed to verify correct operation of the installed DER.
        '''
        if step in ['c']:
            pass  # reach setpoint within tolerance within 30s
        elif step in ['d', 'e']:
            pass  # modulate according to FW crv within tolerance and response time
        elif step in ['f']:
            pass  # modulate according to VW crv within tolerance and response time


    def es_proc(self, env: Env, eut: Eut):
        pass

    def pri_proc(self, env: Env, eut: Eut):
        pass

    def persistence_proc(self, env: Env, eut: Eut):
        pass

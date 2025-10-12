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

from pyUL1741SB.IEEE1547.FreqSupp import FWChar
from pyUL1741SB.IEEE1547.VoltReg.vw import VWCurve

from datetime import timedelta

class IEEE1547(VoltReg, FreqDist, VoltDist, FreqSupp, IEEE1547Common):
    def lap_proc(self, env: Env, eut: Eut):
        """"""
        dflt_fwchar = {
            eut.aopCat.I: FWChar.CatI_CharI(),
            eut.aopCat.II: FWChar.CatII_CharI(),
            eut.aopCat.III: FWChar.CatIII_CharI(),
        }[eut.aopCat]
        if eut.Prated_prime < 0:
            dflt_vwcrv = {
                eut.Category.A: VWCurve.Crv_1A_abs(eut),
                eut.Category.B: VWCurve.Crv_1B_abs(eut),
            }[eut.Cat]
        else:
            dflt_vwcrv = {
                eut.Category.A: VWCurve.Crv_1A_inj(eut),
                eut.Category.B: VWCurve.Crv_1B_inj(eut),
            }[eut.Cat]
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
        for i in range(3):
            for aplim_pu in [0.66, 0.33, 0]:
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
                dct_label = {
                    'proc': 'lap',
                    'iter': i,
                    'aplim_pu': aplim_pu,
                }
                def y_of_fw(x):
                    if eut.Prated_prime < 0:
                        ymin_pu = -1
                    else:
                        ymin_pu = 0
                    ymax_pu = 1
                    fw_val = dflt_fwchar.y_of_x(x, ymin_pu, aplim_pu, ymax_pu) * eut.Prated
                    return fw_val
                def y_of_vw(x):
                    vw_val = dflt_vwcrv.y_of_x(x) * eut.Prated
                    return min(vw_val, aplim_pu * eut.Prated)
                lst_tup_steps = [
                    # step label, perturbation, y_ss_target, olrt
                    ('c', lambda: eut.set_ap_lim(Ena=True, pu=aplim_pu), aplim_pu * eut.Prated, timedelta(seconds=30)),
                    ('d1', lambda: env.ac_config(freq=59, rocof=eut.rocof()), y_of_fw(59), timedelta(seconds=dflt_fwchar.tr)),
                    ('d2', lambda: env.ac_config(freq=60, rocof=eut.rocof()), y_of_fw(60), timedelta(seconds=dflt_fwchar.tr)),
                    ('e1', lambda: env.ac_config(freq=61, rocof=eut.rocof()), y_of_fw(61), timedelta(seconds=dflt_fwchar.tr)),
                    ('e2', lambda: env.ac_config(freq=60, rocof=eut.rocof()), y_of_fw(60), timedelta(seconds=dflt_fwchar.tr)),
                    ('f1', lambda: env.ac_config(Vac=1.08 * eut.VN), y_of_vw(1.08), timedelta(seconds=dflt_vwcrv.Tr)),
                    ('f2', lambda: env.ac_config(Vac=eut.VN), y_of_vw(1.0), timedelta(seconds=dflt_vwcrv.Tr))
                ]
                for tup in lst_tup_steps:
                    self.lap_validation(env, eut, dct_label, *tup)

    def lap_validation(self, env: Env, eut: Eut, dct_label, step_label, perturbation, y_ss_target, olrt: timedelta):
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
        yarg = 'P'
        yMRA = eut.mra.static.P
        df_meas = self.meas_perturb(env, eut, perturbation, olrt, 4 * olrt, (yarg,))
        y_init = df_meas.loc[df_meas.index[0], yarg]
        y_ss = df_meas.loc[df_meas.index[1] + olrt:, yarg].mean()
        ss_valid = y_ss <= y_ss_target + 1.5 * yMRA
        env.validate(dct_label={
            **dct_label,
            'step': step_label,
            'y_init': y_init,
            'olrt': olrt.total_seconds(),
            'y_ss': y_ss,
            'y_ss_target': y_ss_target + 1.5 * yMRA,
            'ss_valid': ss_valid,
            'data': df_meas
        })

    def es_proc(self, env: Env, eut: Eut):
        pass

    def pri_proc(self, env: Env, eut: Eut):
        pass

    def persistence_proc(self, env: Env, eut: Eut):
        pass

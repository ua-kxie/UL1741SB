from datetime import timedelta
from pyUL1741SB.IEEE1547 import IEEE1547
from pyUL1741SB.IEEE1547.FreqSupp import FWChar
from pyUL1741SB.IEEE1547.VoltReg.vw import VWCurve


class LAP(IEEE1547):
    def lap_proc(self):
        """"""
        dflt_fwchar = {
            self.c_eut.aopCat.I: FWChar.CatI_CharI(),
            self.c_eut.aopCat.II: FWChar.CatII_CharI(),
            self.c_eut.aopCat.III: FWChar.CatIII_CharI(),
        }[self.c_eut.aopCat]
        if self.c_eut.Prated_prime < 0:
            dflt_vwcrv = {
                self.c_eut.Category.A: VWCurve.Crv_1A_abs(self.c_eut),
                self.c_eut.Category.B: VWCurve.Crv_1B_abs(self.c_eut),
            }[self.c_eut.Cat]
        else:
            dflt_vwcrv = {
                self.c_eut.Category.A: VWCurve.Crv_1A_inj(self.c_eut),
                self.c_eut.Category.B: VWCurve.Crv_1B_inj(self.c_eut),
            }[self.c_eut.Cat]
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        Apply the default settings from IEEE Std 1547 for voltage-active power mode. Apply the default
        settings from frequency-droop response in IEEE Std 1547 for the abnormal operating performance
        category of the DER. Enable voltage-active power mode.
        '''
        self.c_env.ac_config(freq=self.c_eut.fN, Vac=self.c_eut.VN)
        self.c_eut.set_cpf(Ena=False)
        self.c_eut.set_crp(Ena=False)
        self.c_eut.set_wv(Ena=False)
        self.c_eut.set_vv(Ena=False)

        self.c_eut.set_fw(Ena=True, crv=dflt_fwchar)
        self.c_eut.set_vw(Ena=True, crv=dflt_vwcrv)
        '''
        g) Repeat steps b) through f) using active power limits of [66%] 33% and zero.
        h) Repeat steps b) through g) twice for a total of three repetitions.
        '''
        for i in range(3):
            for aplim_pu in [0.66, 0.33, 0]:
                '''
                b) Establish nominal operating conditions as specified by the manufacturer at the terminals of the
                self.c_eut. Make available sufficient input power for the EUT to reach its rated active power. Allow (or
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
                self.c_eut.set_ap(Ena=True, pu=1)
                self.c_env.sleep(timedelta(seconds=self.c_eut.olrt.lap))

                def y_of_fw(x):
                    if self.c_eut.Prated_prime < 0:
                        ymin_pu = -1
                    else:
                        ymin_pu = 0
                    ymax_pu = 1
                    fw_val = dflt_fwchar.y_of_x(x, ymin_pu, aplim_pu, ymax_pu) * self.c_eut.Prated
                    return fw_val

                def y_of_vw(x):
                    vw_val = dflt_vwcrv.y_of_x(x) * self.c_eut.Prated
                    return min(vw_val, aplim_pu * self.c_eut.Prated)

                lst_tup_steps = [
                    # step label, perturbation, y_ss_target, olrt
                    ('c', lambda: self.c_eut.set_lap(Ena=True, pu=aplim_pu), aplim_pu * self.c_eut.Prated, timedelta(seconds=30)),
                    ('d1', lambda: self.c_env.ac_config(freq=59, rocof=self.c_eut.rocof()), y_of_fw(59),
                     timedelta(seconds=dflt_fwchar.tr)),
                    ('d2', lambda: self.c_env.ac_config(freq=60, rocof=self.c_eut.rocof()), y_of_fw(60),
                     timedelta(seconds=dflt_fwchar.tr)),
                    ('e1', lambda: self.c_env.ac_config(freq=61, rocof=self.c_eut.rocof()), y_of_fw(61),
                     timedelta(seconds=dflt_fwchar.tr)),
                    ('e2', lambda: self.c_env.ac_config(freq=60, rocof=self.c_eut.rocof()), y_of_fw(60),
                     timedelta(seconds=dflt_fwchar.tr)),
                    ('f1', lambda: self.c_env.ac_config(Vac=1.08 * self.c_eut.VN), y_of_vw(1.08), timedelta(seconds=dflt_vwcrv.Tr)),
                    ('f2', lambda: self.c_env.ac_config(Vac=self.c_eut.VN), y_of_vw(1.0), timedelta(seconds=dflt_vwcrv.Tr))
                ]
                for tup in lst_tup_steps:
                    dct_label = {
                        'proc': 'lap',
                        'iter': i,
                        'aplim_pu': aplim_pu,
                        'step': tup[0],
                    }
                    self.lap_validation(dct_label, *tup[1:])

    def lap_validation(self, dct_label, perturbation, y_ss_target, olrt: timedelta):
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
        yMRA = self.c_eut.mra.static.P
        df_meas = self.meas_perturb(perturbation, olrt, 4 * olrt, (yarg,))
        t_init, t_olrt, t_ss0, t_ss1 = self.ts_of_interest(df_meas.index, olrt)

        y_init = df_meas.loc[t_init, yarg]
        y_olrt = df_meas.loc[t_olrt, yarg]
        y_ss = df_meas.loc[t_ss0:, yarg].mean()

        olrt_s = olrt.total_seconds()
        y_of_t = lambda t: self.expapp(olrt_s, t, y_init, y_ss)
        y_olrt_min, y_olrt_max = self.range_4p2(y_of_t, olrt_s, 0, yMRA)
        y_olrt_target = y_of_t(olrt_s)
        olrt_valid = y_olrt <= y_olrt_max


        y_ss_max = y_ss_target + self.mra_scale * yMRA
        ss_valid = y_ss <= y_ss_max

        df_meas['y_ss_target'] = y_ss_target
        df_meas['y_min'] = 0
        df_meas['y_max'] = y_ss_max

        self.c_env.validate(dct_label={
            **dct_label,
            't_init': t_init,
            't_olrt': t_olrt,
            't_ss0': t_ss0,
            't_ss1': t_ss1,

            'y_init': y_init,

            'y_olrt': y_olrt,
            'y_olrt_target': y_olrt_target,
            'y_olrt_max': y_olrt_max,

            'y_ss': y_ss,
            'y_ss_target': y_ss_target,
            'y_ss_max': y_ss_max,

            'olrt_valid': olrt_valid,
            'ss_valid': ss_valid,
            'data': df_meas
        })
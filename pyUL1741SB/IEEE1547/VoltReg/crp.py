from datetime import timedelta
from pyUL1741SB import Eut, Env

from typing import Callable

class CRP:
    def crp_validate_step(self, env: Env, label: str, perturb: Callable, olrt: timedelta,
                          y_of_x: Callable[[float], float], yMRA, xMRA
                          ):
        raise NotImplementedError("IEEE 1547 crp step validation")

    def crp_proc(self, env: Env, eut: Eut, pre_cbk=None, post_cbk=None):
        """
        """
        env.log(msg="cpf proc against 1547")
        def validate(env: Env, dct_label: dict, perturbation, olrt, y_of_x):
            if pre_cbk is not None:
                pre_cbk(**dct_label)
            slabel = ''.join([f'{k}: {v}; ' for k, v in dct_label.items()])
            self.crp_validate_step(
                env=env,
                label=slabel,
                perturb=perturbation,
                olrt=olrt,
                y_of_x=y_of_x,
                yMRA=eut.mra.static.Q,
                xMRA=eut.mra.static.P,
            )
            if post_cbk is not None:
                post_cbk(**dct_label)
        olrt = timedelta(seconds=10)
        Qsets = [eut.Qrated_inj, eut.Qrated_abs, 0.5 * eut.Qrated_inj, 0.5 * eut.Qrated_abs]
        Vins = [v for v in [eut.Vin_nom, eut.Vin_min, eut.Vin_max] if v is not None]
        Pmin, Prated, multiphase = eut.Pmin, eut.Prated, eut.multiphase
        VL, VN, VH = eut.VL, eut.VN, eut.VH
        av = 1.5 * eut.mra.static.V
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all voltage trip parameters to the widest range of adjustability. Disable all reactive/active power
        control functions.
        c) Set all ac test source parameters to the nominal operating voltage and frequency.
        '''
        '''
        t) Repeat steps d) through s) for additional reactive power settings: [Qmax,inj] Qmax,ab, 0.5Qmax,inj, 0.5Qmax,ab.
        '''
        for Q in Qsets:
            '''
            u) For an EUT with an input voltage range, repeat steps d) through t) for Vin_min and Vin_max
            '''
            def y_of_x(x):
                return Q
            for Vin in Vins:
                '''
                v) Steps d) through s) may be repeated to test additional protocols methods.
                '''
                '''
                d) Adjust the EUT’s active power to Prated. For an EUT with an input voltage range, set the input
                voltage to Vin_nom.
                e) Enable constant var mode and set the EUT reactive power command to Qmax,inj.
                f) Verify constant var mode is reported as active and that the reactive power setting is reported as
                Qmax,inj.
                '''
                eut.active_power(Ena=True, W=Prated)
                env.dc_config(Vin=Vin)
                eut.reactive_power(Ena=True, Q=Q)
                '''
                g) Step the EUT’s active power to 20% of Prated, or Pmin, whichever is less.
                h) Step the EUT’s active power to 5% of Prated, or Pmin, whichever is less.
                i) Step the EUT’s active power to Prated.
                j) Step the ac test source voltage to (VL + av).
                k) Step the ac test source voltage to (VH − av).
                l) Step the ac test source voltage to (VL + av).
                '''
                dct_steps = {
                    'g': lambda: eut.active_power(Ena=True, W=min(0.2*Prated, Pmin)),
                    'h': lambda: eut.active_power(Ena=True, W=min(0.05*Prated, Pmin)),
                    'i': lambda: eut.active_power(Ena=True, W=Prated),
                    'j': lambda: env.ac_config(Vac=VL + av),
                    'k': lambda: env.ac_config(Vac=VL - av),
                    'l': lambda: env.ac_config(Vac=VL + av),
                }
                for k, perturbation in dct_steps.items():
                    validate(
                        env=env,
                        dct_label={'Qset': f'{Q:.2f}', 'Vin': f'{Vin:.2f}', 'Step': f'{k}'},
                        perturbation=perturbation,
                        olrt=olrt,
                        y_of_x=y_of_x,
                    )
                if multiphase:
                    raise NotImplementedError
                    '''
                    m) For multiphase units, step the ac test source voltage to VN.
                    n) For multiphase units, step the ac test source voltage to Case A from Table 24.
                    o) For multiphase units, step the ac test source voltage to VN.
                    p) For multiphase units, step the ac test source voltage to Case B from Table 24.
                    q) For multiphase units, step the ac test source voltage to VN.
                    '''
                '''
                r) Disable constant reactive power mode. Reactive power should return to zero.
                s) Verify all reactive/active power control functions are disabled.
                '''
                validate(
                    env=env,
                    dct_label={'Qset': f'{Q:.2f}', 'Vin': f'{Vin:.2f}', 'Step': f'r'},
                    perturbation=lambda: eut.reactive_power(Ena=False),
                    olrt=olrt,
                    y_of_x=y_of_x,
                )
                vars_ctrl = eut.reactive_power()['Ena']
                watts_ctrl = eut.active_power()['Ena']
                env.log(msg=f"cpf Qset: {Q}, Vin: {Vin}, Step: s; vars_ctrl_en: {vars_ctrl}, watts_ctrl_en: {watts_ctrl}")

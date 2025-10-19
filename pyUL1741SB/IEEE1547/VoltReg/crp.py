from datetime import timedelta
from pyUL1741SB import Eut, Env

from typing import Callable

class CRP:
    def crp_step_validate(self, env: Env, eut: Eut, dct_label: dict, perturb: Callable, olrt: timedelta,
                          y_of_x: Callable[[float], float]
                          ):
        raise NotImplementedError("IEEE 1547 crp step validation")

    def crp_proc(self, env: Env, eut: Eut):
        """
        """
        env.log(msg="cpf proc against 1547")
        olrt = timedelta(seconds=eut.olrt.crp)
        Qpusets = [
            1 * eut.Qrated_inj / eut.Srated, -1 * eut.Qrated_abs / eut.Srated,
            0.5 * eut.Qrated_inj / eut.Srated, -0.5 * eut.Qrated_abs / eut.Srated
        ]
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
        eut.set_cpf(Ena=False)
        eut.set_crp(Ena=False)
        eut.set_wv(Ena=False)
        eut.set_vv(Ena=False)
        eut.set_vw(Ena=False)
        eut.set_lap(Ena=False, pu=1)
        '''
        t) Repeat steps d) through s) for additional reactive power settings: [Qmax,inj] Qmax,ab, 0.5Qmax,inj, 0.5Qmax,ab.
        '''
        for Qpu in Qpusets:
            '''
            u) For an EUT with an input voltage range, repeat steps d) through t) for Vin_min and Vin_max
            '''
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
                eut.set_ap(Ena=True, pu=1)
                eut.dc_config(Vdc=Vin)
                eut.set_crp(Ena=True, pu=Qpu)
                '''
                g) Step the EUT’s active power to 20% of Prated, or Pmin, whichever is less.
                h) Step the EUT’s active power to 5% of Prated, or Pmin, whichever is less.
                i) Step the EUT’s active power to Prated.
                j) Step the ac test source voltage to (VL + av).
                k) Step the ac test source voltage to (VH − av).
                l) Step the ac test source voltage to (VL + av).
                '''
                dct_steps = {
                    'g': lambda: eut.set_ap(Ena=True, pu=max(0.2, Pmin / Prated)),
                    'h': lambda: eut.set_ap(Ena=True, pu=max(0.05, Pmin / Prated)),
                    'i': lambda: eut.set_ap(Ena=True, pu=1),
                    'j': lambda: env.ac_config(Vac=VL + av),
                    'k': lambda: env.ac_config(Vac=VH - av),
                    'l': lambda: env.ac_config(Vac=VL + av),
                }
                for k, perturbation in dct_steps.items():
                    self.crp_step_validate(
                        env=env,
                        eut=eut,
                        dct_label={'proc': 'crp', 'Qset': f'{Qpu:.2f}', 'Vin': f'{Vin:.2f}', 'Step': f'{k}'},
                        perturb=perturbation,
                        olrt=olrt,
                        y_of_x=lambda x: Qpu * eut.Qrated_inj if Qpu > 0 else Qpu * eut.Qrated_abs,
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
                self.crp_step_validate(
                    env=env,
                    eut=eut,
                    dct_label={'proc': 'crp', 'Qset': f'{0:.2f}', 'Vin': f'{Vin:.2f}', 'Step': f'r'},
                    perturb=lambda: eut.set_crp(Ena=False),
                    olrt=olrt,
                    y_of_x=lambda x: 0,
                )

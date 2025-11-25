from datetime import timedelta
from pyUL1741SB import Eut, Env

from typing import Callable
from pyUL1741SB import viz
from pyUL1741SB.IEEE1547.VoltReg import VoltReg
import pandas as pd

proc = 'crp'
class CRP(VoltReg):
    def crp(self, outdir, final):
        self.validator = viz.Validator(proc)
        try:
            self.crp_proc()
            final()
        finally:
            self.validator.draw_new(outdir)

    def crp_proc(self):
        """
        """
        self.c_env.log(msg="cpf proc against 1547")
        olrt = timedelta(seconds=self.c_eut.olrt.crp)
        Qpusets = [
            1 * self.c_eut.Qrated_inj / self.c_eut.Srated, -1 * self.c_eut.Qrated_abs / self.c_eut.Srated,
            0.5 * self.c_eut.Qrated_inj / self.c_eut.Srated, -0.5 * self.c_eut.Qrated_abs / self.c_eut.Srated
        ]
        Vins = [v for v in [self.c_eut.Vin_nom, self.c_eut.Vin_min, self.c_eut.Vin_max] if v is not None]
        Pmin, Prated, multiphase = self.c_eut.Pmin, self.c_eut.Prated, self.c_eut.multiphase
        VL, VN, VH = self.c_eut.VL, self.c_eut.VN, self.c_eut.VH
        av = self.mra_scale * self.c_eut.mra.static.V
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all voltage trip parameters to the widest range of adjustability. Disable all reactive/active power
        control functions.
        c) Set all ac test source parameters to the nominal operating voltage and frequency.
        '''
        self.conn_to_grid()
        self.c_eut.set_cpf(Ena=False)
        self.c_eut.set_crp(Ena=False)
        self.c_eut.set_wv(Ena=False)
        self.c_eut.set_vv(Ena=False)
        self.c_eut.set_vw(Ena=False)
        self.c_eut.set_lap(Ena=False, pu=1)
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
                self.c_eut.set_ap(Ena=True, pu=1)
                self.c_eut.dc_config(Vdc=Vin)
                self.c_eut.set_crp(Ena=True, pu=Qpu)
                '''
                g) Step the EUT’s active power to 20% of Prated, or Pmin, whichever is less.
                h) Step the EUT’s active power to 5% of Prated, or Pmin, whichever is less.
                i) Step the EUT’s active power to Prated.
                j) Step the ac test source voltage to (VL + av).
                k) Step the ac test source voltage to (VH − av).
                l) Step the ac test source voltage to (VL + av).
                '''
                dct_steps = {
                    'g': lambda: self.c_eut.set_ap(Ena=True, pu=max(0.2, Pmin / Prated)),
                    'h': lambda: self.c_eut.set_ap(Ena=True, pu=max(0.05, Pmin / Prated)),
                    'i': lambda: self.c_eut.set_ap(Ena=True, pu=1),
                    'j': lambda: self.c_env.ac_config(Vac=VL + av),
                    'k': lambda: self.c_env.ac_config(Vac=VH - av),
                    'l': lambda: self.c_env.ac_config(Vac=VL + av),
                }
                for k, perturbation in dct_steps.items():
                    self.crp_step_validate(
                        dct_label={'proc': proc, 'Qset': f'{Qpu:.2f}', 'Vin': f'{Vin:.2f}', 'Step': f'{k}'},
                        perturb=perturbation,
                        olrt=olrt,
                        y_of_x=lambda x: Qpu * self.c_eut.Qrated_inj if Qpu > 0 else Qpu * self.c_eut.Qrated_abs,
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
                    dct_label={'proc': proc, 'Qset': f'{0:.2f}', 'Vin': f'{Vin:.2f}', 'Step': f'r'},
                    perturb=lambda: self.c_eut.set_crp(Ena=False),
                    olrt=olrt,
                    y_of_x=lambda x: 0,
                )


    def crp_step_validate(self, dct_label: dict, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
        self.cpf_crp_meas_validate(dct_label, perturb, olrt, y_of_x)


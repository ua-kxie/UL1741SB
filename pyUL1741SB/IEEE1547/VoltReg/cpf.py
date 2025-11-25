from datetime import timedelta

from typing import Callable
import math
from pyUL1741SB import viz

from pyUL1741SB.IEEE1547.VoltReg import VoltReg

proc = 'cpf'


class CPF(VoltReg):
    def cpf(self, outdir, final):
        self.validator = viz.Validator(proc)
        try:
            self.cpf_proc()
        finally:
            final()
            self.validator.draw_new(outdir)

    def cpf_proc(self):
        """
        """
        appu_max = 1  # should be 1
        self.c_env.log(msg="cpf proc against 1547")
        olrt = timedelta(seconds=self.c_eut.olrt.cpf)
        VH, VN, VL, Pmin, Prated, multiphase = self.c_eut.VH, self.c_eut.VN, self.c_eut.VL, self.c_eut.Pmin, self.c_eut.Prated, self.c_eut.multiphase
        av = self.mra_scale * self.c_eut.mra.static.V
        '''
        5.14.3.2 
        PFmin,inj: Minimum injected power factor, 0.90 for both Category A and B equipment
        PFmin,ab: Minimum absorbed power factor, 0.97 for Category A, 0.90 for Category B
        PFmid,inj: A power factor setting chosen to be less than 1 and greater than PFmin,inj
        PFmid,ab: A power factor setting chosen to be less than 1 and greater than PFmin,ab
        '''
        if self.c_eut.Cat == self.c_eut.Category.A:
            # PFmin,inj, PFmin,ab, PFmid,inj, PFmid,ab
            targetPFs = [0.9, 0.97, 0.95, 0.98]
        elif self.c_eut.Cat == self.c_eut.Category.B:
            targetPFs = [0.9, 0.9, 0.95, 0.95]
        else:
            raise TypeError(f'unknown eut category {self.c_eut.Cat}')
        targetPFs = list(zip(targetPFs, ['inj', 'abs', 'inj', 'abs']))
        '''
        5.14.2:
        The term av is used throughout these tests and is defined as 150% of the minimum required measurement accuracy
        (MRA) for voltage, as specified in Table 3 of IEEE Std 1547-2018 for steady-state conditions. 

        5.14.3.2:
        Every time a parameter is stepped or ramped, measure and record the time domain current and voltage
        response for at least 4 times the maximum expected response time after the stimulus, and measure or
        derive, active power, apparent power, reactive power, and power factor. 
        '''
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
        self.c_eut.set_ap(Ena=False, pu=appu_max)
        """
        t) For an EUT with an input voltage range, repeat steps d) through p) for [Vin_nom,] Vin_min and Vin_max.		
        """
        Vins = [v for v in [self.c_eut.Vin_nom, self.c_eut.Vin_min,
                            self.c_eut.Vin_max] if v is not None]
        for Vin in Vins:
            self.c_eut.dc_config(Vdc=Vin)
            """
            s) Repeat steps d) through p) for additional power factor settings: [PFmin,inj,] PFmin,ab, PFmid,inj, PFmid,ab.		
            """
            for PF, Exct in targetPFs:
                def y_of_x(x):
                    q = x * math.sqrt(1 / PF ** 2 - 1)
                    if Exct == 'inj':
                        return q
                    elif Exct == 'abs':
                        return -q
                    else:
                        raise ValueError(f'unknown Ext {Exct}')
                '''
                (c) - set to nominal and wait for steady state
                '''
                self.c_env.ac_config(Vac=VN)
                '''
                d) Adjust the EUT’s available active power to Prated. For an EUT with an input voltage range, set the
                input voltage to Vin_nom. The EUT may limit active power throughout the test to meet reactive
                power requirements.
                '''
                self.c_eut.set_ap(Ena=True, pu=appu_max)
                '''
                e) Enable constant power factor mode and set the EUT power factor to [tagetPF].
                '''
                self.c_eut.set_cpf(Ena=True, PF=PF, Exct=Exct)
                '''
                f) Wait for steady state to be reached.		
                '''
                self.c_env.sleep(2 * olrt)
                '''
                g) Step the EUT’s active power to Pmin.		
                h) Step the EUT’s available active power to Prated. - interpreted as stepping the EUT's active power
                i) Step the ac test source voltage to (VL + av)		
                j) Step the ac test source voltage to (VH - av).		
                k) Step the ac test source voltage to (VL + av).		
                '''
                dct_steps = {
                    'g': lambda: self.c_eut.set_ap(Ena=True, pu=Pmin / Prated),
                    'h': lambda: self.c_eut.set_ap(Ena=True, pu=appu_max),
                    'i': lambda: self.c_env.ac_config(Vac=VL + av),
                    'j': lambda: self.c_env.ac_config(Vac=VH - av),
                    'k': lambda: self.c_env.ac_config(Vac=VL + av),
                }
                for k, perturbation in dct_steps.items():
                    self.cpf_step_validate(
                        dct_label={'proc': proc, 'Vin': f'{Vin:.2f}',
                                   'PF': f'{PF:.2f}{Exct}', 'Step': f'{k}'},
                        perturb=perturbation,
                        olrt=olrt,
                        y_of_x=y_of_x,
                    )
                if multiphase:
                    '''
                    l) For multiphase units, step the ac test source voltage to VN.		
                    m) For multiphase units, step the ac test source voltage to Case A from Table 24.		
                    n) For multiphase units, step the ac test source voltage to VN.		
                    o) For multiphase units, step the ac test source voltage to Case B from Table 24.		
                    p) For multiphase units, step the ac test source voltage to VN		
                    '''
                    '''
                                                            Table 24 - Imbalanced Voltage Test Cases
                            +-----------------------------------------------------+-----------------------------------------------+
                            | Phase A (p.u.)  | Phase B (p.u.)  | Phase C (p.u.)  | In order to keep V0 magnitude                 |
                            |                 |                 |                 | and angle at 0. These parameter can be used.  |
                            +-----------------+-----------------+-----------------+-----------------------------------------------+
                            |       Mag       |       Mag       |       Mag       | Mag   | Ang  | Mag   | Ang   | Mag   | Ang    |
                    +-------+-----------------+-----------------+-----------------+-------+------+-------+-------+-------+--------+
                    |Case A |     >= 1.07     |     <= 0.91     |     <= 0.91     | 1.08  | 0.0  | 0.91  |-126.59| 0.91  | 126.59 |
                    +-------+-----------------+-----------------+-----------------+-------+------+-------+-------+-------+--------+
                    |Case B |     <= 0.91     |     >= 1.07     |     >= 1.07     | 0.9   | 0.0  | 1.08  |-114.5 | 1.08  | 114.5  |
                    +-------+-----------------+-----------------+-----------------+-------+------+-------+-------+-------+--------+
                    '''
                    raise NotImplementedError
                    for grid_config in [
                        lambda: self.c_env.ac_config(Vac=VN),
                        lambda: self.c_env.ac_config_asym(mag=[1.08 * VN, 0.9 * VN, 0.9 * VN],
                                                          pha=[0, -120, 120]),
                        lambda: self.c_env.ac_config(Vac=VN),
                        lambda: self.c_env.ac_config_asym(mag=[0.9 * VN, 1.08 * VN, 1.08 * VN],
                                                          pha=[0, -120, 120]),
                        lambda: self.c_env.ac_config(Vac=VN),
                    ]:
                        grid_config()
                        # do evaluation
                '''
                q) Disable constant power factor mode. Power factor should return to unity.
                r) Verify all reactive/active power control functions are disabled.
                '''
                self.cpf_step_validate(
                    dct_label={'proc': proc, 'Vin': f'{Vin:.2f}',
                               'PF': f'off', 'Step': f'q'},
                    perturb=lambda: self.c_eut.set_cpf(Ena=False),
                    olrt=olrt,
                    y_of_x=lambda x: 0,
                )

    def cpf_step_validate(self, dct_label: dict, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float]):
        self.cpf_crp_meas_validate(dct_label, perturb, olrt, y_of_x)

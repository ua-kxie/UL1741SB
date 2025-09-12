from datetime import timedelta
from pyUL1741SB import Eut, Env

from typing import Callable
import math

class CPF:
    def cpf_validate_step(self, env: Env, label: str, perturb: Callable, olrt: timedelta,
                          y_of_x: Callable[[float], float], yMRA, xMRA
                          ):
        raise NotImplementedError("IEEE 1547 cpf step validation")

    def cpf_proc(self, env: Env, eut: Eut, pre_cbk=None, post_cbk=None):
        """
        """
        def validate(env: Env, dct_label: dict, perturbation, olrt, y_of_x):
            if pre_cbk is not None:
                pre_cbk(**dct_label)
            slabel = ''.join([f'{k}: {v}; ' for k, v in dct_label.items()])
            self.cpf_validate_step(
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
        env.log(msg="cpf proc against 1547")
        olrt = timedelta(seconds=10)
        VH, VN, VL, Pmin, Prated, multiphase = eut.VH, eut.VN, eut.VL, eut.Pmin, eut.Prated, eut.multiphase
        av = 1.5 * eut.mra.static.V
        '''
        5.14.3.2 
        PFmin,inj: Minimum injected power factor, 0.90 for both Category A and B equipment
        PFmin,ab: Minimum absorbed power factor, 0.97 for Category A, 0.90 for Category B
        PFmid,inj: A power factor setting chosen to be less than 1 and greater than PFmin,inj
        PFmid,ab: Apower factor setting chosen to be less than 1 and greater than PFmin,ab
        '''
        if eut.Cat == Eut.Category.A:
            targetPFs = [0.9, -0.97, 0.95, -0.98]  # PFmin,inj, PFmin,ab, PFmid,inj, PFmid,ab
        elif eut.Cat == Eut.Category.B:
            targetPFs = [0.9, -0.9, 0.95, -0.95]
        else:
            raise TypeError(f'unknown category {eut.Cat}')
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
        eut.reactive_power(Ena=False)
        eut.active_power(Ena=False)
        """
        t) For an EUT with an input voltage range, repeat steps d) through p) for [Vin_nom,] Vin_min and Vin_max.		
        """
        Vins = [v for v in [eut.Vin_nom, eut.Vin_min, eut.Vin_max] if v is not None]
        for Vin in Vins:
            env.dc_config(Vin=Vin)
            """
            s) Repeat steps d) through p) for additional power factor settings: [PFmin,inj,] PFmin,ab, PFmid,inj, PFmid,ab.		
            """
            for targetPF in targetPFs:
                def y_of_x(x):
                    q = x * math.sqrt(1 / targetPF ** 2 - 1)
                    if targetPF > 0:
                        return q
                    else:
                        return -q
                '''
                (c) - set to nominal and wait for steady state
                '''
                env.ac_config(Vac=VN)
                '''
                d) Adjust the EUT’s available active power to Prated. For an EUT with an input voltage range, set the
                input voltage to Vin_nom. The EUT may limit active power throughout the test to meet reactive
                power requirements.
                '''
                env.dc_config(power=Prated)
                '''
                e) Enable constant power factor mode and set the EUT power factor to [tagetPF].
                '''
                eut.fixed_pf(Ena=True, PF=targetPF)
                '''
                f) Wait for steady state to be reached.		
                '''
                env.sleep(2 * olrt)
                '''
                g) Step the EUT’s active power to Pmin.		
                h) Step the EUT’s available active power to Prated. - interpreted as stepping the EUT's active power
                i) Step the ac test source voltage to (VL + av)		
                j) Step the ac test source voltage to (VH - av).		
                k) Step the ac test source voltage to (VL + av).		
                '''
                dct_steps = {
                    'g': lambda: eut.active_power(Ena=True, WMaxPct=100 * Pmin / Prated),
                    'h': lambda: eut.active_power(Ena=True, WMaxPct=100 * Prated / Prated),
                    'i': lambda: env.ac_config(Vac=VL + av),
                    'j': lambda: env.ac_config(Vac=VH - av),
                    'k': lambda: env.ac_config(Vac=VL + av),
                }
                for k, perturbation in dct_steps.items():
                    validate(
                        env=env,
                        dct_label={'Vin': f'{Vin:.2f}', 'PF': f'{targetPF:.2f}', 'Step': f'{k}'},
                        perturbation=perturbation,
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
                        lambda: env.ac_config(Vac=VN),
                        lambda: env.ac_config_asym(mag=[1.08 * VN, 0.9 * VN, 0.9 * VN],
                                                    pha=[0, -120, 120]),
                        lambda: env.ac_config(Vac=VN),
                        lambda: env.ac_config_asym(mag=[0.9 * VN, 1.08 * VN, 1.08 * VN],
                                                    pha=[0, -120, 120]),
                        lambda: env.ac_config(Vac=VN),
                    ]:
                        grid_config()
                        # do evaluation
                '''
                q) Disable constant power factor mode. Power factor should return to unity.
                r) Verify all reactive/active power control functions are disabled.
                '''
                targetPF = 1
                validate(
                    env=env,
                    dct_label={'Vin': f'{Vin:.2f}', 'PF': f'{targetPF:.2f}', 'Step': f'q'},
                    perturbation=lambda: eut.fixed_pf(Ena=False),
                    olrt=olrt,
                    y_of_x=y_of_x,
                )
                vars_ctrl = eut.reactive_power()['Ena']
                watts_ctrl = eut.active_power()['Ena']
                env.log(msg=f'cpf Vin: {Vin}, PF: {targetPF}, vars_ctrl_en: {vars_ctrl}, watts_ctrl_en: {watts_ctrl}')
        '''
        s) Repeat steps d) through p) for additional power factor settings: PFmin,ab, PFmid,inj, PFmid,ab.
        t) For an EUT with an input voltage range, repeat steps d) through p) for Vin_min and Vin_max.
        '''
        '''
        u) Steps d) through f) may be repeated to test additional communication protocols. 
        '''
        # do procedure
        # make meas after each step
        # validate
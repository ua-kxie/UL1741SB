from datetime import timedelta
from pyUL1741SB.eut import Eut
from pyUL1741SB.env import Env
from typing import Callable
import math

class CPF:
    def cpf_validate_step(self, env: Env, label: str, perturb: Callable, olrt: timedelta, y_of_x: Callable[[float], float], yMRA, xMRA):
        raise NotImplementedError("IEEE 1547 cpf step validation")

    def cpf_proc(self, env: Env, eut: Eut):
        """
        """
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
                        return -q
                    else:
                        return q
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
                '''
                self.cpf_validate_step(
                    env=env,
                    label=f"cpf Vin: {Vin}, PF: {targetPF}, Power: {Pmin}, Step: g",
                    perturb=lambda: eut.active_power(Ena=True, WMaxPct=100 * Pmin / Prated),
                    olrt=olrt,
                    y_of_x=y_of_x,
                    yMRA=eut.mra.static.Q,
                    xMRA=eut.mra.static.P,
                )
                '''
                h) Step the EUT’s available active power to Prated. - interpreted as stepping the EUT's active power
                '''
                self.cpf_validate_step(
                    env=env,
                    label=f"cpf Vin: {Vin}, PF: {targetPF}, Power: {Prated}, Step: h",
                    perturb=lambda: eut.active_power(Ena=True, WMaxPct=100 * Prated / Prated),
                    olrt=olrt,
                    y_of_x=y_of_x,
                    yMRA=eut.mra.static.Q,
                    xMRA=eut.mra.static.P,
                )
                '''
                i) Step the ac test source voltage to (VL + av)		
                j) Step the ac test source voltage to (VH - av).		
                k) Step the ac test source voltage to (VL + av).		
                '''
                for k, Vac in {'i': VL + av, 'j': VH - av, 'k': VL + av}.items():
                    self.cpf_validate_step(
                        env=env,
                        label=f"cpf Vin: {Vin}, PF: {targetPF}, Vac: {Vac}, Step: {k}",
                        perturb=lambda: env.ac_config(Vac=Vac),
                        olrt=olrt,
                        y_of_x=y_of_x,
                        yMRA=eut.mra.static.Q,
                        xMRA=eut.mra.static.P,
                    )
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
                if multiphase:
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
                self.cpf_validate_step(
                    env=env,
                    label=f"cpf Vin: {Vin}, PF: {targetPF}, Vac: {Vac}, step: q",
                    perturb=lambda: eut.fixed_pf(Ena=False),
                    olrt=olrt,
                    y_of_x=y_of_x,
                    yMRA=eut.mra.static.Q,
                    xMRA=eut.mra.static.P,
                )
                vars_ctrl = eut.reactive_power()['Ena']
                watts_ctrl = eut.active_power()['Ena']
                env.log(msg=f'cpf Vin: {Vin}, PF: {targetPF}, Vac: {Vac} vars_ctrl_en: {vars_ctrl}, watts_ctrl_en: {watts_ctrl}')
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
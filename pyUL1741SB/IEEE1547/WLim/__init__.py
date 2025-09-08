from pyUL1741SB import Eut, Env


class WLim:
    def limw_proc(self, env: Env, eut: Eut):
        """"""
        '''
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        Apply the default settings from IEEE Std 1547 for voltage-active power mode. Apply the default
        settings from frequency-droop response in IEEE Std 1547 for the abnormal operating performance
        category of the DER. Enable voltage-active power mode.
        '''
        '''
        h) Repeat steps b) through g) twice for a total of three repetitions.
        '''
        for _ in range(3):
            '''
            g) Repeat steps b) through f) using active power limits of [66%] 33% and zero.
            '''
            for wlim_pct in [0.66, 0.33, 0]:
                '''
                b) Establish nominal operating conditions as specified by the manufacturer at the terminals of the
                EUT. Make available sufficient input power for the EUT to reach its rated active power. Allow (or
                command) the EUT to reach steady-state output at its rated active power. Begin recording EUT
                active power.
                '''
                eut.active_power(wlim_pct=100)
                # wait for ss
                '''
                In step c), the EUT steady-state active power shall be reduced to the commanded percentage of its rated
                power plus 1.5 × (MRA of active power) or less within a time that complies with 4.6.2 of IEEE Std 1547-
                2018.
                '''
                '''
                c) Apply an active power limit to the EUT of 66% of its rated active power. Wait until the EUT active
                power reaches a new steady state.
                '''
                eut.active_power(wlim_pct=wlim_pct)
                # wait for ss,
                '''
                In steps d) and e), the EUT steady-state active power shall be modulated in accordance with the equations
                in Table 23 of IEEE Std 1547-2018 within the tolerance as defined in 4.2 of this standard. 85 The response
                time shall comply with 4.6.2 of IEEE Std 1547-2018.
                '''
                '''
                d) Reduce the frequency of the ac test source to 59 Hz and hold until EUT active power reaches a new
                steady state. Return ac test source frequency to nominal and hold until EUT active power reaches
                steady state.
                '''
                env.ac_config(freq=59)
                # wait for ss, eval subject to freq droop
                env.ac_config(freq=eut.fN)
                # wait for ss, eval subject to freq droop
                '''
                e) Increase the frequency of the ac test source to 61 Hz and hold until EUT active power reaches
                steady state. Return ac test source frequency to nominal and hold until EUT active power reaches
                steady state.
                '''
                env.ac_config(freq=61)
                # wait for ss, eval subject to freq droop
                env.ac_config(freq=eut.fN)
                # wait for ss, eval subject to freq droop
                '''
                In step f), the EUT steady-state active power shall be modulated in accordance with the applied volt-watt
                curve within the tolerance as defined in 4.2 of this standard.
                '''
                '''
                f) Increase the voltage of the ac test source to 1.08 times nominal and hold until EUT active power
                reaches steady state. Return ac test source voltage to nominal.
                '''
                env.ac_config(freq=eut.fN * 1.08)
                # wait for ss
                env.ac_config(freq=eut.fN)
                raise NotImplementedError
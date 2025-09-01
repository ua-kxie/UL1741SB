def crp():
    """
    """
    '''
    a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
    b) Set all voltage trip parameters to the widest range of adjustability. Disable all reactive/active power
    control functions.
    c) Set all ac test source parameters to the nominal operating voltage and frequency.
    '''
    '''
    t) Repeat steps d) through s) for additional reactive power settings: Qmax,ab, 0.5Qmax,inj, 0.5Qmax,ab.
    '''
    for Q in [Qmax_inj, Qmax_ab, 0.5 * Qmax_inj, 0.5 * Qmax_ab]:
        '''
        u) For an EUT with an input voltage range, repeat steps d) through t) for Vin_min and Vin_max
        '''
        for Vin in [Vin_nom, Vin_min, Vin_max]:
            '''
            v) Steps d) through s) may be repeated to test additional protocols methods.
            '''
            '''
            d) Adjust the EUT’s active power to Prated. For an EUT with an input voltage range, set the input
            voltage to Vin_nom.
            e) Enable constant var mode and set the EUT reactive power command to Qmax,inj.
            f) Verify constant var mode is reported as active and that the reactive power setting is reported as
            Qmax,inj.
            g) Step the EUT’s active power to 20% of Prated, or Pmin, whichever is less.
            h) Step the EUT’s active power to 5% of Prated, or Pmin, whichever is less.
            i) Step the EUT’s active power to Prated.
            j) Step the ac test source voltage to (VL + av).
            k) Step the ac test source voltage to (VH − av).
            l) Step the ac test source voltage to (VL + av).
            '''
            if multiphase:
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
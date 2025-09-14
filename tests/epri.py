import opender as der
import pandas as pd
import datetime as dt
from pyUL1741SB.UL1741SB import UL1741SB
from pyUL1741SB import Eut, Env, VoltShallTripTable, FreqShallTripTable

std = UL1741SB()

class EpriEut(Eut):
    def __init__(self, **kwargs):
        self.der = der.DER()
        self.der.der_file.NP_PHASE = "SINGLE"
        self.der.update_der_input(f=60)
        super().__init__(
            Cat=Eut.Category.B,
            aopCat=Eut.AOPCat.III,
            voltshalltrip_tbl=VoltShallTripTable.AOPCatIII(240),
            freqshalltrip_tbl=FreqShallTripTable.MaxRange(),
            vfo=False,
            rocof=3,
            Prated=self.der.der_file.NP_P_MAX,
            Prated_prime=0,
            Srated=self.der.der_file.NP_P_MAX,
            Vin_nom=self.der.der_file.NP_V_DC,
            Vin_min=None,
            Vin_max=None,
            VN=self.der.der_file.NP_AC_V_NOM,
            VL=self.der.der_file.NP_AC_V_NOM * 0.9,
            VH=self.der.der_file.NP_AC_V_NOM * 1.1,
            Pmin=0,
            Pmin_prime=0,
            Qrated_abs=self.der.der_file.NP_Q_MAX_ABS,
            Qrated_inj=-self.der.der_file.NP_Q_MAX_INJ,
            Comms=[Eut.Comms.SUNS],
            multiphase=False,
            fL=59.0,  # minimum frequency in continuous operating region (Hz)
            fN=60.0,  # nominal frequency (Hz)
            fH=61.0,  # maximum frequency in continuous operating region (Hz)
            delta_Psmall=0.1,  # small power change threshold (p.u.)
            delta_Plarge=0.5  # large power change threshold (p.u.)
        )
    # eut.fixed_pf(Ena=True, PF=targetPF)
    def fixed_pf(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'Ena':
                self.der.der_file.CONST_PF_MODE_ENABLE = v
            elif k == 'PF':
                if v < 0:
                    self.der.der_file.CONST_PF_EXCITATION = 'ABS'
                    self.der.der_file.CONST_PF = -v
                else:
                    self.der.der_file.CONST_PF_EXCITATION = 'INJ'
                    self.der.der_file.CONST_PF = v
            else:
                raise NotImplementedError

eut = EpriEut()


class EpriEnv(Env):
    def __init__(self, eut: EpriEut):
        super().__init__()
        self.time = dt.datetime.fromtimestamp(0)
        self.eut = eut

    def elapsed_since(self, interval: dt.timedelta, start: dt.datetime) -> bool:
        # return datetime.now() - start >= interval - what this should do during actual validation
        return self.time - start >= interval

    def time_now(self):
        return self.time

    def sleep(self, td: dt.timedelta):
        self.time += td
        der.DER.t_s = td.total_seconds()
        self.eut.der.run()

    def meas(self, *args):
        data = {}
        data['P'] = self.eut.der.der_output.p_out_w
        data['Q'] = self.eut.der.der_output.q_out_var
        data['V'] = self.eut.der.der_output.v_out_mag_v
        data1 = {}
        for arg in args:
            data1[arg] = data[arg]

        # Create DataFrame with time as the index
        df = pd.DataFrame(data1, index=[self.time])
        return df

    def meas_single(self, *args) -> pd.DataFrame:
        df = self.meas(*args)
        self.time += dt.timedelta(seconds=0.01)
        return df

    def meas_for(self, dur: dt.timedelta, tres: dt.timedelta, *args) -> pd.DataFrame:
        start = self.time
        dfs = []
        der.DER.t_s = tres.total_seconds()

        while self.time - start < dur:
            dfs.append(self.meas(*args))
            self.eut.der.run()
            self.time += tres

        df = pd.concat(dfs)
        return df

    def ac_config(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'Vac':
                self.eut.der.update_der_input(v=v)
            else:
                raise NotImplementedError

    def ac_config_asym(self, **kwargs):
        raise NotImplementedError

    def log(self, **kwargs):
        print(kwargs['msg'])

    def dc_config(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'power':
                self.eut.der.update_der_input(p_dc_w=v)
            elif k =='Vin':
                pass
            else:
                raise NotImplementedError

    def validate(self, is_valid: bool, msg: str):
        if is_valid:
            # steady state value is good
            passfail = 'passed'
        else:
            passfail = 'failed'
        print(passfail + ' ' + msg)
env = EpriEnv(eut)

std.cpf_proc(env=env, eut=eut)
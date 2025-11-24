import pandas as pd
import datetime as dt
from pyUL1741SB import Eut, Env
from EpriEut import EpriEut
import opender as der

DTS = 0.1

class EpriEnv(Env):
    def __init__(self, eut: EpriEut):
        super().__init__()
        self.time = dt.datetime.fromtimestamp(0, tz=dt.timezone.utc)
        self.eut = eut
        self.results = {}  # dct of dataframes

    def elapsed_since(self, interval: dt.timedelta, start: dt.datetime) -> bool:
        # return datetime.now() - start >= interval - what this should do during actual validation
        return self.time - start >= interval

    def time_now(self):
        return self.time

    def sleep(self, td: dt.timedelta):
        self.time += td
        der.DER.t_s = td.total_seconds()
        self.eut.der.run()
        der.DER.t_s = DTS

    def meas(self):
        v = self.eut.der.der_input.v_meas_pu * self.eut.der.der_file.NP_AC_V_NOM
        # s = (self.eut.der.der_output.p_out_w**2 + self.eut.der.der_output.q_out_var**2) ** 0.5
        data = {
            'time': self.time,
            'F': self.eut.der.der_input.freq_hz,
            'P': self.eut.der.der_output.p_out_w,
            'Q': self.eut.der.der_output.q_out_var,
            'V': v,
            # 'I': s / v if v != 0 else s
        }
        return data

    def meas_single(self, *args) -> pd.DataFrame:
        dct = self.meas()
        der.DER.t_s = 0.01
        df = pd.DataFrame([dct]).set_index('time').loc[:, [*args]]
        self.time += dt.timedelta(seconds=0.01)
        self.eut.der.run()
        der.DER.t_s = DTS
        return df

    def meas_for(self, dur: dt.timedelta, tres: dt.timedelta, *args) -> pd.DataFrame:
        start = self.time
        dfs = []
        der.DER.t_s = tres.total_seconds()

        while self.time - start < dur:
            dfs.append(self.meas())
            self.eut.der.run()
            self.time += tres
        df = pd.DataFrame(dfs).set_index('time').loc[:, [*args]]
        der.DER.t_s = DTS
        return df

    def log(self, **kwargs):
        print(kwargs['msg'])

    def ac_config(self, **kwargs):
        """"""
        '''
        block until settings are applied (i.e. wait for rocof-limited f change)
        '''
        for k, v in kwargs.items():
            if k == 'Vac':
                self.eut.der.update_der_input(v_pu=v/self.eut.der.der_file.NP_AC_V_NOM)
            elif k =='freq':
                self.eut.der.update_der_input(f=v)
            elif k =='rocof':
                pass
            else:
                raise NotImplementedError(k)

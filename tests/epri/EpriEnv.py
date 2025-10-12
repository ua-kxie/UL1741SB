import pandas as pd
import datetime as dt
from pyUL1741SB import Eut, Env, VoltShallTripTable, FreqShallTripTable
from EpriEut import EpriEut
import opender as der

DTS = 0.1

class EpriEnv(Env):
    def __init__(self, eut: EpriEut):
        super().__init__()
        self.time = dt.datetime.fromtimestamp(0)
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
        data = {
            'time': self.time,
            'F': self.eut.der.der_input.freq_hz,
            'P': self.eut.der.der_output.p_out_w,
            'Q': self.eut.der.der_output.q_out_var,
            'V': self.eut.der.der_input.v_meas_pu * self.eut.der.der_file.NP_AC_V_NOM
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

    def validate(self, dct_label: dict):
        df_row = pd.DataFrame([dct_label])
        proc = dct_label.pop('proc')
        if proc in self.results.keys():
            self.results[proc] = pd.concat([self.results[proc], df_row])
        else:
            self.results[proc] = df_row

    def pre_cbk(self, **kwargs):
        pass

    def post_cbk(self, **kwargs):
        pass

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

    def reset_to_nominal(self):
        """"""
        """
        Called for the following instructions:
        a) Connect the EUT according to the instructions and specifications provided by the manufacturer.
        b) Set all voltage and frequency trip parameters to the widest range of adjustability. Disable all
        reactive/active power control functions.
        """
        self.eut.der.update_der_input(p_dem_pu=1, v_pu=1, f=60)

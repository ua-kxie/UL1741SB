import pandas as pd
import datetime as dt
from pyUL1741SB import Eut, Env
from NimaEut import NimaEut
import opender as der

DTS = 0.1

class NimaEnv(Env):
    def __init__(self, eut: NimaEut):
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
        self.eut.run(td)

    def meas(self):
        data = {
            'time': self.time,
            'F': self.eut.fac,
            'P': self.eut.rslt['p'],
            'Q': self.eut.rslt['q'],
            'V': self.eut.vac,
            # 'I': s / v if v != 0 else s
        }
        return data

    def meas_single(self, *args) -> pd.DataFrame:
        dct = self.meas()
        df = pd.DataFrame([dct]).set_index('time').loc[:, [*args]]
        self.time += dt.timedelta(seconds=0.01)
        self.eut.run(dt.timedelta(seconds=0.01))
        return df

    def meas_for(self, dur: dt.timedelta, tres: dt.timedelta, *args) -> pd.DataFrame:
        start = self.time
        dfs = []
        der.DER.t_s = tres.total_seconds()

        while self.time - start < dur:
            dfs.append(self.meas())
            self.eut.run(tres)
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

    def ac_config(self, **kwargs):
        """"""
        '''
        block until settings are applied (i.e. wait for rocof-limited f change)
        '''
        for k, v in kwargs.items():
            if k == 'Vac':
                self.eut.vac = v
            elif k =='freq':
                self.eut.fac = v
            elif k =='rocof':
                pass
            else:
                raise NotImplementedError(k)

from datetime import timedelta, datetime
import pandas as pd
import numpy as np
import random
Prated = 5e3
class Env:  # step voltage, power, sleep, etc.
    def __init__(self):
        self.time = datetime.now()

    def elapsed_since(self, interval: timedelta, start: datetime) -> bool:
        # return datetime.now() - start >= interval - what this should do during actual validation
        return self.time - start >= interval

    def time_now(self):
        return self.time

    def sleep(self, td: timedelta):
        self.time += td + timedelta(seconds=0.001)  # add a little to simulate extra time taken to run code

    def meas_single(self, *args) -> pd.DataFrame:
        self.time += timedelta(seconds=random.random() * 0.001)

        data = {}
        for arg in args:
            data[arg] = random.random()

        # Create DataFrame with time as the index
        df = pd.DataFrame(data, index=[self.time])
        if 'P' in df.columns:
            df['P'] = df['P'] * Prated  # Assuming Prated is an instance variable
        return df

    def meas_for(self, dur: timedelta, tres: timedelta, *args) -> pd.DataFrame:
        self.time += dur
        self.time += timedelta(seconds=random.random() * 0.001)  # add a little to simulate extra time taken to run code
        # Calculate number of periods based on duration and time resolution
        num_periods = int(dur.total_seconds() / tres.total_seconds())

        # Generate timestamp index starting from current time
        index = pd.date_range(
            start=self.time,
            periods=num_periods,
            freq=pd.Timedelta(tres)
        )

        # Create DataFrame with random data for each specified column
        data = {}
        for column_name in args:
            # Generate random data (you can modify the distribution as needed)
            data[column_name] = np.random.randn(num_periods)

        df = pd.DataFrame(data, index=index)
        if 'P' in df.columns:
            df['P'] = df['P'] * Prated
        return df

    def ac_config(self, **kwargs):
        pass

    def ac_config_asym(self, **kwargs):
        pass

    def log(self, **kwargs):
        print(kwargs['msg'])

    def dc_config(self, **kwargs):
        pass

    def validate(self, dct_label: dict):
        print(''.join([f'{k}: {v}; ' for k, v in dct_label.items()]))

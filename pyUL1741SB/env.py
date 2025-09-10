from datetime import timedelta, datetime
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

    def meas(self, *args):
        self.time += timedelta(seconds=random.random() * 0.001)  # add a little to simulate extra time taken to run code
        ret = []
        for arg in args:
            # ensure that the time variable is returned
            if arg.lower() == 'time':
                ret.append(self.time)
            elif arg == 'P':
                ret.append(random.random() * Prated)
            else:
                ret.append(random.random())
        return ret

    def ac_config(self, **kwargs):
        pass

    def ac_config_asym(self, **kwargs):
        pass

    def log(self, **kwargs):
        print(kwargs['msg'])

    def dc_config(self, **kwargs):
        pass

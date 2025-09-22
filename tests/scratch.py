from opender import DER, DER_PV

der_obj = DER_PV()
# der_obj.der_file.CONST_PF_MODE_ENABLE=True
# der_obj.der_file.CONST_PF=0.9
der_obj.der_file.QV_MODE_ENABLE=True
der_obj.der_file.NP_PHASE = "SINGLE"
der_obj.update_der_input(v_pu=1, f=60, p_dc_pu=1.2)
# Configure dynamic simulation timestep

DER.t_s = 0.1
der_obj.run()
der_obj.update_der_input(f=58.5)
der_obj.update_der_input(f=61.2)

der_obj.der_file.QP_MODE_ENABLE=True

class RMSVolts(float):
    def __new__(cls, value):
        obj = super().__new__(cls, value)
        return obj

    def __add__(self, other):
        if isinstance(other, RMSVolts):
            return RMSVolts(super().__add__(other))
        else:
            raise ValueError(f"Cannot add {type(self)} to {type(other)}, must be {type(self)} and {type(self)}")

    def __mul__(self, other):
        if isinstance(other, RMSAmps):
            return AvgAP(super().__mul__(other))
        elif isinstance(other, float):
            return RMSVolts(super().__mul__(other))
        else:
            raise ValueError(f"Cannot mul {type(self)} to {type(other)}, must be {type(RMSAmps)} or {type(float)}")

class RMSAmps(float):
    def __new__(cls, value):
        obj = super().__new__(cls, value)
        return obj

    def __add__(self, other):
        if isinstance(other, RMSAmps):
            return RMSAmps(super().__add__(other))
        else:
            raise ValueError(f"Cannot add {type(self)} to {type(other)}, must be {type(self)} and {type(self)}")

    def __mul__(self, other):
        if isinstance(other, RMSVolts):
            return AvgAP(super().__mul__(other))
        elif isinstance(other, float):
            return RMSAmps(super().__mul__(other))
        else:
            raise ValueError(f"Cannot mul {type(self)} to {type(other)}, must be {type(RMSVolts)} or {type(float)}")

class AvgAP(float):
    def __new__(cls, value):
        obj = super().__new__(cls, value)
        return obj

    def __add__(self, other):
        if isinstance(other, AvgAP):
            return AvgAP(super().__add__(other))
        else:
            raise ValueError(f"Cannot add {type(self)} to {type(other)}, must be {type(self)} and {type(self)}")

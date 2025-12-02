from pyUL1741SB.IEEE1547.VoltReg.vv import VVCurve
from pyUL1741SB.IEEE1547.VoltReg.vw import VWCurve
from pyUL1741SB.IEEE1547.VoltReg.wv import WVCurve
from pyUL1741SB.IEEE1547.FreqSupp import FWChar
from pyUL1741SB import Eut
import opender as der
from pyUL1741SB.eut import VoltShallTripTable, FreqShallTripTable

import wrapper as nc
import datetime as dt


class NimaEut(Eut):
    def __init__(self):
        nc.init()
        self.vac = 240
        self.fac = 60
        self.pcmd = 5000
        nc.set_emc(OF_Pmin=-5000)
        self.rslt = nc.step(self.vac, self.fac, self.pcmd, 1)
        olrt = super().Olrt(crp=10, cpf=10, wv=10, lap=1)
        super().__init__(
            olrt=olrt,
            Cat=Eut.Category.B,
            aopCat=Eut.AOPCat.III,
            voltshalltrip_tbl=VoltShallTripTable.AOPCatIII(240),
            freqshalltrip_tbl=FreqShallTripTable.MaxRange(),
            Prated=5000,
            Prated_prime=-5000,
            Srated=5000,
            Vin_nom=400,
            Vin_min=None,
            Vin_max=None,
            VN=240,
            VL=220,
            VH=260,
            Pmin=0,
            Pmin_prime=-5000,
            Qrated_abs=5000,
            Qrated_inj=5000,
            Comms=[Eut.Comms.SUNS],
            multiphase=False,
            fL=59,  # minimum frequency in continuous operating region (Hz)
            fN=60.0,  # nominal frequency (Hz)
            fH=61,  # maximum frequency in continuous operating region (Hz)
            vfo_capable=False,
            demonstrable_rocof=float('inf'),
            delta_Psmall=0.1,
        )

    def run(self, td: dt.timedelta):
        n = int(td.total_seconds() * 1000)
        self.rslt = nc.step(self.vac, self.fac, int(self.pcmd), n)

    def set_cpf(self, **kwargs):
        emc_kwargs = {}
        for k, v in kwargs.items():
            if k == 'Ena':
                emc_kwargs['PF_enable'] = v
            elif k == 'PF':
                emc_kwargs['PF_cmd'] = v
            elif k == 'Exct':
                if v.upper() == 'ABS':
                    emc_kwargs['PF_exct'] = -1
                elif v.upper() == 'INJ':
                    emc_kwargs['PF_exct'] = 1
                else:
                    raise ValueError(f'Exct: {v}')
            else:
                raise NotImplementedError
        nc.set_emc(**emc_kwargs)

    def set_lap(self, Ena: bool, pu):
        nc.set_emc(P_lim_enable=Ena, P_lim_cmd=int(
            pu * 100))  # Convert pu to percentage

    def set_aap(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'pu':
                self.pcmd = 5000 * v
            elif k == 'Ena':
                pass
            else:
                raise NotImplementedError

    def set_crp(self, **kwargs):
        emc_kwargs = {}
        for k, v in kwargs.items():
            if k == 'Ena':
                emc_kwargs['VAr_enable'] = v
            elif k == 'pu':
                # Convert pu to percentage (assuming v is in [-1, 1])
                emc_kwargs['VAr_cmd'] = int(v * 100 * 5 / 2.2)
            else:
                raise NotImplementedError
        nc.set_emc(**emc_kwargs)

    def set_vv(self, Ena: bool, crv: VVCurve = None, autoVrefEna=None, vrefTr_s=None):
        emc_kwargs = {'V_VAr_enable': Ena}
        if crv is not None:
            emc_kwargs.update({
                'V_VAr_V1': int(crv.V1 * 100),
                'V_VAr_Q1': int(crv.Q1 * 100 * 5 / 2.2),
                'V_VAr_V2': int(crv.V2 * 100),
                'V_VAr_Q2': int(crv.Q2 * 100 * 5 / 2.2),
                'V_VAr_V3': int(crv.V3 * 100),
                'V_VAr_Q3': int(crv.Q3 * 100 * 5 / 2.2),
                'V_VAr_V4': int(crv.V4 * 100),
                'V_VAr_Q4': int(crv.Q4 * 100 * 5 / 2.2),
                'V_VAr_T': crv.Tr
            })
        if autoVrefEna is not None:
            emc_kwargs['V_VAr_Auto_enable'] = autoVrefEna
        if vrefTr_s is not None:
            emc_kwargs['V_VAr_Auto_T'] = vrefTr_s
        nc.set_emc(**emc_kwargs)

    def set_wv(self, Ena: bool, crv: WVCurve = None):
        emc_kwargs = {'W_VAr_enable': Ena}
        if crv is not None:
            emc_kwargs.update({
                'W_VAr_P1_prim': int(crv.P1_prime * 100),
                'W_VAr_Q1_prim': int(crv.Q1_prime * 100 * 5 / 2.2),
                'W_VAr_P2_prim': int(crv.P2_prime * 100),
                'W_VAr_Q2_prim': int(crv.Q2_prime * 100 * 5 / 2.2),
                'W_VAr_P3_prim': int(crv.P3_prime * 100),
                'W_VAr_Q3_prim': int(crv.Q3_prime * 100 * 5 / 2.2),
                'W_VAr_P1': int(crv.P1 * 100),
                'W_VAr_Q1': int(crv.Q1 * 100 * 5 / 2.2),
                'W_VAr_P2': int(crv.P2 * 100),
                'W_VAr_Q2': int(crv.Q2 * 100 * 5 / 2.2),
                'W_VAr_P3': int(crv.P3 * 100),
                'W_VAr_Q3': int(crv.Q3 * 100 * 5 / 2.2)
            })
        nc.set_emc(**emc_kwargs)

    def set_vw(self, Ena: bool, crv: VWCurve = None):
        emc_kwargs = {'V_W_enable': Ena}
        if crv is not None:
            emc_kwargs.update({
                'V_W_V1': int(crv.V1 * 100),
                'V_W_P1': int(crv.P1 * 100),
                'V_W_V2': int(crv.V2 * 100),
                'V_W_P2': int(crv.P2 * 100),
                'V_W_T': crv.Tr
            })
        nc.set_emc(**emc_kwargs)

    def set_vt(self, **kwargs):
        emc_kwargs = {}
        for k, v in kwargs.items():
            if k == 'OV2':
                emc_kwargs['OV_V2'] = v['vpu'] * 100  # Convert to percentage
                emc_kwargs['OV_T2'] = v['cts']
            elif k == 'OV1':
                emc_kwargs['OV_V1'] = v['vpu'] * 100  # Convert to percentage
                emc_kwargs['OV_T1'] = v['cts']
            elif k == 'UV1':
                emc_kwargs['UV_V1'] = v['vpu'] * 100  # Convert to percentage
                emc_kwargs['UV_T1'] = v['cts']
            elif k == 'UV2':
                emc_kwargs['UV_V2'] = v['vpu'] * 100  # Convert to percentage
                emc_kwargs['UV_T2'] = v['cts']
            else:
                raise NotImplementedError
        nc.set_emc(**emc_kwargs)

    def set_ft(self, **kwargs):
        emc_kwargs = {}
        for k, v in kwargs.items():
            if k == 'OF2':
                emc_kwargs['OF_F2'] = v['freq']
                emc_kwargs['OF_T2'] = v['cts']
            elif k == 'OF1':
                emc_kwargs['OF_F1'] = v['freq']
                emc_kwargs['OF_T1'] = v['cts']
            elif k == 'UF1':
                emc_kwargs['UF_F1'] = v['freq']
                emc_kwargs['UF_T1'] = v['cts']
            elif k == 'UF2':
                emc_kwargs['UF_F2'] = v['freq']
                emc_kwargs['UF_T2'] = v['cts']
            else:
                raise NotImplementedError
        nc.set_emc(**emc_kwargs)

    def set_fw(self, Ena: bool, crv: FWChar = None):
        emc_kwargs = {
            'OF_drp_enable': Ena,
            'UF_drp_enable': Ena
        }
        if crv is not None:
            emc_kwargs.update({
                'OF_db': crv.dbof_hz,
                'UF_db': crv.dbuf_hz,
                'OF_k': crv.kof,
                'UF_k': crv.kuf,
                'drp_OF_T': crv.tr,
                'drp_UF_T': crv.tr
            })
        nc.set_emc(**emc_kwargs)

    def set_es(self, **kwargs):
        emc_kwargs = {}
        for k, v in kwargs.items():
            if k == 'Ena':
                emc_kwargs['Prm_serv_enable'] = v
            elif k == 'esDelay':
                emc_kwargs['ES_dl'] = v
            elif k == 'esPeriod':
                emc_kwargs['ES_rmp'] = v
            elif k == 'esVpuHi':
                emc_kwargs['ES_OV'] = v * 100  # Convert to percentage
            elif k == 'esVpuLo':
                emc_kwargs['ES_UV'] = v * 100  # Convert to percentage
            elif k == 'esfHzHi':
                emc_kwargs['ES_OF'] = v
            elif k == 'esfHzLo':
                emc_kwargs['ES_UF'] = v
            else:
                raise NotImplementedError
        nc.set_emc(**emc_kwargs)

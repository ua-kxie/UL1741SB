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

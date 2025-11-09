import pandas as pd
import numpy as np

# NIKHEF designs

A = {'inn_ht': 24, 'inn_rad': 11, 'inn_layers': 6, 'inn_dist': 0, 'out_ht': 13.5, 'out_rad': 35, 'out_layers': 5,
         'out_dist': 54.5, 'mag_len': 40, 'mag_dia': 10, 'ver_shi': 0}
A_1 = {'inn_ht': 24, 'inn_rad': 11, 'inn_layers': 6, 'inn_dist': 0, 'out_ht': 13.5, 'out_rad': 35, 'out_layers': 7,
         'out_dist': 54.5, 'mag_len': 40, 'mag_dia': 10, 'ver_shi': 0}
B = {'inn_ht': 10, 'inn_rad': 4.5, 'inn_layers': 6, 'inn_dist': 0, 'out_ht': 10, 'out_rad': 25, 'out_layers': 7,
     'out_dist': 36, 'mag_len': 8, 'mag_dia': 5, 'ver_shi': 0}
C = {'inn_ht': 15, 'lowinn_ht': 22.5, 'lowinn_rad': 13.55,'lowinn_layers': 6, 'inn_rad': 13.55, 'inn_layers': 6, 'inn_dist': 45,
     'out_ht': 12, 'out_rad': 20.5, 'out_layers': 5, 'out_dist': 13, 'mag_len': 0, 'mag_dia': 0, 'ver_shi': 0, 'mag_inn':24.1,
     'mag_out':28.57, 'mag_ht':6.35,'mag_ver_shi':0, 'inner_distance':45, 'yoke_inn_dia':5}
D = {'inn_ht': 8, 'inn_rad': 7, 'inn_layers': 6, 'inn_dist': 0, 'out_ht': 8, 'out_rad': 11.5, 'out_layers': 7,
     'out_dist': 10, 'mag_len': 0, 'mag_dia': 0, 'ver_shi': 0}
E = {'inn_ht': 8, 'inn_rad': 8, 'inn_layers': 6, 'inn_dist': 0, 'out_ht': 8, 'out_rad': 13, 'out_layers': 7,
     'out_dist': 10, 'mag_len': 0, 'mag_dia': 0, 'ver_shi': 0}
F = {'inn_ht': 18, 'inn_rad': 21, 'inn_layers': 6, 'inn_dist': 0, 'out_ht': 13.5, 'out_rad': 31.5, 'out_layers': 5,
     'out_dist': 14.5, 'mag_len': 0, 'mag_dia': 0, 'ver_shi': 0}
G = {'inn_ht': 24, 'inn_rad': 9, 'inn_layers': 6, 'inn_dist': 0, 'out_ht': 13.5, 'out_rad': 20, 'out_layers': 5,
     'out_dist': 28.5, 'mag_len': 40, 'mag_dia': 10, 'ver_shi': 0}
H = {'inn_ht': 0, 'inn_rad': 0, 'inn_layers': 0, 'inn_dist': 0, 'out_ht': 10, 'out_rad': 16, 'out_layers': 8,
     'out_dist': 0, 'mag_len': 6, 'mag_dia': 3, 'ver_shi': 0}
I = {'inn_ht': 0, 'inn_rad': 0, 'inn_layers': 0, 'inn_dist': 0, 'out_ht': 5.2, 'out_rad': 10, 'out_layers': 8,
     'out_dist': 0, 'mag_len': 3, 'mag_dia': 1.5, 'ver_shi': 0}
J = {'inn_ht': 18, 'lowinn_ht': 23,'lowinn_rad': 21, 'lowinn_layers': 6, 'inn_rad': 21, 'inn_layers': 6, 'inn_dist': 60.5, 'out_ht': 13.5,
     'out_rad': 31.5, 'out_layers': 5, 'out_dist': 14.5, 'mag_len': 0, 'mag_dia': 0, 'ver_shi': 0,
     'mag_inn':31.65, 'mag_out':44.45, 'mag_ht':6.35,'mag_ver_shi':0, 'inner_distance':60.5, 'yoke_inn_dia':8}
A1 = {'inn_ht': 20, 'inn_rad': 9, 'inn_layers': 6, 'inn_dist': 0, 'out_ht': 10, 'out_rad': 20, 'out_layers': 5,
         'out_dist': 40, 'mag_len': 30, 'mag_dia': 8, 'ver_shi': 0}
A2 = {'inn_ht': 20, 'inn_rad':7 , 'inn_layers':6 , 'inn_dist': 0, 'out_ht':25 , 'out_rad':17 , 'out_layers':5 ,
         'out_dist': 35, 'mag_len':30 , 'mag_dia':8 , 'ver_shi':0 }

# naming for the designs
data = {'A':A, 'B':B, 'C':C, 'D':D, 'E':E, 'F':F, 'G':G, 'H':H, 'I':I, 'J':J, 'top_up':A1, 'A_1':A_1,
        'top_up_m':A2}


#MATERIALS
#[wire_dia, insulation_thickness, name, resistance(Ω/mm), electrical_conductivity(MS/m)[S is Siemens=1/Ω], resistivity(Ω*m), magnetic_perm(H/m)]
wire_types = {'30 AWG': [0.254, 0.0216,'30 AWG', 103.7/304800],
              '31 AWG': [0.2261, 0.0190,'31 AWG', 130.9/304800],
              '31 AWG_top': [0.2261, 0.0190+0.0015,'31 AWG_top', 130.9/304800],
              '32 AWG': [0.2032, 0.0178,'32 AWG', 162/304800, 58, 1.68 * (10 ** (-8)), 1.256 * (10 ** (-6))],
              '34 AWG': [0.1602, 0.01652,'34 AWG', 261.3/304800],
              '32 AWG_JO_FI': [0.2032, 0.0178+(0.0062/2),'32 AWG_JO_FI', 162 / 304800, 58, 1.68 * (10 ** (-8)), 1.256 * (10 ** (-6))],
              '32 AWG_JI_FO': [0.2032, 0.0178+(0.0202/2),'32 AWG_JI_FO', 162 / 304800, 58, 1.68 * (10 ** (-8)), 1.256 * (10 ** (-6))],
              '32 AWG_AI': [0.2032, 0.0178+(0.0102/2),'32 AWG_AI', 162 / 304800, 58, 1.68 * (10 ** (-8)), 1.256 * (10 ** (-6))], #winded typeA inner
              '32 AWG_small': [0.2032, 0.0184,'32 AWG_small', 162/304800, 58, 1.68 * (10 ** (-8)), 1.256 * (10 ** (-6))], #smallip_inner
              '31 AWG_AI_s': [0.2261, 0.0190+(0.004/2),'31 AWG_AI_s', 130.9/304800, 58, 1.68 * (10 ** (-8)), 1.256 * (10 ** (-6))],   #smallip_inner
              '31 AWG_AO_s': [0.2261, 0.0190+(0.0029/2),'31 AWG_AO_s', 130.9/304800, 58, 1.68 * (10 ** (-8)), 1.256 * (10 ** (-6))],
              '31 AWG_AO': [0.2261, 0.0190+(0.0159/2),'31 AWG_AO', 130.9/304800], #winded typeA outer
              '31 AWG_AO1': [0.2261-0.017, 0.0190+((0.0159+0.017)/2),'31 AWG_AO1', 130.9/304800], #typeA micron
              '31 AWG_AO2': [0.2261, 0.0250,'31 AWG_AO2', 130.9/304800],
              '41 SWG': [0.112, 0.003,'41 SWG', 1735],
              'RS': [0.2, 0.033/2,'RS', 0.5441/1000],
              'electrisola_1a': [0.190, 0.0155,'electrisola_1a', 0.6029/1000],   #winded typeJ-inner
              'electrisola_1b': [0.190, 0.021,'electrisola_1b', 0.6029/1000],    #winded typeF-outer
              'electrisola_2a': [0.200, 0.0195,'electrisola_2a', 0.5441/1000],   #winded typeF-inner
              'electrisola_2b': [0.200, 0.017,'electrisola_2b', 0.5441/1000],    #winded typeJ-outer
              'electrisola_2c': [0.200, 0.0295,'electrisola_2c', 0.5441/1000],
              'electrisola_p': [0.190, 0.0175, 'electrisola_p', 0.6029/1000]}

blocks = dict(C = dict(b1 = [3.25, 28], b2 = [2.75, 9], b3 = [12.58, 9], b4 = [6.53, 8.65], b5 = [2.055, 2], b6 = [4.47, 4], b7 = [15.85, 6],
                       yoke_innrad = 5, yoke_uppend =-7.5-26.25-6.75, yoke_outrad = 28.575, yoke_inngap = 2.45),
              J = dict(b1 = [7, 33.5], b2 = [2.75, 9], b3 = [18.95, 9], b4 = [16.20, 12.5], b5 = [3.4, 2], b6 = [12.8, 6], b7 = [16.65, 2],
                       yoke_innrad =8, yoke_uppend =-14-42, yoke_outrad = 44.45, yoke_inngap =4.25))

#[name, relative per_x, relative_perm_y, coercivity(A/m), electrical_conductivity(MS/m)[S is Siemens=1/Ω], resistivity(Ω*m), magnetic_perm(H/m)]
magnet_types = {'N40_low' : ['N40_low', 1.05, 1.05, 860000, 0.667],
                'N40_high' : ['N40_high', 1.05, 1.05, 955000, 0.667],
                'N42_low' : ['N42_low', 1.05, 1.05, 860000, 0.667],
                'N42_high' : ['N42_high', 1.05, 1.05, 955000, 0.667]}

class Input:
    def __init__(self):
        pass
    def general(self):
        return [A, B, C, D, E, F, G, H, I, J]
    def return_data(self, design_type: str):
        return data[design_type]


# WIRE DIAMETER(mm) - bare wire diameter
# INSULATION(mm)    - thickness of the insulation
#name =
# COERCIVITY(A/m) - ability of ferromagnetic material to withstand an external magnetic field without becoming demagnetized.
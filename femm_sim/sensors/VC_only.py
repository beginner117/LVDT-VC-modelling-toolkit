import femm
import numpy as np
import matplotlib.pyplot as plt
from materials import feed as feed
from models import design as design
from models import coil as coil
from models import femm_model as femm_model

class Analysis:
    def __init__(self, save, sim_range:list, default, filename, design_type,input_excitation, materials, boundary_conditions,
                 coil_dimensions = None, sim_type = None,  parameter1=None):
        self.save = save
        self.sim_range = sim_range
        self.filename = filename
        self.parameter1 = parameter1
        self.design_type = design_type
        self.default = default
        self.sim_type = sim_type
        self.materials = materials
        self.des_dim = coil_dimensions
        self.input_excitation = input_excitation
        self.bc = boundary_conditions
    def simulate(self):
        with open('paths.txt', 'r') as file:
            path1 = file.read()
        try:
            femm.openfemm()  # The package must be initialized with the openfemm command.
        except:
            femm.openfemm(femmpath=path1)
        femm.newdocument(0)
        value = feed.data
        in_pa = feed.Input()
        pre_simulation = design.Simulation(Nsteps=self.sim_range[0], stepsize=self.sim_range[1], inncoil_offset=self.sim_range[2], data_file=self.filename)
        sensor = design.Sensortype(InnCoilCurrent=self.input_excitation[0], Simfreq=self.input_excitation[1], OutCoilCurrent=self.input_excitation[2])
        femm.mi_probdef(sensor.para()[1], 'millimeters', 'axi', 1.0e-10)
        wire = design.Wiretype(outcoil_material=self.materials[0], inncoil_material='32 AWG', magnet_material=self.materials[1])
        input_par1 = {'TotalSteps_StepSize(mm)_Offset(mm)': self.sim_range, 'uppercoil Diameter(mm)_Insulation(mm)_Wiretype': wire.prop_out(),
                       'Magnet_material':wire.mag_mat(), 'Frequency(Hz)': sensor.para()[1], 'Outercoil_current(A)': sensor.para()[2]}
        if self.default == 'yes':
            geo = design.Geometry(value[self.design_type]["inn_ht"], value[self.design_type]['inn_rad'], value[self.design_type]['inn_layers'], value[self.design_type]['inn_dist'],
                                  value[self.design_type]['out_ht'], value[self.design_type]['out_rad'], value[self.design_type]['out_layers'], value[self.design_type]['out_dist'],
                                  value[self.design_type]['mag_len'], value[self.design_type]['mag_dia'], value[self.design_type]['ver_shi'])
            input_par2 = in_pa.return_data(self.design_type)
            input_par3 = 'design type ' + self.design_type
        if self.default == 'no':
            try:
                input_par2 = {'IC_height': 0, 'IC_radius': 0,
                              'IC_layers': 0, 'IC_distance': 0,
                              'OC_height': self.des_dim['outer'][0], 'OC_radius': self.des_dim['outer'][1],
                              'OC_layers': self.des_dim['outer'][2], 'OC_distance': 0,
                              'mag_len': self.des_dim['magnet'][0], 'mag_dia': self.des_dim['magnet'][1], 'ver_shi': 0}
            except:
                input_par2 = {'IC_height': self.parameter1[0], 'IC_radius': 7, 'IC_layers': 6, 'IC_distance': 0,
                              'OC_height': self.parameter1[1], 'OC_radius': 17, 'OC_layers': 7,
                              'OC_distance': self.parameter1[2], 'mag_len': 30, 'mag_dia': 8, 'ver_shi': 0}
            geo = design.Geometry(input_par2['IC_height'], input_par2['IC_radius'], input_par2['IC_layers'], input_par2['IC_distance'],
                                  input_par2['OC_height'], input_par2['OC_radius'], input_par2['OC_layers'], input_par2['OC_distance'],
                                  input_par2['mag_len'], input_par2['mag_dia'], input_par2['ver_shi'])
            input_par3 = 'not a priliminary NIKHEF design'
        position = coil.Position(inn_ht=geo.inncoil()[0], inn_rad=geo.inncoil()[1], inn_layers=geo.inncoil()[2],
                                 inn_dist=geo.inncoil()[3], out_ht=geo.outcoil()[0], out_rad=geo.outcoil()[1],
                                 out_layers=geo.outcoil()[2], out_dist=geo.outcoil()[3],
                                 ver_shi=geo.mag()[2], inn_wiredia=wire.prop_inn()[0], inn_wireins=wire.prop_inn()[1],
                                 out_wiredia=wire.prop_out()[0], out_wireins=wire.prop_out()[1], mag_len=geo.mag()[0],
                                 mag_dia=geo.mag()[1])
        length = coil.Length(inn_layers=geo.inncoil()[2], inn_rad=geo.inncoil()[1], inn_wiredia=wire.prop_inn()[0],
                             inn_wireins=wire.prop_inn()[1], innwind_pr_layer=position.inncoil()[3],
                             out_layers=geo.outcoil()[2], out_rad=geo.outcoil()[1],
                             out_wiredia=wire.prop_out()[0], out_wireins=wire.prop_out()[1],
                             outwind_pr_layer=position.upp_outcoil()[3])
        print('coil config - [Coil_OutRadius, Coil_LowEnd, Coil_UppEnd, Coil_NrWind_p_Layer, Coil_NrWindings, Circuit_name]')
        print('outer coil config :', position.upp_outcoil())
        print(', outer coil material - ', wire.outcoil_material, ', magnet material - ', wire.mag_mat())
        out_dc = length.upp_outcoil() * wire.prop_out()[3]
        print('outer dc resistance as per catalog :', out_dc)
        full_length = (pre_simulation.parameters()[0] * pre_simulation.parameters()[1]) + pre_simulation.parameters()[2] + position.upp_outcoil()[2]
        if full_length < self.bc[0]:
            bc_con = self.bc
        else:
            bc_con = [full_length + 50, self.bc[1], self.bc[2], full_length + 150, self.bc[4], self.bc[5], self.bc[6]]
        uppoutstr = femm_model.Femm_coil(x1=geo.outcoil()[1], y1=position.upp_outcoil()[2], x2=position.upp_outcoil()[0], y2=position.upp_outcoil()[1],
                                         circ_name=position.upp_outcoil()[5], circ_current=sensor.para()[2][0], circ_type=1, material=wire.outcoil_material,
                                         edit_mode=4, group=3, label1=wire.prop_out()[1], label2=geo.outcoil()[0], blockname=wire.prop_out()[2],
                                         turns_pr_layer=position.upp_outcoil()[4])
        magnetstr = femm_model.Femm_magnet(x1=0, y1=position.magnet()[0], x2=position.magnet()[2], y2=position.magnet()[1], material=wire.mag_mat(), edit_mode=4, group=2, label1=0.5, label2=geo.mag()[0])

        bc = femm_model.Femm_bc(AirSpaceRadius_1=bc_con[0], material1=bc_con[1], grid1=bc_con[2],
                                AirSpaceRadius_2=bc_con[3], material2=bc_con[4], grid2=bc_con[5], BC_Name=bc_con[6],
                                BC_Group=10)
        bc_conditions_mesh = {'region1_radius_material_grid': [bc_con[0], bc_con[1], bc_con[2]],
                              'region2_radius_mesh_material': [bc_con[3], bc_con[4], bc_con[5]]}
        print('boundary : ', bc_conditions_mesh)

        res = coil.Coil_prop(pre_simulation.parameters()[0])
        uppout_prop = res.gen_coil()
        mag_for = res.magnet()
        move_group = femm_model.Femm_move(groups=[3], x_dist=0, y_dist=pre_simulation.parameters()[2])
        for_def = []; for_imp = []; for_ana = []
        for i in range(0, pre_simulation.parameters()[0] + 1):
            print('coil position (from centre) : ', pre_simulation.parameters()[2] + pre_simulation.parameters()[1] * i)
            uppout_prop['position'][i] = pre_simulation.parameters()[2] + pre_simulation.parameters()[1] * i
            femm.mi_zoom(-2, -50, 50, 50)
            femm.mi_refreshview()
            femm.mi_saveas('VConly_ETpf_LIP.fem')
            femm.mi_analyze()
            femm.mi_loadsolution()

            femm.mo_groupselectblock(3)
            UppOut_Force19 = femm.mo_blockintegral(19)
            femm.mo_clearblock()
            femm.mo_groupselectblock(2)
            Magn_Force19 = femm.mo_blockintegral(19)
            femm.mo_clearblock()

            UppOutCoil_I, UppOutCoil_V, UppOutCoil_FluxLink = femm.mo_getcircuitproperties(position.upp_outcoil()[5])
            uppout_prop['voltage'][i] = UppOutCoil_V
            uppout_prop['current'][i] = UppOutCoil_I
            uppout_prop['flux'][i] = UppOutCoil_FluxLink
            uppout_prop['force'][i] = UppOut_Force19
            mag_for['Magnet_forces'][i] = Magn_Force19
            move_group = femm_model.Femm_move(groups=[3], x_dist=0, y_dist=pre_simulation.parameters()[1])

        Upp_Inductance = abs(uppout_prop['flux'] / uppout_prop['current'])
        Upp_resistance = abs(uppout_prop['voltage'] / uppout_prop['current'])
        print('upp out resistance as per femm :', abs(Upp_resistance))
        print('magnet force :', np.real(mag_for['Magnet_forces']))

        if self.save:
            if self.sim_type == 'FEMM+ana':
                np.savez_compressed(self.filename, Design_type=input_par3, Design = input_par2, Input_parameters=input_par1,
                                    UpperOutcoil_config=position.upp_outcoil(),
                                    UOC_positions=uppout_prop['position'], UOC_forces=uppout_prop['force'],
                                    Mag_forces=np.array(for_def), Mag_forces_imp=np.array(for_imp),
                                    UOC_flux=uppout_prop['flux'], UOC_voltages=uppout_prop['voltage'], UOC_currents=uppout_prop['current'])
            if self.sim_type == 'math+ana':
                np.savez_compressed(self.filename, Design_type=input_par3, Design = input_par2, Input_parameters=input_par1,
                                    UpperOutcoil_config=position.upp_outcoil(),
                                    UOC_positions=uppout_prop['position'], UOC_forces=uppout_prop['force'], Mag_forces=np.array(for_ana),
                                    UOC_flux=uppout_prop['flux'], UOC_voltages=uppout_prop['voltage'], UOC_currents=uppout_prop['current'])
            if self.sim_type == None:
                np.savez_compressed(self.filename, Design_type=input_par3, Design = input_par2, Input_parameters = input_par1, UpperOutcoil_config=position.upp_outcoil(),
                                    UOC_positions = uppout_prop['position'], UOC_forces = uppout_prop['force'], Mag_forces = mag_for['Magnet_forces'],Boundary_conditions = bc_conditions_mesh,
                                    UOC_flux=uppout_prop['flux'], UOC_voltages = uppout_prop['voltage'], UOC_currents=uppout_prop['current'])


        return {'coil_positions': np.real(uppout_prop['position']), 'magnet_forces': np.real(mag_for['Magnet_forces'])}

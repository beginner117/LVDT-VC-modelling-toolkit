import femm
import numpy as np
import matplotlib.pyplot as plt
import sys
from materials import feed as feed
from models import design as design
from models import coil as coil
from models import femm_model as femm_model
from models import fields as fields

class Analysis:
    def __init__(self,save, sim_range: list, default, filename, design_type,input_excitation, materials, boundary_conditions,
                 coil_dimensions=None, parameter1=None, simulation_type=None):
        self.save = save
        self.sim_range = sim_range
        self.filename = filename
        self.parameter1 = parameter1
        self.sim_type = simulation_type
        self.design_type = design_type
        self.default = default
        self.materials = materials
        self.des_dim = coil_dimensions
        self.input_excitation = input_excitation
        self.bc = boundary_conditions
    def simulate(self):
        """"
        simulates the Voice coil performance"""
        with open('paths.txt', 'r') as file:
            path1 = file.read()
        try:
            femm.openfemm()  # The package must be initialized with the openfemm command.
        except:
            femm.openfemm(femmpath=path1)
        femm.newdocument(0)  # We need to create a new Magnetostatics document to work on.
        value = feed.data
        in_pa = feed.Input()
        pre_simulation = design.Simulation(Nsteps=self.sim_range[0], stepsize=self.sim_range[1], inncoil_offset=self.sim_range[2], data_file=self.filename)
        sensor = design.Sensortype(InnCoilCurrent=self.input_excitation[0], Simfreq=self.input_excitation[1], OutCoilCurrent=self.input_excitation[2])
        femm.mi_probdef(sensor.para()[1], 'millimeters', 'axi', 1.0e-10)
        wire = design.Wiretype(outcoil_material=self.materials[1],inncoil_material= self.materials[0], magnet_material=self.materials[2])
        input_par1 = {'TotalSteps_StepSize(mm)_Offset': self.sim_range, 'outercoil Diameter(mm)_Insulation(mm)_Wiretype': wire.prop_out()[:3], 'innercoil Diameter(mm)_Insulation(mm)_Wiretype': wire.prop_inn()[:3],
                      'Innercoil_current(A)': sensor.para()[0], 'Frequency(Hz)': sensor.para()[1], 'Outercoil_current(A)': sensor.para()[2], 'Magnet_material':wire.mag_mat()}
        if self.default=='yes':
            geo = design.Geometry(value[self.design_type]["inn_ht"], value[self.design_type]['inn_rad'], value[self.design_type]['inn_layers'], value[self.design_type]['inn_dist'], value[self.design_type]['out_ht'], value[self.design_type]['out_rad'],
                                  value[self.design_type]['out_layers'], value[self.design_type]['out_dist'], value[self.design_type]['mag_len'], value[self.design_type]['mag_dia'], value[self.design_type]['ver_shi'])
            input_par2 = in_pa.return_data(self.design_type)
            input_par3 = 'NIKHEF design type : ' + self.design_type
        if self.default == 'no':
            try:
                input_par2 = {'IC_height': self.des_dim['inner'][0], 'IC_radius': self.des_dim['inner'][1],
                              'IC_layers': self.des_dim['inner'][2], 'IC_distance': 0,
                              'OC_height': self.des_dim['outer'][0], 'OC_radius': self.des_dim['outer'][1],
                              'OC_layers': self.des_dim['outer'][2], 'OC_distance': self.des_dim['outer'][3],
                              'mag_len': self.des_dim['magnet'][0], 'mag_dia': self.des_dim['magnet'][1], 'ver_shi': 0}
            except:
                input_par2 = {'IC_height': self.parameter1[0], 'IC_radius': self.parameter1[1], 'IC_layers': 6,
                              'IC_distance': 0, 'OC_height': self.parameter1[2], 'OC_radius': self.parameter1[3],
                              'OC_layers': 7,
                              'OC_distance': self.parameter1[4], 'mag_len': 40, 'mag_dia': 10, 'ver_shi': 0}
            geo = design.Geometry(input_par2['IC_height'], input_par2['IC_radius'], input_par2['IC_layers'], input_par2['IC_distance'], input_par2['OC_height'], input_par2['OC_radius'],
                                  input_par2['OC_layers'], input_par2['OC_distance'], input_par2['mag_len'], input_par2['mag_dia'], input_par2['ver_shi'])
            input_par3 = 'not a NIKHEF design'
        position = coil.Position(inn_ht=geo.inncoil()[0], inn_rad=geo.inncoil()[1], inn_layers=geo.inncoil()[2], inn_dist=geo.inncoil()[3], out_ht=geo.outcoil()[0], out_rad=geo.outcoil()[1], out_layers=geo.outcoil()[2], out_dist=geo.outcoil()[3],
                                 ver_shi=geo.mag()[2], inn_wiredia=wire.prop_inn()[0], inn_wireins=wire.prop_inn()[1], out_wiredia=wire.prop_out()[0], out_wireins=wire.prop_out()[1], mag_len=geo.mag()[0], mag_dia=geo.mag()[1])
        length = coil.Length(inn_layers=geo.inncoil()[2], inn_rad=geo.inncoil()[1], inn_wiredia=wire.prop_inn()[0], inn_wireins=wire.prop_inn()[1], innwind_pr_layer=position.inncoil()[3], out_layers=geo.outcoil()[2],
                             out_rad=geo.outcoil()[1], out_wiredia=wire.prop_out()[0], out_wireins=wire.prop_out()[1], outwind_pr_layer=position.upp_outcoil()[3])
        full_length = (pre_simulation.parameters()[0] * pre_simulation.parameters()[1]) + pre_simulation.parameters()[2] + position.inncoil()[2]
        if full_length < self.bc[0]:
            bc_con = self.bc
        else:
            bc_con = [full_length + 50, self.bc[1], self.bc[2], full_length + 150, self.bc[4], self.bc[5], self.bc[6]]
        print('coil config - [Coil_OutRadius, Coil_LowEnd, Coil_UppEnd, Coil_NrWind_p_Layer, Coil_NrWindings, Circuit_name]')
        print('inner coil config :', position.inncoil(), '\nupper outer coil config :', position.upp_outcoil(),'\nlower out coil config :', position.low_outcoil())
        print('inner coil material - ', wire.inncoil_material, ', outer coil material - ', wire.outcoil_material, ', magnet material - ', wire.magnet_material)
        print('inner, upper outer, total coil lengths : ', length.inncoil(), length.upp_outcoil(),
              length.inncoil() + (2 * length.upp_outcoil()))
        coil_con = ['Coil_OutRadius', 'Coil_Lowend', 'Coil_Uppend', 'Coil_turns(per layer)', 'Coil_turns total','coil_name']
        if wire.prop_out()[3] and wire.prop_inn()[3]:
            inn_dc = length.inncoil() * wire.prop_inn()[3]
            out_dc = length.upp_outcoil() * wire.prop_out()[3]
            lowout_dc = length.low_outcoil() * wire.prop_out()[3]
            print('inner, upper outer coil Dc resistance as per datasheet (in ohms) :', inn_dc, out_dc)
        inncoil_str = femm_model.Femm_coil(x1=geo.inncoil()[1], y1=position.inncoil()[2], x2=position.inncoil()[0], y2=position.inncoil()[1],
                                           circ_name=position.inncoil()[5], circ_current=sensor.para()[0], circ_type=1, material=wire.inncoil_material,
                                           edit_mode=4, group=1, label1=wire.prop_inn()[1], label2=geo.inncoil()[0], blockname=wire.prop_inn()[2],
                                           turns_pr_layer=position.inncoil()[4], simulation_type=self.sim_type)
        uppoutstr = femm_model.Femm_coil(x1=geo.outcoil()[1], y1=position.upp_outcoil()[2], x2=position.upp_outcoil()[0], y2=position.upp_outcoil()[1],
                                         circ_name=position.upp_outcoil()[5], circ_current=sensor.para()[2][0], circ_type=1, material=wire.outcoil_material,
                                         edit_mode=4, group=3, label1=wire.prop_out()[1],
                                         label2=geo.outcoil()[0], blockname=wire.prop_out()[2], turns_pr_layer=position.upp_outcoil()[4], simulation_type=self.sim_type)
        lowoutstr = femm_model.Femm_coil(x1=geo.outcoil()[1], y1=position.low_outcoil()[2], x2=position.low_outcoil()[0], y2=position.low_outcoil()[1],
                                         circ_name=position.low_outcoil()[5], circ_current=-sensor.para()[2][1], circ_type=1, material=wire.outcoil_material,
                                         edit_mode=4, group=4, label1=wire.prop_out()[0],
                                         label2=geo.outcoil()[0], blockname=wire.prop_out()[2], turns_pr_layer=position.low_outcoil()[4], simulation_type=self.sim_type)
        magnetstr = femm_model.Femm_magnet(x1=0, y1=position.magnet()[0], x2=position.magnet()[2], y2=position.magnet()[1], material=wire.mag_mat(), edit_mode=4, group=2, label1=0.5, label2=geo.mag()[0])
        bc = femm_model.Femm_bc(AirSpaceRadius_1=bc_con[0], material1=bc_con[1], grid1=bc_con[2],
                                AirSpaceRadius_2=bc_con[3], material2=bc_con[4], grid2=bc_con[5], BC_Name=bc_con[6],
                                BC_Group=10)
        bc_conditions_mesh = {'region1_radius_material_grid': [bc_con[0], bc_con[1], bc_con[2]],
                              'region2_radius_mesh_material': [bc_con[3], bc_con[4], bc_con[5]]}
        print('boundary : ', bc_conditions_mesh)

        res = coil.Coil_prop(pre_simulation.parameters()[0])
        mag_prop = res.magnet()
        inn_prop = res.gen_coil()
        uppout_prop = res.gen_coil()
        lowout_prop = res.gen_coil()

        move_group = femm_model.Femm_move(groups = [1,2], x_dist=0, y_dist=pre_simulation.parameters()[2])

        for i in range(0, pre_simulation.parameters()[0] + 1):
            print('coil position (from centre) : ', pre_simulation.parameters()[2] + pre_simulation.parameters()[1] * i)
            inn_prop['position'][i] = pre_simulation.parameters()[2] + pre_simulation.parameters()[1] * i
            femm.mi_zoom(-2, -50, 50, 50)
            femm.mi_refreshview()
            femm.mi_saveas('VC_ETpf_LIP.fem')
            femm.mi_analyze()
            femm.mi_loadsolution()

            femm.mo_groupselectblock(3)
            UppOut_Force19 = femm.mo_blockintegral(19)
            femm.mo_clearblock()
            femm.mo_groupselectblock(4)
            LowOut_Force19 = femm.mo_blockintegral(19)
            femm.mo_clearblock()
            femm.mo_groupselectblock(1)
            Innercoil_Force19 = femm.mo_blockintegral(19)
            femm.mo_clearblock()
            femm.mo_groupselectblock(2)
            Magn_Force19 = femm.mo_blockintegral(19)
            femm.mo_clearblock()

            UppOutCoil_I, UppOutCoil_V, UppOutCoil_FluxLink = femm.mo_getcircuitproperties(position.upp_outcoil()[5])
            uppout_prop['voltage'][i] = UppOutCoil_V
            uppout_prop['current'][i] = UppOutCoil_I
            uppout_prop['flux'][i] = UppOutCoil_FluxLink
            uppout_prop['force'][i] = UppOut_Force19

            LowOutCoil_I, LowOutCoil_V, LowOutCoil_FluxLink = femm.mo_getcircuitproperties(position.low_outcoil()[5])
            lowout_prop['voltage'][i] = LowOutCoil_V
            lowout_prop['current'][i] = LowOutCoil_I
            lowout_prop['flux'][i] = LowOutCoil_FluxLink
            lowout_prop['force'][i] = LowOut_Force19

            InnCoil_I, InnCoil_V, InnCoil_FluxLink = femm.mo_getcircuitproperties(position.inncoil()[5])
            inn_prop['voltage'][i] = InnCoil_V
            inn_prop['current'][i] = InnCoil_I
            inn_prop['flux'][i] = InnCoil_FluxLink
            inn_prop['force'][i] = Innercoil_Force19

            mag_prop['Magnet_forces'][i] = Magn_Force19

            if self.sim_type == 'semi_analytical':
                mag_field = fields.B_field(40, 45, 0.01, 0.1, self.filename, input_par3, input_par2, input_par1, inn_prop['Inncoil_voltage'][0], inn_prop['Inncoil_flux'][0]
                                           ,uppout_prop['UppOut_voltage'][0], uppout_prop['UppOut_flux'][0])
                mag_field.calculate()
                print('field calculation completed')
                sys.exit()

            move_group = femm_model.Femm_move(groups=[1, 2], x_dist=0, y_dist=pre_simulation.parameters()[1])

        if sensor.para()[2][0] != 0:
            print("magnet force :", mag_prop['Magnet_forces'])
            Upp_Inductance = abs(uppout_prop['flux'] / uppout_prop['current'])
            Upp_resistance = abs(uppout_prop['voltage'] / uppout_prop['current'])

            print('upper out coil ind, imp :', Upp_Inductance, Upp_resistance)

        k1, k2, k3 = np.polyfit(np.real(inn_prop['position']), mag_prop['Magnet_forces'], 2)
        fit_forces = k1*((np.real(inn_prop['position']))**2) + k2*(np.real(inn_prop['position'])) + k3

        coil_forces = uppout_prop['force']+lowout_prop['force']

        plt.plot(np.real(inn_prop['position']), abs(uppout_prop['force']), 'o--', label = 'upper')
        plt.plot(np.real(inn_prop['position']), abs(lowout_prop['force']), 'o--', label = 'lower')
        plt.xlabel('Inner Coil Position [mm]')
        plt.ylabel('Fitted Magnet Force [N/A]')
        plt.title('Actuation force')
        plt.legend()
        plt.grid()
        plt.show()

        #plt.plot(np.real(inn_prop['position']), fit_forces, 'o--', label = 'fit')
        #plt.plot(np.real(inn_prop['position']), mag_prop['Magnet_forces'], 'o--', label = 'unfit')
        plt.plot(np.real(inn_prop['position']), abs(coil_forces), 'o--')
        plt.ylabel(r'Normalised coil force $[\frac{N}{A}]$', fontsize=13, fontname='Arial')
        plt.xlabel('Primary Coil Position[in mm] relative to the secondary', fontsize=13, fontname='Arial')
        plt.title(r'Actuation force with 1A DC excitation' + '\n' + 'ETpathfinder design type : ' + self.design_type, fontsize=14, fontname='Arial')
        plt.grid(b=True)
        plt.legend()
        plt.xticks(rotation=0, fontsize=14)
        plt.tight_layout()
        #plt.savefig("C:\\Users\\kumar\\OneDrive\\Desktop\\new\\pic\\simul\\summary\\B_vc_for", format = 'pdf')
        plt.show()

        plt.plot(np.real(inn_prop['position']), abs(coil_forces)/np.max(abs(coil_forces)), 'o--')
        plt.ylabel(r'Stability [%]', fontsize=13, fontname='Arial')
        plt.xlabel('Primary Coil Position[in mm] relative to the secondary', fontsize=13, fontname='Arial')
        plt.title(r'Force stability with 1A DC excitation' + '\n' + 'ETpathfinder design type : ' + self.design_type,
                  fontsize=14, fontname='Arial')
        plt.grid(b=True)
        plt.legend()
        plt.xticks(rotation=0, fontsize=14)
        plt.tight_layout()
        #plt.savefig("C:\\Users\\kumar\\OneDrive\\Desktop\\new\\pic\\simul\\summary\\B_vc_stab", format='pdf')
        plt.show()

        if self.save:
            np.savez_compressed(self.filename, Design_parameters = input_par2, Input_parameters = input_par1, coil_config_parameters = coil_con,Boundary_conditions = bc_conditions_mesh,
                                Innercoil_config=position.inncoil(), UpperOutcoil_config=position.upp_outcoil(), LowerOutercoil_config=position.low_outcoil(),
                                UOC_forces = uppout_prop['force'], LOC_forces = lowout_prop['force'], Mag_forces = mag_prop['Magnet_forces'], IC_forces = inn_prop['force'],
                                IC_currents = inn_prop['current'], UOC_currents=uppout_prop['current'], LOC_currents = lowout_prop['current'],
                                UOC_voltages = uppout_prop['voltage'], LOC_voltages = lowout_prop['voltage'], IC_voltages = inn_prop['voltage'],
                                IC_positions = inn_prop['position'], IC_flux=inn_prop['flux'], UOC_flux=uppout_prop['flux'], LOC_flux=lowout_prop['flux'],
                                Inn_Uppout_Lowout_DCR_as_per_catalog = [inn_dc, out_dc, lowout_dc])

        return {'coil_positions': np.real(inn_prop['position']), 'Magnet_forces': abs(mag_prop['Magnet_forces'])}
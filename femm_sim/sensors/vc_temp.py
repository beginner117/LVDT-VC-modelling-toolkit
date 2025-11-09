import femm
import numpy as np
import matplotlib.pyplot as plt
from models import design
from models import femm_model
from models import coil
from materials import feed as feed


class Analysis:
    def __init__(self, save, sim_range: list, default, filename: str, design_type, input_excitation, materials,
                 coil_dimensions=None, parameter1=None):
        self.save = save
        self.sim_range = sim_range
        self.filename = filename
        self.parameter1 = parameter1
        self.design_type = design_type
        self.default = default
        self.materials = materials
        self.des_dim = coil_dimensions
        self.input_excitation = input_excitation

    def simulate(self):
        print(self.parameter1)
        femm.openfemm()  # The package must be initialized with the openfemm command.
        femm.newdocument(2)  # We need to create a new Magnetostatics document to work on.
        value = feed.data
        pre_simulation = design.Simulation(Nsteps=self.sim_range[0], stepsize=self.sim_range[1],
                                           inncoil_offset=self.sim_range[2], data_file=self.filename)
        sensor = design.Sensortype(InnCoilCurrent=self.input_excitation[0], Simfreq=self.input_excitation[1],
                                   OutCoilCurrent=self.input_excitation[2])
        femm.hi_probdef('millimeters', 'axi', 1.0e-8)
        wire = design.Wiretype(self.materials[1], self.materials[0], magnet_material=self.materials[2])
        input_par1 = {'TotalSteps_StepSize_Offset': self.sim_range,
                      'uppercoil Diameter_Insulation_Wiretype': wire.prop_out()[:3],
                      'innercoil Diameter_Insulation_Wiretype': wire.prop_inn()[:3],
                      'Innercoil_current': sensor.para()[0], 'Frequency': sensor.para()[1],
                      'Outercoil_current': sensor.para()[2], 'Magnet_material': wire.mag_mat()}
        if self.default == 'yes':
            geo = design.Geometry(value[self.design_type]["inn_ht"], value[self.design_type]['inn_rad'],
                                  value[self.design_type]['inn_layers'], value[self.design_type]['inn_dist'],
                                  value[self.design_type]['out_ht'], value[self.design_type]['out_rad'],
                                  value[self.design_type]['out_layers'], value[self.design_type]['out_dist'],
                                  value[self.design_type]['mag_len'], value[self.design_type]['mag_dia'],
                                  value[self.design_type]['ver_shi'])
            input_par2 = 'type' + self.design_type
        if self.default == 'no':
            try:
                input_par2 = {'IC_height': self.des_dim['inner'][0], 'IC_radius': self.des_dim['inner'][1],
                              'IC_layers': self.des_dim['inner'][2], 'IC_distance': 0,
                              'OC_height': self.des_dim['outer'][0], 'OC_radius': self.des_dim['outer'][1],
                              'OC_layers': self.des_dim['outer'][2], 'OC_distance': self.des_dim['outer'][3],
                              'mag_len': self.des_dim['magnet'][0], 'mag_dia': self.des_dim['magnet'][1], 'ver_shi': 0}
            except:
                input_par2 = {'IC_height': self.parameter1[0], 'IC_radius': 7, 'IC_layers': 6, 'IC_distance': 0,
                              'OC_height': self.parameter1[1], 'OC_radius': 17, 'OC_layers': 7,
                              'OC_distance': self.parameter1[2], 'mag_len': 30, 'mag_dia': 8, 'ver_shi': 0}
            geo = design.Geometry(input_par2['IC_height'], input_par2['IC_radius'], input_par2['IC_layers'],
                                  input_par2['IC_distance'], input_par2['OC_height'], input_par2['OC_radius'],
                                  input_par2['OC_layers'], input_par2['OC_distance'], input_par2['mag_len'],
                                  input_par2['mag_dia'], input_par2['ver_shi'])
            input_par3 = 'not a NIKHEF design'
        other_par = {'inner coil current_frequency_wire': [sensor.para()[0], sensor.para()[1], wire.inncoil_material],
                     'outer coil_current_frequency_wire': [sensor.para()[2], sensor.para()[1], wire.outcoil_material]}
        position = coil.Position(inn_ht=geo.inncoil()[0], inn_rad=geo.inncoil()[1], inn_layers=geo.inncoil()[2],
                                 inn_dist=geo.inncoil()[3], out_ht=geo.outcoil()[0], out_rad=geo.outcoil()[1],
                                 out_layers=geo.outcoil()[2], out_dist=geo.outcoil()[3],
                                 ver_shi=geo.mag()[2], inn_wiredia=wire.prop_inn()[0], inn_wireins=wire.prop_inn()[1],
                                 out_wiredia=wire.prop_out()[0], out_wireins=wire.prop_out()[1], mag_len=geo.mag()[0],
                                 mag_dia=geo.mag()[1])
        length = coil.Length(inn_layers=geo.inncoil()[2], inn_rad=geo.inncoil()[1], inn_wiredia=wire.prop_inn()[0],
                             inn_wireins=wire.prop_inn()[1], innwind_pr_layer=position.inncoil()[3],
                             out_layers=geo.outcoil()[2],
                             out_rad=geo.outcoil()[1], out_wiredia=wire.prop_out()[0], out_wireins=wire.prop_out()[1],
                             outwind_pr_layer=position.upp_outcoil()[3])
        print(
            'coil config - [Coil_OutRadius, Coil_LowEnd, Coil_UppEnd, Coil_NrWind_p_Layer, Coil_NrWindings, Circuit_name]')
        print('inner coil config :', position.inncoil(), '\nupper outer coil config :', position.upp_outcoil(),
              '\nlower out coil config :', position.low_outcoil())
        print('inner coil material - ', wire.inncoil_material, ', outer coil material - ', wire.outcoil_material,
              ', magnet material - ', wire.magnet_material)
        print('inner, upper outer, total coil lengths : ', length.inncoil(), length.upp_outcoil(),
              length.inncoil() + (2 * length.upp_outcoil()))
        coil_con = ['Coil_OutRadius', 'Coil_Lowend', 'Coil_Uppend', 'Coil_turns(per layer)', 'Coil_turns total',
                    'coil_name']
        if wire.prop_out()[3] and wire.prop_inn()[3]:
            inn_dc = length.inncoil() * wire.prop_inn()[3]
            out_dc = length.upp_outcoil() * wire.prop_out()[3]
            lowout_dc = length.low_outcoil() * wire.prop_out()[3]
            print('inner, upper outer coil Dc resistance as per datasheet (in ohms) :', inn_dc, out_dc)
        # magnetstr = femm_model.Femm_magnet(x1=0, y1=position.magnet()[0], x2=position.magnet()[2],
        #                                    y2=position.magnet()[1], material=wire.magnet_material, edit_mode=4, group=2,
        #                                    label1=0.5, label2=geo.mag()[0])
        # bc = femm_model.Femm_bc(AirSpaceRadius_1=100, AirSpaceRadius_2=300, BC_Name='Outside', BC_Group=10,
        #                         material='Air')


        femm.hi_drawrectangle(0, position.magnet()[0], position.magnet()[2], position.magnet()[1])
        femm.hi_getmaterial(wire.magnet_material)
        femm.hi_clearselected()
        femm.hi_selectrectangle(0, position.magnet()[0], position.magnet()[2], position.magnet()[1], 4)
        femm.hi_setgroup(2)
        femm.hi_clearselected()
        femm.hi_addblocklabel(0+ 0.5, position.magnet()[1] + (geo.mag()[0] / 2))
        femm.hi_selectlabel(0+ 0.5, position.magnet()[1] + (geo.mag()[0] / 2))
        femm.hi_setblockprop(wire.magnet_material, 0, 0.1, 2)
        femm.hi_clearselected()

        # Airspace1
        # femm.hi_drawline(0, 100, 0, -100)
        # femm.hi_drawarc(0, -100, 0, 100, 180, 2)
        # femm.hi_getmaterial("Air")
        # femm.hi_clearselected()
        # femm.hi_addblocklabel(100 / 4, 100/ 2)
        # femm.hi_selectlabel(100 / 4, 100 / 2)
        # femm.hi_setblockprop("Air", 0, 0.5, '')
        # femm.hi_clearselected()
        # Airspace2
        femm.hi_drawline(0, 50, 0, -50)
        femm.hi_drawarc(0, -50, 0, 50, 180, 2)
        femm.hi_getmaterial("Air")
        femm.hi_clearselected()
        femm.hi_addblocklabel(50 / 2, 50 / 1.2)
        femm.hi_selectlabel(50 / 2, 50 / 1.2)
        femm.hi_setblockprop("Air", 1, 0, 10)
        femm.hi_clearselected()
        # Boundary properties
        femm.hi_addboundprop('Fixed Temperature', 0, 100, 0, 0, 0, 0)
        femm.hi_clearselected()
        femm.hi_selectarcsegment(0, 50)
        femm.hi_setarcsegmentprop(2, 'Outside', 0, 10, "None")
        femm.hi_clearselected()


        res = coil.Coil_prop(pre_simulation.parameters()[0])
        inn_prop = res.gen_coil()
        mag_prop = res.magnet()

        femm.hi_selectgroup(2)
        femm.hi_movetranslate(0, pre_simulation.parameters()[2])
        femm.hi_clearselected()
        for_def = [];
        mag_field_uppercoil = [];
        mag_field_lowercoil = []
        for i in range(0, pre_simulation.parameters()[0] + 1):
            print('coil position (from centre) : ', pre_simulation.parameters()[2] + pre_simulation.parameters()[1] * i)
            inn_prop['position'][i] = pre_simulation.parameters()[2] + pre_simulation.parameters()[1] * i
            femm.hi_zoom(-2, -50, 50, 50)
            femm.hi_refreshview()
            femm.hi_saveas('VC_ETpf_LIP.feh')
            print('test')
            femm.hi_analyze()
            print('test2')
            femm.hi_loadsolution()

            femm.ho_groupselectblock(2)

            Magn_Force19 = femm.ho_blockintegral(19)
            femm.ho_clearblock()

            mag_prop['Magnet_forces'][i] = Magn_Force19

            mag_fie_x_lower = [];
            mag_fie_y_lower = [];
            gri_x_lower = [];
            gri_y_lower = []
            gri_x = [];
            mag_fie_x = [];
            mag_fie_y = [];
            gri_y = []
            def_force = [];
            mag_field_upper = [];
            mag_field_lower = []
            turns_per_layer = int(position.upp_outcoil()[3])

            for item in range(0, geo.outcoil()[2]):
                for j in range(0, turns_per_layer):
                    grid_pt = [geo.outcoil()[1] + (item * (wire.prop_out()[0] + 2 * wire.prop_out()[1])),
                               (geo.outcoil()[3] + geo.outcoil()[0]) / 2 - (
                                           j * (wire.prop_out()[0] + 2 * wire.prop_out()[1]))]
                    grid_pt_lower = [geo.outcoil()[1] + (item * (wire.prop_out()[0] + 2 * wire.prop_out()[1])),
                                     -(geo.outcoil()[3] + geo.outcoil()[0]) / 2 + (
                                                 j * (wire.prop_out()[0] + 2 * wire.prop_out()[1]))]

                    b_field = femm.mo_getb(grid_pt[0], grid_pt[1]);
                    mag_field_upper.append([grid_pt[0], grid_pt[1], b_field[0], b_field[1]])
                    b_field_lower = femm.mo_getb(grid_pt_lower[0], grid_pt_lower[1]);
                    mag_field_lower.append([grid_pt_lower[0], grid_pt_lower[1], b_field_lower[0], b_field_lower[1]])

                    gri_x.append(grid_pt[0])
                    gri_x_lower.append(grid_pt_lower[0])
                    gri_y.append(grid_pt[1])
                    gri_y_lower.append(grid_pt_lower[1])

                    mag_fie_x.append(b_field[0])
                    mag_fie_y.append(b_field[1])
                    mag_fie_x_lower.append(b_field_lower[0])
                    mag_fie_y_lower.append(b_field_lower[1])

                    g = (2 * np.pi * grid_pt[0] * b_field[0] * sensor.para()[2][0]) / (10 ** 3)
                    g_lower = (2 * np.pi * grid_pt_lower[0] * b_field_lower[0] * sensor.para()[2][1]) / (10 ** 3)
                    def_force.append(g - g_lower)

            # print('default force:', sum(np.array(def_force)), 'updated force:', sum(np.array(imp_force)), 'int_for:')
            mag_field_uppercoil.append(mag_field_upper); mag_field_lowercoil.append(mag_field_lower)
            for_def.append(sum(def_force))
            femm.hi_movetranslate(0, pre_simulation.parameters()[1])
        print('semi-analytical', '\nsemi analytical force :', for_def, '\nfemm force:', mag_prop['Magnet_forces'])

        plt.quiver(gri_x, gri_y, mag_fie_x, np.zeros(turns_per_layer * geo.outcoil()[2]), color='g', label='default',
                   alpha=0.5)
        # plt.quiver(gri_x, gri_y, rot_x, np.zeros(turns_per_layer*geo.outcoil()[2]),color = 'b', label = 'rotated', alpha = 0.3)
        plt.quiver(gri_x_lower, gri_y_lower, mag_fie_x_lower, np.zeros(turns_per_layer * geo.outcoil()[2]), color='g',
                   alpha=0.5)
        plt.legend()
        plt.grid()
        plt.show()

        plt.plot(np.real(inn_prop['position']), abs(mag_prop['Magnet_forces']), 'o-', label='femm')
        plt.plot(np.real(inn_prop['position']), for_def, 'o-', label='semi-analytical')
        plt.ylabel('Force [N]')
        plt.xlabel('Inner Coil Position [mm]')
        plt.legend()
        plt.grid()
        plt.show()

        # if self.save:
        #     np.savez_compressed(self.filename, Design=input_par2, Input_parameters=input_par1,
        #                         coil_config_parameters=coil_con,
        #                         Innercoil_config=position.inncoil(), UpperOutcoil_config=position.upp_outcoil(),
        #                         LowerOutercoil_config=position.low_outcoil(),
        #                         UOC_forces=uppout_prop['force'], LOC_forces=lowout_prop['force'],
        #                         IC_forces=inn_prop['force'],
        #                         Mag_forces=mag_prop['Magnet_forces'], semi_analytical_def=for_def,
        #                         Magnetic_field_upper=mag_field_uppercoil, Magnetic_field_lower=mag_field_lowercoil,
        #                         IC_currents=inn_prop['current'], UOC_currents=uppout_prop['current'],
        #                         LOC_currents=lowout_prop['current'],
        #                         UOC_voltages=uppout_prop['voltage'], LOC_voltages=lowout_prop['voltage'],
        #                         IC_voltages=inn_prop['voltage'],
        #                         IC_positions=abs(inn_prop['position']), IC_flux=inn_prop['flux'],
        #                         UOC_flux=uppout_prop['flux'], LOC_flux=lowout_prop['flux'],
        #                         Inn_Uppout_Lowout_DCR_as_per_catalog=[inn_dc, out_dc, lowout_dc])

        return {'coil_positions': np.real(inn_prop['position']), 'magnet_forces': abs(mag_prop['Magnet_forces'])}

c1 = Analysis(save = False, sim_range=[3, 1, 0], default='no', filename='hj', design_type='jk', input_excitation=[0, 0, [1, 1]],
              materials=['32 AWG', '32 AWG', 'Cobalt'], coil_dimensions={'inner':[24, 11, 6], 'outer':[13.5, 35, 5, 54.5], 'magnet':[40, 10]})
c1.simulate()
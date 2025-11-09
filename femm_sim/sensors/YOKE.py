import femm
import numpy as np
import matplotlib.pyplot as plt
from materials import feed as feed
from models import design as design
from models import coil as coil
from models import femm_model as femm_model
from models import fields as fields

class Analysis:
    def __init__(self, save, sim_range:list, default, filename:str, input_excitation, design_type:None, materials, boundary_conditions, coil_dimensions=None, parameter1=None, simulation_type = None):
        self.save = save
        self.sim_range = sim_range
        self.filename = filename
        self.parameter1 = parameter1
        self.sim_type = simulation_type
        self.design_type = design_type
        self.default = default
        self.des_dim = coil_dimensions
        self.materials = materials
        self.input_excitation = input_excitation
        self.bc = boundary_conditions
    def simulate(self):
        des_type = self.design_type
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
        wire = design.Wiretype(outcoil_material=self.materials[1], inncoil_material=self.materials[0],
                               magnet_material=self.materials[2])
        input_par1 = {'TotalSteps_StepSize(mm)_Offset': self.sim_range, 'innercoil Diameter(mm)_Insulation(mm)_Wiretype': wire.prop_inn(),
                      'Innercoil_current(A)': sensor.para()[0], 'Frequency(Hz)': sensor.para()[1],}
        block = design.Blocks(self.design_type)
        if self.default == 'yes':
            geo = design.Geometry(inn_ht=value[self.design_type]["inn_ht"], inn_rad=value[self.design_type]["inn_rad"], inn_layers=value[self.design_type]["inn_layers"], inn_dist=value[self.design_type]["inn_dist"],
                                  out_ht=value[self.design_type]["out_ht"], out_rad=value[self.design_type]["out_rad"], out_layers=value[self.design_type]["out_layers"], out_dist=value[self.design_type]["out_dist"],
                                  mag_len=value[self.design_type]["mag_len"], mag_dia=value[self.design_type]["mag_dia"], ver_shi=value[self.design_type]["ver_shi"],
                                  innlow_ht=value[self.design_type]["lowinn_ht"], innlow_rad=value[self.design_type]["lowinn_rad"], innlow_layers=value[self.design_type]["lowinn_layers"],
                                  mag_ht= value[self.design_type]["mag_ht"], mag_innrad=value[self.design_type]["mag_inn"], mag_outrad=value[self.design_type]["mag_out"], mag_ver_shi=value[self.design_type]["mag_ver_shi"])
            input_par3 = 'NIKHEF design type (with Yoke) : ' + self.design_type
            input_par2 = in_pa.return_data(self.design_type)
        if self.default == 'no':
            try:
                input_par2 = {'IC_height': self.des_dim['inner'][0], 'IC_radius': self.des_dim['inner'][1], 'IC_layers': self.des_dim['inner'][2], 'IC_distance': self.des_dim['inner'][3],
                              'OC_height': self.des_dim['outer'][0], 'OC_radius': self.des_dim['outer'][1], 'OC_layers': self.des_dim['outer'][2], 'OC_distance': self.des_dim['outer'][3],
                              'mag_len': self.des_dim['magnet'][0], 'mag_dia': self.des_dim['magnet'][1], 'ver_shi': 0,
                              'IC2_height': self.des_dim['inner'][0], 'IC2_radius': self.des_dim['inner'][1], 'IC2_layers': self.des_dim['inner'][2]}
            except:
                input_par2 = {'inn_ht': 18, 'inn_rad': 21, 'inn_layers': 6, 'inn_dist': 0,'lowinn_ht': 23,'lowinn_rad': 21, 'lowinn_layers': 6,
                              'out_ht': 13.5, 'out_rad': self.parameter1[0], 'out_layers': 5, 'out_dist': 14.5, 'mag_len': 0, 'mag_dia': 0, 'ver_shi': 0,
                            'mag_inn':31.65, 'mag_out':44.45, 'mag_ht':6.35,'mag_ver_shi':0, 'inner_distance':60.5, 'yoke_inn_dia':8}
            geo = design.Geometry(inn_ht=input_par2['inn_ht'],  inn_rad=input_par2['IC_radius'], inn_layers=input_par2['IC_layers'], inn_dist=input_par2['IC_distance'],
                                  out_ht=input_par2['OC_height'], out_rad=input_par2['OC_radius'], out_layers=input_par2['OC_layers'], out_dist=input_par2['OC_distance'],
                                  mag_ht=input_par2['mag_len'], mag_innrad=input_par2['mag_inn'],mag_outrad=input_par2['mag_out'],
                                  ver_shi=input_par2['ver_shi'], innlow_ht=input_par2['IC2_height'], innlow_rad=input_par2['IC2_radius'], innlow_layers=input_par2['IC2_layers'])
            input_par3 = 'not a priliminary NIKHEF design'
        Low_Inncoil_OutRadius = geo.Low_Inncoil()[1] + ((wire.prop_inn()[0] + wire.prop_inn()[1] * 2) * geo.Low_Inncoil()[2])
        Low_Inncoil_Lowend = -1 * (geo.Low_Inncoil()[3] + (geo.Low_Inncoil()[0]/2))
        Low_Inncoil_Uppend = Low_Inncoil_Lowend + geo.Low_Inncoil()[0]
        Low_Inncoil_NrWind_p_Layer = (geo.Low_Inncoil()[0]) / (wire.prop_inn()[0] + wire.prop_inn()[1] * 2)
        Low_Inncoil_NrWindings = Low_Inncoil_NrWind_p_Layer * geo.Low_Inncoil()[2]
        Low_Inncoil_Circuit = "Low_Inncoil_Circuit"
        Low_Inn_config = [Low_Inncoil_OutRadius, Low_Inncoil_Lowend, Low_Inncoil_Uppend,Low_Inncoil_NrWind_p_Layer, Low_Inncoil_NrWindings, Low_Inncoil_Circuit]
        coil_con = ['Coil_OutRadius', 'Coil_Lowend', 'Coil_Uppend', 'Coil_turns(per layer)', 'Coil_turns total',
                    'coil_name']

        full_length = (pre_simulation.parameters()[0] * pre_simulation.parameters()[1]) + pre_simulation.parameters()[
            2] + Low_Inncoil_Uppend
        if full_length < self.bc[0]:
            bc_con = self.bc
        else:
            bc_con = [full_length + 50, self.bc[1], self.bc[2], full_length + 150, self.bc[4], self.bc[5], self.bc[6]]

        class Yoke:
            #des_type = self.design_type
            def __init__(self):
                pass
            def block1(self):
                b1_lowend = -1 * (geo.Low_Inncoil()[3] + (block.dimension('b3')[1]) / 2 + block.dimension('b4')[1] + geo.mag_yoke()[0] + block.dimension('b6')[1])
                b1_uppend = b1_lowend + block.dimension('b1')[1]
                print(block.yoke_dim[des_type]['yoke_innrad'])
                b1_innrad = block.yoke_dim[des_type]['yoke_innrad']
                b1_outrad = b1_innrad + block.dimension('b1')[0]
                b1_dim = [b1_innrad, b1_uppend, b1_outrad, b1_lowend]
                return b1_dim

            def block2(self):
                b2_innrad = block.yoke_dim[des_type]['yoke_innrad'] + block.dimension('b1')[0]   #block.b1_l
                b2_uppend = block.yoke_dim[des_type]['yoke_uppend']
                b2_lowend = b2_uppend - block.dimension('b2')[1]    #block.b2_h
                b2_outrad = b2_innrad + block.dimension('b2')[0]    #block.b2_l
                b2_dim = [b2_innrad, b2_uppend, b2_outrad, b2_lowend]
                return b2_dim

            def block3(self):
                b3_innrad = geo.Low_Inncoil()[1] + block.yoke_dim[des_type]['yoke_inngap']
                b3_outrad = b3_innrad + block.dimension('b3')[0]    #block.b3_l
                b3_uppend = block.yoke_dim[des_type]['yoke_uppend']
                b3_lowend = b3_uppend - block.dimension('b3')[1]    #block.b3_h
                b3_dim = [b3_innrad, b3_uppend, b3_outrad, b3_lowend]
                return b3_dim

            def block4(self):
                b4_innrad = block.yoke_dim[des_type]['yoke_outrad'] - block.dimension('b4')[0] #block.b4_l
                b4_uppend = block.yoke_dim[des_type]['yoke_uppend'] - block.dimension('b3')[1] #block.b3_h
                b4_outrad = b4_innrad + block.dimension('b4')[0]    #block.b4_l
                b4_lowend = b4_uppend - block.dimension('b4')[1]    #block.b4_h
                b4_dim = [b4_innrad, b4_uppend, b4_outrad, b4_lowend]
                return b4_dim

            def block5(self):
                b5_innrad = block.yoke_dim[des_type]['yoke_outrad'] - geo.mag_yoke()[1] - block.dimension('b5')[0]   #block.b5_l
                b5_uppend = block.yoke_dim[des_type]['yoke_uppend'] - block.dimension('b3')[1] - block.dimension('b4')[1] #block.b3_h - block.b4_h
                b5_outrad = b5_innrad + block.dimension('b5')[0]    #block.b5_l
                b5_lowend = b5_uppend - block.dimension('b5')[1]    #block.b5_h
                b5_dim = [b5_innrad, b5_uppend, b5_outrad, b5_lowend]
                return b5_dim

            def block6(self):
                b6_innrad = block.yoke_dim[des_type]['yoke_outrad'] - geo.mag_yoke()[1]
                b6_uppend = block.yoke_dim[des_type]['yoke_uppend']  - geo.mag_yoke()[0]- block.dimension('b3')[1] - block.dimension('b4')[1]  #block.b3_h - block.b4_h
                b6_outrad = b6_innrad + block.dimension('b6')[0]    #block.b6_l
                b6_lowend = b6_uppend - block.dimension('b6')[1]    #block.b6_h
                b6_dim = [b6_innrad, b6_uppend, b6_outrad, b6_lowend]
                return b6_dim

            def block7(self):
                b7_innrad = block.yoke_dim[des_type]['yoke_innrad'] + block.dimension('b1')[0] #block.b1_l
                b7_outrad = b7_innrad + block.dimension('b7')[0]    #block.b7_l
                b7_lowend = block.yoke_dim[des_type]['yoke_uppend']- geo.mag_yoke()[0] - block.dimension('b3')[1]-block.dimension('b4')[1]-block.dimension('b6')[1]   #block.b3_h - block.b4_h  - block.b6_h
                b7_uppend = b7_lowend + block.dimension('b7')[1]    #block.b7_h
                b7_dim = [b7_innrad, b7_uppend, b7_outrad, b7_lowend]
                return b7_dim

            def mag(self):
                mag_innrad = block.yoke_dim[des_type]['yoke_outrad'] - geo.mag_yoke()[1]
                mag_outrad = mag_innrad + geo.mag_yoke()[1]
                mag_uppend = block.yoke_dim[des_type]['yoke_uppend'] - block.dimension('b3')[1] - block.dimension('b4')[1]
                mag_lowend = mag_uppend - geo.mag_yoke()[0]
                # mag_lowend = block.yoke_dim[des_type]['yoke_uppend']- (block.dimension('b1')[1])/2 - (geo.mag_yoke()[0])/2
                # mag_uppend = block.yoke_dim[des_type]['yoke_uppend'] - (block.dimension('b1')[1])/2 + (geo.mag_yoke()[0])/2
                ring_magnet_dim = [mag_innrad, mag_uppend, mag_outrad, mag_lowend]
                return ring_magnet_dim

        yoke = Yoke()
        material = wire.yoke_mat()
        sim_gap = 0.01 #gaps btw the blocks for simulation
        block_positions = [yoke.block1(), yoke.block2(), yoke.block3(), yoke.block4(), yoke.block5(), yoke.block6(), yoke.block7(), yoke.mag()]
        block_innrad = [parameter[0] for parameter in block_positions]; block_outrad = [parameter[2] for parameter in block_positions]
        block_uppend = [parameter[1] for parameter in block_positions]; block_lowend = [parameter[3] for parameter in block_positions]
        block_rad = np.array(block_outrad) - np.array(block_innrad)
        block_ht = abs(np.array(block_uppend) - np.array(block_lowend))
        block_dims = {'block heights':block_ht, 'block_radius':block_rad, 'block_uppend_pos':block_uppend, 'block_lowend_pos':block_lowend}


        print('inner coil material - ', wire.inncoil_material, ', outer coil material - ', wire.outcoil_material,
              ', magnet material - ', wire.magnet_material, ', yoke material - ', material)
        print('excitations :', sensor.para())
        print('geometry :', input_par2)
        inncoil_str = femm_model.Femm_coil(x1=geo.Low_Inncoil()[1], y1=Low_Inncoil_Uppend, x2=Low_Inncoil_OutRadius,
                                           y2=Low_Inncoil_Lowend, circ_name=Low_Inncoil_Circuit,
                                           circ_current=sensor.para()[0], circ_type=1,
                                           material=wire.inncoil_material, edit_mode=4, group=1,
                                           label1=wire.prop_inn()[1],
                                           label2=geo.Low_Inncoil()[1], blockname=wire.prop_inn()[2],
                                           turns_pr_layer=Low_Inncoil_NrWind_p_Layer)
        print("startpoint is ", geo.Low_Inncoil()[1])
        block1 = femm_model.Femm_block(x1=yoke.block1()[0], y1=yoke.block1()[1], x2=yoke.block1()[2],
                                           y2=yoke.block1()[3], material=material, edit_mode=4, group=3,
                                           label1=block.dimension('b1')[0], label2=block.dimension('b1')[1])
        print('simulating block 2')
        block2 = femm_model.Femm_block(x1=yoke.block2()[0]+sim_gap, y1=yoke.block2()[1], x2=yoke.block2()[2],
                                       y2=yoke.block2()[3], material=material, edit_mode=4, group=4,
                                       label1=block.dimension('b2')[0], label2=block.dimension('b2')[1])
        print('simulating block 3')
        block3 = femm_model.Femm_block(x1=yoke.block3()[0], y1=yoke.block3()[1], x2=yoke.block3()[2],
                                       y2=yoke.block3()[3]+sim_gap, material=material, edit_mode=4, group=5,
                                       label1=block.dimension('b3')[0], label2=block.dimension('b3')[1])
        print('simulating block 4')
        block4 = femm_model.Femm_block(x1=yoke.block4()[0], y1=yoke.block4()[1], x2=yoke.block4()[2],
                                       y2=yoke.block4()[3]+sim_gap, material=material, edit_mode=4, group=6,
                                       label1=block.dimension('b4')[0], label2=block.dimension('b4')[1])
        print('simulating block 5')
        block5 = femm_model.Femm_block(x1=yoke.block5()[0], y1=yoke.block5()[1], x2=yoke.block5()[2]-sim_gap,
                                       y2=yoke.block5()[3], material=material, edit_mode=4, group=7,
                                       label1=block.dimension('b5')[0], label2=block.dimension('b5')[1])
        print('simulating block 6')
        block6 = femm_model.Femm_block(x1=yoke.block6()[0], y1=yoke.block6()[1]-sim_gap, x2=yoke.block6()[2],
                                       y2=yoke.block6()[3], material=material, edit_mode=4, group=8,
                                       label1=block.dimension('b6')[0], label2=block.dimension('b6')[1])
        print('simulating block 7')
        block7 = femm_model.Femm_block(x1=yoke.block7()[0]+sim_gap, y1=yoke.block7()[1], x2=yoke.block7()[2]-sim_gap,
                                       y2=yoke.block7()[3], material=material, edit_mode=4, group=9,
                                       label1=block.dimension('b7')[0], label2=block.dimension('b7')[1])
        print('simulating magnet')
        magnet = femm_model.Femm_magnet(x1=yoke.mag()[0], y1=yoke.mag()[1], x2=yoke.mag()[2],
                                       y2=yoke.mag()[3], material=wire.mag_mat(), edit_mode=4, group=2,
                                       label1=geo.mag_yoke()[1]/2, label2=geo.mag_yoke()[0])
        bc = femm_model.Femm_bc(AirSpaceRadius_1=bc_con[0], material1=bc_con[1], grid1=bc_con[2],
                                AirSpaceRadius_2=bc_con[3], material2=bc_con[4], grid2=bc_con[5], BC_Name=bc_con[6],
                                BC_Group=10)
        bc_conditions_mesh = {'region1_radius_material_grid': [bc_con[0], bc_con[1], bc_con[2]],
                              'region2_radius_mesh_material': [bc_con[3], bc_con[4], bc_con[5]]}
        print('boundary : ', bc_conditions_mesh)

        Magnet_Forces1 = np.zeros(self.sim_range[0] + 1)
        Magnet_Forces_m = np.zeros(self.sim_range[0] + 1)
        Magnet_Forces_c = np.zeros(self.sim_range[0] + 1)
        Magnet_Forces2 = np.zeros(self.sim_range[0] + 1)
        Magnet_Forces3 = np.zeros(self.sim_range[0] + 1)
        Magnet_Forces4 = np.zeros(self.sim_range[0] + 1)
        Magnet_Forces5 = np.zeros(self.sim_range[0] + 1)
        Magnet_Forces6 = np.zeros(self.sim_range[0] + 1)
        Magnet_Forces7 = np.zeros(self.sim_range[0]+ 1)
        tot_block = np.zeros(self.sim_range[0] + 1)
        InnCoil_Positions = np.zeros(self.sim_range[0] + 1)

        res = coil.Coil_prop(pre_simulation.parameters()[0])
        inn2_prop = res.gen_coil()
        move_group = femm_model.Femm_move(groups=[1], x_dist=0, y_dist=pre_simulation.parameters()[2])

        for i in range(0, self.sim_range[0] + 1):
            print(pre_simulation.parameters()[2] + pre_simulation.parameters()[1] * i)
            InnCoil_Positions[i] = pre_simulation.parameters()[2] + pre_simulation.parameters()[1] * i
            femm.mi_zoom(-2, -50, 50, 50)
            femm.mi_refreshview()
            femm.mi_saveas('Yoke position_ETpf_LIP.fem')
            femm.mi_analyze()
            femm.mi_loadsolution()

            femm.mo_groupselectblock(2)
            Magn_Force_m = femm.mo_blockintegral(19)
            femm.mo_clearblock()
            Magnet_Forces_m[i] = Magn_Force_m
            femm.mo_groupselectblock(1)
            Magn_Force_c = femm.mo_blockintegral(19)
            femm.mo_clearblock()
            Magnet_Forces_c[i] = Magn_Force_c

            femm.mo_groupselectblock(3)
            Magn_Force1 = femm.mo_blockintegral(19)
            femm.mo_clearblock()
            Magnet_Forces1[i] = Magn_Force1
            femm.mo_groupselectblock(4)
            Magn_Force2 = femm.mo_blockintegral(19)
            femm.mo_clearblock()
            Magnet_Forces2[i] = Magn_Force2
            femm.mo_groupselectblock(5)
            Magn_Force3 = femm.mo_blockintegral(19)
            femm.mo_clearblock()
            Magnet_Forces3[i] = Magn_Force3
            femm.mo_groupselectblock(6)
            Magn_Force4 = femm.mo_blockintegral(19)
            femm.mo_clearblock()
            Magnet_Forces4[i] = Magn_Force4
            femm.mo_groupselectblock(7)
            Magn_Force5 = femm.mo_blockintegral(19)
            femm.mo_clearblock()
            Magnet_Forces5[i] = Magn_Force5
            femm.mo_groupselectblock(8)
            Magn_Force6 = femm.mo_blockintegral(19)
            femm.mo_clearblock()
            Magnet_Forces6[i] = Magn_Force6
            femm.mo_groupselectblock(9)
            Magn_Force7 = femm.mo_blockintegral(19)
            femm.mo_clearblock()
            Magnet_Forces7[i] = Magn_Force7

            for j in range(3, 10):
                femm.mo_groupselectblock(j)

            total = femm.mo_blockintegral(19)
            femm.mo_clearblock()
            tot_block[i] = total

            InnCoil2_I, InnCoil2_V, InnCoil2_FluxLink = femm.mo_getcircuitproperties(Low_Inn_config[5])
            inn2_prop['voltage'][i] = InnCoil2_V
            inn2_prop['current'][i] = InnCoil2_I
            inn2_prop['flux'][i] = InnCoil2_FluxLink

            move_group = femm_model.Femm_move(groups=[1], x_dist=0, y_dist=pre_simulation.parameters()[1])
        print(np.array(Magnet_Forces_m))
        plt.style.use(['science', 'grid', 'notebook'])
        plt.plot(np.array(InnCoil_Positions), np.array(tot_block), "o--", label="block")
        plt.plot(np.array(InnCoil_Positions), np.array(Magnet_Forces_c), "o--", label="inn")
        plt.plot(np.array(InnCoil_Positions), np.array(Magnet_Forces_m), "o--", label="mag")
        plt.title("F0 mirror tower(LVDT with Yoke) VC force \n 1A DC excitation")
        plt.ylabel('Normalised force [N/A]')
        plt.xlabel('Relative (upper) inner Coil Position [mm]')
        plt.legend()
        plt.show()

        if self.save:
            np.savez_compressed(self.filename,Design_type=input_par3, Design_parameters = input_par2, Input_parameters = input_par1, coil_config_parameters = coil_con, Low_Innercoil_config = Low_Inn_config,
                                IC1_positions = InnCoil_Positions, IC2_voltages = inn2_prop['voltage'], IC2_currents = inn2_prop['current'],IC2_flux = inn2_prop['flux'], Boundary_conditions = bc_conditions_mesh,
                                IC2_forces = Magnet_Forces_c, Mag_forces = Magnet_Forces_m, block_forces = tot_block, block_dimensions = block_dims, b7_forces = Magnet_Forces7,
                                b1_forces = Magnet_Forces1, b2_forces = Magnet_Forces2, b3_forces = Magnet_Forces3, b4_forces = Magnet_Forces4, b5_forces = Magnet_Forces5, b6_forces = Magnet_Forces6
                                )

        return {'coil_positions': InnCoil_Positions, 'magnet_forces': Magnet_Forces_m}
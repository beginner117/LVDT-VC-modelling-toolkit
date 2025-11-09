import simulation.femm_simulation as femm_simulation

sim_code = femm_simulation.Position_sensor(sensor_type = ['LVDT'], save=False, sim_range={'steps_size_offset':[[9, 0.5, -5]]},
                               data = {'filename(s)':['trial'], 'is default':['no'], 'design or parameter':['none']}
                                 , material_prop=['32 AWG_AI','31 AWG_AO', 'N40'], dimensions={'inner':[24, 11, 6], 'outer':[13.5, 35, 7, 54.5], 'magnet':[40, 10]})
a = sim_code.execute([0.005, 10000, [0, 0]])


# sensor_type = list with names of sensors that should be simulated
    # available types (i)LVDT (with maxwell pair config), (ii)VC (with maxwell pair config), (iii)VC_only (traditional actuators with a coil and a magnet)

# save = 'True' to save all the simulated files or 'False' to not save the files
    # True to get all the information of the simulated file. (recommended)

# sim_range = list containg a list (nested list) of total steps, grid size and offset. Ex - [[10,1,-5]]
# filename(s) = name(s) of the simulated file(s) in a list
# is default = 'no'
# design or parameter = 'None'

# for the sensor type 'VC_only',
# material_prop = list containing (i) Coil material (ii) magnet material
    #Materials are found in the last part (from line 40) in 'feed.py' file in material module. More materials can be added as per the user's requirements following the order used in the feed.py file
# dimensions = dictionary with the coil geometry with 'outer', 'magnet' as keys and corresponding dimensions (in mm)in lists as values.
#            Values of the keys are height, radius, layers (for the 'outer') and length, diameter (in mm) for the magnet
#            Example - {'outer':[13.5, 35, 7], 'magnet':[40, 10]}

# for the sensor type 'LVDT' or 'VC',
# material_prop = list containing (i) inner coil material (ii) outer coil material (iii) magnet material
    ##Materials are found in the last part (from line 40) in 'feed.py' file in material module. More materials can be added as per the user's requirements following the order used in the feed.py file
# dimensions = dictionary with the coil geometry with 'inner', 'outer', 'magnet' as keys and corresponding dimensions (in mm)in lists as values.
#            Values of the keys are height, radius, layers, distance (for the 'outer') and height, radius, layers (for the inner) and length, diameter (in mm) for the magnet
#            Example - {'inner':[24, 11, 6], 'outer':[13.5, 35, 7, 54.5], 'magnet':[40, 10]}
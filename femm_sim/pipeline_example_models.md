The data files obtained by running below scripts are stored in '.npz' format.  

Example (for three simultaneous simulations of LVDT, VC, VC_only)

    simulation = femm_simulation.Position_sensor(sensor_type=['LVDT', 'VC', 'VC_only'], save=False, sim_range={'steps_size_offset':[[20, 1, -10], [10, 1, -5], [20, 1, -10]]},
                                    data = {'filename(s)':['trail1', 'trial2', 'trail3'], 'is default':['yes', 'no', 'yes'], 'design or parameter':['A', 3, 'I']})
    simulation.execute() 

Example to compute the mutual inductances of the coils

    simulation = femm_simulation.Position_sensor(sensor_type=['LVDT_mutual_inductance', 'LVDT_mutual_inductance'], save=False, sim_range={'steps_size_offset':[[20, 1, -10], [20, 1, -10]]},
                                    data = {'filename(s)':['trail1', 'trial2'], 'is default':['yes', 'no'], 'design or parameter':['A', 3]})
    simulation.execute()

Example to compute the correction factor of the coils

    simulation = femm_simulation.Position_sensor(sensor_type=['LVDT_corrected', 'LVDT_corrected'], save=False, sim_range={'steps_size_offset':[0, 0]]},
                                    data = {'filename(s)':['trail1', 'trial2'], 'is default':['yes', 'no'], 'design or parameter':['A', 3]})
    simulation.execute()

Example to compute the response semi-analytically (i.e, just by using magnetic fields from FEMM)

    analytical = femm_simulation.Position_sensor(sensor_type=['VC_fields'], save=False, sim_range={'steps_size_offset':[[10,1,-5]},
                                    data = {'filename(s)':['mag_field1'], 'is default':['yes'], 'design or parameter':['A']})
    analytical.execute()

The above code saves the magnetic field information in an '.npz' file. (It takes time) 

Below is the code to get the outer coil flux from the magnetic field files(obtained from the above script). The outer coil flux should be saved as an '.npz' file to compute the response.
The mandatory input arguments to save the '.npz' flux files are the offset of the outer coil and the file name

    compute = analytical_simulation.LVDT('mag_field1.npz')
    flux = compute.outer_flux(0, 'flux_file1')


Here is the final script to calculate the outer coil response from the flux file (saved as explained above). 
mandatory input argument here is the movement range of the inner coil in 'mm'. (2.5 indicates 2.5mm motion of inner coil on either sides (i.e, 5mm in total) of reference-0 position.)

    calculate = analytical_simulation.LVDT('flux_file1.npz')
    calculate.response(2.5)

    
Example to compute the voltages, forces numerically
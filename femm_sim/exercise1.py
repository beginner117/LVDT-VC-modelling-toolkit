# import sys
# sys.path.append('C:\\Users\\kumar\\PycharmProjects\\lvdtsimulations\\Kumar\\modules\\femm_sim')

import simulation.femm_simulation as femm_simulation


#[[no.of steps, step size, initial offset]]

currents = [0.01, 0.02, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1]
currents = [16, 18, 20, 22, 24]
currents = ['A_1']
for item in currents:
    input_para = {'sensor_type' : ['LVDT'], 'SaveFile' :False,
                'file_names' : [item+'_vc'],
                'default_design' : ['no','no','no','no', 'no','yes','yes','yes', 'yes','yes'],
                'type_or_parameter_OR_angle' : [item,'I','I','I','I','I','I','I','I','I','A_1','A_1','A_1'], #2737.03 - 2503.67j, 2743.93 - 2501.63j, -2743.93+2501.63j
                'TotalSteps_StepSize_Offset_OR_offset' : [[2, 1, -1], [20, 0.5, -5],  [20, 0.5, -5], [20, 0.5, -5], [20, 0.5, -5]]}
    coil_geo = {'inner':[24, 11, 6], 'outer':[13.5, 35, 5, 54.5], 'magnet':[0, 0]}
    sim_code = femm_simulation.Position_sensor(sensor_type = input_para['sensor_type'], save=input_para['SaveFile'], sim_range={'steps_size_offset':input_para['TotalSteps_StepSize_Offset_OR_offset']},
                                   data = {'filename(s)':input_para['file_names'], 'is default':input_para['default_design'], },
                               dimensions=coil_geo)
    a = sim_code.execute()
# print(a)
# #for semi analytical, put the offset to be 0 above, else wrong calculation
#
# with open('paths.txt', 'r') as file:
#     content = file.read()
# print(content)
#'design or parameter':input_para['type_or_parameter_OR_angle']
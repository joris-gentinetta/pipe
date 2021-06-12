######################################
animals = ['11'] # set of animals, 2 char string, example animal 9: '09'
treatment = 'medication' # one of ['none', 'saline', 'medication']
score = 'treatment_score'  # one of:         ['ezm_closed_score', 'ezm_transition_score', 'of_corners_score', 'of_middle_score', 'treatment_score']
threshold = 20                      # recommended: [0                 ,  0                    ,  0                ,  0            , 20   ]
data_separations = ['under_threshold_all', 'over_threshold_all', 'under_threshold_plus', 'over_threshold_plus',
                   'under_threshold_minus', 'over_threshold_minus']  # selection of ['under_threshold_all', 'over_threshold_all', 'under_threshold_plus', 'over_threshold_plus',
# 'under_threshold_minus', 'over_threshold_minus']

#significance plus/minus: plus['ezm_closed_score': firing rate higer in closed area,
# 'ezm_transition_score': firing rate higher in transition zones, 'of_corners_score': firing rate higher in corners,
# 'of_middle_score': firing rate higher in the middle, 'treatment_score': firing rate higher before treatment]

toplot = ['phase']
# selection of: ['circle', 'grid', 'arms', 'corners', 'transitions', 'phase']
transition_modes = ['open_closed_entrytime']
# selection of: ['open_closed_entrytime', 'open_closed_exittime', 'closed_open_entrytime', 'closed_open_exittime',
# 'lingering_entrytime', 'lingering_exittime', 'prolonged_open_closed_entrytime', 'prolonged_open_closed_exittime',
# 'prolonged_closed_open_entrytime', 'prolonged_closed_open_exittime', 'withdraw_entrytime', 'withdraw_exittime',
# 'nosedip_starttime', 'nosedip_stoptime']
phase_modes = ['theta_phase_OFT', 'theta_phase_EZM', 'theta_phase_before', 'theta_phase_after']
# selection of: ['theta_phase_OFT', 'theta_phase_EZM', 'theta_phase_before', 'theta_phase_after']
delete_plot_folder = False
show = True
save = False
alert_when_done = True
######################################
import copy
import pandas as pd
import os
import shutil
import time
import numpy as np
import pickle5 as pkl
import treatment_plots
from utils import alert

treatment_dict = {'none': '1', 'saline': '2', 'medication': '3'}
_ , animals = (list(t) for t in zip(*sorted(zip([int(animal) for animal in animals], animals))))
days = [treatment_dict[treatment] + animal for animal in animals]

sorter = 'circus'
data_folder = r'E:/anxiety_ephys/'
score_folder = data_folder + 'multiple_day_plots/' + treatment + '/' + score + '/'
threshold_folder = score_folder + 'threshold_' + str(threshold) + '/'
plot_folder = threshold_folder + '-'.join(animals) + '/'
framerate = 50
if not os.path.exists(score_folder):
    os.mkdir(score_folder)
if not os.path.exists(threshold_folder):
    os.mkdir(threshold_folder)
if os.path.exists(plot_folder):
    if delete_plot_folder:
        shutil.rmtree(plot_folder, ignore_errors=True)
        time.sleep(3)
        os.mkdir(plot_folder)
else:
    os.mkdir(plot_folder)



archives = []
for day in days:
    target_folder = data_folder + day + '/' + sorter + '/'
    archive = pd.read_pickle(target_folder + 'archive.pkl')
#    archive_index = archive.index.tolist()
    archive.drop(255, axis='index')
 #   archive.index = [day + '_' + str(old_index) for old_index in archive_index]
    archives.append(archive)
archive = pd.concat(archives, ignore_index=True, join= 'inner')
plusminus = score[:-6]
# scorer = archive.loc[:,('characteristics', score)]
# n1 = archive.loc[:,('characteristics', score)].values < threshold
# n2 = archive.index != -1

if plusminus == 'treatment':
    mean_before = archive.loc[:, ('characteristics', 'mean_before')].values
    mean_after = archive.loc[:, ('characteristics', 'mean_after')].values
    plus_minus_values = (mean_before-mean_after)*100/mean_before
    score_values = np.abs(plus_minus_values)
else:
    score_values = archive.loc[:, ('characteristics', score)].values
    plus_minus_values = archive.loc[:,('characteristics',plusminus)].values

under_threshold_all = archive.loc[score_values < threshold]
under_threshold_plus = archive.loc[
    np.logical_and(score_values < threshold, plus_minus_values > 0)]
under_threshold_minus = archive.loc[
    np.logical_and(score_values < threshold, plus_minus_values <= 0)]
over_threshold_all = archive.loc[score_values >= threshold]
over_threshold_plus = archive.loc[
    np.logical_and(score_values >= threshold, plus_minus_values > 0)]
over_threshold_minus = archive.loc[
    np.logical_and(score_values >= threshold, plus_minus_values <= 0)]

for data_separation in data_separations:
    if data_separation == 'under_threshold_all':
        data = under_threshold_all
    elif data_separation == 'over_threshold_all':
        data = over_threshold_all
    elif data_separation == 'under_threshold_plus':
        data = under_threshold_plus
    elif data_separation == 'over_threshold_plus':
        data = over_threshold_plus
    elif data_separation == 'under_threshold_minus':
        data = under_threshold_minus
    elif data_separation == 'over_threshold_minus':
        data = over_threshold_minus
    else:
        raise Exception('invalid data separation entry: ' + data_separation)
    if 'circle' in toplot:
        treatment_plots.plot_circle(plot_folder, data.loc[:, 'ROI_EZM'], data_separation, show=show, save=save)
    if 'grid' in toplot:
        treatment_plots.plot_grid(plot_folder, data.loc[:, 'ROI_OF'], data_separation, show=show, save=save)
    if 'arms' in toplot:
        treatment_plots.plot_arms(plot_folder, data.loc[:, 'ROI_EZM'], data_separation, show=show, save=save)
    if 'corners' in toplot:
        treatment_plots.plot_corners(plot_folder, data.loc[:, 'ROI_OF'], data_separation, show=show, save=save)
    if 'transitions' in toplot:
        for transition_mode in transition_modes:
            treatment_plots.plot_transitions(plot_folder, data.loc[:, transition_mode], data_separation,
                                             mode=transition_mode, show=show, save=save)

    if 'phase' in toplot:
        for phase_mode in phase_modes:

            column_names = data.columns.levels[0].values
            pad_columns = [column_name for column_name in column_names if column_name[:len(phase_mode)] == phase_mode]

            mean_theta = np.zeros((data.shape[0], data.loc[:,pad_columns[0]].shape[1]), dtype=np.float32)
            counter = 0
            for pad_column in pad_columns :
                mean_theta += data.loc[:,pad_column].values.astype(np.float32)
                counter+=1
            mean_theta = mean_theta // counter

            treatment_plots.plot_phase(plot_folder, mean_theta, data_separation, phase_mode,
                                       show=show, save=save)
            if len(animals) == 1:
                treatment_plots.plot_phase_all_pads(plot_folder, data.loc[:, pad_columns], pad_columns, data_separation, phase_mode,
                                                    show=show, save=save)


print('treatment_analysis done for animals: {}, treatment: {}, score: {}, threshold: {}'.format(animals, treatment, score, threshold))
if alert_when_done:
    alert()
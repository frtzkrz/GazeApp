import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from typing import Any

def plot_ntcp_curve(rois, metrics, complications, path='ntcp_data/') -> None:   

    for roi, metric, complication in zip(rois, metrics, complications):
        f_name = path+f"{roi}_{metric}_{complication}"

        data_line = pd.read_csv(filepath_or_buffer=f_name + '.csv', header=None)
        data_line.sort_values(by=data_line.columns[0], inplace=True)
        data_upper = pd.read_csv(filepath_or_buffer=f_name + '_upper.csv', header=None)
        data_upper.sort_values(by=data_upper.columns[0], inplace=True)
        data_lower = pd.read_csv(filepath_or_buffer=f_name + '_lower.csv', header=None)
        data_lower.sort_values(by=data_lower.columns[0], inplace=True)

        plt.figure()
        plt.plot(data_line[0], data_line[1], label='Mean Line', color='green')
        plt.plot(data_upper[0], data_upper[1], label='Upper Line', color='lightgreen')
        plt.plot(data_lower[0], data_lower[1], label='Lower Line', color='lightgreen')
        plt.title(f'NTCP Curve for {complication.replace("_", " ").title()}')
        plt.savefig(f'{f_name}.png')
        plt.show()
    
def find_name(keyword, names) -> Any | None:
    for name in names:
        if keyword in name:
            return name
    return None

def find_ntcp(keyword, metric_value, names, path='ntcp_data/') -> Any | None:
    name = find_name(keyword, names)
    if name is None:
        return None
    
    f_name = path + name
    data_line = pd.read_csv(filepath_or_buffer=f_name + '.csv', header=None)
    data_line.sort_values(by=data_line.columns[0], inplace=True)

    data_upper = pd.read_csv(filepath_or_buffer=f_name + '_upper.csv', header=None)
    data_upper.sort_values(by=data_upper.columns[0], inplace=True)
    data_lower = pd.read_csv(filepath_or_buffer=f_name + '_lower.csv', header=None)
    data_lower.sort_values(by=data_lower.columns[0], inplace=True)

    
    
    ntcp_upper = np.interp(metric_value, data_upper[0], data_upper[1])
    ntcp_lower = np.interp(metric_value, data_lower[0], data_lower[1])
    ntcp_value = np.interp(metric_value, data_line[0], data_line[1])
    return ntcp_value

def main() -> None:
    path = 'ntcp_data/'
    rois = ['ciliary_body', 'cornea', 'macula', 'macula', 'optic_disc', 'retina', 'retina']
    metrics = ['v26', 'd20', 'd2', 'd2', 'd20', 'd20', 'v52']
    
    complications = ['cataract', 
                     'neovascular_glaucoma', 
                     'loss_pre_treatment_visual_acuity', 
                     'visual_acuity_det', 
                     'optic_neuropathy', 
                     'maculopathy', 
                     'retinal_detachment']
    
    names = [roi+"_"+metric+"_"+complication for roi, metric, complication in zip(rois, metrics, complications)]
    print(names)

    plot_ntcp_curve(rois=rois, metrics=metrics, complications=complications, path=path)
    

if __name__ == "__main__":
    main()
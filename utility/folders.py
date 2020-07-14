import datetime
import os


def get_experiment_folders(list_of_paths):
    all_paths = list()
    for path in list_of_paths:
        all_paths.extend(get_csv_folders(path))
    return all_paths


def get_group_file_paths(list_of_paths):
    all_paths = list()
    for path in list_of_paths:
        for (dirpath, dirnames, filenames) in os.walk(path):
            all_paths += [os.path.join(dirpath, file) for file in filenames if file.endswith('.gpkl')]
    return all_paths


def get_csv_folders(path):
    path_list = list()
    if os.path.isfile(path):
        return []
    # add dir to pathlist if it contains .txt files
    if len([f for f in os.listdir(path)
            if f.endswith('.csv') and (os.path.basename(f).startswith('IV_Curve_') or
                                       os.path.basename(f).startswith('IV Characterizer'))]) > 0:
        path_list.append(os.path.normpath(path))
    for d in os.listdir(path):
        new_path = os.path.join(path, d)
        if os.path.isdir(new_path):
            path_list += get_csv_folders(new_path)
    return path_list


def get_kickstart_paths(path):
    path_list = [f for f in os.listdir(path) if os.path.basename(f).startswith('IV Characterizer')]
    return path_list


def get_number_of_csv(path):
    # returns number of csv files in the directory
    n_csv = [0, 0]
    if os.path.isdir(path):
        for entry in os.scandir(path):
            if os.path.basename(entry).startswith('IV_Curve_') and entry.path.endswith(".csv"):
                n_csv[0] += 1
            elif os.path.basename(entry).startswith('IV Characterizer') and entry.path.endswith(".csv"):
                n_csv[1] += 1
        return n_csv
    else:
        return [-1, -1]


def get_datetime(path):
    d = datetime.datetime.fromtimestamp(os.path.getctime(path))
    return d.replace(microsecond=0)

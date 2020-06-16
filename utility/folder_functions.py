import datetime
import os


def get_list_of_csv(path):
    # create a list of file and sub directories
    # names in the given directory
    all_files = list()
    if not path:  # no path set - return empty list
        pass
    elif os.path.isdir(path):
        # Iterate over all the entries
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if full_path.endswith('.csv'):
                all_files.append(os.path.normpath(full_path))
        if len(all_files) == 1:  # if there were no csv files in the folder, return empty instead
            all_files = list()
    elif path.endswith('.csv'):
        all_files.append(os.path.normpath(path))
    return all_files


def get_number_of_csv(path):
    # returns number of csv files in the directory
    n_csv = 0
    if os.path.isdir(path):
        for entry in os.scandir(path):
            if os.path.basename(entry).startswith('IV_Curve_') and entry.path.endswith(".csv"):
                n_csv += 1
        return n_csv
    else:
        return -1


def get_datetime(path):
    d = datetime.datetime.fromtimestamp(os.path.getctime(path))
    return d.replace(microsecond=0)

import os


def get_list_of_csv(path):
    # create a list of file and sub directories
    # names in the given directory
    all_files = list()
    if os.path.isdir(path):
        # all_files.append(path)  # directory name as first entry
        list_of_files = os.listdir(path)
        # Iterate over all the entries
        for entry in list_of_files:
            full_path = os.path.join(path, entry)
            if full_path.endswith('.csv'):
                all_files.append(full_path)
        if len(all_files) == 1:  # if there were no csv files in the folder, return empty instead
            all_files = list()
    elif path.endswith('.csv'):
        all_files.append(path)

    return all_files

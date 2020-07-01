import fnmatch
from openpyxl import Workbook
import os


def save_to_xlsx(experiments, filepath):
    wb = Workbook()

    ws1 = wb.active
    ws1.title = "Average"
    ws2 = wb.create_sheet(title="Efficiency")

    for i, experiment in enumerate(experiments.values()):
        ws_title = title_from_name(wb, experiment.name)
        ws = wb.create_sheet(title=ws_title)

    wb.save(filepath)


def title_from_name(workbook, experiment_name):
    if len(experiment_name) > 25:
        experiment_name = experiment_name[:25]
    if experiment_name in workbook.sheetnames:
        i = 1
        if fnmatch.fnmatch(experiment_name, '*(?)'):
            i = int(experiment_name[-2]) + 1
        experiment_name = experiment_name[:25] + ' (%d)'%i
    return experiment_name

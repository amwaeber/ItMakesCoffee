import numpy as np
import matplotlib.pyplot as plt


def format_yaxis(ax1, ax2, rescale=True):
    axes = (ax1, ax2)
    is_empty = [ax.lines == [] for ax in axes]
    if any(is_empty):  # at least one axis has no plots
        if all(is_empty):  # no plots on either axis
            return
        else:
            empty_axis = [ax for i, ax in enumerate(axes) if is_empty[i] is True][0]
            empty_axis.get_yaxis().set_visible(False)  # hide empty axis
            axis = [ax for i, ax in enumerate(axes) if is_empty[i] is False][0]
            minmax_vals = minmax(axis)
            if all([minmax_vals[0] * minmax_vals[1] >= 0, not rescale]):  # ensure plot includes zero
                minmax_vals = [0, minmax_vals[1]] if minmax_vals[1] > 0 else [minmax_vals[0], 0]
            span = (minmax_vals[1] - minmax_vals[0]) if minmax_vals[1] > minmax_vals[0] else 0.05
            axis.set_ylim(minmax_vals[0] - 0.1 * span, minmax_vals[1] + 0.1 * span)
    else:  # both axes contain plots
        minmax_vals = [minmax(ax) for ax in axes]
        if any([minmax_vals[0][0] * minmax_vals[0][1] <= 0,
                minmax_vals[1][0] * minmax_vals[1][1] <= 0, not rescale]):
            for i, vals in enumerate(minmax_vals):
                if vals[0] * vals[1] >= 0:
                    minmax_vals[i] = [0, vals[1]] if vals[1] > 0 else [vals[0], 0]
                span = [vs[1] - vs[0] if vs[1] > vs[0] else 0.05 for vs in minmax_vals]
                minmax_vals[i] = [minmax_vals[i][0] - 0.1 * span[i], minmax_vals[i][1] + 0.1 * span[i]]
            tops = [vals[1] / (vals[1] - vals[0]) for vals in minmax_vals]
            # Ensure that plots (intervals) are ordered bottom to top:
            if tops[0] > tops[1]:
                axes, minmax_vals, tops = [list(reversed(i)) for i in (axes, minmax_vals, tops)]

            # How much would the plot overflow if we kept current zoom levels?
            tot_span = tops[1] + 1 - tops[0]

            b_new_t = minmax_vals[0][0] + tot_span * (minmax_vals[0][1] - minmax_vals[0][0])
            t_new_b = minmax_vals[1][1] - tot_span * (minmax_vals[1][1] - minmax_vals[1][0])
            axes[0].set_ylim(minmax_vals[0][0], b_new_t)
            axes[1].set_ylim(t_new_b, minmax_vals[1][1])
        else:
            span = [vals[1] - vals[0] if vals[1] > vals[0] else 0.05 for vals in minmax_vals]
            axes[0].set_ylim(minmax_vals[0][0] - 0.1 * span[0], minmax_vals[0][1] + 0.1 * span[0])
            axes[1].set_ylim(minmax_vals[1][0] - 0.1 * span[1], minmax_vals[1][1] + 0.1 * span[1])


def minmax(ax):
    try:
        vals = np.hstack([line.get_ydata() for line in ax.lines])
        return [np.amin(vals), np.amax(vals)]
    except ValueError:  # no plots on axis
        return [-1, -1]

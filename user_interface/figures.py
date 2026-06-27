import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from matplotlib.patches import ConnectionPatch, Patch
from math import floor, log10
from typing import Optional
from helper_functions import space_and_title


def get_colors(altair_style: bool = False):
    """Get a list of colors to use in making plots

    Returns:
        list: A list of matplotlib color specifiers
    """
    if altair_style:
        return [
            '#1f77b4',
            '#ff7f0e',
            '#2ca02c',
            '#d62728',
            '#9467bd',
            '#8c563b',
            '#7f7f7f',
            '#bcbd22'
        ]
    else:
        return [
            "royalblue",
            "green",
            "firebrick",
            "dimgray",
            "olive",
            "#DB3E3B",
            "#23ce6b",
            "#389BFB",
            "#AA4FD0",
            "#FBB943",
            "#D64F2B",
            "#A62C4A",
            "navy",
            "black",
            "#087BEC",
            "cornflowerblue",
    ]


def get_markers():
    """Get lists of markers to use in making plots

    Returns:
        tuple of lists: two lists of marker specifiers, the first
            being open and the second filled
    """
    return [
        "$\u25ef$",
        "$\u25a1$",
        "$\u25c7$",
        "$\u2206$",
        "$\u2606$",
        "$\u2661$",
    ], [
        "$\u2b24$",
        "$\u25a0$",
        "$\u25c6$",
        "$\u25b2$",
        "*",
        "$\u2665$",
    ]


def get_hatches():
    return ['//', '\\\\', '||', '--', '++', 'xx', 'oo', 'OO', '..', '**']


# Get colors, markers, and linestyles to use throughout
colors = get_colors(altair_style=True)
markers_open = get_markers()[0]
markers_closed = get_markers()[1]
linestyles = ["-", "--", ":", "-."]
    
# Fix common capitalization errors
replace_elements = {
    "kwh": "kWh",
    "mwh": "MWh",
    "therms": "Therms",
    "mmbtu": "MMBtu",
    "Ghg": "GHG",
    "ghg": "GHG",
    "Btm": "BTM",
    "Sfo": "SFO",
    "Lax": "LAX",
    " Dollar Per Unit Year": '',
    " Dollar Per Unit": '',
    " Dollar Per Year": '',
    "Rps": "RPS",
    "Nei":"NEI",
    "Ng":"NG",
    " Dollar": ""
    }


def get_unit_from_column_name(col: str):
    """Automatically extract units from column names

    For example, if a column is named savings_kwh, this will extract
    the string 'kWh' to use as a unit in figure labeling.

    This can extract kWh, MWh, Therms, and MMBtu.

    Args:
        col (str): A string (corresponding to a pandas column name in
            normal usage)

    Returns:
        str: The extracted unit value, if any. Empty string otherwise.
    """
    unit = ""
    for k in replace_elements.keys():
        if k in col.lower():
            unit = replace_elements[k]
    return unit


def replace_multiple_string_elements(string: str, elements: dict = replace_elements):
    """Replace a set of substrings within a string with other substrings

    Args:
        string (str): The string to be modified
        elements (dict, optional): A dictionary of string-to-string mappings.
            The keys are the substrings to be replaced, and the values are
            the replacements.  The default value is the replace_elements
            dictionary defined in the figures library.

    Returns:
        str: The modified string
    """
    for before, after in elements.items():
        string = string.replace(before, after)

    return string


def num_decimals(number):
    """Set the number of decimal places to show for a given number.

    Currently uses one decimal place for zero and for numbers with
    absolute value > 1.  For numbers between -1 and 1 (except zero),
    uses N+2 decimal places, where N is the number of leading zeros.

    In other words, this function returns the number of decimal places
    needed to display a number to two significant figures.

    Args:
        number (_type_): The number for which decimal places are to
            be determined

    Returns:
        int: The calculated number of decimal places
    """
    return 1 if number == 0 or abs(number) > 1 else -floor(log10(abs(number))) + 1


def set_y_axis_params(
    df: pd.DataFrame,
    col_list: list,
    num_y_ticks: int = 5,
    ylims: list = None,
    multiplier: float = 0.08,
    ):
    """Generate nice y ticks, y minor ticks and y tick labels

    Function will always place a major tick and label at 0 unless
    ylims doesn't span 0. Function formats floating point tick
    labels depending on the number of 0s after the decimal point
    (for values < 1)

    Args:
        df (pd.DataFrame): A dataframe containing some columns that
            are being plotted
        col_list (list): The column names being plotted
        num_y_ticks (int, optional): Number of major ticks. Defaults to 5.
        ylims (list, optional): Custom y limits. If not passed, ymin or
            ymax will be set to zero. Defaults to None.

    Returns:
        ymin, ymax, yticks, y_minor_ticks, y_ticks_labels:
            The axis limits, major ticks, minor ticks, and tick labels
    """
    ymin = min(0, df[col_list].min().min()) if ylims == None else min(ylims)
    ymax = max(0, df[col_list].max().max()) if ylims == None else max(ylims)

    ymin, ymax = set_axis_lims(ylims, ymin, ymax, multiplier)

    y_tick_decimals = num_decimals(ymax - ymin)

    y_tick_delta = (ymax - ymin) / num_y_ticks
    y_minor_tick_delta = y_tick_delta / 3
    y_ticks = [0] if ylims == None or min(ylims) < 0 else []
    y_minor_ticks = []

    for t in range(int(ymax / y_minor_tick_delta)):
        y_minor_ticks.append((t + 1) * y_minor_tick_delta)

    for t in range(int(abs(ymin) / y_minor_tick_delta)):
        y_minor_ticks.append(-(t + 1) * y_minor_tick_delta)

    for t in range(int(ymax / y_tick_delta)):
        y_ticks.append((t + 1) * y_tick_delta)

    for t in range(int(abs(ymin) / y_tick_delta)):
        y_ticks.append(-(t + 1) * y_tick_delta)

    y_ticks_labels = [f"{num:.{y_tick_decimals}f}" for num in y_ticks]

    return ymin, ymax, y_ticks, y_minor_ticks, y_ticks_labels


def set_axis_lims(
    lims: list,
    min_val: float,
    max_val: float,
    multiplier: float = 0.06,
    force_zero_lim: bool = True,
    ):
    if lims is not None:
        axis_min = min(lims)
        axis_max = max(lims)

    elif lims is None:
        axis_min = min_val - (max_val - min_val) * multiplier
        if force_zero_lim and min_val >= 0:
            axis_min = 0
        axis_max = max_val + (max_val - min_val) * multiplier
        if force_zero_lim and max_val <= 0:
            axis_max = 0

    return axis_min, axis_max


def create_label_from_column_name(col: str, replace_elements: dict = replace_elements):
    """Generate a formatted figure label from a column name.

    Example: 'savings_kwh' gets converted to Savings kWh

    Args:
        col (str): The input string (typically a pandas column name in
            ordinary usage)
        replace_elements (dict, optional): A dictionary of substring replacements
            to be made. Defaults to the replace_elements dict defined in the figures
            library.

    Returns:
        str: the final formatted label
    """
    initial_label = " ".join(
        [
            i.capitalize() if i.lower() not in replace_elements.keys() else i.lower()
            for i in col.split("_")
        ]
    )

    final_label = replace_multiple_string_elements(
        initial_label, elements=replace_elements
    )

    return final_label


def generate_legend_labels(df: pd.DataFrame, cols_dict: dict):
    """Add high and low uncertainty columns to a dataframe for easy plotting

    Args:
        df (pd.DataFrame): A dataframe for which we are plotting a set of
            columns with uncertainty for each tabulated in a separate column
        cols_dict (dict): A cols_dict dictionary (see the figures notebook
            for details).


    Returns:
        _type_: _description_
    """

    col_list = list(cols_dict.keys())
    legend_labels = []

    for ls_col in cols_dict:

        legend_labels.append(
            create_label_from_column_name(ls_col)
            if cols_dict[ls_col]["label"] is None
            else cols_dict[ls_col]["label"]
        )

    return col_list, legend_labels


def waterfall_multitier_fig(
    df: pd.DataFrame,
    col: str,
    category: str,
    tiers: str = None,
    sorting_list: list = None,
    sort_directions: list = None,
    figsize: tuple = None,
    include_line: bool = False,
    include_value_labels: bool = True,
    value_labels_decimals: int = 1,
    title: str = None,
    annotations: list = [None],
    ylabel: str = None,
    ylims: list = None,
    ):

    annotations = [a for a in annotations if a != None]

    df["tiers"] = "none"
    if tiers != None:
        df["tiers"] = df[tiers]

    if sorting_list == None:
        sorting_list = ["tiers", category]

    if sort_directions == None:
        sort_directions = [True] * len(sorting_list)

    unique_xtick_labels = [
        #replace_multiple_string_elements(" ".join(str(cat).title().split("_")))
        space_and_title(cat)
        for cat in list(
            df.sort_values(by=sorting_list, ascending=sort_directions)[
                category
            ].unique()
        )
    ]

    df_totals = df.query(f"{category} == 'total'").sort_values(
        by=sorting_list, ascending=sort_directions
    )

    df = df.query(f"{category} != 'total'").sort_values(
        by=sorting_list, ascending=sort_directions
    )

    df["cumsum"] = df.groupby("tiers")[col].cumsum()

    stacked_dfs = []
    totals_dfs = []
    for i, tier in enumerate(sorted(list(df["tiers"].unique()))):
        df_stacked = df.query(f"tiers == '{tier}'")
        df_stacked["tier_number"] = i
        df_stacked["lead_cumsum"] = df_stacked["cumsum"].shift(1).fillna(0)

        stacked_dfs.append(df_stacked)
        totals_dfs.append(df_totals.query(f"tiers == '{tier}'"))

    figsize = (14, min(18, 4 * len(stacked_dfs))) if figsize == None else figsize

    fig, axs = plt.subplots(
        len(stacked_dfs),
        1,
        figsize=figsize,
        dpi=150,
        sharex=True,
    )

    plt.subplots_adjust(hspace=0.1, wspace=0.0)
    if len(stacked_dfs) == 1:
        axs = [axs]

    for i, stacked_df in enumerate(stacked_dfs):
        axs[i].grid(axis='y', alpha=0.5)

        axs[i].bar(
            stacked_df[category],
            stacked_df[col],
            bottom=stacked_df["lead_cumsum"],
            color=[
                colors[0] if x >= 0 else colors[3] for x in stacked_df[col]
            ],
            # color=[
            #     "cornflowerblue" if x >= 0 else "lightcoral" for x in stacked_df[col]
            # ],
            zorder=3
        )

        if len(totals_dfs[i]) > 0:
            axs[i].bar(
                totals_dfs[i][category],
                totals_dfs[i][col],
                #color=colors[2],
                color="green", 
                alpha=0.65, 
                zorder=3
            )

        if include_line:
            for j in range(1, len(stacked_df)):
                axs[i].plot(
                    [j - 1, j],
                    [stacked_df["cumsum"][j - 1], stacked_df["cumsum"][j]],
                    color="black",
                    zorder=1000
                )

        if ylims != None:
            axs[i].set_ylim(min(ylims), max(ylims))
        else:
            ymin = axs[i].get_ylim()[0]
            ymax = axs[i].get_ylim()[1]
            y_range = ymax - ymin
            axs[i].set_ylim(
                min(0, ymin - 0.06 * y_range), max(0, ymax + 0.08 * y_range)
            )

        ymin = axs[i].get_ylim()[0]
        ymax = axs[i].get_ylim()[1]
        y_range = ymax - ymin
        figsize_ratio = (figsize[0] / figsize[1]) * len(stacked_dfs)

        if include_value_labels:
            for k, (cs, lcs, val) in enumerate(
                zip(stacked_df["cumsum"], stacked_df["lead_cumsum"], stacked_df[col])
            ):
                axs[i].annotate(
                    f"{val:,.{value_labels_decimals}f}",
                    (
                        k,
                        (
                            (cs + y_range * 0.01)
                            if val > 0
                            else (lcs + val - y_range * figsize_ratio * 0.025)
                        ),
                    ),
                    ha="center",
                    fontsize=14,
                )

        if len(totals_dfs[i]) > 0:
            val = totals_dfs[i][[col]].values[0][0]
            axs[i].annotate(
                f"{val:,.{value_labels_decimals}f}", 
                (
                    len(stacked_df),
                    (
                        (val + y_range * 0.01)
                        if val > 0
                        else (val - y_range * figsize_ratio * 0.025)
                    ),
                ),
                ha="center",
                fontsize=14,
            )

        axs[i].set_ylabel(
            (
                ylabel
                if ylabel is not None
                else replace_multiple_string_elements(" ".join(col.split("_")).title())
            ),
            size=16,
        )

        axs[i].tick_params(axis="y", labelsize=15)
        axs[i].yaxis.set_minor_locator(AutoMinorLocator())

        if len(annotations) > 0:
            if annotations[i] != None:
                axs[i].annotate(
                    annotations[i],
                    xy=(0.01, 0.9),
                    # xy=(0.01 if left_orient else 0.99, 0.92),
                    xycoords="axes fraction",
                    ha="left",
                    # ha="left" if left_orient else "right",
                    fontsize=16,
                )

    axs[0].set_title(
        "Load Impact" if title is None else title,
        fontsize=18,
        loc="left",
    )

    rotate = -45 if max([len(k) for k in unique_xtick_labels]) > 5 else 0
    axs[-1].set_xticks(np.arange(len(unique_xtick_labels)))
    axs[-1].set_xticklabels(
        unique_xtick_labels,
        rotation=rotate,
        ha="left" if rotate == -45 else "center",
        fontsize=13,
    )

    return fig


def hour_of_day_ls_fig(
    df: pd.DataFrame,
    cols_dict: dict,
    peak_period: list[int] = [-1],
    figsize: tuple = (10, 6),
    title: str = None,
    ylims: list = None,
    ylabel: str = None,
    legend_loc: str = None,
    ):
    """
    This function plots 24-hour load shape(s) for a set of columns in a single panel.
    The dataframe is expected to have an 'hour_of_day' column.
    The cols_dict keys are the column names to plot, and each key may have
    an associated uncertainty column and a legend label.

    Args:
        df (pd.DataFrame): A dataframe containing various columns that could be plotted over a 24 hour day.
            Example: an average 24 hour resource curve
            (i.e. savings profile) for a portfolio of meters.
        cols_dict (dict): A dictionary of the column names being plotted.  Each key may
            have an associated label, which can be None. If None, the label will be generated from the column name.
        peak_period (int, optional): Starting and ending hours of the peak period, to be indicated
            with a shaded region. Defaults to None. Defaults to None.
        title (str, optiona). Plot title. Defaults to None.
        ylims (list, optional): Custom y limits. If not passed, ymin or
            ymax will be set to zero. Defaults to None.
        ylabel (str, optional): Y-axis label. Defaults to None.

    Returns:
        None
    """

    fig = plt.figure(figsize=figsize, dpi=120)
    ax = fig.gca()

    if "hour_of_day" not in df.columns:
        print("No hour_of_day column in dataframe.")

    col_list, legend_labels = generate_legend_labels(df=df, cols_dict=cols_dict)

    ymin, ymax, y_ticks, y_minor_ticks, y_ticks_labels = set_y_axis_params(
        df=df, col_list=col_list, num_y_ticks=5, ylims=ylims
    )

    df = df.sort_values(by=["hour_of_day"])
    x = df["hour_of_day"]

    for i, ls_col in enumerate(cols_dict):

        ax.plot(
            x,
            df[ls_col],
            color=colors[i % len(colors)],
            linewidth=(i + 1) % 4 + 1,
            linestyle=linestyles[i % len(linestyles)],
        )

    if max(peak_period) > 0:
        ax.axvspan(
            min(peak_period) - 0.5,
            max(peak_period) + 0.5,
            color="cornflowerblue",
            alpha=0.2,
        )

        ax.annotate(
            "Peak Period",
            (
                (min(peak_period) + (max(peak_period) - min(peak_period)) / 2) / 23.5,
                1.01,
            ),
            xycoords="axes fraction",
            color="navy",
            fontsize=14,
            ha="center",
        )

    ax.axhline(0, linestyle="--", color="dimgray")

    # Axis Limits
    ax.set_xlim(min(x) - 0.5, max(x) + 0.5)
    ax.set_ylim(set_axis_lims(ylims, ymin, ymax))

    # Axis Labels
    ax.set_xlabel("Hour of Day", size=14, labelpad=6)
    ax.set_ylabel(
        (
            ylabel
            if ylabel is not None
            else f"{'Avg. ' if 'avg' in col_list[0] else ''}{get_unit_from_column_name(col_list[0])}"
        ),
        size=15,
    )

    # Ticks and Grid
    ax.set_xticks(np.arange(0, 24, 4))
    ax.set_xticks(np.arange(0, 24), minor=True)
    ax.set_xticklabels(np.arange(0, 24, 4), size=14)
    ax.set_yticks(y_ticks)
    ax.set_yticks(y_minor_ticks, minor=True)
    ax.set_yticklabels(y_ticks_labels, size=14)
    ax.tick_params(axis="both", labelsize=14)
    ax.tick_params(left=True, bottom=True, length=5, width=1)
    ax.tick_params(which="minor", bottom=True, left=True, length=3)
    ax.grid(False)

    # Titles, Legends, Annotations
    ax.set_title(
        "Daily Loadshapes" if title is None else title,
        fontsize=15,
        loc="left",
    )

    ax.legend(
        legend_labels,
        loc=(
            (
                "upper left"
                if abs(min(ax.get_ylim())) > abs(max(ax.get_ylim()))
                else "lower right"
            )
            if legend_loc == None
            else legend_loc
        ),
        ncol=1,
        frameon=False,
        fontsize=12,
    )

    plt.show()

    return fig


def numeric_bar_fig(
    df: pd.DataFrame,
    col: str,
    category: str,
    value_stream_df: pd.DataFrame = None,
    figsize: tuple = (10, 6),
    y2_col: str = None,
    pin_yaxis_zeros: bool = False,  # Whether to force the y1 and y2 axes to share 0
    single_bar_color="dimgray",
    horizontal: bool = False,  # Whether to plot a horizontal bar chart
    space_fraction: float = 0.65,
    peak_period: list[int] = [],
    title: str = None,
    xlabel: str = None,
    ylabel: str = None,
    y2label: str = None,
    legend: bool = True,
    legend_loc: str = None,
    ):

    df.sort_values(by=category, inplace=True, ascending=True)

    fig = plt.figure(figsize=figsize, dpi=200)
    ax = fig.gca()

    if horizontal:
        ax.barh(
            y=df[category],
            width=df[col],
            height=space_fraction,
            color=colors[i] if single_bar_color is None else single_bar_color,
            #label=label,
            zorder=1000
        )
    else:
        ax.bar(
            x=df[category],
            height=df[col],
            width=space_fraction,
            color=colors[i] if single_bar_color is None else single_bar_color,
            alpha=1 if value_stream_df is None else 0.75,
            zorder=1000
        )
    
    if len(peak_period) > 0:
        ax.bar(
            x=df.query(f"{category} in {peak_period}")[category],
            height=df.query(f"{category} in {peak_period}")[col],
            width=space_fraction,
            color="dimgray",
            label="Peak Period",
            alpha=1 if value_stream_df is None else 0.75,
            zorder=1000
        )

        ax.legend(
            frameon=False,
            fontsize=12,
        )

    line_colors = [
        "green",
        "darkorange",
        "#AA4FD0",
        "#DB3E3B",
        "#FBB943",
        "#D64F2B",
        "#A62C4A",
        "black",
        "#087BEC",
    ]

    if value_stream_df is not None:
        for i, value_stream in enumerate(value_stream_df['value_stream'].unique()):
            plot_df = value_stream_df.query(f"value_stream == '{value_stream}'").sort_values(by=category, ascending=True)
            ax.plot(
                #df_value_stream.query(f"value_stream == '{value_stream}'")[category] + shift,
                plot_df[category],
                plot_df[col],
                linewidth=3,
                color=line_colors[i%len(line_colors)],
                linestyle = linestyles[i%len(linestyles)],
                label=value_stream,
                zorder=1000
            )

    ax.set_title(
        "Load Impact" if title is None else title,
        fontsize=19,
        loc="left",
    )

    if ylabel is not None:
        y_label = ylabel
    elif "pct" in col:
        y_label = "Fraction Savings"
    elif "savings" in col:
        y_label = "Avg. Hourly Savings (kWh)"
    else:
        y_label = " ".join(col.split("_")).title()

    if horizontal:
        sylab = ax.set_xlabel
        sxlab = ax.set_ylabel
    else:
        sylab = ax.set_ylabel
        sxlab = ax.set_xlabel

    sylab(y_label, size=16, labelpad=5)
    sxlab(" ".join(category.split("_")).title() if xlabel == None else xlabel, size=16)

    ax.tick_params(left=True, bottom=True, length=4, width=1, labelsize=15)
    ax.tick_params(which="minor", bottom=True, left=True, length=2)

    unique_xtick_labels = list(df[category].unique())

    if len(unique_xtick_labels) > 20:
        unique_xtick_labels = unique_xtick_labels[::2]

    total_label_len = 0
    for label in unique_xtick_labels:
        total_label_len += len(str(label))

    rotate = -45 if (max([len(str(k)) for k in unique_xtick_labels]) > 4 or total_label_len > 30) else 0

    if horizontal:
        ax.set_yticks(np.arange(len(unique_xtick_labels)))
        ax.set_yticklabels(unique_xtick_labels, fontsize=15)
        ax.xaxis.set_minor_locator(AutoMinorLocator())

    else:
        ax.set_xticks(unique_xtick_labels)
        ax.set_xticklabels(
            unique_xtick_labels,
            rotation=rotate,
            ha="left" if rotate == -45 else "center",
            fontsize=15,
        )
        ax.yaxis.set_minor_locator(AutoMinorLocator())

    ax.grid(axis='x' if horizontal else 'y', alpha=0.5)
    
    if horizontal:
        ax.axvline(0)
    else:
        ax.axhline(0)

    if legend:
        ax.legend(
            loc="upper left" if legend_loc == None else legend_loc,
            fontsize=11,
            frameon=True,
            labelspacing=0.78,
            prop={"size": 15 - np.floor(len(value_stream_df['value_stream'].unique()) * 0.5)},
        )

    if y2_col != None:
        ax1 = ax.twinx()
        ax1.scatter(
            df[category],
            df[y2_col],
            s=75,
            color="firebrick",
            label="Count Meters" if y2label is None else y2label,
        )

        ax1.set_ylabel(
            "Savings" if y2label is None else y2label,
            size=16,
            labelpad=20,
            rotation=-90,
        )

        if pin_yaxis_zeros:
            a = ax.get_ylim()[1] # max value of y axis
            b = ax.get_ylim()[0] # min value of y axis
            c = max(df[y2_col]) * 1.05 # max value of y2 data buffered by 5%
            if c > 0:
                ax1.set_ylim(c * (1 - (a - b) / a), c) # set y2 axis limits in case of positive maxy2 data
            else:
                c = min(df[y2_col]) * 1.05 # set y2 axis limits in case of negative max y2 data
                ax1.set_ylim(c, a)

        ax1.legend(
            ["Count Meters" if y2label is None else y2label],
            frameon=False,
            bbox_to_anchor=(1.0, 1.1),
            prop={"size": 15},
        )

        ax1.grid(False)
        ax1.tick_params(left=False, right=True, length=4, width=1, labelsize=15)
        ax1.yaxis.set_minor_locator(AutoMinorLocator())

    return fig


def scatter_fig(
    df: pd.DataFrame,
    xy_cols_dict: dict,
    marker_size: int = 10,
    include_line: bool = False,
    vlines: list = [None],
    marker: str = markers_open[0],
    marker_color: str = colors[3],
    color_by_col: str = None,
    include_45_degree_line: bool = False,
    label_points: bool = False,
    labels: list = None,
    label_size: int = 10,
    figsize: tuple = (8, 7),
    title: str = None,
    xlims: list = None,
    xlabel: str = None,
    ylims: list = None,
    ylabel: str = None,
    legend: bool = False,
    legend_labels: list = [],
    legend_loc: str = "upper left",
    ax=None,
    ):
    """
    Create a scatter plot with optional labels and uncertainty.

    Args:
        df (pd.DataFrame): Input DataFrame containing data.
        xy_cols_dict (dict): Dictionary specifying columns for x and y axes.
        marker (str): Matplotlib marker to use for plotting points
            (default open circle).
        marker_size (int): Size of markers in the scatter plot
            (default 10 points).
        marker_color (str): Color of the markers in the scatter plot
            (default black)
        color_by_col (str): Name of a column containing a categorical variable
            to be used to color the data points. If this keyword is passed, then
            the marker_color keyword can be a dict that maps category names to colors.
            If marker_color is not a dict, it will be ignored in this context.
        include_45_degree_line (bool): Whether to plot a 45 degree line.
        label_points (bool): Whether to label data points.
        labels (list): List of labels for each data point if label_points is True.
        label_size (int): Font size of labels.
        figsize (tuple): Figure size (width, height) in inches.
        title (str): Title of the plot.
        xlims (list): List containing the x-axis limits.
        xlabel (str): Label for the x-axis.
        ylims (list): List containing the y-axis limits.
        ylabel (str): Label for the y-axis.
        legend (bool): Whether to plot a legend.
        ax (plt.Axes): Can pass in a Matplotlib Axes object to put the plot on.

    Returns:
        None
    """
    vlines = [v for v in vlines if v != None]
    if ax is None:
        fig = plt.figure(figsize=figsize, dpi=120)
        ax = fig.gca()

    # Generate column list and legend labels
    col_list, leg_labels = generate_legend_labels(df=df, cols_dict=xy_cols_dict)

    x = list(df[list(xy_cols_dict.keys())[0]])
    y = list(df[list(xy_cols_dict.keys())[1]])

    xmin, xmax = min(x), max(x)
    ymin, ymax = min(y), max(y)

    # Scatter plot
    if color_by_col is not None:
        grouped = df.groupby(color_by_col)
        for i, (n, g) in enumerate(grouped):
            xg = list(g[list(xy_cols_dict.keys())[0]])
            yg = list(g[list(xy_cols_dict.keys())[1]])
            if type(marker_color) == type({}):
                colg = marker_color[g[color_by_col].iloc[0]]
            else:
                colg = get_colors()[i]

            ax.scatter(
                xg,
                yg,
                marker=markers_open[i % len(markers_open)],
                s=marker_size,
                color=colg,
                label=None if len(legend_labels) == 0 else legend_labels[i],
            )

            if include_line:
                ax.plot(xg, yg, color=colg)
            if len(vlines) > 0:
                ax.axvline(vlines[i], linestyle="--", color=colg)

    else:
        ax.scatter(
            x,
            y,
            marker=marker,
            s=marker_size,
            color=marker_color,
        )

        if include_line:
            ax.plot(x, y, color=marker_color)

    if include_45_degree_line:
        ax.plot([min(xmin, ymin), max(xmax, ymax)], [min(xmin, ymin), max(xmax, ymax)], linestyle="--", color="dimgray")

    # Horizontal dashed line at y=0
    ax.axhline(0, linestyle="--", color="dimgray")

    # Set axis limits set_axis_lims(ylims, ymin, ymax, multiplier)
    try:
        ax.set_xlim(set_axis_lims(xlims, xmin, xmax))
        ax.set_ylim(set_axis_lims(ylims, ymin, ymax))
    except:
        pass

    # Set Axis Labels
    ax.set_xlabel(
        (
            xlabel
            if xlabel is not None
            else f"{'Avg. ' if 'avg' in col_list[0] else ''}{get_unit_from_column_name(col_list[0])}"
        ),
        size=14,
    )
    ax.set_ylabel(
        (
            ylabel
            if ylabel is not None
            else f"{'Avg. ' if 'avg' in col_list[1] else ''}{get_unit_from_column_name(col_list[1])}"
        ),
        size=14,
    )

    # Ticks and Grid
    ax.tick_params(axis="both", labelsize=13)
    ax.tick_params(left=True, bottom=True, length=5, width=1)
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.grid(True, alpha=0.5)

    # Set Titles, Legends, Annotations
    ax.set_title(
        "" if title is None else title,
        fontsize=15,
        loc="left",
    )

    y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
    # Annotate data points with labels
    if label_points:
        for i, label in enumerate(labels):
            ax.annotate(label, (x[i], y[i]+0.033*y_range), fontsize=label_size, ha="center")

    if legend:
        ax.legend(
            loc="lower left" if legend_loc == None else legend_loc,
            fontsize=11,
            frameon=True,
            labelspacing=0.78,
        )

    return fig


def categorical_bar_fig(
    df: pd.DataFrame,
    col: str,
    category: str,
    groupings: str = None,
    figsize: tuple = (10, 6),
    y2_col: str = None,
    min_y2_counts: Optional[int] = None,  # None = no filter (show negative y2); int = keep only rows with y2 >= value
    pin_yaxis_zeros: bool = False,  # Whether to force the y1 and y2 axes to share 0
    single_bar_color: str = colors[0],
    horizontal: bool = False,  # Whether to plot a horizontal bar chart
    space_fraction: float = 0.65,
    sort_by: list = None,
    sort_ascending: bool = True,
    title: str = None,
    xlabel: str = None,
    ylabel: str = None,
    y2label: str = None,
    legend: bool = True,
    legend_loc: "str" = None,
    ):
    df = df.copy()

    if sort_by is None:
        sort_by = [category]
        if groupings != None:
            sort_by += [groupings]

    try:
        df[category] = pd.to_numeric(df[category], downcast='integer')
    except:
        pass

    if groupings != None:
        try:
            df[groupings] = pd.to_numeric(df[groupings])
        except:
            pass
    else:
        groupings = "dummy"
        df[groupings] = "dummy"
        groups = ["dummy"]

    fig = plt.figure(figsize=figsize, dpi=200)
    ax = fig.gca()

    if y2_col != None:
        if min_y2_counts is not None:
            df = df[df[y2_col] >= min_y2_counts].copy()
        ax1 = ax.twinx()  

    groups = df[groupings].unique()
    num_bars = len(groups)
    bar_width = space_fraction / num_bars

    df = df.sort_values(by=sort_by, ascending=sort_ascending)
    for i, group in enumerate(sorted(list(groups), reverse=True)):
        
        x1 = pd.Series(
            [j for j in range(len(df[category][(df[groupings] == group)]))]
        )
        
        y = df[col][(df[groupings] == group)]
        
        shift = bar_width * (-0.5 - i + num_bars / 2)

        # Create legend labels or use the provided mapping
        label = space_and_title(group)

        if horizontal:
            ax.barh(
                x1 + shift,
                y,
                height=bar_width,
                color=colors[i] if len(groups) > 1 else single_bar_color,
                label=label,
                zorder=1000
            )
        else:
            ax.bar(
                x1 + shift,
                y,
                width=bar_width,
                color=colors[i] if len(groups) > 1 else single_bar_color,
                label=label,
                zorder=1000
            )

    ax.set_title(
        "Load Impact" if title is None else title,
        fontsize=19,
        loc="left",
    )

    if ylabel is not None:
        y_label = ylabel
    elif "pct" in col:
        y_label = "Fraction Savings"
    elif "savings" in col:
        y_label = "Avg. Hourly Savings (kWh)"
    else:
        y_label = " ".join(col.split("_")).title()

    if horizontal:
        sylab = ax.set_xlabel
        sxlab = ax.set_ylabel
    else:
        sylab = ax.set_ylabel
        sxlab = ax.set_xlabel

    sylab(y_label, size=16, labelpad=5)
    sxlab(space_and_title(category) if xlabel == None else xlabel, size=16)

    ax.tick_params(left=True, bottom=True, length=4, width=1, labelsize=15)
    ax.tick_params(which="minor", bottom=True, left=True, length=2)

    unique_xtick_labels = [
        space_and_title(cat)
        for cat in list(df[category].unique())
    ]

    if len(unique_xtick_labels) > 20:
        unique_xtick_labels = [label if index % 2 == 0 else '' for index, label in enumerate(unique_xtick_labels)]

    total_label_len = 0
    for label in unique_xtick_labels:
        total_label_len += len(label)

    if horizontal:
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.set_yticks(np.arange(len(unique_xtick_labels)))
        ax.set_yticklabels(unique_xtick_labels, fontsize=15)
    else:
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        rotate = -45 if (max([len(k) for k in unique_xtick_labels]) > 5 or total_label_len > 30) else 0
        ax.set_xticks(np.arange(len(unique_xtick_labels)))
        ax.set_xticklabels(
            unique_xtick_labels,
            rotation=rotate,
            ha="left" if rotate == -45 else "center",
            fontsize=15,
        )

    if legend and (groupings != "dummy"):
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(
            handles[::-1],
            labels[::-1],
            frameon=False,
            loc="upper left" if legend_loc == None else legend_loc,
            prop={"size": 15 - np.floor(len(groups) * 0.3)},
        )

    ax.grid(axis='x' if horizontal else 'y', alpha=0.5)
    
    if horizontal:
        ax.axvline(0)
    else:
        ax.axhline(0)

    if y2_col != None:
        ax1.scatter(
            x1,
            df[(df[groupings] == groups[0])][y2_col],
            s=75,
            color="firebrick",
            label="Count Meters" if y2label is None else y2label,
        )

        ax1.set_ylabel(
            "Count Meters" if y2label is None else y2label,
            size=16,
            labelpad=20,
            rotation=-90,
        )

        if pin_yaxis_zeros:
            a = ax.get_ylim()[1]
            b = ax.get_ylim()[0]
            c = max(df[(df[groupings] == groups[0])][y2_col]) * 1.05
            if c > 0:
                ax1.set_ylim(c * (1 - (a - b) / a), c)
            else:
                c = min(df[(df[groupings] == groups[0])][y2_col]) * 1.05
                ax1.set_ylim(c, a)

        ax1.legend(
            ["Count Meters" if y2label is None else y2label],
            frameon=False,
            bbox_to_anchor=(1.0, 1.1),
            prop={"size": 15},
        )

        ax1.grid(False)
        ax1.tick_params(left=False, right=True, length=4, width=1, labelsize=15)

    return fig


def pie_chart(
    df: pd.DataFrame,
    col: str,
    label_col: str,
    max_slices: int = 10,
    min_slice_fraction: float = 0.02,
    figsize: tuple = (9, 5),
    title: str = "Proportional Values",
    ):
    
    conditional = '>' if len(df.query(f"{col} > 0")) > 0 else '<'

    df_pos_pie = df[[label_col, col]].query(f"{col} {conditional} 0").sort_values(by=col, ascending=False).reset_index(drop=True)
    df_pos_pie['plot'] = df_pos_pie[col] / df_pos_pie[col].sum()
    df_pos_pie = df_pos_pie.reset_index().rename(columns={'index': 'slice_number'})
    df_pos_pie['slice_number'] = df_pos_pie['slice_number'] + 1
    df_pos_bar = df_pos_pie.query(f"plot < {min_slice_fraction} or slice_number > {max_slices}")

    if len(df_pos_bar) > 1: 
        df_pos_pie.query(f"plot >= {min_slice_fraction} and slice_number <= {max_slices}", inplace=True)
        df_pos_other = df_pos_bar[[col, 'plot']].sum().to_frame().T
        df_pos_other['slice_number'] = 0
        df_pos_other[label_col] = 'Other'
        
        df_pos_pie = pd.concat([df_pos_other[['slice_number', label_col, col,'plot']], df_pos_pie])

        bar_vals = df_pos_bar['plot']
        bar_legend_labels = df_pos_bar[label_col]
        bar_value_labels = [f"${v:,.2f}" for v in list(df_pos_bar[col])]

    pie_vals = list(df_pos_pie['plot'])
    pie_legend_labels = list(df_pos_pie[label_col])
    pie_value_labels = [f"${v:,.1f}" for v in list(df_pos_pie[col])] if len(pie_vals) >= 4 else [f"${v:,.2f}" for v in list(df_pos_pie[col])]

    if len(df_pos_bar) > 1:
    # make figure and assign axis objects
        fig, (ax1, ax2) = plt.subplots(1, 2, width_ratios=[1, 0.4], figsize=figsize, dpi=200)
        fig.subplots_adjust(wspace=0)
        # pie chart parameters (no labels in pie to avoid compressing it)
        explode = [0.1]+[0]*(len(pie_vals)-1)
        ax1.set_title(title, fontsize=17, loc="left")
    else:
        fig = plt.figure(figsize=figsize, dpi=200)
        ax1 = fig.gca()
        explode = [0]*len(pie_vals)
        ax1.set_title(title, fontsize=14, loc="left")

    # rotate so that first wedge is split by the x-axis
    angle = -180 * pie_vals[0]
    # Greens palette: sample from matplotlib colormap (same idea as seaborn "Greens")
    pie_colors = plt.cm.cividis(np.linspace(0.15, 0.95, len(pie_vals)))
    
    wedges, label_texts = ax1.pie(
        pie_vals, labels=pie_value_labels, startangle=angle,
        explode=explode, pctdistance=1.18, colors=pie_colors
    )

    for t in label_texts:
        t.set_fontsize(15)
    # color-coded legend at bottom of pie chart
    legend_handles = [
        Patch(facecolor=w.get_facecolor(), edgecolor=w.get_edgecolor(), label=l)
        for w, l in zip(wedges, pie_legend_labels)
    ]

    ax1.legend(
        handles=legend_handles[1:]+[legend_handles[0]],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.02),
        ncol=1,
        frameon=False,
        fontsize=12,
    )

    if len(df_pos_bar) > 1:
        # bar chart parameters
        bottom = 1
        width = 0.5
        bar_colors = plt.cm.Blues(np.linspace(0.5, 0.95, len(bar_vals)))
        # Reversed order for stacking (top bar = last row); label index is len(bar_vals)-1-j
        bar_value_labels_rev = list(reversed(bar_value_labels))
        # Adding from the top matches the legend.
        for j, (height, legend_label) in enumerate(reversed([*zip(bar_vals, bar_legend_labels)])):
            bottom -= height
            bc = ax2.bar(0, height, width, bottom=bottom, color=bar_colors[j], label=legend_label,
                        alpha=0.1 + 0.25 * j)
            # Only label bars with non-zero height (zero-height bars can make get_bbox() return None)
            if height > 0:
                ax2.bar_label(bc, labels=[bar_value_labels_rev[j]], label_type='center', fontsize=12)

        #ax2.set_title('Other Value Streams', fontsize=13)
        ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=1, frameon=False, fontsize=12)
        ax2.axis('off')
        ax2.set_xlim(- 2.5 * width, 2.5 * width)

        # use ConnectionPatch to draw lines between the two plots
        theta1, theta2 = wedges[0].theta1, wedges[0].theta2
        center, r = wedges[0].center, wedges[0].r
        bar_height = sum(bar_vals)
        # Bar stack is drawn from bottom=1 downward, so it occupies y from 1 - bar_height to 1
        bar_top_y = 1.0
        bar_bottom_y = 1.0 - bar_height

        # draw top connecting line
        x = r * np.cos(np.pi / 180 * theta2) + center[0]
        y = r * np.sin(np.pi / 180 * theta2) + center[1]
        con = ConnectionPatch(xyA=(-width / 2, bar_top_y), coordsA=ax2.transData,
                            xyB=(x, y), coordsB=ax1.transData)
        con.set_color('dimgray')
        con.set_linewidth(1)
        con.set_linestyle('dotted')
        ax2.add_artist(con)

        # draw bottom connecting line
        x = r * np.cos(np.pi / 180 * theta1) + center[0]
        y = r * np.sin(np.pi / 180 * theta1) + center[1]
        con = ConnectionPatch(xyA=(-width / 2, bar_bottom_y), coordsA=ax2.transData,
                            xyB=(x, y), coordsB=ax1.transData)
        con.set_color('dimgray')
        con.set_linewidth(1)
        con.set_linestyle('dotted')
        ax2.add_artist(con)

    return fig
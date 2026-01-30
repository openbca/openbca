import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import numpy as np
from math import floor, log10
from typing import Optional



def get_colors():
    """Get a list of colors to use in making plots

    Returns:
        list: A list of matplotlib color specifiers
    """
    return [
        "green",
        "firebrick",
        "royalblue",
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


# Get colors, markers, and linestyles to use throughout
colors = get_colors()
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
    "Rps": "RPS",
    "Nei":"NEI",
    "Ng":"NG"
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
        replace_multiple_string_elements(" ".join(str(cat).title().split("_")))
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

        axs[i].bar(
            stacked_df[category],
            stacked_df[col],
            bottom=stacked_df["lead_cumsum"],
            color=[
                "cornflowerblue" if x >= 0 else "lightcoral" for x in stacked_df[col]
            ],
        )

        axs[i].grid(axis='y', alpha=0.5)

        if len(totals_dfs[i]) > 0:
            axs[i].bar(
                totals_dfs[i][category], totals_dfs[i][col], color="green", alpha=0.65
            )

        if include_line:
            for j in range(1, len(stacked_df)):
                axs[i].plot(
                    [j - 1, j],
                    [stacked_df["cumsum"][j - 1], stacked_df["cumsum"][j]],
                    color="black",
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


def bar_fig(
    df: pd.DataFrame,
    col: str,
    category: str,
    groupings: str = None,
    uncertainty_col: str = None,
    figsize: tuple = (10, 6),
    y2_col: str = None,
    min_y2_counts: Optional[int] = None,  # None = no filter (show negative y2); int = keep only rows with y2 >= value
    pin_yaxis_zeros: bool = False,  # Whether to force the y1 and y2 axes to share 0
    single_bar_color="dimgray",
    horizontal: bool = False,  # Whether to plot a horizontal bar chart
    space_fraction: float = 0.65,
    sort_by: list = None,
    sort_ascending: bool = True,
    title: str = None,
    xlabel: str = None,
    ylabel: str = None,
    y2label: str = None,
    ax: Optional[list] = None,
    legend: bool = True,
    legend_loc: "str" = None,
    label_map: dict = None,  # Maps group names to legend labels
    ):

    if sort_by is None:
        sort_by = [
            category,
        ]
        if groupings != None:
            sort_by += [groupings]

    df_1 = df.copy()

    try:
        df_1[category] = pd.to_numeric(df_1[category], downcast='integer')
    except:
        pass

    if groupings != None:
        try:
            df_1[groupings] = pd.to_numeric(df_1[groupings])
        except:
            pass
    else:
        groupings = "dummy"
        df_1[groupings] = "dummy"
        groups = ["dummy"]

    if ax is None:
        # Plot a standalone figure if no axes object was passed
        fig = plt.figure(figsize=figsize, dpi=200)
        ax = fig.gca()
        return_ax = False
    else:
        return_ax = True

    if y2_col != None:
        if min_y2_counts is not None:
            df_1 = df_1[df_1[y2_col] >= min_y2_counts]
        ax1 = ax.twinx()  

    groups = df_1[groupings].unique()
    num_bars = len(groups)
    bar_width = space_fraction / num_bars

    df_1.sort_values(by=sort_by, inplace=True, ascending=sort_ascending)
    for i, group in enumerate(sorted(list(groups), reverse=True)):
        x1 = pd.Series(
            [j for j in range(len(df_1[category][(df_1[groupings] == group)]))]
        )
        y = df_1[col][(df_1[groupings] == group)]
        shift = bar_width * (-0.5 - i + num_bars / 2)

        # Create legend labels or use the provided mapping
        label = " ".join(str(group).split("_")).title()
        if label_map is not None:
            try:
                label = label_map[group]
            except KeyError:
                pass

        if horizontal:
            ax.barh(
                x1 + shift,
                y,
                height=bar_width,
                color=colors[i] if len(groups) > 1 else single_bar_color,
                label=label,
            )
        else:
            ax.bar(
                x1 + shift,
                y,
                width=bar_width,
                color=colors[i] if len(groups) > 1 else single_bar_color,
                label=label,
            )

        if uncertainty_col != None:
            error = df_1[uncertainty_col][(df_1[groupings] == group)]
            ax.errorbar(
                y if horizontal else x1 + shift,
                x1 + shift if horizontal else y,
                yerr=None if horizontal else error,
                xerr=error if horizontal else None,
                ecolor="darkorange",
                capsize=5,
                capthick=1,
                linestyle="none",
            )
    
    if y2_col != None:
        ax1.scatter(
            x1,
            df_1[(df_1[groupings] == groups[0])][y2_col],
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
            c = max(df_1[(df_1[groupings] == groups[0])][y2_col]) * 1.05
            if c > 0:
                ax1.set_ylim(c * (1 - (a - b) / a), c)
            else:
                ax.set_ylim(min(b, c), a)
                ax1.set_ylim(min(b, c), a)

        if legend:
            ax1.legend(
                ["Count Meters" if y2label is None else y2label],
                frameon=False,
                bbox_to_anchor=(1.0, 1.1),
                prop={"size": 15},
            )

        ax1.grid(False)
        ax1.tick_params(left=False, right=True, length=4, width=1, labelsize=15)

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

    unique_xtick_labels = [
        replace_multiple_string_elements(" ".join(str(cat).title().split("_")))
        for cat in list(df_1[category].unique())
    ]

    if len(unique_xtick_labels) > 20:
        unique_xtick_labels = [label if index % 2 == 0 else '' for index, label in enumerate(unique_xtick_labels)]


    if horizontal:
        #plt.yticks(fontsize=15)
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.set_yticks(np.arange(len(unique_xtick_labels)))
        ax.set_yticklabels(unique_xtick_labels, fontsize=15)
    else:
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        rotate = -45 if max([len(k) for k in unique_xtick_labels]) > 5 else 0
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
            prop={"size": 15},
        )

    ax.grid(axis='x' if horizontal else 'y', alpha=0.5)
    if horizontal:
        ax.axvline(0)
    else:
        ax.axhline(0)

    if return_ax:
        return ax

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

    # legend_labels_ovewrite = legend_labels

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
            fontsize=12,
            frameon=True,
            labelspacing=0.78,
        )

    return fig
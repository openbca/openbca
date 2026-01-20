import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import numpy as np


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
        # df_stacked["base"] = df_stacked.apply(
        #     lambda row: row["lead_cumsum"] if row[col] > 0 else row["cumsum"], axis=1
        # )
        # if i == 0:
        #     display(df_stacked)

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
                min(0, ymin - 0.04 * y_range), max(0, ymax + 0.04 * y_range)
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
                    f"{int(val) if value_labels_decimals == 0 else round(val, value_labels_decimals)}",
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
                f"{int(val) if value_labels_decimals == 0 else round(val, value_labels_decimals)}",
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
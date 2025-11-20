# from typing import Any
# #from pandas import DataFrame
# from sqlmesh import model, ExecutionContext
# import pandas as pd
# #from tabulate import tabulate
# import os

# ID_COLUMNS = ["avoided_cost", "adder"]

# @model(
#     name="nspm.openbca_input_adder_value_streams",
#     kind="FULL",
#     grain=ID_COLUMNS,
#     columns={
#         "avoided_cost": "string",
#         "adder": "float",
#     },
# )

# def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
#     return load_adders_from_excel(
#         input_file="OpenBCA Code CONFIG File - with Data.xlsm"
#     )

# BASE_DIR = os.path.dirname(__file__)  # directory of the model file
# DATA_DIR = os.path.join(BASE_DIR, "..", "Input")  # adjust if needed

# def load_adders_from_excel(
#     input_file: str,
# ) -> pd.DataFrame:
#     """
#     Generate dataframe of adder value streams from the Configuration Data sheet in the OpenBCA CONFIG file.
#     """
#     file_path = os.path.join(DATA_DIR, input_file)
#     xls = pd.ExcelFile(file_path)
    
#     adder_value_stream_df = pd.read_excel(
#         xls, 
#         sheet_name="Configuration Data", 
#         header=0, 
#         skiprows=3, 
#         usecols="C:I").query("`Include in Test` == 'Yes' and not `If Adder (%), specify`.isna()")[[
#             'Value Stream', 
#             'If Adder (%), specify'
#             ]]   

#     adder_value_stream_df.columns = ['avoided_cost', 'adder']

#     return adder_value_stream_df
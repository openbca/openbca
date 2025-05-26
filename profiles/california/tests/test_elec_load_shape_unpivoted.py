import pandas as pd

from profiles.california.models.load_shapes import elec_load_shape_unpivoted


def test_unpivot_logic():
    df = pd.DataFrame({
        'utility': ['PG&E'],
        'quarter': [1],
        'month': [1],
        'hour_of_year': [0],
        'hour_of_day': [0],
        'Res_Ltg': [1.1],
        'NonRes_AC': [2.2]
    })

    result = elec_load_shape_unpivoted.unpivot(df)

    assert len(result) == 2
    assert set(result['load_shape']) == {'RES_LTG', 'NONRES_AC'}
    assert round(result['value'].sum(), 1) == 3.3

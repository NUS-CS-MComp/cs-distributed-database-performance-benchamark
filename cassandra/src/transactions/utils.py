class Constants:
    CONST_PARTITION_KEY_WAREHOUSE = 'constant_warehouse'
    CONST_PARTITION_KEY_DISTRICT = 'constant_district'

def single_select(session, query, data=None, default=0):
    rows = session.execute(query, data)
    for row in rows:
        return row[0]
    return default

def single_select(session, query, data=None, default=0):
    rows = session.execute(query, data)
    for row in rows:
        return row[0]
    return default

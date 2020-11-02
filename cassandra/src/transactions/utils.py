def do_query(session, query, data=None):
    query_type = ''
    if query[0] == 'S' or query[0] == 's':     # indicates 'SELECT' or 'select'
        query_type = 'read'
    else:
        query_type = 'write'
    return session.execute(query, data, execution_profile=query_type)

def single_select(session, query, data=None, default=0):
    # rows = session.execute(query, data)
    rows = do_query(session, query, data)
    for row in rows:
        return row[0]
    return default

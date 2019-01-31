from pyad import adquery

def query(get_attributes=[], where_clause="objectClass = '*'", base_dn = ''):
    q = adquery.ADQuery()
    q.execute_query(attributes = get_attributes,where_clause = where_clause, base_dn = base_dn)
    return list(q.get_results())

def query_generator(get_attributes=[], where_clause="objectClass = '*'", base_dn = ''):
    q = adquery.ADQuery()
    q.execute_query(attributes = get_attributes,where_clause = where_clause, base_dn = base_dn)
    for r in q.get_results():
        yield r

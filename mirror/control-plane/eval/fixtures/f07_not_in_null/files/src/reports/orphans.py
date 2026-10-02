def orphan_customers(conn):
    return conn.execute(
        "SELECT id FROM customers WHERE id NOT IN (SELECT customer_id FROM orders)"
    ).fetchall()

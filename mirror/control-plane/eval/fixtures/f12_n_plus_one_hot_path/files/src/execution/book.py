def enrich(orders, db):
    out = []
    for o in orders:
        acct = db.execute("SELECT * FROM accounts WHERE id = ?", (o.account_id,)).fetchone()
        out.append((o, acct))
    return out

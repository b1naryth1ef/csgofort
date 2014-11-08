from flask import Blueprint, render_template, g, Response
from fortdb import User
from database import db
from util import *
import socket

admin = Blueprint("admin", __name__, subdomain="admin")

RELATION_SIZE_QUERY = """SELECT nspname || '.' || relname AS "relation",
    pg_size_pretty(pg_relation_size(C.oid)) AS "size"
  FROM pg_class C
  LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
  WHERE nspname NOT IN ('pg_catalog', 'information_schema')
  ORDER BY pg_relation_size(C.oid) DESC
  LIMIT 20;
"""

TABLE_SIZE_QUERY = """SELECT nspname || '.' || relname AS "relation",
    pg_size_pretty(pg_total_relation_size(C.oid)) AS "total_size"
  FROM pg_class C
  LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
  WHERE nspname NOT IN ('pg_catalog', 'information_schema')
    AND C.relkind <> 'i'
    AND nspname !~ '^pg_toast'
  ORDER BY pg_total_relation_size(C.oid) DESC
  LIMIT 20;
"""

INDEX_INFO_QUERY = """SELECT t.tablename, indexname, c.reltuples AS num_rows,
    pg_size_pretty(pg_relation_size(quote_ident(t.tablename)::text)) AS table_size,
    pg_size_pretty(pg_relation_size(quote_ident(indexrelname)::text)) AS index_size,
    CASE WHEN indisunique THEN 'Y'
       ELSE 'N'
    END AS UNIQUE,
    idx_scan AS number_of_scans, idx_tup_read AS tuples_read, idx_tup_fetch AS tuples_fetched
FROM pg_tables t
LEFT OUTER JOIN pg_class c ON t.tablename=c.relname
LEFT OUTER JOIN
    ( SELECT c.relname AS ctablename, ipg.relname AS indexname, x.indnatts AS number_of_columns,
        idx_scan, idx_tup_read, idx_tup_fetch, indexrelname, indisunique FROM pg_index x
           JOIN pg_class c ON c.oid = x.indrelid
           JOIN pg_class ipg ON ipg.oid = x.indexrelid
           JOIN pg_stat_all_indexes psai ON x.indexrelid = psai.indexrelid )
    AS foo
    ON t.tablename = foo.ctablename
WHERE t.schemaname='public'
ORDER BY 1,2;
"""

@admin.before_request
def admin_before_request():
    if not g.user or not g.user.level >= User.Level.ADMIN:
        return flashy("You can't see that silly!", u=build_url("", ""))

@admin.route("/")
def admin_index():
    return render_template("admin/index.html")

@admin.route("/users")
def admin_users():
    return render_template("admin/users.html")

@admin.route("/postgres")
def admin_postgres():
    return render_template("admin/postgres.html")

@admin.route("/api/uwsgi/stats")
def admin_api_uwsgi_stats():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 9191))
    data = s.recv(2048 * 24)
    s.close()

    r = Response(data)
    r.mimetype = "application/json"
    return r

@admin.route("/api/stats")
def admin_api_stats():
    return jsonify({
        "users": User.select().count(),
    })

@admin.route("/api/users")
def admin_api_users():
    return jsonify({
        "users": map(lambda i: i.toDict(admin=True),
            User.select().order_by(User.id).paginate(int(request.values.get("page", 1)), 25)),
        "count": User.select().count(),
    })

@admin.route("/api/user/<id>/edit")
def admin_user_edit(id):
    try:
        u = User.get(User.id == id)
    except User.DoesNotExist:
        return APIError("User does not exist")

    for field in request.values:
        setattr(u, field, request.values[field])

    u.save()
    return jsonify({"success": True, "changed": len(request.values)})

@admin.route("/api/postgres/raw")
def admin_api_postgres_raw():
    q = request.values.get("query")

    # Use protection kids, even a broken condom is better than no condom!!!!!!!!!
    if "DROP" in q:
        raise APIError("Fuck you")

    # Why does this exist...
    query = db.get_conn().cursor()
    query.execute("BEGIN")

    try:
        query.execute(q)
        data = query.fetchall()
    except Exception as e:
        query.execute("ROLLBACK")
        return jsonify({"result": "ERROR %s" % e})

    query.execute("COMMIT")
    return jsonify({
        "result": data
    })

@admin.route("/api/postgres/queries")
def admin_api_postgres_queries():
    query_count = db.get_conn().cursor()
    query_count.execute(
        "SELECT xact_commit+xact_rollback FROM pg_stat_database WHERE datname = 'fort';")
    query_count = query_count.fetchall()[0][0]

    return jsonify({
        "queries": query_count
    })

def multi(a, b):
    if b.lower() == "kb":
        return a
    if b.lower() == "mb":
        return int(a) * 1000
    if b.lower() == "gb":
        return int(a) * 1000000

@admin.route("/api/postgres/status")
def admin_api_postgres_status():
    relations = db.get_conn().cursor()
    relations.execute(RELATION_SIZE_QUERY)
    relations = map(lambda i: {"name": i[0], "size": i[1], "real": multi(*i[1].split(" ", 1))},
        relations.fetchall())

    tables = db.get_conn().cursor()
    tables.execute(TABLE_SIZE_QUERY)
    tables = map(lambda i: {"name": i[0], "size": i[1], "real": multi(*i[1].split(" ", 1))},
        tables.fetchall())

    indexes = db.get_conn().cursor()
    indexes.execute(INDEX_INFO_QUERY)
    indexes = map(lambda i: i[:7], indexes.fetchall())

    return jsonify({
        "relations": relations,
        "tables": tables,
        "indexes": indexes
    })

from flask import Blueprint, render_template, g
from fortdb import User
from database import db
from util import *

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

@admin.route("/api/stats")
def admin_api_stats():
    return jsonify({
        "users": User.select().count(),
    })

@admin.route("/api/users")
def admin_api_users():
    return jsonify({
        "users": map(lambda i: i.toDict(admin=True),
            User.select().order_by(User.id).paginate(int(request.values.get("page", 1)), 100))
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

@admin.route("/api/postgres/queries")
def admin_api_postgres_queries():
    query_count = db.get_conn().cursor()
    query_count.execute("SELECT xact_commit+xact_rollback FROM pg_stat_database WHERE datname = 'fort';")
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
    relations = map(lambda i: {"name": i[0], "size": i[1], "real": multi(*i[1].split(" ", 1))}, relations.fetchall())

    tables = db.get_conn().cursor()
    tables.execute(TABLE_SIZE_QUERY)
    tables = map(lambda i: {"name": i[0], "size": i[1], "real": multi(*i[1].split(" ", 1))}, tables.fetchall())

    return jsonify({
        "relations": relations,
        "tables": tables
    })

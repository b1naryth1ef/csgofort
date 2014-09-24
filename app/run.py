from app import csgofort, register_views

register_views()
csgofort.run(debug=True, port=6015, host="0.0.0.0")
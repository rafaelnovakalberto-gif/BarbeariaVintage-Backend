import database

database.create_tables()
database.create_user("admin", "Barbearia2026!", role="admin")
print("Usuario admin criado! Login: admin / Barbearia2026!")
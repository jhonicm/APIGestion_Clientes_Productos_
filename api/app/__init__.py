from app import crud, schemas, database, models

def crear_admin_unico():
    db = next(database.get_db())
    admin = db.query(models.Administrador).filter_by(usuario="admin").first()
    if not admin:
        admin_data = schemas.ClienteCreate(
            nombre="Administrador Sistema",
            email="admin@empresa.com",
            contraseña="admin123"
        )
        nuevo_admin = models.Administrador(
            usuario="admin",
            email=admin_data.email,
            contraseña=crud.get_password_hash(admin_data.contraseña),
            nombre=admin_data.nombre
        )
        db.add(nuevo_admin)
        db.commit()
        db.refresh(nuevo_admin)
    db.close()

crear_admin_unico()
from datetime import date, datetime
from app.infrastructure.database import Base, SessionLocal, engine
from app.infrastructure.models import (
    CategoriaModel,
    HabitoModel,
    RegistroHabitoModel,
    UsuarioModel,
)


def ejecutar_seeders():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(UsuarioModel).first() is not None:
            return

        u1 = UsuarioModel(name="Ariel Covarrubias", email="ariel@uct.cl", fecha_registro=datetime.now())
        u2 = UsuarioModel(name="Beatriz Martin", email="bmartin@uct.cl", fecha_registro=datetime.now())
        u3 = UsuarioModel(name="Patricio Salazar", email="psalazar@uct.cl", fecha_registro=datetime.now())
        db.add_all([u1, u2, u3])
        db.commit()

        c1 = CategoriaModel(nombre="Salud", descripcion="Hábitos relacionados con el bienestar físico y mental", activa=True)
        c2 = CategoriaModel(nombre="Estudio", descripcion="Hábitos para el desarrollo académico y profesional", activa=True)
        c3 = CategoriaModel(nombre="Deporte", descripcion="Actividad física y ejercicio regular", activa=True)
        db.add_all([c1, c2, c3])
        db.commit()

        h1 = HabitoModel(usuario_id=u1.id, categoria_id=c1.id, nombre="Beber 2 litros de agua", frecuencia_semanal=7, estado="ACTIVO")
        h2 = HabitoModel(usuario_id=u1.id, categoria_id=c3.id, nombre="Ir al gimnasio", frecuencia_semanal=4, estado="ACTIVO")
        h3 = HabitoModel(usuario_id=u2.id, categoria_id=c2.id, nombre="Repasar apuntes de clase", frecuencia_semanal=5, estado="ACTIVO")
        db.add_all([h1, h2, h3])
        db.commit()

        r1 = RegistroHabitoModel(habito_id=h1.id, fecha_registro=date.today(), completado=True, valor_medido=2.0, nota="Meta cumplida")
        r2 = RegistroHabitoModel(habito_id=h2.id, fecha_registro=date.today(), completado=True, valor_medido=1.5, nota="Rutina de piernas completada")
        db.add_all([r1, r2])
        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    ejecutar_seeders()


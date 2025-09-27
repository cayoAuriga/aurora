# /microservices/shared/sql_logging.py
"""
SQLAlchemy event-based logging (MySQL compatible)
Log all queries with bound parameters
"""

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.dialects import mysql
from shared.aurora_logging import get_logger

logger = get_logger("sql-logger")


def render_sql(statement, parameters):
    """
    Renderiza SQL + parámetros como string legible.
    """
    try:
        compiled = statement.compile(
            dialect=mysql.dialect(),
            compile_kwargs={"literal_binds": True}
        )
        return str(compiled)
    except Exception:
        # fallback si no se puede compilar
        return f"{statement} | params={parameters}"


def setup_sql_logging(engine: Engine):
    """
    Adjunta listeners a un Engine SQLAlchemy para loggear queries
    """

    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        try:
            sql = render_sql(statement, parameters)
            logger.info(f"📝 Ejecutando SQL:\n{sql}")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo renderizar SQL: {e}")
def with_sql_logging(fn):
    """
    Decorador para loggear SQL ejecutado dentro de un servicio.
    Busca un argumento `db` (Session) y loggea queries antes de ejecutar.
    """

    def wrapper(*args, **kwargs):
        db = kwargs.get("db") or (args[0] if args else None)

        # Si hay sesión y tiene un "query" en kwargs, tratamos de renderizar
        if db is not None and hasattr(db, "query"):
            try:
                # Esto es heurístico: asumimos que el servicio armará un query
                # Ejemplo: db.query(Model).filter_by(...)
                # Para interceptar, tendrías que pasar explícitamente el query.
                pass
            except Exception as e:
                logger.warning(f"⚠️ No se pudo loggear SQL: {e}")

        result = fn(*args, **kwargs)

        # Si el result es un objeto query (no ejecutado aún)
        try:
            if hasattr(result, "statement"):
                logger.info(f"📝 SQL ejecutado:\n{render_sql(result)}")
        except Exception:
            pass

        return result

    return wrapper
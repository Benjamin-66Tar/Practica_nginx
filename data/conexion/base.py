import os
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
from typing import Generator, Optional
import mysql.connector
from mysql.connector import pooling, Error
from mysql.connector.cursor import MySQLCursorDict

load_dotenv()

logger = logging.getLogger("db_connection")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] (%(name)s): %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class Database:

    _pool: Optional[pooling.MySQLConnectionPool] = None

    @classmethod
    def get_pool(cls) -> pooling.MySQLConnectionPool:
        if cls._pool is None:
            try:
                host = os.getenv("DB_HOST", "localhost")
                port = int(os.getenv("DB_PORT", 3306))
                user = os.getenv("DB_USER", "root")
                password = os.getenv("DB_PASSWORD", "")
                database = os.getenv("DB_NAME", "pruebas")
                pool_name = os.getenv("DB_POOL_NAME", "app_mysql_pool")
                pool_size = int(os.getenv("DB_POOL_SIZE", "5"))

                if not database:
                    logger.warning("No se ha definido DB_NAME en las variable de entorno.")

                logger.info(f"Creando pool de conexiones {pool_name} hacia {host}:{port}/{database}")
                cls._pool = pooling.MySQLConnectionPool(
                    pool_name=pool_name,
                    pool_size=pool_size,
                    pool_reset_session=True,
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=database,
                    autocommit=False
                )
                logger.info("Pool de conexiones creado exitosamente.")
            except Exception as err:
                logger.critical(f"Error al crear el pool de conexiones: {err} (Codigo: {err.errno})")
                raise
        return cls._pool

@contextmanager
def get_connection() -> Generator[mysql.connector.connection.MySQLConnection, None, None]:  

    #Es un gestor de contexto que solicita una conexión al pool, la entrega temporalmente para ejecutar operaciones y garantiza
    #que siempre se cierre y retorne al pool, manejando y registrando cualquier error que ocurra durante la obtención o el uso

    pool = Database.get_pool()
    connection = None
    try:
        connection = pool.get_connection()
        yield connection
    except Exception as err:
        logger.error(f"Error al obtener la conexión: {err} ")
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()

@contextmanager
def get_cursor(dictionary: bool = True) -> Generator[MySQLCursorDict, None, None]:
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=dictionary)
        try:
            yield cursor
            conn.commit()
        except Exception as err:
            conn.rollback()
            logger.error(f"Transacción revertida (Rollback) por error: {err}")
            raise
        finally:
            cursor.close()


def test_connection() -> bool:
    try:
        with get_cursor() as cursor:
            cursor.execute("SELECT VERSION() AS version, DATABASE() AS database_name, CURRENT_USER() AS user;")

            info = cursor.fetchone()
            logger.info(f"Conexión exitosa a MySQL.")
            logger.info(f" -> Versión del Servidor: {info['version']}")
            logger.info(f" -> Base de Datos Actual: {info['database_name']}")
            logger.info(f" -> Usuario Conectado:   {info['user']}")
            return True
    except Exception as err:
        logger.error(f"Error al probar la conexión: {err}")
        return False


if __name__ == "__main__":
    if test_connection():
        logger.info("Prueba de conexión completada exitosamente.")
    else:
        logger.error("Prueba de conexión fallida.")
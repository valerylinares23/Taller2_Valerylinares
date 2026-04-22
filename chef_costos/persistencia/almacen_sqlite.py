"""Conexión SQLite, esquema normalizado (PK/FK) y operaciones CRUD."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from chef_costos.constantes import MARGEN_GANANCIA_DEFECTO
from chef_costos.entidades.ingrediente import (
    Ingrediente,
    IngredienteCarbohidrato,
    IngredienteProteina,
    IngredienteVerdura,
)
from chef_costos.entidades.plato import Plato, PlatoEntrada, PlatoPostre, PlatoPrincipal


def _fabrica_ingrediente(
    categoria: str,
    nombre: str,
    precio_base: float,
    precio_mercado: float,
    identificador: int | None,
) -> Ingrediente:
    c = (categoria or "PROTEINA").upper()
    if c == "CARBOHIDRATO":
        return IngredienteCarbohidrato(nombre, precio_base, precio_mercado, identificador)
    if c == "VERDURA":
        return IngredienteVerdura(nombre, precio_base, precio_mercado, identificador)
    return IngredienteProteina(nombre, precio_base, precio_mercado, identificador)


def _fabrica_plato(
    tipo: str, nombre: str, margen: float, identificador: int | None
) -> Plato:
    t = (tipo or "PRINCIPAL").upper()
    if t == "ENTRADA":
        return PlatoEntrada(nombre, margen, identificador)
    if t == "POSTRE":
        return PlatoPostre(nombre, margen, identificador)
    return PlatoPrincipal(nombre, margen, identificador)


class AlmacenSQLite:
    """Gestiona el archivo .db: tablas relacionadas platos ↔ receta ↔ ingredientes."""

    def __init__(self, ruta_bd: Path | str) -> None:
        self._ruta = Path(ruta_bd)

    def conectar(self) -> sqlite3.Connection:
        self._ruta.parent.mkdir(parents=True, exist_ok=True)
        cx = sqlite3.connect(self._ruta)
        cx.execute("PRAGMA foreign_keys = ON")
        return cx

    def inicializar_esquema(self, conexion: sqlite3.Connection) -> None:
        cur = conexion.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS platos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tipo_plato TEXT NOT NULL,
                margen_ganancia REAL NOT NULL DEFAULT 0.35
            );

            CREATE TABLE IF NOT EXISTS ingredientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria TEXT NOT NULL,
                precio_base REAL NOT NULL,
                precio_mercado REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS receta_detalle (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plato_id INTEGER NOT NULL,
                ingrediente_id INTEGER NOT NULL,
                cantidad REAL NOT NULL DEFAULT 1.0,
                FOREIGN KEY (plato_id) REFERENCES platos(id) ON DELETE CASCADE,
                FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_receta_plato ON receta_detalle(plato_id);
            CREATE INDEX IF NOT EXISTS idx_receta_ing ON receta_detalle(ingrediente_id);
            """
        )
        conexion.commit()

    def sembrar_datos_demo(self, conexion: sqlite3.Connection) -> None:
        """Al menos 5 filas por tabla si están vacías (auditoría del taller)."""
        cur = conexion.cursor()
        cur.execute("SELECT COUNT(*) FROM platos")
        if cur.fetchone()[0] > 0:
            conexion.commit()
            return

        platos_rows = [
            ("Sopa del día", "ENTRADA", MARGEN_GANANCIA_DEFECTO),
            ("Ensalada tropical", "ENTRADA", MARGEN_GANANCIA_DEFECTO),
            ("Bandeja paisa", "PRINCIPAL", MARGEN_GANANCIA_DEFECTO),
            ("Ajiaco santafereño", "PRINCIPAL", MARGEN_GANANCIA_DEFECTO),
            ("Torta de chocolate", "POSTRE", 0.40),
        ]
        cur.executemany(
            "INSERT INTO platos (nombre, tipo_plato, margen_ganancia) VALUES (?,?,?)",
            platos_rows,
        )

        ingredientes_rows = [
            ("Carne molida premium", "PROTEINA", 12000, 14800),
            ("Frijol cargamanto", "CARBOHIDRATO", 3500, 4100),
            ("Papa sabanera", "VERDURA", 2800, 2200),
            ("Aguacate hass", "VERDURA", 4500, 6200),
            ("Arroz blanco", "CARBOHIDRATO", 3200, 3000),
            ("Pollo entero", "PROTEINA", 9000, 11500),
            ("Crema de leche", "PROTEINA", 5500, 5800),
        ]
        cur.executemany(
            """
            INSERT INTO ingredientes (nombre, categoria, precio_base, precio_mercado)
            VALUES (?,?,?,?)
            """,
            ingredientes_rows,
        )

        cur.execute("SELECT id, nombre FROM platos ORDER BY id")
        ids_platos = {nombre: pid for pid, nombre in cur.fetchall()}
        cur.execute("SELECT id, nombre FROM ingredientes ORDER BY id")
        ids_ings = {nombre: iid for iid, nombre in cur.fetchall()}

        receta = [
            ("Bandeja paisa", "Carne molida premium", 0.35),
            ("Bandeja paisa", "Frijol cargamanto", 0.45),
            ("Bandeja paisa", "Arroz blanco", 0.5),
            ("Ajiaco santafereño", "Papa sabanera", 0.8),
            ("Ajiaco santafereño", "Pollo entero", 0.4),
            ("Ajiaco santafereño", "Aguacate hass", 0.25),
            ("Torta de chocolate", "Crema de leche", 0.3),
        ]
        detalle_vals = []
        for plato_n, ing_n, cant in receta:
            detalle_vals.append(
                (ids_platos[plato_n], ids_ings[ing_n], cant),
            )
        cur.executemany(
            """
            INSERT INTO receta_detalle (plato_id, ingrediente_id, cantidad)
            VALUES (?,?,?)
            """,
            detalle_vals,
        )
        conexion.commit()

    # --- CRUD Platos ---
    def listar_platos(self, conexion: sqlite3.Connection) -> list[dict[str, Any]]:
        cur = conexion.cursor()
        cur.execute(
            "SELECT id, nombre, tipo_plato, margen_ganancia FROM platos ORDER BY id"
        )
        cols = ["id", "nombre", "tipo_plato", "margen_ganancia"]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def insertar_plato(self, conexion: sqlite3.Connection, plato: Plato) -> int:
        cur = conexion.cursor()
        cur.execute(
            """
            INSERT INTO platos (nombre, tipo_plato, margen_ganancia)
            VALUES (?,?,?)
            """,
            (
                plato.get_nombre(),
                plato.tipo_plato_codigo(),
                plato.get_margen_ganancia(),
            ),
        )
        conexion.commit()
        return int(cur.lastrowid)

    def actualizar_plato(self, conexion: sqlite3.Connection, plato: Plato) -> None:
        if plato.get_id() is None:
            raise ValueError("Plato sin id no se puede actualizar.")
        cur = conexion.cursor()
        cur.execute(
            """
            UPDATE platos SET nombre=?, tipo_plato=?, margen_ganancia=?
            WHERE id=?
            """,
            (
                plato.get_nombre(),
                plato.tipo_plato_codigo(),
                plato.get_margen_ganancia(),
                plato.get_id(),
            ),
        )
        conexion.commit()

    def eliminar_plato(self, conexion: sqlite3.Connection, plato_id: int) -> None:
        cur = conexion.cursor()
        cur.execute("DELETE FROM receta_detalle WHERE plato_id=?", (plato_id,))
        cur.execute("DELETE FROM platos WHERE id=?", (plato_id,))
        conexion.commit()

    def obtener_plato_por_id(
        self, conexion: sqlite3.Connection, plato_id: int
    ) -> Plato | None:
        cur = conexion.cursor()
        cur.execute(
            "SELECT id, nombre, tipo_plato, margen_ganancia FROM platos WHERE id=?",
            (plato_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return _fabrica_plato(row[2], row[1], row[3], row[0])

    # --- CRUD Ingredientes ---
    def listar_ingredientes(self, conexion: sqlite3.Connection) -> list[dict[str, Any]]:
        cur = conexion.cursor()
        cur.execute(
            """
            SELECT id, nombre, categoria, precio_base, precio_mercado
            FROM ingredientes ORDER BY id
            """
        )
        cols = ["id", "nombre", "categoria", "precio_base", "precio_mercado"]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def insertar_ingrediente(
        self, conexion: sqlite3.Connection, ing: Ingrediente
    ) -> int:
        cur = conexion.cursor()
        cur.execute(
            """
            INSERT INTO ingredientes (nombre, categoria, precio_base, precio_mercado)
            VALUES (?,?,?,?)
            """,
            (
                ing.get_nombre(),
                ing.categoria_codigo(),
                ing.get_precio_base(),
                ing.get_precio_mercado(),
            ),
        )
        conexion.commit()
        return int(cur.lastrowid)

    def actualizar_ingrediente(
        self, conexion: sqlite3.Connection, ing: Ingrediente
    ) -> None:
        if ing.get_id() is None:
            raise ValueError("Ingrediente sin id no se puede actualizar.")
        cur = conexion.cursor()
        cur.execute(
            """
            UPDATE ingredientes SET nombre=?, categoria=?, precio_base=?, precio_mercado=?
            WHERE id=?
            """,
            (
                ing.get_nombre(),
                ing.categoria_codigo(),
                ing.get_precio_base(),
                ing.get_precio_mercado(),
                ing.get_id(),
            ),
        )
        conexion.commit()

    def eliminar_ingrediente(self, conexion: sqlite3.Connection, ing_id: int) -> None:
        cur = conexion.cursor()
        cur.execute("DELETE FROM receta_detalle WHERE ingrediente_id=?", (ing_id,))
        cur.execute("DELETE FROM ingredientes WHERE id=?", (ing_id,))
        conexion.commit()

    def obtener_ingrediente_por_id(
        self, conexion: sqlite3.Connection, ing_id: int
    ) -> Ingrediente | None:
        cur = conexion.cursor()
        cur.execute(
            """
            SELECT id, nombre, categoria, precio_base, precio_mercado
            FROM ingredientes WHERE id=?
            """,
            (ing_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return _fabrica_ingrediente(row[2], row[1], row[3], row[4], row[0])

    # --- CRUD Receta detalle ---
    def listar_receta(self, conexion: sqlite3.Connection) -> list[dict[str, Any]]:
        cur = conexion.cursor()
        cur.execute(
            """
            SELECT rd.id, rd.plato_id, rd.ingrediente_id, rd.cantidad,
                   p.nombre AS plato_nombre, i.nombre AS ingrediente_nombre
            FROM receta_detalle rd
            JOIN platos p ON p.id = rd.plato_id
            JOIN ingredientes i ON i.id = rd.ingrediente_id
            ORDER BY rd.id
            """
        )
        cols = [
            "id",
            "plato_id",
            "ingrediente_id",
            "cantidad",
            "plato_nombre",
            "ingrediente_nombre",
        ]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    def insertar_receta_linea(
        self,
        conexion: sqlite3.Connection,
        plato_id: int,
        ingrediente_id: int,
        cantidad: float,
    ) -> int:
        cur = conexion.cursor()
        cur.execute(
            """
            INSERT INTO receta_detalle (plato_id, ingrediente_id, cantidad)
            VALUES (?,?,?)
            """,
            (plato_id, ingrediente_id, cantidad),
        )
        conexion.commit()
        return int(cur.lastrowid)

    def actualizar_receta_linea(
        self, conexion: sqlite3.Connection, linea_id: int, cantidad: float
    ) -> None:
        cur = conexion.cursor()
        cur.execute(
            "UPDATE receta_detalle SET cantidad=? WHERE id=?",
            (cantidad, linea_id),
        )
        conexion.commit()

    def eliminar_receta_linea(self, conexion: sqlite3.Connection, linea_id: int) -> None:
        cur = conexion.cursor()
        cur.execute("DELETE FROM receta_detalle WHERE id=?", (linea_id,))
        conexion.commit()

    def informe_costeo_platos(self, conexion: sqlite3.Connection) -> list[dict[str, Any]]:
        """Consulta obligatoria con JOIN: costo a precio mercado y precio sugerido."""
        cur = conexion.cursor()
        cur.execute(
            """
            SELECT
                p.id AS plato_id,
                p.nombre AS plato,
                p.tipo_plato,
                p.margen_ganancia,
                SUM(rd.cantidad * i.precio_mercado) AS costo_mercado,
                SUM(rd.cantidad * i.precio_base) AS costo_base
            FROM platos p
            JOIN receta_detalle rd ON rd.plato_id = p.id
            JOIN ingredientes i ON i.id = rd.ingrediente_id
            GROUP BY p.id, p.nombre, p.tipo_plato, p.margen_ganancia
            ORDER BY p.nombre
            """
        )
        rows = cur.fetchall()
        resultado: list[dict[str, Any]] = []
        for row in rows:
            costo_m = float(row[4] or 0)
            margen = float(row[3])
            precio_sugerido = costo_m * (1.0 + margen)
            resultado.append(
                {
                    "plato_id": row[0],
                    "plato": row[1],
                    "tipo_plato": row[2],
                    "margen_ganancia": margen,
                    "costo_mercado": costo_m,
                    "costo_base": float(row[5] or 0),
                    "precio_sugerido_venta": precio_sugerido,
                }
            )
        return resultado

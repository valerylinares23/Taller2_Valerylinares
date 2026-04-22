"""Menú interactivo CRUD y reportes (Chef-Costos, persistencia SQLite)."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from chef_costos.constantes import MARGEN_GANANCIA_DEFECTO, UMBRAL_ALERTA_PRECIO
from chef_costos.entidades import (
    IngredienteCarbohidrato,
    IngredienteProteina,
    IngredienteVerdura,
    PlatoEntrada,
    PlatoPostre,
    PlatoPrincipal,
    RegistroAltaIngrediente,
    RegistroAlertaPrecio,
    RegistroCosteoPlato,
)
from chef_costos.persistencia import AlmacenSQLite

# Ruta por defecto del archivo de base de datos (requisito del taller)
RUTA_BD_DEFECTO = (
    Path(__file__).resolve().parent.parent / "base_datos_startup_grupo_sofia.db"
)


def _leer_entero(mensaje: str) -> int:
    while True:
        try:
            return int(input(mensaje).strip())
        except ValueError:
            print("Ingresa un número entero válido.")


def _leer_flotante(mensaje: str, positivo: bool = True) -> float:
    while True:
        try:
            v = float(input(mensaje).strip().replace(",", "."))
            if positivo and v <= 0:
                print("Debe ser un valor positivo.")
                continue
            if not positivo and v < 0:
                print("Valor no válido.")
                continue
            return v
        except ValueError:
            print("Ingresa un número válido.")


def _elegir_categoria_ingrediente():
    print("Categoría: 1=Proteína 2=Carbohidrato 3=Verdura")
    op = _leer_entero("Opción: ")
    if op == 1:
        return IngredienteProteina
    if op == 2:
        return IngredienteCarbohidrato
    if op == 3:
        return IngredienteVerdura
    print("Opción inválida; usando Proteína.")
    return IngredienteProteina


def _elegir_tipo_plato():
    print("Tipo: 1=Entrada 2=Principal 3=Postre")
    op = _leer_entero("Opción: ")
    if op == 1:
        return PlatoEntrada
    if op == 2:
        return PlatoPrincipal
    if op == 3:
        return PlatoPostre
    print("Opción inválida; usando Principal.")
    return PlatoPrincipal


def _submenu_ingredientes(almacen: AlmacenSQLite, cx: sqlite3.Connection) -> None:
    while True:
        print(
            "\n--- Ingredientes ---\n"
            "1 Listar  2 Crear  3 Actualizar  4 Eliminar  0 Volver"
        )
        op = input("Opción: ").strip()
        try:
            if op == "0":
                return
            if op == "1":
                for r in almacen.listar_ingredientes(cx):
                    alerta = (
                        "⚠ >20% vs base"
                        if r["precio_mercado"] > r["precio_base"] * UMBRAL_ALERTA_PRECIO
                        else "OK"
                    )
                    print(
                        f"  [{r['id']}] {r['nombre']} ({r['categoria']}) | "
                        f"base ${r['precio_base']:,.0f} mercado ${r['precio_mercado']:,.0f} | {alerta}"
                    )
            elif op == "2":
                cls = _elegir_categoria_ingrediente()
                nombre = input("Nombre: ").strip()
                pb = _leer_flotante("Precio base (COP): ")
                pm = _leer_flotante("Precio mercado actual (COP): ", positivo=False)
                if pm < 0:
                    print("Precio mercado no puede ser negativo.")
                    continue
                ent = cls(nombre, pb, pm)
                nuevo_id = almacen.insertar_ingrediente(cx, ent)
                ent.set_id(nuevo_id)
                reg = RegistroAltaIngrediente(
                    descripcion=ent.get_nombre(), referencia_id=nuevo_id
                )
                print(reg.resumen())
                if ent.mercado_supera_umbral():
                    alerta = RegistroAlertaPrecio(
                        descripcion="Mercado supera 20% sobre base",
                        referencia_id=nuevo_id,
                    )
                    print(alerta.resumen())
            elif op == "3":
                iid = _leer_entero("ID ingrediente: ")
                actual = almacen.obtener_ingrediente_por_id(cx, iid)
                if not actual:
                    print("No existe ese ID.")
                    continue
                cls = _elegir_categoria_ingrediente()
                nombre = input(f"Nombre [{actual.get_nombre()}]: ").strip()
                nombre = nombre or actual.get_nombre()
                pb = input(f"Precio base [{actual.get_precio_base()}]: ").strip()
                precio_base = float(pb) if pb else actual.get_precio_base()
                pm = input(f"Precio mercado [{actual.get_precio_mercado()}]: ").strip()
                precio_mercado = float(pm) if pm else actual.get_precio_mercado()
                editado = cls(nombre, precio_base, precio_mercado, iid)
                almacen.actualizar_ingrediente(cx, editado)
                print("Actualizado.")
            elif op == "4":
                iid = _leer_entero("ID a eliminar: ")
                conf = input("¿Seguro? (s/N): ").strip().lower()
                if conf == "s":
                    almacen.eliminar_ingrediente(cx, iid)
                    print("Eliminado (y líneas de receta asociadas).")
        except sqlite3.Error as e:
            print(f"Error de base de datos: {e}")
        except ValueError as e:
            print(f"Dato inválido: {e}")


def _submenu_platos(almacen: AlmacenSQLite, cx: sqlite3.Connection) -> None:
    while True:
        print("\n--- Platos ---\n1 Listar  2 Crear  3 Actualizar  4 Eliminar  0 Volver")
        op = input("Opción: ").strip()
        try:
            if op == "0":
                return
            if op == "1":
                for r in almacen.listar_platos(cx):
                    print(
                        f"  [{r['id']}] {r['nombre']} | {r['tipo_plato']} | "
                        f"margen {r['margen_ganancia']:.0%}"
                    )
            elif op == "2":
                cls = _elegir_tipo_plato()
                nombre = input("Nombre del plato: ").strip()
                mg_txt = input(
                    f"Margen ganancia (0-1) [defecto {MARGEN_GANANCIA_DEFECTO}]: "
                ).strip()
                margen = float(mg_txt) if mg_txt else MARGEN_GANANCIA_DEFECTO
                plato = cls(nombre, margen)
                pid = almacen.insertar_plato(cx, plato)
                print(f"Creado con id={pid}")
            elif op == "3":
                pid = _leer_entero("ID plato: ")
                actual = almacen.obtener_plato_por_id(cx, pid)
                if not actual:
                    print("No existe ese ID.")
                    continue
                cls = _elegir_tipo_plato()
                nombre = input(f"Nombre [{actual.get_nombre()}]: ").strip()
                nombre = nombre or actual.get_nombre()
                mg = input(
                    f"Margen [{actual.get_margen_ganancia()}]: "
                ).strip()
                margen = float(mg) if mg else actual.get_margen_ganancia()
                editado = cls(nombre, margen, pid)
                almacen.actualizar_plato(cx, editado)
                print("Actualizado.")
            elif op == "4":
                pid = _leer_entero("ID a eliminar: ")
                if input("¿Seguro? (s/N): ").strip().lower() == "s":
                    almacen.eliminar_plato(cx, pid)
                    print("Eliminado.")
        except sqlite3.Error as e:
            print(f"Error de base de datos: {e}")
        except ValueError as e:
            print(f"Dato inválido: {e}")


def _submenu_receta(almacen: AlmacenSQLite, cx: sqlite3.Connection) -> None:
    while True:
        print(
            "\n--- Receta (detalle) ---\n"
            "1 Listar  2 Agregar línea  3 Cambiar cantidad  4 Eliminar línea  0 Volver"
        )
        op = input("Opción: ").strip()
        try:
            if op == "0":
                return
            if op == "1":
                for r in almacen.listar_receta(cx):
                    print(
                        f"  [{r['id']}] {r['plato_nombre']} + {r['ingrediente_nombre']} "
                        f"x{r['cantidad']}"
                    )
            elif op == "2":
                pid = _leer_entero("ID plato: ")
                iid = _leer_entero("ID ingrediente: ")
                cant = _leer_flotante("Cantidad (factor por porción): ")
                lid = almacen.insertar_receta_linea(cx, pid, iid, cant)
                print(f"Línea creada id={lid}")
            elif op == "3":
                lid = _leer_entero("ID línea receta: ")
                cant = _leer_flotante("Nueva cantidad: ")
                almacen.actualizar_receta_linea(cx, lid, cant)
                print("Actualizado.")
            elif op == "4":
                lid = _leer_entero("ID línea: ")
                if input("¿Seguro? (s/N): ").strip().lower() == "s":
                    almacen.eliminar_receta_linea(cx, lid)
                    print("Eliminado.")
        except sqlite3.Error as e:
            print(f"Error de base de datos: {e}")


def _mostrar_informe_costeo(almacen: AlmacenSQLite, cx: sqlite3.Connection) -> None:
    try:
        filas = almacen.informe_costeo_platos(cx)
        if not filas:
            print("No hay platos con receta para costear.")
            return
        print("\n=== Informe costeo (JOIN platos + receta + ingredientes) ===")
        for r in filas:
            reg = RegistroCosteoPlato(
                descripcion=r["plato"],
                referencia_id=r["plato_id"],
                monto_relacionado=r["costo_mercado"],
            )
            print(
                f"- {reg.resumen()} | "
                f"Precio sugerido: ${r['precio_sugerido_venta']:,.0f} COP "
                f"({r['tipo_plato']}, margen {r['margen_ganancia']:.0%})"
            )
    except sqlite3.Error as e:
        print(f"Error de base de datos: {e}")


def ejecutar(ruta_bd: Path | None = None) -> None:
    ruta = Path(ruta_bd) if ruta_bd else RUTA_BD_DEFECTO
    almacen = AlmacenSQLite(ruta)
    try:
        cx = almacen.conectar()
    except sqlite3.Error as e:
        print(f"No se pudo conectar a la base de datos: {e}")
        sys.exit(1)

    try:
        almacen.inicializar_esquema(cx)
        almacen.sembrar_datos_demo(cx)
    except sqlite3.Error as e:
        print(f"Error al preparar esquema o datos: {e}")
        cx.close()
        sys.exit(1)

    print("=== Chef-Costos (Gastronomía) — Arquitectura Corte 2 ===")
    print(f"Base de datos: {ruta}")
    print(
        f"MVP Corte 1: margen {MARGEN_GANANCIA_DEFECTO:.0%}, "
        f"alerta si mercado > {UMBRAL_ALERTA_PRECIO:.0%} sobre base."
    )

    while True:
        print(
            "\n--- Menú principal ---\n"
            "1 Ingredientes (CRUD)\n"
            "2 Platos (CRUD)\n"
            "3 Receta / composición (CRUD)\n"
            "4 Informe de costeo con JOIN\n"
            "0 Salir"
        )
        op = input("Opción: ").strip()
        try:
            if op == "0":
                break
            if op == "1":
                _submenu_ingredientes(almacen, cx)
            elif op == "2":
                _submenu_platos(almacen, cx)
            elif op == "3":
                _submenu_receta(almacen, cx)
            elif op == "4":
                _mostrar_informe_costeo(almacen, cx)
            else:
                print("Opción no reconocida.")
        except KeyboardInterrupt:
            print("\nInterrumpido.")
            break

    cx.close()
    print("Sesión finalizada.")


if __name__ == "__main__":
    ejecutar()

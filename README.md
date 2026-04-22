# Proyecto Corte 2 — Grupo Sofía

Sistema **Chef-Costos** (dominio **gastronomía**): evolución del MVP de Corte 1 (`taller_parte2_corte1.py`), que guardaba todo en memoria y en flujo secuencial, hacia una **arquitectura por capas** con **POO**, **encapsulación** y **persistencia relacional en SQLite**.

## Objetivo

- **De** datos volátiles y código lineal **a** entidades de negocio modeladas en clases y un archivo `.db` local.
- Mantener la lógica del reto original: comparación **precio base vs mercado** (alerta si el mercado supera ~20% sobre la base), **costo total** y **precio sugerido** con margen de ganancia (por defecto **35%**).

## Requisitos

- Python **3.10+** (tipado con `int | None`, etc.).
- Sin dependencias externas: solo biblioteca estándar (`sqlite3`, `pathlib`).

## Estructura del repositorio

| Ruta | Descripción |
|------|-------------|
| `app_escalada_grupo_sofia.py` | Punto de entrada del taller |
| `chef_costos/` | Paquete: entidades, persistencia, menú |
| `design/diagrama_clases.md` | Diagrama de clases (Mermaid) |
| `design/erd_base_datos.md` | ERD y notas de normalización (Mermaid) |
| `base_datos_startup_grupo_sofia.db` | Creado al ejecutar (ignorado en Git) |

## Cómo ejecutar

Desde la raíz del proyecto:

```bash
python app_escalada_grupo_sofia.py
```

En el primer arranque se crean las tablas (`CREATE TABLE IF NOT EXISTS`), se cargan **datos demo** (mínimo **5 registros por tabla** si la base está vacía) y el menú permite **CRUD** sobre ingredientes, platos y líneas de receta, además de un **informe de costeo** con **JOIN** entre tablas.

## Arquitectura técnica (resumen)

### POO

- **Tres jerarquías** de negocio, cada una con **tres subclases**:
  - `Ingrediente` → proteína, carbohidrato, verdura.
  - `Plato` → entrada, principal, postre.
  - `RegistroOperacion` → alta de insumo, costeo de plato, alerta de precio.
- Atributos sensibles con prefijo **`__`** y acceso mediante **getters/setters**.

### Base de datos

- Archivo: `base_datos_startup_grupo_sofia.db`.
- **Tres tablas relacionadas**: `platos`, `ingredientes`, `receta_detalle` con **PK** y **FK**.
- Consulta de negocio con **`JOIN`** + `GROUP BY` para costo a precio de mercado y precio de venta sugerido.

### Robustez

- **`try` / `except`** ante entradas inválidas, errores `sqlite3` y uso de `KeyboardInterrupt` en el menú principal.

## Equipo

**Grupo Sofía** — Proyecto académico 2026.

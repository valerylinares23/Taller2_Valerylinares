# Modelo entidad-relación (SQLite) — `base_datos_startup_grupo_sofia.db`

Tres tablas relacionadas con **PK** y **FK** (normalización básica: plato ↔ composición ↔ ingrediente).

```mermaid
erDiagram
    PLATOS ||--o{ RECETA_DETALLE : contiene
    INGREDIENTES ||--o{ RECETA_DETALLE : usado_en

    PLATOS {
        int id PK
        text nombre
        text tipo_plato
        real margen_ganancia
    }
    INGREDIENTES {
        int id PK
        text nombre
        text categoria
        real precio_base
        real precio_mercado
    }
    RECETA_DETALLE {
        int id PK
        int plato_id FK
        int ingrediente_id FK
        real cantidad
    }
```

### Reglas de negocio reflejadas

- Cada línea de `receta_detalle` asocia **un plato** con **un ingrediente** y una **cantidad** (factor por porción).
- Al eliminar un plato o un ingrediente, se eliminan primero las filas dependientes en `receta_detalle` (integridad referencial en la aplicación; SQLite con `ON DELETE CASCADE` y `PRAGMA foreign_keys=ON`).
- El **costeo** del MVP (Corte 1) se generaliza: \(\text{precio sugerido} = \sum(\text{cantidad} \times \text{precio\_mercado}) \times (1 + \text{margen})\), implementado en la consulta con `JOIN` y `GROUP BY`.

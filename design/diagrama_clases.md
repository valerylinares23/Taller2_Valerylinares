# Diagrama de clases — Chef-Costos (Corte 2)

Vista simplificada de la jerarquía OOP: **tres clases padre**, cada una con **tres hijas**, encapsulación con atributos privados (`__...`) y acceso mediante getters/setters.

```mermaid
classDiagram
    class Ingrediente {
        -int|None __id
        -str __nombre
        -float __precio_base
        -float __precio_mercado
        +get_nombre() str
        +set_nombre(str)
        +get_precio_base() float
        +set_precio_base(float)
        +categoria_codigo() str
        +mercado_supera_umbral() bool
    }
    class IngredienteProteina
    class IngredienteCarbohidrato
    class IngredienteVerdura
    Ingrediente <|-- IngredienteProteina
    Ingrediente <|-- IngredienteCarbohidrato
    Ingrediente <|-- IngredienteVerdura

    class Plato {
        -int|None __id
        -str __nombre
        -float __margen_ganancia
        +get_nombre() str
        +tipo_plato_codigo() str
        +get_margen_ganancia() float
    }
    class PlatoEntrada
    class PlatoPrincipal
    class PlatoPostre
    Plato <|-- PlatoEntrada
    Plato <|-- PlatoPrincipal
    Plato <|-- PlatoPostre

    class RegistroOperacion {
        -datetime __fecha_hora
        -str __descripcion
        -int|None __referencia_id
        -float|None __monto_relacionado
        +resumen() str
        +codigo_tipo() str
    }
    class RegistroAltaIngrediente
    class RegistroCosteoPlato
    class RegistroAlertaPrecio
    RegistroOperacion <|-- RegistroAltaIngrediente
    RegistroOperacion <|-- RegistroCosteoPlato
    RegistroOperacion <|-- RegistroAlertaPrecio

    class AlmacenSQLite {
        +conectar()
        +inicializar_esquema()
        +sembrar_datos_demo()
        +CRUD platos/ingredientes/receta
        +informe_costeo_platos() JOIN
    }
    AlmacenSQLite ..> Plato : persiste
    AlmacenSQLite ..> Ingrediente : persiste
```

La clase `AlmacenSQLite` no forma parte de las tres jerarquías de negocio exigidas; actúa como **capa de persistencia** entre objetos y SQLite.

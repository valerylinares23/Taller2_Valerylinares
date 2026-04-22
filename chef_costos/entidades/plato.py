"""Jerarquía 2/3: platos del menú con tipología OOP."""

from __future__ import annotations

from chef_costos.constantes import MARGEN_GANANCIA_DEFECTO


class Plato:
    """Plato costeable: margen y nombre encapsulados."""

    def __init__(
        self,
        nombre: str,
        margen_ganancia: float | None = None,
        identificador: int | None = None,
    ) -> None:
        self.__id = identificador
        self.__nombre = nombre.strip()
        self.__margen_ganancia = (
            float(margen_ganancia)
            if margen_ganancia is not None
            else MARGEN_GANANCIA_DEFECTO
        )

    def get_id(self) -> int | None:
        return self.__id

    def set_id(self, valor: int | None) -> None:
        self.__id = valor

    def get_nombre(self) -> str:
        return self.__nombre

    def set_nombre(self, valor: str) -> None:
        self.__nombre = valor.strip()

    def get_margen_ganancia(self) -> float:
        return self.__margen_ganancia

    def set_margen_ganancia(self, valor: float) -> None:
        self.__margen_ganancia = float(valor)

    def tipo_plato_codigo(self) -> str:
        return "GENERICO"

    def tiempo_preparacion_minutos_referencia(self) -> int:
        return 30


class PlatoEntrada(Plato):
    def tipo_plato_codigo(self) -> str:
        return "ENTRADA"

    def tiempo_preparacion_minutos_referencia(self) -> int:
        return 20


class PlatoPrincipal(Plato):
    def tipo_plato_codigo(self) -> str:
        return "PRINCIPAL"

    def tiempo_preparacion_minutos_referencia(self) -> int:
        return 45


class PlatoPostre(Plato):
    def tipo_plato_codigo(self) -> str:
        return "POSTRE"

    def tiempo_preparacion_minutos_referencia(self) -> int:
        return 25

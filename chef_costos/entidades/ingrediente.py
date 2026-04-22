"""Jerarquía 1/3: insumos gastronómicos con encapsulación."""

from __future__ import annotations

from chef_costos.constantes import UMBRAL_ALERTA_PRECIO


class Ingrediente:
    """Insumo base: precios sensibles encapsulados con getters/setters."""

    def __init__(
        self,
        nombre: str,
        precio_base: float,
        precio_mercado: float,
        identificador: int | None = None,
    ) -> None:
        self.__id = identificador
        self.__nombre = nombre.strip()
        self.__precio_base = float(precio_base)
        self.__precio_mercado = float(precio_mercado)

    def get_id(self) -> int | None:
        return self.__id

    def set_id(self, valor: int | None) -> None:
        self.__id = valor

    def get_nombre(self) -> str:
        return self.__nombre

    def set_nombre(self, valor: str) -> None:
        self.__nombre = valor.strip()

    def get_precio_base(self) -> float:
        return self.__precio_base

    def set_precio_base(self, valor: float) -> None:
        self.__precio_base = float(valor)

    def get_precio_mercado(self) -> float:
        return self.__precio_mercado

    def set_precio_mercado(self, valor: float) -> None:
        self.__precio_mercado = float(valor)

    def categoria_codigo(self) -> str:
        return "BASE"

    def factor_merma_sugerido(self) -> float:
        return 1.0

    def mercado_supera_umbral(self) -> bool:
        base = self.__precio_base
        if base <= 0:
            return False
        return self.__precio_mercado > base * UMBRAL_ALERTA_PRECIO


class IngredienteProteina(Ingrediente):
    def categoria_codigo(self) -> str:
        return "PROTEINA"

    def factor_merma_sugerido(self) -> float:
        return 1.12


class IngredienteCarbohidrato(Ingrediente):
    def categoria_codigo(self) -> str:
        return "CARBOHIDRATO"

    def factor_merma_sugerido(self) -> float:
        return 1.05


class IngredienteVerdura(Ingrediente):
    def categoria_codigo(self) -> str:
        return "VERDURA"

    def factor_merma_sugerido(self) -> float:
        return 1.08

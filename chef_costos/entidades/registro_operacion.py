"""Jerarquía 3/3: registros de negocio (trazabilidad de operaciones de costeo)."""

from __future__ import annotations

from datetime import datetime


class RegistroOperacion:
    """Registro abstracto de operación con metadatos privados."""

    def __init__(
        self,
        descripcion: str,
        referencia_id: int | None = None,
        monto_relacionado: float | None = None,
    ) -> None:
        self.__fecha_hora = datetime.now()
        self.__descripcion = descripcion.strip()
        self.__referencia_id = referencia_id
        self.__monto_relacionado = (
            float(monto_relacionado) if monto_relacionado is not None else None
        )

    def get_fecha_hora(self) -> datetime:
        return self.__fecha_hora

    def get_descripcion(self) -> str:
        return self.__descripcion

    def set_descripcion(self, valor: str) -> None:
        self.__descripcion = valor.strip()

    def get_referencia_id(self) -> int | None:
        return self.__referencia_id

    def set_referencia_id(self, valor: int | None) -> None:
        self.__referencia_id = valor

    def get_monto_relacionado(self) -> float | None:
        return self.__monto_relacionado

    def set_monto_relacionado(self, valor: float | None) -> None:
        self.__monto_relacionado = float(valor) if valor is not None else None

    def codigo_tipo(self) -> str:
        return "GENERICO"

    def resumen(self) -> str:
        return f"[{self.codigo_tipo()}] {self.__descripcion}"


class RegistroAltaIngrediente(RegistroOperacion):
    def codigo_tipo(self) -> str:
        return "ALTA_INSUMO"

    def resumen(self) -> str:
        rid = self.get_referencia_id()
        return f"Alta de insumo id={rid}: {self.get_descripcion()}"


class RegistroCosteoPlato(RegistroOperacion):
    def codigo_tipo(self) -> str:
        return "COSTEO_PLATO"

    def resumen(self) -> str:
        m = self.get_monto_relacionado()
        m_txt = f"{m:,.0f} COP" if m is not None else "N/D"
        return f"Costeo plato id={self.get_referencia_id()}: costo mercado {m_txt}"


class RegistroAlertaPrecio(RegistroOperacion):
    def codigo_tipo(self) -> str:
        return "ALERTA_PRECIO"

    def resumen(self) -> str:
        return (
            f"Alerta precio insumo id={self.get_referencia_id()}: "
            f"{self.get_descripcion()}"
        )

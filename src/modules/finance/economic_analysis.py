"""
Модуль экономического анализа (ОП.04).
Расширяет финансовый модуль (ОП.03) коэффициентами ликвидности,
рентабельности, деловой активности и маржинальным анализом.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class FinancialStabilityType(str, Enum):
    """Типы финансовой устойчивости предприятия"""
    ABSOLUTE = "Абсолютная финансовая устойчивость"
    NORMAL = "Нормальная финансовая устойчивость"
    UNSTABLE = "Неустойчивое финансовое состояние"
    CRISIS = "Кризисное финансовое состояние"


@dataclass
class MarginData:
    """Данные для маржинального анализа"""
    price_per_unit: float
    variable_cost_per_unit: float
    total_fixed_costs: float


@dataclass
class DuPontComponents:
    """Компоненты трёхфакторной модели Дюпона"""
    net_profit_margin: float
    asset_turnover: float
    financial_leverage: float
    roe: float


class EconomicAnalysisEngine:
    """
    Движок экономического анализа предприятия.
    Используется для подготовки раздела 'Финансовый анализ' в отчёте об оценке.
    Реализует требования ПП РФ от 25.06.2003 №367.
    """

    @staticmethod
    def calculate_current_liquidity(
        current_assets: float,
        current_liabilities: float
    ) -> float:
        """
        Коэффициент текущей ликвидности (Ктл).

        НПА: ПП РФ от 25.06.2003 №367 «Правила проведения финансового
        анализа арбитражным управляющим».
        Тема 11. Анализ ликвидности.

        Формула: Ктл = Оборотные активы / Краткосрочные обязательства
        Норма: 2.0 — 3.5

        Пример (Волгоградская область):
        ОАО «Волгограднефтемаш»: ОА = 1 500 000, КО = 600 000.
        Ктл = 2.5 (в пределах нормы).

        В отчёте: раздел «Финансовый анализ», таблица коэффициентов ликвидности.
        """
        if current_liabilities <= 0:
            return 0.0
        return round(current_assets / current_liabilities, 4)

    @staticmethod
    def calculate_financial_leverage(
        debt_capital: float,
        equity_capital: float
    ) -> float:
        """
        Коэффициент финансового рычага.

        НПА: ПП РФ от 25.06.2003 №367.
        Тема 11. Анализ финансовой устойчивости.

        Формула: Кфр = Заёмный капитал / Собственный капитал
        Норма: < 1.0

        Пример (Волгоградская область):
        ООО «Волгоград-Агро»: ЗК = 400 000, СК = 500 000.
        Кфр = 0.8 (норма).

        В отчёте: раздел «Финансовый анализ», таблица финансовой устойчивости.
        """
        if equity_capital <= 0:
            return 0.0
        return round(debt_capital / equity_capital, 4)

    @staticmethod
    def calculate_fixed_assets_turnover(
        revenue: float,
        avg_fixed_assets: float
    ) -> float:
        """
        Фондоотдача (оборачиваемость основных средств).

        НПА: ПБУ 4/99, ФСБУ 6/2020.
        Тема 4. Анализ основных средств.

        Формула: Фотд = Выручка / Средняя стоимость ОС

        Пример (Волгоградская область):
        Волгоградский тракторный завод: Выручка = 10 000 000, ОС = 5 000 000.
        Фотд = 2.0

        В отчёте: раздел «Финансовый анализ», показатели деловой активности.
        """
        if avg_fixed_assets <= 0:
            return 0.0
        return round(revenue / avg_fixed_assets, 4)

    @staticmethod
    def calculate_dupont_roe(
        net_profit: float,
        revenue: float,
        total_assets: float,
        equity: float
    ) -> DuPontComponents:
        """
        Трёхфакторная модель Дюпона (декомпозиция ROE).

        НПА: ФЗ от 06.12.2011 №402-ФЗ «О бухгалтерском учёте».
        Лекция: Мультипликативные модели анализа.

        Формула: ROE = (ЧП/Выручка) × (Выручка/Активы) × (Активы/СК)
                     = Маржа × Оборачиваемость × Леверидж

        Пример (Волгоградская область):
        ООО «Царицын-Трейд»: ЧП=200к, Выручка=2м, Активы=1м, СК=500к.
        Маржа=0.1, Отдача=2.0, Рычаг=2.0. ROE = 0.4 (40%).

        В отчёте: раздел «Финансовый анализ», факторный анализ рентабельности.
        """
        if revenue == 0 or total_assets == 0 or equity == 0:
            return DuPontComponents(0.0, 0.0, 0.0, 0.0)

        margin = net_profit / revenue
        turnover = revenue / total_assets
        leverage = total_assets / equity
        roe = margin * turnover * leverage

        return DuPontComponents(
            net_profit_margin=round(margin, 4),
            asset_turnover=round(turnover, 4),
            financial_leverage=round(leverage, 4),
            roe=round(roe, 4),
        )

    @staticmethod
    def calculate_break_even_point(margin_data: MarginData) -> float:
        """
        Точка безубыточности в натуральном выражении.

        НПА: ФСО V «Подходы и методы оценки» (Приказ МЭР №200).
        Тема 8. Маржинальный анализ.

        Формула: ТБ = Постоянные расходы / (Цена - Переменные расходы на ед.)

        Пример (Волгоградская область):
        Производство труб в г. Волжский:
        FC = 60 000 000, Цена = 65 000, VC = 45 000.
        МП_ед = 20 000. ТБ = 3 000 шт.

        В отчёте: раздел «Доходный подход», обоснование прогноза объёмов.
        """
        mp_per_unit = margin_data.price_per_unit - margin_data.variable_cost_per_unit
        if mp_per_unit <= 0:
            raise ValueError(
                "Маржинальная прибыль на единицу <= 0. "
                "Бизнес генерирует убыток на каждой проданной единице."
            )
        return round(margin_data.total_fixed_costs / mp_per_unit, 2)

    # TODO [ОП.04]: Добавить classify_financial_stability (абсолютная/нормальная/неустойчивая/кризис)
    # TODO [bankruptcy]: Z-счёт Альтмана и коэффициенты ФУДН → bankruptcy/
    # TODO [calc]: NPV, IRR → calc_engine.py при ОП.06


if __name__ == "__main__":
    engine = EconomicAnalysisEngine()

    print("--- ТЕСТИРОВАНИЕ ОП.04 ---\n")

    # 1. Ликвидность
    ktl = engine.calculate_current_liquidity(1_500_000, 600_000)
    print(f"1. Текущая ликвидность: {ktl} (ожидание: 2.5)")

    # 2. Финансовый рычаг
    kfr = engine.calculate_financial_leverage(400_000, 500_000)
    print(f"2. Финансовый рычаг: {kfr} (ожидание: 0.8)")

    # 3. Фондоотдача
    fo = engine.calculate_fixed_assets_turnover(10_000_000, 5_000_000)
    print(f"3. Фондоотдача: {fo} (ожидание: 2.0)")

    # 4. Модель Дюпона
    dp = engine.calculate_dupont_roe(200_000, 2_000_000, 1_000_000, 500_000)
    print(f"4. Дюпон: маржа={dp.net_profit_margin}, оборот={dp.asset_turnover}, "
          f"рычаг={dp.financial_leverage} => ROE={dp.roe} (ожидание: 0.4)")

    # 5. Точка безубыточности
    md = MarginData(price_per_unit=65_000, variable_cost_per_unit=45_000, total_fixed_costs=60_000_000)
    bep = engine.calculate_break_even_point(md)
    print(f"5. Точка безубыточности: {bep} шт. (ожидание: 3000.0)")

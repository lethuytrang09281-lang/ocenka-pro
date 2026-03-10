from dataclasses import dataclass
from typing import Optional, Dict
import math

from src.common.types import CyclePhase, InflationCategory


@dataclass
class MarketDataPoint:
    price: float
    quantity: float


class MicroMacroEngine:
    """
    Ядро микро- и макроэкономических расчетов для анализа рынка.
    Реализует логику согласно Темам 2, 7, 9 лекционного курса.
    """

    @staticmethod
    def calculate_price_elasticity(current: MarketDataPoint, previous: MarketDataPoint) -> float:
        """
        Расчет дуговой эластичности спроса по цене (Epd).
        Используется для обоснования прогнозных значений выручки.

        НПА: ФСО VI, п. 7, подп. 12 (анализ внешних факторов).
        Тема 2, слайд 19.

        Пример (Волгоградская область):
        Цена на хлеб выросла с 40 до 46 руб. (+15%), объем продаж упал с 1000 до 800 ед.
        >>> MicroMacroEngine.calculate_price_elasticity(MarketDataPoint(46, 800), MarketDataPoint(40, 1000))
        1.53 (Спрос эластичный)
        """
        delta_q = current.quantity - previous.quantity
        avg_q = (current.quantity + previous.quantity) / 2
        delta_p = current.price - previous.price
        avg_p = (current.price + previous.price) / 2

        if delta_p == 0:
            return 0.0
        return abs((delta_q / avg_q) / (delta_p / avg_p))

    @staticmethod
    def calculate_inflation_rate(current_index: float, previous_index: float) -> float:
        """
        Расчет темпа инфляции (pi).

        НПА: ФСО V, п. 17 (соответствие ставки дисконтирования виду денежного потока).
        Тема 9, слайд 194.

        Пример: ИПЦ в Волгограде на начало года 110.5, на конец 121.2.
        >>> MicroMacroEngine.calculate_inflation_rate(121.2, 110.5)
        0.0968 (9.68% - Умеренная инфляция)
        """
        return (current_index - previous_index) / previous_index

    @staticmethod
    def calculate_real_gdp(nominal_gdp: float, price_index: float) -> float:
        """
        Пересчет номинального ВВП в реальный через дефлятор.

        НПА: ФСО V, п. 19, подп. 3 (сопоставление с темпами экономического роста).
        Тема 7, слайд 162.
        """
        return nominal_gdp / price_index

    @staticmethod
    def get_okun_law_impact(actual_u: float, natural_u: float = 0.05) -> float:
        """
        Расчет отставания фактического ВВП от потенциального (Закон Оукена).

        Тема 9, слайд 191.
        """
        if actual_u <= natural_u:
            return 0.0
        return (actual_u - natural_u) * 2.25  # Коэффициент 2-2.5%

    @staticmethod
    def classify_inflation(rate_pct: float) -> InflationCategory:
        """
        Классификация темпа инфляции по категориям.
        Тема 9, слайд 193.
        """
        if rate_pct < 5:
            return InflationCategory.NORMAL
        elif rate_pct < 10:
            return InflationCategory.MODERATE
        elif rate_pct < 200:
            return InflationCategory.GALLOPING
        return InflationCategory.HYPER

    @staticmethod
    def determine_cycle_phase(gdp_growth: float, inflation_rising: bool) -> CyclePhase:
        """
        Упрощённое определение фазы экономического цикла.
        Тема 9, слайд 184.
        """
        if gdp_growth < 0:
            return CyclePhase.RECESSION
        elif gdp_growth == 0:
            return CyclePhase.DEPRESSION
        elif inflation_rising:
            return CyclePhase.BOOM
        return CyclePhase.REVIVAL


# TODO [calc]: Интегрировать инфляцию в модуль calc_engine.py для индексации потоков DCF.
# TODO [finance]: Передавать показатель Epd в финансовый анализ для проверки планов продаж.

if __name__ == "__main__":
    engine = MicroMacroEngine()
    # Тест: Анализ эластичности для пекарни в Волжском
    epd = engine.calculate_price_elasticity(MarketDataPoint(50, 900), MarketDataPoint(45, 1000))
    print(f"Коэффициент эластичности: {epd:.2f}")

    # Тест: Инфляция
    pi = engine.calculate_inflation_rate(120, 110)
    print(f"Инфляция: {pi*100:.2f}%")

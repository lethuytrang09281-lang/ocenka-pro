from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
import math


class InvestmentLifeCycle(Enum):
    """Стадии жизненного цикла инвестиционного проекта"""
    PRE_INVESTMENT = "предынвестиционная"
    INVESTMENT = "инвестиционная"
    OPERATIONAL = "эксплуатационная"
    LIQUIDATION = "ликвидационная"


class BondPricingMethod(Enum):
    """Методы расчёта купонной ставки по облигациям"""
    AMERICAN = "американский"  # im = i / m
    EUROPEAN = "европейский"   # im = (1 + i)^(1/m) - 1


@dataclass
class AssetStats:
    """Статистика инвестиционного актива"""
    expected_return: float
    standard_deviation: float
    weight: float = 0.0
    alpha: Optional[float] = None  # Параметр Шарпа
    beta: Optional[float] = None   # Параметр Шарпа


class InvestmentAnalyst:
    """
    Модуль анализа инвестиционных проектов и ценных бумаг.
    Реализует логику тем 7-11 лекционного курса.
    """

    # --- ТЕМА 10: ОПТИМИЗАЦИЯ ПОРТФЕЛЯ (МОДЕЛЬ МАРКОВИЦА) ---

    @staticmethod
    def get_portfolio_return(assets: List[AssetStats]) -> float:
        """
        Расчет ожидаемой доходности портфеля.
        Ссылка: лекция "Инвестиции", Тема 10, слайд 41.
        Формула: E(r_p) = Σ (w_i * E(r_i)).

        Пример: Портфель акций агрохолдингов Волгоградской области.
        Акция А (доходность 15%, вес 0.6), Акция Б (доходность 10%, вес 0.4).
        Результат: 0.6*0.15 + 0.4*0.10 = 0.13 (13%).
        """
        return sum(asset.weight * asset.expected_return for asset in assets)

    @staticmethod
    def get_portfolio_risk(assets: List[AssetStats], covariance_matrix: List[List[float]]) -> float:
        """
        Расчет риска портфеля (дисперсии).
        Ссылка: лекция "Инвестиции", Тема 10, слайд 42.
        Формула: σ_p^2 = ΣΣ (w_i * w_j * σ_ij).

        # TODO [ОП.06]: Матричные вычисления переедут в библиотеку numpy при масштабировании.
        """
        variance = 0.0
        n = len(assets)
        for i in range(n):
            for j in range(n):
                variance += assets[i].weight * assets[j].weight * covariance_matrix[i][j]
        return math.sqrt(variance)

    # --- ТЕМА 10: МОДЕЛЬ ШАРПА ---

    @staticmethod
    def get_asset_return_sharpe(alpha: float, beta: float, market_return: float) -> float:
        """
        Расчет доходности акции по однофакторной модели Шарпа.
        Ссылка: лекция "Инвестиции", Тема 10, слайд 47.
        Формула: E(r_i) = α_i + β_i * E(r_m).

        Пример: Предприятие в г. Волжский. α=0.02, β=1.1, рынок (индекс Мосбиржи)=0.10.
        E(r) = 0.02 + 1.1 * 0.10 = 0.13 (13%).
        """
        return alpha + beta * market_return

    # --- ТЕМА 11: ПОРТФЕЛЬ ОБЛИГАЦИЙ ---

    @staticmethod
    def get_bond_price(nominal: float, coupon_rate: float, market_rate: float,
                       years_to_maturity: int, m_payments_per_year: int = 1,
                       method: BondPricingMethod = BondPricingMethod.AMERICAN) -> float:
        """
        Определение текущей цены облигации (PV).
        Ссылка: лекция "Инвестиции", Тема 11, слайды 50-51.
        НПА: ФСО II (Виды стоимости), п. 15 (Равновесная стоимость).

        Пример: Облигация администрации Волгоградской области.
        Номинал 1000 руб., купон 10%, рыночная ставка 8%, 3 года, выплата 2 раза в год.
        Метод: Американский.

        В отчёте: раздел «Доходный подход», оценка долговых инструментов.
        Используется при оценке бизнеса (СД.05) для определения стоимости
        облигационного портфеля предприятия.
        """
        i = market_rate
        n = years_to_maturity
        m = m_payments_per_year
        coupon = (nominal * coupon_rate) / m

        if method == BondPricingMethod.AMERICAN:
            im = i / m
        else:
            im = math.pow(1 + i, 1 / m) - 1

        total_periods = n * m
        pv_coupons = sum(coupon / math.pow(1 + im, t) for t in range(1, total_periods + 1))
        pv_nominal = nominal / math.pow(1 + im, total_periods)

        return pv_coupons + pv_nominal

    @staticmethod
    def get_macaulay_duration(nominal: float, coupon_rate: float, market_rate: float,
                              years_to_maturity: int) -> float:
        """
        Расчет дюрации Маколея (средневзвешенный срок погашения).
        Ссылка: лекция "Инвестиции", Тема 11, слайд 55.
        Формула: D = Σ [t * PV(CF_t)] / P.

        Пример: Оценка волатильности портфеля облигаций местного застройщика.
        """
        # Упрощенная модель для ежегодных выплат
        price = InvestmentAnalyst.get_bond_price(nominal, coupon_rate, market_rate, years_to_maturity)
        duration_weighted_sum = 0.0

        for t in range(1, years_to_maturity + 1):
            cf = nominal * coupon_rate
            if t == years_to_maturity:
                cf += nominal
            pv_cf = cf / math.pow(1 + market_rate, t)
            duration_weighted_sum += t * pv_cf

        return duration_weighted_sum / price

    # --- TODO: ИНТЕГРАЦИОННЫЕ ТОЧКИ ---
    # # TODO [ОП.06]: Расчет простых показателей (ROI, PP) и дисконтированных (NPV, PI, IRR)
    #   согласно Теме 3 [слайды 15-18] выполняется в calc_engine.py.
    # # TODO [finance]: План денежных потоков (операционная, инвестиционная, финансовая)
    #   согласно Теме 4 [слайд 21] импортируется из модуля финанализа.

# --- ПРАВОВОЙ КОМПЛАЕНС (ФЗ-39) ---


class InvestmentCompliance:
    """
    Проверка соответствия инвестиционной деятельности законодательству РФ.
    """

    @staticmethod
    def is_capital_investment(description: str) -> bool:
        """
        Определение, является ли вложение капитальным.
        НПА: ФЗ-39 "Об инвестиционной деятельности... в форме капвложений", ст. 1.
        Ссылка: лекция "Инвестиции", Тема 1, слайд 7.

        Пример: Покупка оборудования для завода в г. Камышин.
        """
        keywords = ["строительство", "реконструкция", "оборудование", "изыскания"]
        return any(word in description.lower() for word in keywords)

    @staticmethod
    def check_accumulation_positive(cum_cash_flows: List[float]) -> bool:
        """
        Критическое условие принятия финансового решения.
        Ссылка: лекция "Инвестиции", Тема 4, слайд 22.

        Условие: Положительное сальдо накопленных денег на любом этапе проекта.
        """
        return all(cf >= 0 for cf in cum_cash_flows)


if __name__ == "__main__":
    # Демонстрация работы модуля
    analyst = InvestmentAnalyst()

    print("--- 1. Оценка облигации (Волгоградский регион) ---")
    bond_p = analyst.get_bond_price(1000, 0.08, 0.10, 5, 1)
    print(f"Цена 5-летней облигации (купон 8%, рынок 10%): {bond_p:.2f} руб.")

    duration = analyst.get_macaulay_duration(1000, 0.08, 0.10, 5)
    print(f"Дюрация облигации: {duration:.2f} лет")

    print("\n--- 2. Доходность портфеля (Агро-сектор) ---")
    a1 = AssetStats(expected_return=0.20, standard_deviation=0.15, weight=0.5)
    a2 = AssetStats(expected_return=0.12, standard_deviation=0.08, weight=0.5)
    p_ret = analyst.get_portfolio_return([a1, a2])
    print(f"Ожидаемая доходность сбалансированного портфеля: {p_ret:.1%}")

    print("\n--- 3. Комплаенс (ФЗ-39) ---")
    is_cap = InvestmentCompliance.is_capital_investment("Реконструкция элеватора")
    print(f"Проект 'Реконструкция элеватора' — капитальное вложение: {is_cap}")

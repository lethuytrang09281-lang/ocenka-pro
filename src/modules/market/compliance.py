from dataclasses import dataclass
from enum import Enum
from typing import List


class DominanceStatus(Enum):
    IMMUNE = "Иммунитет (доминирование не признается)"
    POTENTIAL = "Потенциальный доминант (доля > 35%)"
    PRESUMED = "Прямой доминант (доля > 50%)"
    RETAIL_LIMIT = "Нарушение лимита расширения (доля > 25%)"


class MarketCompliance:
    """
    Модуль проверки антимонопольных ограничений и госрегулирования цен.
    Реализует юридическую логику ФЗ-135 и ФЗ-381.
    """

    @staticmethod
    def check_dominance_threshold(
        market_share: float,
        revenue: float,
        is_retail: bool = False
    ) -> DominanceStatus:
        """
        Проверка порогов доминирования и ограничений на расширение.

        НПА:
        - ФЗ-135 "О защите конкуренции", ст. 5 (пороги 35% и 50%).
        - ФЗ-381 "О торговой деятельности", ст. 14 (порог 25% для ритейла).
        - ФЗ-135, ст. 5, п. 2.1 (иммунитет при выручке < 800 млн руб).

        Пример (Волгоград): Торговая сеть "Покупочка" в Жирновском районе.
        Если доля > 25%, расширение (аренда новых площадей) запрещено.
        """
        # Иммунитет малого бизнеса (ст. 5 ФЗ-135)
        if revenue <= 800_000_000:
            return DominanceStatus.IMMUNE

        # Ограничение для ритейла (ст. 14 ФЗ-381)
        if is_retail and market_share > 25:
            return DominanceStatus.RETAIL_LIMIT

        if market_share > 50:
            return DominanceStatus.PRESUMED
        elif market_share > 35:
            return DominanceStatus.POTENTIAL

        return DominanceStatus.IMMUNE

    @staticmethod
    def is_social_good_risk(product_name: str) -> bool:
        """
        Проверка товара на принадлежность к социально значимым (риск заморозки цен).

        НПА: ФЗ-381, ст. 8, п. 5.
        """
        # TODO [npa]: Расширить до полного списка 24 товаров по ПП РФ.
        # Текущий список — минимальный для MVP.
        social_goods = ["хлеб", "молоко", "сахар", "масло подсолнечное", "яйца"]
        return any(good in product_name.lower() for good in social_goods)

    @staticmethod
    def check_digital_platform_dominance(revenue: float, share: float, has_network_effect: bool) -> bool:
        """
        Проверка доминирования цифровых платформ (Пятый антимонопольный пакет).

        НПА: ФЗ-135, ст. 10.1.
        Условия: выручка > 2 млрд, доля > 35%, наличие сетевого эффекта.
        """
        return revenue > 2_000_000_000 and share > 35 and has_network_effect

    @staticmethod
    def calculate_concentration_ratio(market_shares: list[float], top_n: int = 3) -> float:
        """
        Расчет индекса концентрации (CR_n).
        Сумма долей n крупнейших фирм на рынке.

        НПА: ФЗ-135, ст. 5, п. 3 (критерии коллективного доминирования).

        Пример: доли [45, 25, 15, 5, 5, 5] → CR3 = 85%
        """
        sorted_shares = sorted(market_shares, reverse=True)
        return round(sum(sorted_shares[:top_n]), 2)


# TODO [npa]: Реализовать автоматическое обновление списка социально значимых товаров через API.
# TODO [report]: Если статус RETAIL_LIMIT, добавить в раздел "Риски" текст о невозможности расширения.

if __name__ == "__main__":
    compliance = MarketCompliance()
    # Кейс: Магазин в Тракторозаводском районе, доля 27%, выручка 1.2 млрд.
    status = compliance.check_dominance_threshold(27.0, 1_200_000_000, is_retail=True)
    print(f"Статус комплаенса: {status.value}")  # RETAIL_LIMIT

from dataclasses import dataclass
from decimal import Decimal
from datetime import date, timedelta
from typing import List, Optional

from src.common.types import ValuationValueType, ValuationObjectType


@dataclass(frozen=True)
class Appraiser:
    """Субъект оценочной деятельности — Оценщик (ст. 4 ФЗ-135)"""
    full_name: str
    sro_membership_id: str
    qual_certificate_expiry: date
    insurance_amount: Decimal  # Не менее 300 000 руб.

    def is_eligible(self) -> bool:
        """Проверка права на осуществление деятельности (аттестат + срок)"""
        return self.qual_certificate_expiry >= date.today()


@dataclass
class ValuationObject:
    """Параметры объекта оценки (ст. 5 ФЗ-135)"""
    name: str
    object_type: ValuationObjectType
    is_state_owned: bool = False
    balance_value: Optional[Decimal] = None  # Балансовая стоимость


class LegalValuationEngine:
    """Логический движок исполнения норм законодательства в оценке"""

    @staticmethod
    def calculate_seizure_compensation(market_value: Decimal,
                                       real_damage: Decimal,
                                       lost_profit: Decimal) -> Decimal:
        """
        Расчет размера возмещения при изъятии участка для гос. нужд.

        НПА: ст. 56.8 ЗК РФ, ст. 32 ЖК РФ.
        Лекция: Тема 3, Слайд "Изъятие имущества".

        Формула: C_возм = C_рын + У (убытки) + УВ (упущенная выгода).

        Пример (Волгоградская область):
        - Рыночная стоимость участка: 2 000 000 руб.
        - Расходы на переезд: 50 000 руб.
        - Упущенная выгода (потеря урожая): 100 000 руб.
        - Итог: 2 150 000 руб.
        """
        return market_value + real_damage + lost_profit

    @staticmethod
    def get_bankruptcy_fee_limit(asset_value: Decimal) -> Decimal:
        """
        Расчет лимита оплаты услуг оценщика в процедурах банкротства.

        НПА: ст. 130 ФЗ № 127-ФЗ, ст. 20.7 ФЗ № 127-ФЗ.
        Лекция: Тема 1, Кейс №1.

        Логика: Для активов от 10 до 100 млн руб. лимит составляет
        395 000 руб. + 1% от суммы превышения над 10 млн руб.

        Пример:
        - Активы предприятия: 50 000 000 руб.
        - Лимит: 395 000 + (40 000 000 * 0.01) = 795 000 руб.
        """
        threshold = Decimal("10000000")
        base_fee = Decimal("395000")

        if asset_value <= threshold:
            # TODO [ОП.06]: Реализовать нижние пороги согласно ст. 20.7
            return base_fee

        excess = asset_value - threshold
        return base_fee + (excess * Decimal("0.01"))

    @staticmethod
    def get_report_validity_period(report_date: date) -> date:
        """
        Определение срока 'рекомендательной силы' отчета (6 месяцев).

        НПА: ст. 12 ФЗ № 135-ФЗ.
        Лекция: Тема 1, "Типичные ошибки".

        Пример: Отчет от 10.03.2026 действителен для сделки до 10.09.2026.
        """
        return report_date + timedelta(days=182)  # Приблизительно 6 месяцев


if __name__ == "__main__":
    # Тест 1: Проверка лимитов банкротства
    assets = Decimal("50000000")
    limit = LegalValuationEngine.get_bankruptcy_fee_limit(assets)
    print(f"Лимит оплаты при активах {assets:,} руб: {limit:,} руб.")

    # Тест 2: Проверка возмещения при изъятии
    comp = LegalValuationEngine.calculate_seizure_compensation(
        market_value=Decimal("2000000"),
        real_damage=Decimal("50000"),
        lost_profit=Decimal("100000")
    )
    print(f"Полное возмещение (ЗК РФ): {comp:,} руб.")

    # Тест 3: Срок действия отчета
    today = date(2026, 3, 10)
    valid_until = LegalValuationEngine.get_report_validity_period(today)
    print(f"Отчет от {today} действителен до {valid_until} (ст. 12 ФЗ-135)")

from decimal import Decimal
from typing import List

from src.modules.npa.legal_logic import Appraiser, ValuationObject


class ComplianceChecker:
    """Сервис правовой проверки (Compliance) процесса оценки"""

    @staticmethod
    def check_mandatory_valuation(obj: ValuationObject, deal_type: str) -> bool:
        """
        Проверка обязательности проведения оценки.

        НПА: ст. 8 ФЗ № 135-ФЗ.
        Лекция: Тема 3, "Случаи обязательной оценки".

        Обязательно при приватизации, национализации, залоге гос. имущества.
        """
        mandatory_deals = {"приватизация", "национализация", "взнос_в_ук", "спор_о_стоимости"}
        if obj.is_state_owned or deal_type in mandatory_deals:
            return True
        return False

    @staticmethod
    def validate_company_staff(appraisers: List[Appraiser]) -> bool:
        """
        Требование к штату оценочной компании.

        НПА: ст. 15.1 ФЗ № 135-ФЗ.
        Лекция: Тема 1, "Субъекты".

        Условие: Минимум два квалифицированных оценщика.
        """
        active_staff = [a for a in appraisers if a.is_eligible()]
        return len(active_staff) >= 2

    @staticmethod
    def check_independence(is_shareholder: bool, has_interest: bool) -> bool:
        """
        Проверка независимости оценщика.

        НПА: ст. 16 ФЗ № 135-ФЗ.
        Лекция: Тема 1, "Нарушение независимости".
        """
        if is_shareholder or has_interest:
            return False
        return True

    @staticmethod
    def calculate_sro_liability_gap(total_damage: Decimal,
                                    appraiser_ins: Decimal,
                                    company_ins: Decimal) -> Decimal:
        """
        Расчет покрытия убытков за счет компенсационного фонда СРО.

        НПА: ст. 24.6 ФЗ № 135-ФЗ.
        Лекция: Тема 4, Кейс №1.

        Лимит выплаты из компфонда СРО — не более 5 000 000 руб.
        при наличии положительного экспертного заключения.
        """
        covered_by_insurance = appraiser_ins + company_ins
        remaining_damage = total_damage - covered_by_insurance

        if remaining_damage <= 0:
            return Decimal("0")

        sro_limit = Decimal("5000000")
        return min(remaining_damage, sro_limit)

from decimal import Decimal


class FinanceCompliance:
    """
    Валидатор финансовой отчётности на соответствие НПА.
    Используется при проверке исходных данных перед оценкой.
    """

    @staticmethod
    def is_mandatory_audit_required(
        revenue: Decimal,
        assets: Decimal
    ) -> bool:
        """
        Проверка критериев обязательного аудита.

        НПА: ФЗ от 30.12.2008 №307-ФЗ 'Об аудиторской деятельности', ст. 5.
        Тема 17, слайд 'Обязательный аудит проводится в случаях'.

        Критерии: Выручка > 800 млн руб. ИЛИ Активы > 400 млн руб.

        Для оценщика: если аудит обязателен но не проведён,
        это снижает достоверность исходных данных (риск в отчёте).
        """
        REVENUE_LIMIT = Decimal("800000000")
        ASSETS_LIMIT = Decimal("400000000")
        return revenue > REVENUE_LIMIT or assets > ASSETS_LIMIT

    @staticmethod
    def validate_reserve_capital_ao(
        charter_capital: Decimal,
        reserve_capital: Decimal
    ) -> bool:
        """
        Проверка минимального размера резервного капитала для АО.

        НПА: ФЗ от 26.12.1995 №208-ФЗ 'Об акционерных обществах', ст. 35.
        Тема 5, слайд 'Размер резервного капитала'.

        Минимум: не менее 5% от уставного капитала.
        """
        return reserve_capital >= (charter_capital * Decimal("0.05"))

    @staticmethod
    def check_balance_equality(
        total_assets: Decimal,
        total_liabilities_and_equity: Decimal
    ) -> bool:
        """
        Проверка равенства Актива и Пассива баланса.

        НПА: ФСБУ 4/2023, п. 24.
        Тема 16, слайд 'Уравнение Баланса'.

        Если не сходится — ошибка в исходных данных, отчёт нельзя строить.
        """
        return total_assets == total_liabilities_and_equity

    # TODO [ОП.04]: Добавить расчёт чистых активов по Приказу Минфина №10н/03-6/пз
    # TODO [СД.05]: Нормализация прибыли (EBITDA) на основе проводок


if __name__ == "__main__":
    # Тест: обязательный аудит
    print(f"Аудит при выручке 900 млн: {FinanceCompliance.is_mandatory_audit_required(Decimal('900000000'), Decimal('100000000'))}")
    print(f"Аудит при выручке 500 млн: {FinanceCompliance.is_mandatory_audit_required(Decimal('500000000'), Decimal('100000000'))}")

    # Тест: резервный капитал
    print(f"Резерв 600к при УК 10 млн: {FinanceCompliance.validate_reserve_capital_ao(Decimal('10000000'), Decimal('600000'))}")

    # Тест: баланс
    print(f"Баланс сходится: {FinanceCompliance.check_balance_equality(Decimal('50000000'), Decimal('50000000'))}")

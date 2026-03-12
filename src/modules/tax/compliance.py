"""
Комплаенс-проверки налоговой логики (ОП.05).
"""
from decimal import Decimal


class TaxCompliance:
    """
    Проверки экономической обоснованности налоговой нагрузки.
    Используется для выявления триггеров оспаривания кадастровой стоимости.
    """

    @staticmethod
    def check_economic_justification(
        tax_amount: float,
        net_income: float,
    ) -> bool:
        """
        Проверка: налог не превышает доход от объекта.

        Если налог > 100% дохода — нарушен принцип экономической
        обоснованности. Это триггер для оспаривания кадастровой стоимости.

        В отчёте: раздел «Допущения и ограничения», если флаг False.
        """
        if net_income <= 0:
            return False
        return tax_amount < net_income

    @staticmethod
    def is_tax_agent_required(is_municipal_lease: bool) -> bool:
        """
        Определение статуса налогового агента по НДС.

        НПА: НК РФ, ст. 161, п. 3.
        Арендаторы муниципального имущества обязаны исчислять
        и уплачивать НДС за арендодателя.
        """
        return is_municipal_lease

    @staticmethod
    def calculate_cadastral_challenge_benefit(
        current_cadastral: Decimal,
        estimated_market: Decimal,
        annual_tax_rate: Decimal,
        years_remaining: int = 3,
    ) -> dict:
        """
        Расчёт экономической выгоды от оспаривания кадастровой стоимости.

        Экономия = (Кадастровая - Рыночная) × Ставка × Кол-во лет
        Стоимость процедуры: отчёт (~30-80к) + пошлина + юрист

        НПА: ФЗ от 03.07.2016 №237-ФЗ «О гос. кадастровой оценке».

        В отчёте: раздел «Выводы», рекомендация заказчику.
        """
        annual_savings = (current_cadastral - estimated_market) * annual_tax_rate
        total_savings = annual_savings * years_remaining
        estimated_cost = Decimal("80000")  # Ориентировочная стоимость процедуры

        return {
            "annual_savings": annual_savings,
            "total_savings_over_years": total_savings,
            "estimated_procedure_cost": estimated_cost,
            "net_benefit": total_savings - estimated_cost,
            "is_worthwhile": total_savings > estimated_cost,
        }

    # TODO [cadastral]: Полная логика оспаривания → cadastral/
    # TODO [npa]: Проверка включения объекта в кадастровый перечень КУГИ ВО


if __name__ == "__main__":
    tc = TaxCompliance()

    # Тест: экономическая обоснованность
    print(f"Налог 200к при доходе 150к: обоснован = {tc.check_economic_justification(200000, 150000)}")
    print(f"Налог 200к при доходе 500к: обоснован = {tc.check_economic_justification(200000, 500000)}")

    # Тест: выгода от оспаривания
    from decimal import Decimal
    benefit = tc.calculate_cadastral_challenge_benefit(
        Decimal("20000000"), Decimal("12000000"), Decimal("0.02"), 3
    )
    print(f"\nОспаривание кадастровой:")
    print(f"  Экономия/год: {benefit['annual_savings']}")
    print(f"  Итого за 3 года: {benefit['total_savings_over_years']}")
    print(f"  Выгодно: {benefit['is_worthwhile']}")

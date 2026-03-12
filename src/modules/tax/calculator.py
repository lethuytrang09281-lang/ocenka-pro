"""
Налоговый калькулятор (ОП.05).
Расчёт налогов для формирования OPEX в доходном подходе.
Дефолтный регион: Волгоградская область.
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Optional


class TaxSystem(Enum):
    """Система налогообложения предприятия"""
    OSNO = "Общая система налогообложения"
    USN_INCOME = "УСН Доходы (6%)"
    USN_PROFIT = "УСН Доходы минус Расходы (15%)"


class PropertyType(Enum):
    """Тип объекта для определения налоговой ставки"""
    ADMIN_CENTER = "Административно-деловой центр"
    RETAIL = "Торговый центр / Общепит"
    INDUSTRIAL = "Промышленный объект"
    LAND_RESIDENTIAL = "Земля: Жильё/СХ"
    LAND_COMMERCIAL = "Земля: Коммерция"


@dataclass
class TaxResult:
    """Результат расчёта налога"""
    amount: Decimal
    base: Decimal
    rate: Decimal
    description: str


class TaxCalculator:
    """
    Налоговый калькулятор для оценочной деятельности.
    Рассчитывает налоговую нагрузку объекта для доходного подхода.

    Дефолтные ставки — Волгоградская область.
    При масштабировании ставки берутся из таблицы regional_tax_rates в БД.
    """

    def __init__(
        self,
        system: TaxSystem = TaxSystem.OSNO,
        region: str = "Волгоградская область"
    ):
        self.system = system
        self.region = region

    def calculate_vat(self, gross_amount: Decimal) -> dict:
        """
        Выделение НДС из суммы (очистка денежного потока).

        НПА: НК РФ, ст. 164, п. 3. Ставка 20%.
        Тема: Косвенные налоги: НДС и Акцизы.

        Формула: НДС = Сумма_брутто × 20 / 120
                 Нетто = Сумма_брутто - НДС

        Пример (Волгоградская область):
        Входящий поток 120 000 руб. → НДС 20 000, Нетто 100 000.

        В отчёте: используется для очистки потоков в DCF.
        Связь: аналогичный расчёт в finance_engine.calculate_net_revenue().
        """
        vat_rate = Decimal("0.20")
        net_amount = gross_amount / (1 + vat_rate)
        vat_amount = gross_amount - net_amount

        return {
            "net": net_amount.quantize(Decimal("0.01"), ROUND_HALF_UP),
            "vat": vat_amount.quantize(Decimal("0.01"), ROUND_HALF_UP),
        }

    def calculate_property_tax(
        self,
        base_value: Decimal,
        prop_type: PropertyType,
        is_cadastral: bool = False,
    ) -> TaxResult:
        """
        Расчёт налога на имущество организаций.

        НПА: НК РФ, гл. 30, ст. 380.
        Региональный НПА: Закон Волгоградской области от 28.11.2003 №888-ОД.
        Тема: Прямые налоги: прибыль и имущество.

        Ставки (Волгоградская область):
        - ТЦ, офисы (по кадастру): 2.0%
        - Прочие (по среднегодовой): макс. 2.2%

        Пример: Офис в Волгограде, кадастр 10 млн → налог 200 000 руб.

        В отчёте: раздел «Доходный подход», строка OPEX «Налог на имущество».
        """
        # TODO [инфра]: Брать ставку из regional_tax_rates в БД по self.region
        if is_cadastral:
            rate = Decimal("0.02")
        else:
            rate = Decimal("0.022")

        tax_amount = base_value * rate
        return TaxResult(
            amount=tax_amount.quantize(Decimal("1"), ROUND_HALF_UP),
            base=base_value,
            rate=rate,
            description=f"Налог на имущество ({prop_type.value}), {self.region}",
        )

    def calculate_land_tax(
        self,
        cadastral_value: Decimal,
        prop_type: PropertyType,
    ) -> TaxResult:
        """
        Расчёт земельного налога (местный налог).

        НПА: НК РФ, гл. 31, ст. 394.
        Муниципальный НПА: Постановление Волгоградской ГД №24/464.
        Тема: Транспортный и земельный налоги.

        Ставки:
        - Жильё, СХ: 0.3%
        - Коммерция: 1.5%

        Пример: Участок под магазин, кадастр 5 млн → налог 75 000 руб.

        В отчёте: раздел «Доходный подход», строка OPEX «Земельный налог».
        """
        # TODO [инфра]: Брать ставку из regional_tax_rates в БД по self.region
        if prop_type == PropertyType.LAND_RESIDENTIAL:
            rate = Decimal("0.003")
        else:
            rate = Decimal("0.015")

        tax_amount = cadastral_value * rate
        return TaxResult(
            amount=tax_amount.quantize(Decimal("1"), ROUND_HALF_UP),
            base=cadastral_value,
            rate=rate,
            description=f"Земельный налог, {self.region}",
        )

    def calculate_income_tax(
        self,
        revenue_net: Decimal,
        expenses_net: Decimal,
    ) -> TaxResult:
        """
        Расчёт налога на прибыль организаций.

        НПА: НК РФ, гл. 25, ст. 284.
        Тема: Прямые налоги: прибыль и имущество.

        Ставка: 20% (3% федеральный + 17% региональный, с 2025 г.)

        Пример: Прибыль 1 000 000 руб. → налог 200 000 руб.

        В отчёте: раздел «Доходный подход», расчёт чистой прибыли.
        """
        profit = revenue_net - expenses_net
        rate = Decimal("0.20")

        if profit <= 0:
            return TaxResult(
                Decimal("0"), profit, rate,
                "Налог на прибыль (убыток — налог не начисляется)"
            )

        tax_amount = profit * rate
        return TaxResult(
            amount=tax_amount.quantize(Decimal("1"), ROUND_HALF_UP),
            base=profit,
            rate=rate,
            description="Налог на прибыль (3% фед. + 17% рег.)",
        )

    # TODO [СД.03]: transport_tax_luxury_coeffs → equipment/ (налог на роскошь для ТС)
    # TODO [СД.05]: mineral_extraction_tax → business/ (НДПИ для добывающих)
    # TODO [quick]: special_regime_optimization → quick/ (выбор УСН 6% vs 15%)


if __name__ == "__main__":
    calc = TaxCalculator()

    print("--- ТЕСТИРОВАНИЕ ОП.05 ---\n")

    # 1. НДС
    vat = calc.calculate_vat(Decimal("1200000"))
    print(f"1. Выручка нетто: {vat['net']} (НДС: {vat['vat']})")

    # 2. Налог на имущество
    prop = calc.calculate_property_tax(
        Decimal("50000000"), PropertyType.RETAIL, is_cadastral=True
    )
    print(f"2. {prop.description}: {prop.amount} руб.")

    # 3. Земельный налог
    land = calc.calculate_land_tax(
        Decimal("10000000"), PropertyType.LAND_COMMERCIAL
    )
    print(f"3. {land.description}: {land.amount} руб.")

    # 4. Налог на прибыль
    income = calc.calculate_income_tax(Decimal("1000000"), Decimal("500000"))
    print(f"4. {income.description}: {income.amount} руб.")

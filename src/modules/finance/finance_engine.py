from dataclasses import dataclass
from typing import List, Optional
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class InventoryItem:
    """Партия материалов на складе"""
    quantity: Decimal
    price: Decimal


@dataclass
class FinancialResultData:
    """Исходные данные для расчёта прибыли предприятия"""
    revenue_brutto: Decimal      # Выручка с НДС
    cogs: Decimal                # Себестоимость
    commercial_expenses: Decimal # Коммерческие расходы
    admin_expenses: Decimal      # Управленческие расходы
    other_income: Decimal        # Прочие доходы
    other_expenses: Decimal      # Прочие расходы
    vat_rate: Decimal = Decimal("0.20")
    income_tax_rate: Decimal = Decimal("0.20")


class FinanceEngine:
    """
    Движок финансовых расчетов для модуля оценки.
    Реализует алгоритмы бухгалтерского учёта, необходимые
    для подготовки данных к оценке бизнеса и имущества.
    """

    @staticmethod
    def calculate_net_revenue(
        revenue_brutto: Decimal,
        vat_rate: Decimal = Decimal("0.20")
    ) -> Decimal:
        """
        Расчет чистой выручки (нетто) за вычетом НДС.

        НПА: ФСБУ 4/2023, п. 26.
        Тема 12, слайд 'Учет продажи продукции'.

        Формула: Выручка_нетто = Выручка_брутто - НДС
        где НДС = Выручка_брутто * Ставка / (1 + Ставка)

        Пример (Волгоградская область):
        Продажа металлоконструкций на 120 000 руб (в т.ч. НДС 20%).
        НДС = 120 000 * 0.20 / 1.20 = 20 000 руб.
        Выручка нетто = 100 000 руб.

        В отчёте: используется в доходном подходе как база для прогноза выручки.
        """
        vat_amount = (
            revenue_brutto * vat_rate / (Decimal("1.0") + vat_rate)
        ).quantize(Decimal("0.01"), ROUND_HALF_UP)
        return revenue_brutto - vat_amount

    @staticmethod
    def calculate_profits(data: FinancialResultData) -> dict:
        """
        Расчет многоуровневой прибыли предприятия.

        НПА: ФСБУ 4/2023, п. 27; ПБУ 9/99, ПБУ 10/99.
        Тема 15, слайд 'Учет прибыли (убытка) организации'.

        Формулы:
        - Валовая прибыль (стр. 2100) = Выручка_нетто - Себестоимость
        - Прибыль от продаж (стр. 2200) = Валовая - Комм.расх - Упр.расх
        - Прибыль до налогообложения (стр. 2300) = От продаж + Проч.дох - Проч.расх
        - Чистая прибыль (стр. 2400) = До налога - Налог на прибыль

        Пример (Волгоград): Завод в г. Волжский.
        Выручка нетто 100 млн, С/С 70 млн, Комм 5 млн, Упр 10 млн.
        Валовая = 30 млн. Прибыль от продаж = 15 млн.

        В отчёте: раздел 'Финансовый анализ', таблица показателей прибыли.
        """
        net_revenue = FinanceEngine.calculate_net_revenue(
            data.revenue_brutto, data.vat_rate
        )

        gross_profit = net_revenue - data.cogs
        sales_profit = gross_profit - data.commercial_expenses - data.admin_expenses
        ebt = sales_profit + data.other_income - data.other_expenses

        income_tax = Decimal("0")
        if ebt > 0:
            income_tax = (ebt * data.income_tax_rate).quantize(
                Decimal("0.01"), ROUND_HALF_UP
            )

        net_profit = ebt - income_tax

        return {
            "net_revenue": net_revenue,
            "gross_profit": gross_profit,
            "sales_profit": sales_profit,
            "ebt": ebt,
            "income_tax": income_tax,
            "net_profit": net_profit,
        }

    @staticmethod
    def calculate_inventory_average(
        items: List[InventoryItem],
        quantity_to_issue: Decimal
    ) -> Decimal:
        """
        Оценка материалов по средней себестоимости.

        НПА: ФСБУ 5/2019, раздел 'Оценка запасов при выбытии'.
        Тема 9, слайд 'Метод средней цены'.

        Формула: Средняя цена = Σ(Кол-во_i × Цена_i) / Σ(Кол-во_i)
        Стоимость отпуска = Кол-во_отпуска × Средняя цена

        Пример (Волгоградская область):
        Склад в Дзержинском районе.
        Партия 1: 20т по 10 000. Партия 2: 30т по 10 500.
        Средняя = (200к + 315к) / 50 = 10 300 руб/т.
        Отпуск 15т = 154 500 руб.

        В отчёте: используется при корректировке запасов в затратном подходе.
        """
        total_qty = sum(item.quantity for item in items)
        total_cost = sum(item.quantity * item.price for item in items)
        if total_qty == 0:
            return Decimal("0")
        avg_price = total_cost / total_qty
        return (quantity_to_issue * avg_price).quantize(
            Decimal("0.01"), ROUND_HALF_UP
        )

    @staticmethod
    def calculate_linear_amortization(
        cost: Decimal,
        remaining_months: int,
        liquidation_value: Decimal = Decimal("0")
    ) -> Decimal:
        """
        Расчет ежемесячной амортизации линейным способом.

        НПА: ФСБУ 6/2020, п. 35.
        Тема 11, слайд 'Сумма амортизации за период'.

        Формула: Амортизация_мес = (Первоначальная - Ликвидационная) / Срок_мес

        Пример (Волгоградская область):
        Сервер в офисе на ул. Рабоче-Крестьянской.
        Цена 1.2 млн, Ликвид. ст-ть 200к, Срок 24 мес.
        Амортизация = (1 200 000 - 200 000) / 24 = 41 666.67 руб/мес.

        В отчёте: используется при расчёте накопленного износа в затратном подходе
        и при корректировке балансовой стоимости ОС до рыночной.
        """
        if remaining_months <= 0:
            return Decimal("0")
        return (
            (cost - liquidation_value) / Decimal(str(remaining_months))
        ).quantize(Decimal("0.01"), ROUND_HALF_UP)

    # TODO [ОП.04]: Добавить расчёт EBITDA = Прибыль от продаж + Амортизация
    # TODO [ОП.04]: Коэффициенты ликвидности, рентабельности, оборачиваемости
    # TODO [СД.05]: Метод чистых активов (корректировка балансовой → рыночная)


if __name__ == "__main__":
    # Тест 1: Расчёт прибыли
    data = FinancialResultData(
        revenue_brutto=Decimal("1200000"),
        cogs=Decimal("700000"),
        commercial_expenses=Decimal("50000"),
        admin_expenses=Decimal("100000"),
        other_income=Decimal("50000"),
        other_expenses=Decimal("20000"),
    )
    profits = FinanceEngine.calculate_profits(data)
    print(f"--- РАСЧЁТ ПРИБЫЛИ ---")
    for key, val in profits.items():
        print(f"  {key}: {val}")

    # Тест 2: Амортизация
    amort = FinanceEngine.calculate_linear_amortization(
        Decimal("1000000"), 24, Decimal("100000")
    )
    print(f"\nАмортизация: {amort} руб/мес")

    # Тест 3: Средняя себестоимость запасов
    items = [
        InventoryItem(Decimal("20"), Decimal("10000")),
        InventoryItem(Decimal("30"), Decimal("10500")),
    ]
    cost = FinanceEngine.calculate_inventory_average(items, Decimal("15"))
    print(f"Стоимость отпуска 15 ед.: {cost} руб")

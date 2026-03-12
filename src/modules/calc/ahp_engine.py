"""
Метод Анализа Иерархий (МАИ/AHP) для согласования результатов оценки (ОП.06).
Реализует алгоритм Томаса Саати для научно обоснованного взвешивания подходов.
"""
import math
from typing import List, Dict
from dataclasses import dataclass

from src.common.types import EvaluationApproach


@dataclass
class AHPReconciliationResult:
    """Результат согласования результатов оценки методом МАИ"""
    weights: Dict[EvaluationApproach, float]
    consistency_ratio: float
    is_consistent: bool
    final_value: float


class AHPEngine:
    """
    Метод Анализа Иерархий Томаса Саати для согласования результатов оценки.

    НПА: ФСО V «Подходы и методы оценки» (Приказ МЭР №200), п. 24 —
    согласование результатов применения подходов к оценке.
    Лекция: Математические методы в оценочной деятельности, Тема 1.

    В отчёте: раздел «Согласование результатов», таблица весов подходов.
    """

    # Случайные индексы (СИ) для матриц разного порядка (n=1..10)
    # Источник: Саати Т.Л. «Принятие решений. Метод анализа иерархий»
    RANDOM_INDEX = {
        1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
        6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
    }

    @staticmethod
    def calculate_priority_vector(matrix: List[List[float]]) -> List[float]:
        """
        Вычисление вектора локальных приоритетов через среднее геометрическое.

        Лекция: Слайд 36-37.

        Алгоритм:
        1. Произведение элементов каждой строки
        2. Корень n-й степени из произведения
        3. Нормализация (деление на сумму)

        Пример (матрица 3x3):
        [[1, 3, 5], [1/3, 1, 3], [1/5, 1/3, 1]]
        Произведения: 15, 1, 0.067
        Корни: 2.466, 1.0, 0.405
        Нормализация: [0.637, 0.258, 0.105]
        """
        n = len(matrix)
        geometric_means = []

        for row in matrix:
            row_product = math.prod(row)
            geometric_means.append(row_product ** (1 / n))

        total_sum = sum(geometric_means)
        return [gm / total_sum for gm in geometric_means]

    @classmethod
    def check_consistency(
        cls,
        matrix: List[List[float]],
        priorities: List[float],
    ) -> float:
        """
        Проверка согласованности суждений (Отношение Согласованности, ОС).

        Лекция: Слайд 40-42.

        Формулы:
        - Lambda_max = Σ(s_j × w_j), где s_j — сумма столбца, w_j — вес
        - ИС = (Lambda_max - n) / (n - 1)
        - ОС = ИС / СИ

        Критерий: ОС ≤ 0.10 (10%) — суждения согласованы.
        Если ОС > 0.10 — матрицу нужно пересмотреть.

        Пример (матрица 4x4):
        Lambda_max = 4.07, ИС = 0.023, ОС = 0.025 (приемлемо).
        """
        n = len(matrix)
        if n <= 2:
            return 0.0

        column_sums = [
            sum(matrix[row][col] for row in range(n))
            for col in range(n)
        ]

        lambda_max = sum(column_sums[i] * priorities[i] for i in range(n))
        consistency_index = (lambda_max - n) / (n - 1)
        random_index = cls.RANDOM_INDEX.get(n, 1.49)

        if random_index == 0:
            return 0.0
        return consistency_index / random_index

    def reconcile(
        self,
        criteria_matrix: List[List[float]],
        alternatives_matrices: Dict[str, List[List[float]]],
        approach_values: Dict[EvaluationApproach, float],
    ) -> AHPReconciliationResult:
        """
        Финальный синтез: согласование результатов трёх подходов к оценке.

        НПА: ФСО V, п. 24.
        Лекция: Слайд 43 — синтез альтернатив.

        Параметры:
        - criteria_matrix: матрица попарного сравнения критериев (4x4)
          Критерии: А (намерения), Б (данные), В (конъюнктура), Г (специфика)
        - alternatives_matrices: матрицы сравнения подходов по каждому критерию (3x3)
        - approach_values: стоимость по каждому подходу

        Результат:
        - weights: научно обоснованные веса подходов
        - final_value: взвешенная итоговая стоимость

        Пример (Волгоградская область):
        Торговый павильон: Затратный 16.5М, Сравнительный 18.3М, Доходный 17.5М.
        Веса после МАИ: Затратный 0.15, Сравнительный 0.45, Доходный 0.40.
        Итог: 17 650 000 руб.

        В отчёте: раздел «Согласование результатов».
        """
        # 1. Веса критериев (второй уровень иерархии)
        criteria_weights = self.calculate_priority_vector(criteria_matrix)
        cr_criteria = self.check_consistency(criteria_matrix, criteria_weights)

        # 2. Веса подходов по каждому критерию (третий уровень)
        approaches = [
            EvaluationApproach.COST,
            EvaluationApproach.COMPARATIVE,
            EvaluationApproach.INCOME,
        ]
        alt_weights_by_criteria = []

        for key in ["A", "B", "V", "G"]:
            weights = self.calculate_priority_vector(alternatives_matrices[key])
            alt_weights_by_criteria.append(weights)

        # 3. Синтез: глобальные веса подходов
        final_weights = {}
        for i, approach in enumerate(approaches):
            weight = sum(
                criteria_weights[j] * alt_weights_by_criteria[j][i]
                for j in range(len(criteria_weights))
            )
            final_weights[approach] = round(weight, 4)

        # 4. Итоговая стоимость = Σ(Стоимость_подхода × Вес_подхода)
        total_value = sum(
            approach_values[app] * final_weights[app] for app in approaches
        )

        return AHPReconciliationResult(
            weights=final_weights,
            consistency_ratio=round(cr_criteria, 4),
            is_consistent=cr_criteria <= 0.1,
            final_value=round(total_value, 2),
        )

    # TODO [ОП.07]: Добавить NPV, IRR, DCF в отдельный calc_engine.py
    # TODO [report]: Передать weights и final_value в генератор отчёта .docx
    # TODO [ОП.06]: Добавить корреляционно-регрессионный анализ в statistics.py


if __name__ == "__main__":
    engine = AHPEngine()

    print("--- ТЕСТИРОВАНИЕ ОП.06 (МАИ) ---\n")

    # Данные из лекции: Торговый павильон ЗАО «МИФ»
    market_values = {
        EvaluationApproach.COST: 16_471_544,
        EvaluationApproach.COMPARATIVE: 18_316_017,
        EvaluationApproach.INCOME: 17_500_000,
    }

    # Матрица критериев (А, Б, В, Г)
    criteria = [
        [1.00, 3.00, 2.00, 2.00],
        [0.33, 1.00, 0.50, 0.50],
        [0.50, 2.00, 1.00, 1.00],
        [0.50, 2.00, 1.00, 1.00],
    ]

    # Матрицы альтернатив по критериям
    alternatives = {
        "A": [[1.0, 0.2, 0.2], [5.0, 1.0, 1.0], [5.0, 1.0, 1.0]],
        "B": [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]],
        "V": [[1.00, 0.33, 0.50], [3.00, 1.00, 2.00], [2.00, 0.50, 1.00]],
        "G": [[1.00, 0.33, 0.33], [3.00, 1.00, 1.00], [3.00, 1.00, 1.00]],
    }

    result = engine.reconcile(criteria, alternatives, market_values)

    print(f"Веса подходов:")
    for approach, weight in result.weights.items():
        print(f"  {approach.value}: {weight}")
    print(f"ОС (отношение согласованности): {result.consistency_ratio}")
    print(f"Суждения согласованы: {'Да' if result.is_consistent else 'Нет'}")
    print(f"Итоговая стоимость: {result.final_value:,.2f} руб.")

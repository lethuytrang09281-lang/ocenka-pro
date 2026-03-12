"""
Общие типы для всех модулей Оценка Pro.
Enum'ы и dataclass'ы, используемые несколькими модулями.
"""
from enum import Enum


class ValuationValueType(Enum):
    """Виды стоимости согласно ФСО II (Приказ МЭР №200 от 14.04.2022)"""
    MARKET = "Рыночная"
    EQUILIBRIUM = "Равновесная"
    INVESTMENT = "Инвестиционная"
    LIQUIDATION = "Ликвидационная"
    CADASTRAL = "Кадастровая"


class ValuationObjectType(Enum):
    """Категории объектов оценки согласно ст. 5 ФЗ-135 и ст. 130 ГК РФ"""
    THING = "Вещь"
    REAL_ESTATE = "Недвижимость"
    BUSINESS_COMPLEX = "Предприятие"
    PROPERTY_RIGHT = "Вещное право"
    RIGHT_OF_CLAIM = "Право требования"
    INTELLECTUAL_PROPERTY = "Интеллектуальная собственность"
    WORK_SERVICE_INFO = "Работы, услуги, информация"


class CyclePhase(Enum):
    """Фазы экономического цикла"""
    RECESSION = "Спад"
    DEPRESSION = "Депрессия"
    REVIVAL = "Оживление"
    BOOM = "Подъем"


class InflationCategory(Enum):
    """Категории инфляции по темпу"""
    NORMAL = "Нормальная (до 5%)"
    MODERATE = "Умеренная (5-10%)"
    GALLOPING = "Галопирующая (20-200%)"
    HYPER = "Гиперинфляция"


class EvaluationApproach(str, Enum):
    """Подходы к оценке согласно ФСО V (Приказ МЭР №200 от 14.04.2022)"""
    COST = "Затратный подход"
    COMPARATIVE = "Сравнительный подход"
    INCOME = "Доходный подход"

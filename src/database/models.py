"""
Модели данных для системы "Оценка Pro".
Реализует схему БД согласно ФСО и 135-ФЗ.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    String, Text, Integer, Numeric, Boolean, DateTime, Date,
    ForeignKey, Enum as SQLEnum, Index, UniqueConstraint
)
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship, DeclarativeBase
)


class Base(DeclarativeBase):
    pass


# === ENUMS ===

class ReportStatus(str, Enum):
    """Статусы отчёта об оценке"""
    DRAFT = "draft"           # Черновик
    CALCULATION = "calc"      # Расчёт
    VERIFICATION = "verify"   # Проверка
    FINAL = "final"           # Финал


class ObjectType(str, Enum):
    """Типы объектов оценки"""
    REAL_ESTATE = "real_estate"       # Недвижимость
    MOVABLE_PROPERTY = "movable"      # Движимое имущество
    BUSINESS = "business"             # Бизнес (предприятие)
    INTANGIBLE = "intangible"         # НМА
    RECEIVABLES = "receivables"       # Дебиторская задолженность
    SECURITIES = "securities"         # Ценные бумаги


class ValuationType(str, Enum):
    """Виды стоимости по ФСО II"""
    MARKET = "market"                 # Рыночная
    CADASTRAL = "cadastral"           # Кадастровая
    INVESTMENT = "investment"         # Инвестиционная
    LIQUIDATION = "liquidation"       # Ликвидационная
    FAIR_VALUE = "fair_value"         # Справедливая


class NpaLevel(str, Enum):
    """Уровень нормативного правового акта"""
    FEDERAL_LAW = "federal_law"       # Федеральный закон
    GOVERNMENT_DECREE = "gov_decree"  # Постановление Правительства
    MINISTRY_ORDER = "ministry_order" # Приказ министерства
    LOCAL = "local"                   # Локальный акт


# === МОДЕЛИ ===

class User(Base):
    """
    Пользователь системы (оценщик или сотрудник).
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50))
    
    # Данные оценщика
    sro_membership_id: Mapped[str | None] = mapped_column(String(100))  # Номер в реестре СРО
    qual_certificate_number: Mapped[str | None] = mapped_column(String(100))  # Аттестат
    qual_certificate_expiry: Mapped[date | None] = mapped_column(Date)
    insurance_amount: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))  # Страховка
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Связи
    reports = relationship("AppraisalReport", back_populates="appraiser")
    companies = relationship("Company", back_populates="owner")

    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
    )


class Company(Base):
    """
    Оценочная компания (юридическое лицо).
    """
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    inn: Mapped[str] = mapped_column(String(12), unique=True, nullable=False, index=True)
    kpp: Mapped[str | None] = mapped_column(String(9))
    ogrn: Mapped[str | None] = mapped_column(String(15))
    
    legal_address: Mapped[str | None] = mapped_column(Text)
    actual_address: Mapped[str | None] = mapped_column(Text)
    
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Данные для СРО
    sro_name: Mapped[str | None] = mapped_column(String(255))
    sro_inn: Mapped[str | None] = mapped_column(String(12))
    compensation_fund: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Связи
    owner = relationship("User", back_populates="companies")
    reports = relationship("AppraisalReport", back_populates="company")


class AppraisalOrder(Base):
    """
    Задание на оценку согласно ФСО IV (Приказ МЭР №200).
    Содержит обязательные реквизиты задания на оценку.
    """
    __tablename__ = "appraisal_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(String(50), nullable=False)  # Номер договора/задания
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Стороны договора
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)  # Заказчик
    customer_inn: Mapped[str | None] = mapped_column(String(12))
    customer_phone: Mapped[str | None] = mapped_column(String(50))
    customer_email: Mapped[str | None] = mapped_column(String(255))
    
    # Цель оценки (обязательно по ФСО IV)
    valuation_purpose: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Вид стоимости (обязательно по ФСО IV)
    valuation_type: Mapped[ValuationType] = mapped_column(
        SQLEnum(ValuationType), nullable=False
    )
    
    # Дата оценки (обязательно по ФСО IV)
    valuation_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Срок действия отчёта (мес.)
    report_validity_months: Mapped[int] = mapped_column(Integer, default=6)
    
    # Ограничения использования (обязательно по ФСО IV)
    usage_restrictions: Mapped[str | None] = mapped_column(Text)
    
    # Допущения и предположения
    assumptions: Mapped[str | None] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Связи
    reports = relationship("AppraisalReport", back_populates="order", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_orders_date", "order_date"),
        Index("ix_orders_valuation_date", "valuation_date"),
    )


class AppraisalObject(Base):
    """
    Объект оценки.
    Может быть связан с отчётом или существовать самостоятельно (для черновиков).
    """
    __tablename__ = "appraisal_objects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    report_id: Mapped[int | None] = mapped_column(
        ForeignKey("appraisal_reports.id", ondelete="CASCADE")
    )
    
    # Тип объекта
    object_type: Mapped[ObjectType] = mapped_column(
        SQLEnum(ObjectType), nullable=False, index=True
    )
    
    # Наименование и описание
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    
    # Адрес/местоположение
    address: Mapped[str | None] = mapped_column(Text)
    cadastral_number: Mapped[str | None] = mapped_column(String(50), index=True)
    conditional_number: Mapped[str | None] = mapped_column(String(100))
    
    # Характеристики
    area: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))  # Площадь
    land_area: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))  # Площадь земли
    building_area: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))  # Площадь застройки
    
    # Правообладатель
    owner_name: Mapped[str | None] = mapped_column(String(255))
    ownership_type: Mapped[str | None] = mapped_column(String(100))  # Вид права
    
    # Балансовая стоимость
    balance_value: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    residual_value: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))  # Остаточная
    
    # Ограничения/обременения
    restrictions: Mapped[str | None] = mapped_column(Text)
    encumbrances: Mapped[str | None] = mapped_column(Text)
    
    # Флаг государственной собственности
    is_state_owned: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Связи
    report = relationship("AppraisalReport", back_populates="objects")

    __table_args__ = (
        Index("ix_objects_type_report", "object_type", "report_id"),
    )


class AppraisalReport(Base):
    """
    Отчёт об оценке.
    Содержит результаты оценки и проходит жизненный цикл от черновика до финала.
    """
    __tablename__ = "appraisal_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    report_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    
    # Связи
    order_id: Mapped[int] = mapped_column(
        ForeignKey("appraisal_orders.id"), nullable=False
    )
    appraiser_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("companies.id")
    )
    
    # Статус отчёта
    status: Mapped[ReportStatus] = mapped_column(
        SQLEnum(ReportStatus), default=ReportStatus.DRAFT, index=True
    )
    
    # Даты
    report_date: Mapped[date] = mapped_column(Date)  # Дата отчёта
    valid_until: Mapped[date | None] = mapped_column(Date)  # Действителен до
    
    # Итоговая стоимость
    final_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    final_value_type: Mapped[ValuationType | None] = mapped_column(SQLEnum(ValuationType))
    
    # Путь к файлу отчёта
    file_path: Mapped[str | None] = mapped_column(String(500))
    
    # Примечания
    notes: Mapped[str | None] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Связи
    order = relationship("AppraisalOrder", back_populates="reports")
    appraiser = relationship("User", back_populates="reports")
    company = relationship("Company", back_populates="reports")
    objects = relationship("AppraisalObject", back_populates="report", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_reports_status_date", "status", "report_date"),
    )


class NpaRegistry(Base):
    """
    Реестр нормативных правовых актов.
    Используется для ссылок в отчётах и проверки актуальности НПА.
    """
    __tablename__ = "npa_registry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Наименование акта
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Тип акта
    npa_level: Mapped[NpaLevel] = mapped_column(SQLEnum(NpaLevel), nullable=False)
    
    # Реквизиты
    document_number: Mapped[str] = mapped_column(String(100), nullable=False)  # Номер
    document_date: Mapped[date] = mapped_column(Date, nullable=False)  # Дата
    
    # Орган, принявший акт
    issuing_author: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Дата начала действия
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)  # Дата окончания (если есть)
    
    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # Ссылка на документ
    document_url: Mapped[str | None] = mapped_column(String(500))
    
    # Описание/комментарий
    description: Mapped[str | None] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        UniqueConstraint("document_number", "document_date", name="uq_npa_doc"),
        Index("ix_npa_level_active", "npa_level", "is_active"),
    )


class RegionalTaxRate(Base):
    """
    Региональные налоговые ставки.
    Используется для расчёта налога на имущество, земельного налога.
    """
    __tablename__ = "regional_tax_rates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Регион
    region_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # Код региона
    region_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Тип налога
    tax_type: Mapped[str] = mapped_column(String(50), nullable=False)  # land, property, transport
    
    # Ставка (в %)
    rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    
    # Категория объекта (если применимо)
    object_category: Mapped[str | None] = mapped_column(String(100))
    
    # Год применения ставки
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Основание (НПА региона)
    legal_basis: Mapped[str | None] = mapped_column(String(500))
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        UniqueConstraint("region_code", "tax_type", "year", "object_category", name="uq_tax_rate"),
    )


class MarketData(Base):
    """
    Рыночные данные для сравнительного подхода.
    Хранит информацию о сделках и предложениях на рынке.
    """
    __tablename__ = "market_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Тип данных
    data_type: Mapped[str] = mapped_column(String(50), nullable=False)  # sale, offer, rent
    object_type: Mapped[ObjectType] = mapped_column(SQLEnum(ObjectType), nullable=False, index=True)
    
    # Местоположение
    region_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    city: Mapped[str | None] = mapped_column(String(100))
    district: Mapped[str | None] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(Text)
    
    # Характеристики объекта
    area: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    land_area: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    building_area: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    
    # Цена
    price: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    price_per_unit: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))  # Цена за ед. площади
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    
    # Дата
    transaction_date: Mapped[date | None] = mapped_column(Date)  # Для сделок
    offer_date: Mapped[date | None] = mapped_column(Date)  # Для предложений
    
    # Источник данных
    source: Mapped[str] = mapped_column(String(255), nullable=False)  # Сайт, база данных
    source_url: Mapped[str | None] = mapped_column(String(500))
    
    # Дополнительные параметры (JSON)
    extra_params: Mapped[str | None] = mapped_column(Text)  # JSON с доп. характеристиками
    
    # Статус проверки
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        Index("ix_market_type_region", "data_type", "object_type", "region_code"),
        Index("ix_market_date", "transaction_date", "offer_date"),
    )

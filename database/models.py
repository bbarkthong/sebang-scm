"""
SQLAlchemy 모델 정의
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """사용자 테이블"""
    __tablename__ = "users"

    user_id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 발주사, 주문담당자, 제조담당자
    company_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)


class ItemMaster(Base):
    """품목 마스터 테이블"""
    __tablename__ = "item_master"

    item_code = Column(String, primary_key=True)
    item_name = Column(String, unique=True, nullable=False)
    lead_time_days = Column(Integer, nullable=False)  # 납기일수 (주문일자 기준)
    unit_price = Column(Numeric(10, 2), nullable=False)  # 기본 단가
    is_active = Column(String, default="Y")  # 사용여부 (Y/N)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, nullable=True)


class OrderMaster(Base):
    """주문 마스터 테이블"""
    __tablename__ = "order_master"

    order_no = Column(String, primary_key=True)
    order_date = Column(Date, nullable=False)
    order_type = Column(String, nullable=False)  # 긴급, 일반
    customer_company = Column(String, nullable=False)
    status = Column(String, default="대기")  # 대기, 승인, 생산중, 입고완료, 출하완료
    priority = Column(Integer, default=5)  # 1-9
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # 관계
    details = relationship("OrderDetail", back_populates="master", cascade="all, delete-orphan")


class OrderDetail(Base):
    """주문 상세 테이블"""
    __tablename__ = "order_detail"

    order_no = Column(String, ForeignKey("order_master.order_no"), primary_key=True)
    order_seq = Column(Integer, primary_key=True)
    item_code = Column(String, nullable=False)
    item_name = Column(String, nullable=False)
    order_qty = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    shipping_qty = Column(Integer, default=0)
    shipping_amount = Column(Numeric(10, 2), default=0)
    planned_shipping_date = Column(Date, nullable=True)
    actual_shipping_date = Column(Date, nullable=True)

    # 관계
    master = relationship("OrderMaster", back_populates="details")


class Warehouse(Base):
    """창고 입고 테이블"""
    __tablename__ = "warehouse"

    warehouse_id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String, ForeignKey("order_master.order_no"), nullable=False)
    order_seq = Column(Integer, nullable=False)
    item_code = Column(String, nullable=False)
    item_name = Column(String, nullable=False)
    received_qty = Column(Integer, nullable=False)
    received_date = Column(Date, nullable=False)
    received_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)


class ShippingPlan(Base):
    """출하 계획 테이블"""
    __tablename__ = "shipping_plan"

    plan_id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String, ForeignKey("order_master.order_no"), nullable=False)
    order_seq = Column(Integer, nullable=False)
    planned_shipping_date = Column(Date, nullable=False)
    planned_qty = Column(Integer, nullable=False)
    status = Column(String, default="계획")  # 계획, 지시, 출하완료
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)


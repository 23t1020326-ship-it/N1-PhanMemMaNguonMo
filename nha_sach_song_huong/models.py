from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Category(db.Model):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))

    books: Mapped[list["Book"]] = relationship("Book", back_populates="category")

class Book(db.Model):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(150), nullable=False)
    publisher: Mapped[str | None] = mapped_column(String(150))
    publish_year: Mapped[int | None] = mapped_column(Integer)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    cover_image: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    category: Mapped["Category"] = relationship("Category", back_populates="books")
    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="book")

class Order(db.Model):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(150), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(15), nullable=False)
    customer_email: Mapped[str | None] = mapped_column(String(150))
    shipping_address: Mapped[str] = mapped_column(String(255), nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False) # COD / BANK
    
    subtotal: Mapped[int] = mapped_column(Integer, nullable=False)
    shipping_fee: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Trạng thái: Chờ xác nhận | Đang giao | Hoàn tất | Đã huỷ
    status: Mapped[str] = mapped_column(String(50), default="Chờ xác nhận", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    histories: Mapped[list["OrderHistory"]] = relationship("OrderHistory", back_populates="order", cascade="all, delete-orphan")

class OrderItem(db.Model):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False) # Giá cố định tại thời điểm đặt

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    book: Mapped["Book"] = relationship("Book", back_populates="order_items")

class OrderHistory(db.Model):
    __tablename__ = "order_histories"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    order: Mapped["Order"] = relationship("Order", back_populates="histories")
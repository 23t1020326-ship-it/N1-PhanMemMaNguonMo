from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Khởi tạo CSDL
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config["SECRET_KEY"] = "quan-ly-sach-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///qlsach.db"

db.init_app(app)

# ---------------------------------------------------------
# MODELS (CSDL SQLite)
# ---------------------------------------------------------
class Category(db.Model):
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Quan hệ 1 - N với Book
    books: Mapped[list["Book"]] = relationship("Book", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category {self.name}>"

class Book(db.Model):
    __tablename__ = "book"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(default=0.0)
    
    # Khóa ngoại nối với Category
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"), nullable=False)
    category: Mapped["Category"] = relationship("Category", back_populates="books")

    def __repr__(self):
        return f"<Book {self.title}>"

# Khởi tạo bảng và dữ liệu mẫu
with app.app_context():
    db.create_all()
    if db.session.scalar(db.select(func.count(Category.id))) == 0:
        cat1 = Category(name="Công nghệ thông tin", description="Sách về lập trình và phần mềm")
        cat2 = Category(name="Kinh tế", description="Sách tài chính và quản trị")
        db.session.add_all([cat1, cat2])
        db.session.commit()

        b1 = Book(title="Lập trình Python cơ bản", author="Nguyễn Văn A", price=120000, category_id=cat1.id)
        b2 = Book(title="Flask Web Development", author="Trần Thị B", price=180000, category_id=cat1.id)
        b3 = Book(title="Kinh tế vĩ mô", author="Lê Hoàng C", price=95000, category_id=cat2.id)
        db.session.add_all([b1, b2, b3])
        db.session.commit()

# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------

# 3. DASHBOARD QUẢN LÝ
@app.route("/")
def dashboard():
    total_categories = db.session.scalar(db.select(func.count(Category.id)))
    total_books = db.session.scalar(db.select(func.count(Book.id)))
    avg_price = db.session.scalar(db.select(func.avg(Book.price))) or 0
    
    # Thống kê số sách theo từng danh mục
    stats = db.session.query(
        Category.name, 
        func.count(Book.id).label("book_count")
    ).outerjoin(Book).group_by(Category.id).all()

    return render_template(
        "dashboard.html", 
        total_categories=total_categories, 
        total_books=total_books, 
        avg_price=avg_price,
        stats=stats
    )

# 1. CRUD DANH MỤC SÁCH
@app.route("/categories")
def list_categories():
    categories = db.session.execute(db.select(Category)).scalars().all()
    return render_template("categories.html", categories=categories)

@app.route("/categories/add", methods=["POST"])
def add_category():
    name = request.form.get("name")
    description = request.form.get("description")
    if name:
        new_cat = Category(name=name, description=description)
        db.session.add(new_cat)
        db.session.commit()
    return redirect(url_for("list_categories"))

@app.route("/categories/edit/<int:id>", methods=["POST"])
def edit_category(id):
    cat = db.session.get(Category, id)
    if cat:
        cat.name = request.form.get("name")
        cat.description = request.form.get("description")
        db.session.commit()
    return redirect(url_for("list_categories"))

@app.route("/categories/delete/<int:id>", methods=["POST"])
def delete_category(id):
    cat = db.session.get(Category, id)
    if cat:
        db.session.delete(cat)
        db.session.commit()
    return redirect(url_for("list_categories"))

# 2. CRUD SÁCH THEO DANH MỤC
@app.route("/books")
def list_books():
    category_id = request.args.get("category_id", type=int)
    categories = db.session.execute(db.select(Category)).scalars().all()
    
    # Lọc theo danh mục nếu người dùng chọn
    if category_id:
        stmt = db.select(Book).where(Book.category_id == category_id)
    else:
        stmt = db.select(Book)
        
    books = db.session.execute(stmt).scalars().all()
    return render_template("books.html", books=books, categories=categories, selected_category=category_id)

@app.route("/books/add", methods=["POST"])
def add_book():
    title = request.form.get("title")
    author = request.form.get("author")
    price = request.form.get("price", type=float)
    category_id = request.form.get("category_id", type=int)

    if title and category_id:
        new_book = Book(title=title, author=author, price=price, category_id=category_id)
        db.session.add(new_book)
        db.session.commit()
    return redirect(url_for("list_books", category_id=category_id))

@app.route("/books/edit/<int:id>", methods=["POST"])
def edit_book(id):
    book = db.session.get(Book, id)
    if book:
        book.title = request.form.get("title")
        book.author = request.form.get("author")
        book.price = request.form.get("price", type=float)
        book.category_id = request.form.get("category_id", type=int)
        db.session.commit()
    return redirect(url_for("list_books"))

@app.route("/books/delete/<int:id>", methods=["POST"])
def delete_book(id):
    book = db.session.get(Book, id)
    if book:
        cat_id = book.category_id
        db.session.delete(book)
        db.session.commit()
        return redirect(url_for("list_books", category_id=cat_id))
    return redirect(url_for("list_books"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
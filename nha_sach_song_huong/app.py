import os
from flask import Flask, session, redirect, url_for, render_template, request, flash
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import func, or_
from models import db, Category, Book, Order
from models import db, Category, Book, Order, OrderItem, OrderHistory
from forms import CheckoutForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "nha-sach-song-huong-secret-2026"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///nhasach.db"
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # Giới hạn upload tối đa 2MB
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db.init_app(app)
csrf = CSRFProtect(app)

@app.context_processor
def inject_global_counts():
    cart = session.get("cart", {})
    cart_count = sum(cart.values()) if isinstance(cart, dict) else 0
    
    pending_count = 0
    try:
        pending_count = db.session.scalar(
            db.select(func.count(Order.id)).where(Order.status == "Chờ xác nhận")
        ) or 0
    except Exception:
        pass
        
    return dict(cart_count=cart_count, pending_orders_count=pending_count)

@app.route("/")
def index():
    return redirect(url_for("store_books"))

# =========================================================
# PHẦN A: TRANG BÁN HÀNG
# =========================================================

# Màn hình 1: Danh sách sách
@app.route("/books")
def store_books():
    q = request.args.get("q", "").strip()
    category_id = request.args.get("category_id", type=int)

    stmt = db.select(Book).order_by(Book.id.asc())
    if q:
        stmt = stmt.where(or_(Book.title.ilike(f"%{q}%"), Book.author.ilike(f"%{q}%")))
    if category_id:
        stmt = stmt.where(Book.category_id == category_id)

    books = db.session.execute(stmt).scalars().all()
    categories = db.session.execute(db.select(Category).order_by(Category.name)).scalars().all()

    return render_template(
        "store/books.html",
        books=books,
        categories=categories,
        q=q,
        selected_category=category_id
    )

# Xử lý thêm sách vào giỏ hàng (dùng chung cho Màn hình 1 và Màn hình 2)
@app.route("/cart/add/<int:book_id>", methods=["POST"])
def store_cart_add(book_id):
    book = db.session.get(Book, book_id)
    next_url = request.form.get("next") or url_for("store_books")
    
    if not book:
        flash("Sách không tồn tại.", "danger")
        return redirect(next_url)

    qty = request.form.get("quantity", type=int)
    cart = session.get("cart", {})
    book_key = str(book.id)
    current_in_cart = cart.get(book_key, 0)
    max_addable = book.stock - current_in_cart

    if qty is None or qty < 1 or qty > max_addable:
        if max_addable <= 0:
            flash(f"Sách '{book.title}' đã đạt giới hạn tồn kho trong giỏ hàng.", "warning")
        else:
            flash(f"Số lượng không hợp lệ (chỉ có thể thêm tối đa {max_addable} cuốn).", "danger")
        return redirect(next_url)

    cart[book_key] = current_in_cart + qty
    session["cart"] = cart
    flash(f"✓ Đã thêm {qty} × {book.title} vào giỏ hàng.", "success")
    return redirect(next_url)

# Route tạm cho Màn hình 2 & Màn hình 3 (sẽ hoàn thiện chi tiết ở bước kế tiếp)
# Màn hình 2: Chi tiết & Chọn sách
@app.route("/books/<int:book_id>")
def store_book_detail(book_id):
    book = db.get_or_404(Book, book_id)
    cart = session.get("cart", {})
    current_in_cart = cart.get(str(book.id), 0)
    max_addable = max(0, book.stock - current_in_cart)

    return render_template(
        "store/book_detail.html",
        book=book,
        current_in_cart=current_in_cart,
        max_addable=max_addable
    )

# Màn hình 3: Giỏ hàng
@app.route("/cart")
def store_cart():
    cart = session.get("cart", {})
    cart_items = []
    total_amount = 0
    updated_cart = {}
    cart_changed = False

    for book_id_str, qty in cart.items():
        book = db.session.get(Book, int(book_id_str))
        if not book or book.stock <= 0:
            cart_changed = True
            continue
        if qty > book.stock:
            qty = book.stock
            cart_changed = True

        updated_cart[book_id_str] = qty
        line_total = book.price * qty
        total_amount += line_total
        cart_items.append({
            "book": book,
            "quantity": qty,
            "line_total": line_total
        })

    if cart_changed:
        session["cart"] = updated_cart

    return render_template(
        "store/cart.html",
        cart_items=cart_items,
        total_amount=total_amount
    )

@app.route("/cart/update/<int:book_id>", methods=["POST"])
def store_cart_update(book_id):
    cart = session.get("cart", {})
    book_key = str(book_id)
    action = request.form.get("action")

    if book_key in cart:
        book = db.session.get(Book, book_id)
        if not book or book.stock <= 0:
            del cart[book_key]
        elif action == "increase":
            if cart[book_key] < book.stock:
                cart[book_key] += 1
            else:
                flash(f"Sách '{book.title}' đã đạt tối đa tồn kho.", "warning")
        elif action == "decrease":
            cart[book_key] -= 1
            if cart[book_key] <= 0:
                del cart[book_key]
        session["cart"] = cart

    return redirect(url_for("store_cart"))

@app.route("/cart/remove/<int:book_id>", methods=["POST"])
def store_cart_remove(book_id):
    cart = session.get("cart", {})
    book_key = str(book_id)
    if book_key in cart:
        del cart[book_key]
        session["cart"] = cart
        flash("Đã xoá sách khỏi giỏ hàng.", "info")
    return redirect(url_for("store_cart"))

@app.route("/cart/clear", methods=["POST"])
def store_cart_clear():
    session["cart"] = {}
    flash("Đã xoá toàn bộ giỏ hàng.", "info")
    return redirect(url_for("store_cart"))

# Route tạm cho Màn hình 4 (sẽ làm ở bước kế tiếp)
# Màn hình 4: Thông tin khách hàng & Đặt hàng
@app.route("/checkout", methods=["GET", "POST"])
def store_checkout():
    cart = session.get("cart", {})
    if not cart:
        flash("Giỏ hàng của bạn đang trống. Vui lòng chọn sách trước khi đặt hàng.", "warning")
        return redirect(url_for("store_cart"))

    cart_items = []
    subtotal = 0
    for book_id_str, qty in cart.items():
        book = db.session.get(Book, int(book_id_str))
        if book:
            line_total = book.price * qty
            subtotal += line_total
            cart_items.append({"book": book, "quantity": qty, "line_total": line_total})

    if not cart_items:
        session["cart"] = {}
        flash("Giỏ hàng trống.", "warning")
        return redirect(url_for("store_cart"))

    shipping_fee = 0 if subtotal >= 200000 else 20000
    total_amount = subtotal + shipping_fee

    form = CheckoutForm()
    if form.validate_on_submit():
        # Kiểm tra lại tồn kho từng cuốn trước khi tạo đơn
        for item in cart_items:
            db.session.refresh(item["book"])
            if item["book"].stock < item["quantity"]:
                flash(
                    f"Sách '{item['book'].title}' chỉ còn {item['book'].stock} cuốn trong kho (không đủ {item['quantity']} cuốn). Vui lòng cập nhật lại giỏ hàng.",
                    "danger"
                )
                return redirect(url_for("store_cart"))

        # Tạo đơn hàng mới
        order = Order(
            customer_name=form.customer_name.data.strip(),
            customer_phone=form.customer_phone.data.strip(),
            customer_email=form.customer_email.data.strip() if form.customer_email.data else None,
            shipping_address=form.shipping_address.data.strip(),
            note=form.note.data.strip() if form.note.data else None,
            payment_method=form.payment_method.data,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            total_amount=total_amount,
            status="Chờ xác nhận"
        )
        db.session.add(order)
        db.session.flush()  # Lấy order.id trước khi commit

        # Lưu từng dòng đơn hàng & trừ tồn kho
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                book_id=item["book"].id,
                quantity=item["quantity"],
                unit_price=item["book"].price
            )
            item["book"].stock -= item["quantity"]
            db.session.add(order_item)

        # Ghi nhận lịch sử trạng thái đầu tiên
        history = OrderHistory(order_id=order.id, status="Chờ xác nhận")
        db.session.add(history)

        db.session.commit()
        session["cart"] = {}
        return redirect(url_for("store_order_success", order_id=order.id))

    return render_template(
        "store/checkout.html",
        form=form,
        cart_items=cart_items,
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        total_amount=total_amount
    )

# Màn hình 5: Đặt hàng thành công
@app.route("/orders/<int:order_id>")
def store_order_success(order_id):
    order = db.get_or_404(Order, order_id)
    return render_template("store/order_success.html", order=order)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
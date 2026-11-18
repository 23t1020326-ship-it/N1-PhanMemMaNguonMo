from app import app
from models import db, Category, Book

with app.app_context():
    db.create_all()
    if Category.query.count() == 0:
        c1 = Category(name="Lập trình", description="Sách ngôn ngữ lập trình và framework")
        c2 = Category(name="Cơ sở dữ liệu", description="Hệ quản trị CSDL và thiết kế dữ liệu")
        c3 = Category(name="Công cụ", description="Git, Docker và công cụ phát triển")
        c4 = Category(name="Mạng", description="Mạng máy tính và bảo mật")
        c5 = Category(name="Kỹ năng lập trình", description="Tư duy thiết kế và viết mã sạch")
        c6 = Category(name="Thiết kế", description="UI/UX và thiết kế hệ thống")
        db.session.add_all([c1, c2, c3, c4, c5, c6])
        db.session.commit()

        books = [
            Book(title="Lập trình Python cơ bản", author="Nguyễn Văn A", publisher="NXB Đại học Huế", publish_year=2024, price=95000, stock=30, category_id=c1.id, description="Giáo trình nhập môn lập trình Python dành cho sinh viên CNTT."),
            Book(title="Giáo trình Flask", author="Miguel Grinberg", publisher="NXB Khoa học", publish_year=2023, price=120000, stock=20, category_id=c1.id, description="Xây dựng ứng dụng web thực tế với Python Flask."),
            Book(title="Cơ sở dữ liệu", author="Trần Văn B", publisher="NXB Giáo dục", publish_year=2022, price=85000, stock=0, category_id=c2.id, description="Nguyên lý thiết kế cơ sở dữ liệu quan hệ và SQL."),
            Book(title="Pro Git", author="Scott Chacon", publisher="Apress", publish_year=2021, price=150000, stock=15, category_id=c3.id, description="Hướng dẫn sử dụng Git từ cơ bản đến nâng cao."),
            Book(title="Mạng máy tính", author="Lê Văn C", publisher="NXB Đại học Huế", publish_year=2023, price=110000, stock=12, category_id=c4.id, description="Kiến trúc phân tầng và các giao thức mạng."),
            Book(title="Clean Code", author="Robert C. Martin", publisher="Prentice Hall", publish_year=2008, price=180000, stock=5, category_id=c5.id, description="Nghệ thuật viết mã sạch và bảo trì phần mềm.")
        ]
        db.session.add_all(books)
        db.session.commit()
        print("Đã tạo dữ liệu mẫu thành công!")
    else:
        print("CSDL đã có dữ liệu.")
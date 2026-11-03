from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask import Flask, render_template

# ==========================================
# BƯỚC 2: CẤU HÌNH KẾT NỐI CSDL
# ==========================================
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-chi-dung-khi-phat-trien"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///qlsv.db"
db.init_app(app)

# ==========================================
# BƯỚC 3: KHAI BÁO MODEL STUDENT
# ==========================================
class Student(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    mssv: Mapped[str] = mapped_column(String(10), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    gpa: Mapped[float] = mapped_column(default=0.0)

    def __repr__(self):
        return f"<Student {self.mssv} {self.name}>"
# ==========================================
# BƯỚC 4: TẠO BẢNG TRONG CSDL
# ==========================================
with app.app_context():
    db.create_all()
# ==========================================
# BƯỚC 5: ROUTE THÊM DỮ LIỆU MẪU
# ==========================================
@app.get("/them-mau")
def add_sample():
    total = db.session.scalar(db.select(func.count(Student.id)))
    if total > 0:
        return f"Đã có {total} sinh viên, không thêm nữa."
    an = Student(mssv="23T1020001", name="Nguyễn Văn An", gpa=8.5)
    before = an.id  
    db.session.add(an) 
    db.session.add_all([
        Student(mssv="23T1020002", name="Trần Thị Bình", gpa=6.8),
        Student(mssv="23T1020003", name="Lê Hoàng Cường", gpa=9.1),
        Student(mssv="23T1020004", name="Phạm Minh Dũng", gpa=4.5),
        Student(mssv="23T1020005", name="Hoàng Thu Hà", gpa=7.4),
    ])
    db.session.commit() 
    return (
        f"Đã thêm 5 sinh viên. id của An: "
        f"trước commit = {before}, "
        f"sau commit = {an.id}"
    )
# ==========================================
# BƯỚC 6: ĐỌC DỮ LIỆU VỚI CÁC TRUY VẤN
# ==========================================
TEXT = {"Content-Type": "text/plain; charset=utf-8"}
@app.get("/thu-truy-van")
def try_queries():
    if db.session.scalar(db.select(func.count(Student.id))) == 0:
        return "Chưa có dữ liệu, hãy mở /them-mau trước."
    lines = []
    lines.append(f"1. get(3): {db.session.get(Student, 3)}")
    lines.append(f"2. get(99): {db.session.get(Student, 99)}")
    everyone = db.session.execute(db.select(Student)).scalars().all()
    lines.append(f"3. Tất cả: {len(everyone)} sinh viên")
    stmt = db.select(Student).where(Student.gpa >= 8).order_by(Student.gpa.desc())
    good = db.session.execute(stmt).scalars().all()
    lines.append(f"4. Điểm >= 8: {good}")

    binh = db.session.scalar(
        db.select(Student).filter_by(mssv="23T1020002")
    )
    lines.append(f"5. MSSV 23T1020002: {binh}")
    count = db.session.scalar(db.select(func.count(Student.id)))
    avg = db.session.scalar(db.select(func.avg(Student.gpa)))
    lines.append(f"6. Số SV: {count}, điểm TB: {avg:.2f}")

    return "\n".join(lines), TEXT

@app.get("/danh-sach")
def list_students():
    students = db.session.execute(db.select(Student)).scalars().all()
    return render_template("students.html", students=students)

if __name__ == "__main__":
    app.run(debug=True, port=5000)

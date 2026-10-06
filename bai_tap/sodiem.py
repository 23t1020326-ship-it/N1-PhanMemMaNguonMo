import csv
import io
from flask import (
    Flask,
    abort,
    make_response,
    redirect,
    render_template_string,
    request,
    url_for,
)

app = Flask(__name__)
app.json.ensure_ascii = False

STUDENTS = {
    "23T1020001": {
        "name": "Nguyễn Văn An",
        "lop": "K47A",
        "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0},
    },
    "23T1020002": {
        "name": "Trần Thị Bình",
        "lop": "K47A",
        "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0},
    },
    "23T1020003": {
        "name": "Lê Hoàng Cường",
        "lop": "K47B",
        "scores": {"PMMNM": 9.5, "CSDL": 9.0},
    },
    "23T1020004": {
        "name": "Phạm Minh Dũng",
        "lop": "K47B",
        "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0},
    },
    "23T1020005": {"name": "Hoàng Thu Hà", "lop": "K47A", "scores": {}},
    "23T1020006": {
        "name": "Võ Quốc Khánh",
        "lop": "K47C",
        "scores": {"PMMNM": 7.5, "MMT": 8.0},
    },
}

INDEX_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Trang Chủ - Quản Lý Sổ Điểm</title>
</head>
<body>
    <h1>Trang Chủ</h1>
    <p>Tổng số sinh viên: <strong>{{ total_students }}</strong></p>
    <p>Số lớp: <strong>{{ total_classes }}</strong></p>
    <hr>
    <ul>
        <li><a href="{{ url_for('student_list') }}">Xem danh sách sinh viên (/students)</a></li>
        <li><a href="{{ url_for('api_students') }}">Xem API sinh viên (/api/students)</a></li>
    </ul>
</body>
</html>
"""

STUDENTS_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Danh Sách Sinh Viên</title>
    <style>
        table, th, td { border: 1px solid black; border-collapse: collapse; padding: 8px; }
        .filter-bar { margin-bottom: 15px; }
        .filter-bar a { margin-right: 10px; text-decoration: none; }
        .active { font-weight: bold; text-decoration: underline; }
        .search-box { margin-bottom: 15px; }
    </style>
</head>
<body>
    <h1>Danh Sách Sinh Viên</h1>

    <div class="search-box">
        <form action="{{ url_for('search_students') }}" method="get">
            <input type="text" name="q" value="{{ query|default('', true) }}" placeholder="Nhập tên hoặc MSSV...">
            <button type="submit">Tìm kiếm</button>
            {% if query %}
                <a href="{{ url_for('student_list') }}">Xóa tìm kiếm</a>
            {% endif %}
        </form>
    </div>

    {% if query is not none %}
        <p>Tìm thấy <strong>{{ students|length }}</strong> kết quả cho "<strong>{{ query }}</strong>"</p>
    {% endif %}

    <div class="filter-bar">
        Lọc theo lớp: 
        <a href="{{ url_for('student_list') }}" class="{% if not selected_class %}active{% endif %}">Tất cả</a>
        {% for c in all_classes %}
            | <a href="{{ url_for('student_list', lop=c) }}" class="{% if selected_class == c %}active{% endif %}">{{ c }}</a>
        {% endfor %}
    </div>

    {% if students %}
    <table>
        <thead>
            <tr>
                <th>MSSV</th>
                <th>Họ tên</th>
                <th>Lớp</th>
                <th>Điểm TB</th>
                <th>Xếp loại</th>
            </tr>
        </thead>
        <tbody>
            {% for s in students %}
            <tr>
                <td><a href="{{ url_for('student_detail', mssv=s.mssv) }}">{{ s.mssv }}</a></td>
                <td>{{ s.name }}</td>
                <td>{{ s.lop }}</td>
                <td>{{ s.dtb }}</td>
                <td>{{ s.xep_loai }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
        <p><strong>Không có sinh viên phù hợp.</strong></p>
    {% endif %}

    <p><a href="{{ url_for('index') }}">Quay lại Trang chủ</a></p>
</body>
</html>
"""

STUDENT_DETAIL_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Chi Tiết Sinh Viên - {{ student.name }}</title>
    <style>
        table, th, td { border: 1px solid black; border-collapse: collapse; padding: 8px; }
    </style>
</head>
<body>
    <h1>Thông Tin Sinh Viên</h1>
    <p><strong>Họ tên:</strong> {{ student.name }}</p>
    <p><strong>MSSV:</strong> {{ mssv }}</p>
    <p><strong>Lớp:</strong> <a href="{{ url_for('student_list', lop=student.lop) }}">{{ student.lop }}</a></p>
    <p><strong>Điểm trung bình:</strong> {{ dtb if dtb != None else '-' }}</p>
    <p><strong>Xếp loại:</strong> {{ xep_loai }}</p>
    <p><strong>Link rút gọn:</strong> <a href="{{ url_for('student_short_link', mssv=mssv) }}">{{ request.host_url }}sv/{{ mssv }}</a></p>

    <h2>Bảng Điểm Học Phần</h2>
    {% if student.scores %}
    <table>
        <thead>
            <tr>
                <th>Môn học</th>
                <th>Điểm</th>
            </tr>
        </thead>
        <tbody>
            {% for mon, diem in student.scores.items() %}
            <tr>
                <td>{{ mon }}</td>
                <td>{{ diem }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <p><a href="{{ url_for('export_student_csv', mssv=mssv) }}">Tải bảng điểm (CSV)</a></p>
    {% else %}
        <p>Sinh viên chưa có điểm học phần nào.</p>
    {% endif %}

    <p><a href="{{ url_for('student_list') }}">Quay lại Danh sách sinh viên</a></p>
</body>
</html>
"""


def tinh_dtb(scores):
    if not scores:
        return None
    return round(sum(scores.values()) / len(scores), 2)


def xep_loai(dtb):
    if dtb is None:
        return "-"
    if dtb >= 8.5:
        return "Xuất sắc"
    if dtb >= 7.0:
        return "Giỏi"
    if dtb >= 5.5:
        return "Khá"
    if dtb >= 4.0:
        return "Trung bình"
    return "Yếu"


# Câu 1
@app.route("/")
def index():
    total_students = len(STUDENTS)
    classes = sorted(list({info["lop"] for info in STUDENTS.values()}))
    total_classes = len(classes)

    return render_template_string(
        INDEX_HTML,
        total_students=total_students,
        total_classes=total_classes,
    )


@app.route("/api/students")
def api_students():
    return STUDENTS


# Câu 2
@app.route("/students", endpoint="student_list")
def student_list():
    lop_filter = request.args.get("lop", "").strip()
    all_classes = sorted(list({info["lop"] for info in STUDENTS.values()}))

    filtered_students = []

    for mssv, info in STUDENTS.items():
        if (
            not lop_filter
            or info["lop"].strip().upper() == lop_filter.upper()
        ):
            dtb = tinh_dtb(info["scores"])
            xl = xep_loai(dtb)

            filtered_students.append(
                {
                    "mssv": mssv,
                    "name": info["name"],
                    "lop": info["lop"],
                    "dtb": dtb if dtb is not None else "-",
                    "xep_loai": xl,
                }
            )

    return render_template_string(
        STUDENTS_HTML,
        students=filtered_students,
        all_classes=all_classes,
        selected_class=lop_filter.upper(),
        query=None,
    )


# Câu 3
@app.route("/students/<mssv>")
def student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")

    student = STUDENTS[mssv]
    dtb = tinh_dtb(student["scores"])
    xl = xep_loai(dtb)

    return render_template_string(
        STUDENT_DETAIL_HTML, mssv=mssv, student=student, dtb=dtb, xep_loai=xl
    )


# Câu 4
@app.route("/sv/<mssv>")
def student_short_link(mssv):
    return redirect(url_for("student_detail", mssv=mssv), code=301)


# Câu 5
@app.route("/students/<mssv>/export")
def export_student_csv(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")

    student = STUDENTS[mssv]

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["hoc_phan", "diem"])

    for mon, diem in student["scores"].items():
        writer.writerow([mon, diem])

    response = make_response(output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = (
        f"attachment; filename=diem_{mssv}.csv"
    )

    return response


# Câu 6
@app.route("/search", endpoint="search_students")
def search_students():
    q = request.args.get("q", "").strip()
    all_classes = sorted(list({info["lop"] for info in STUDENTS.values()}))

    matched_students = []

    if q:
        q_lower = q.lower()
        for mssv, info in STUDENTS.items():
            if q_lower in mssv.lower() or q_lower in info["name"].lower():
                dtb = tinh_dtb(info["scores"])
                xl = xep_loai(dtb)
                matched_students.append(
                    {
                        "mssv": mssv,
                        "name": info["name"],
                        "lop": info["lop"],
                        "dtb": dtb if dtb is not None else "-",
                        "xep_loai": xl,
                    }
                )

    return render_template_string(
        STUDENTS_HTML,
        students=matched_students,
        all_classes=all_classes,
        selected_class="",
        query=q,
    )


if __name__ == "__main__":
    app.run(debug=True, port=8000)
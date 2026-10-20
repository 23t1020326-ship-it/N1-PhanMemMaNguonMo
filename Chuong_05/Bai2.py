from flask import Flask, render_template, request

app = Flask(__name__)


def validate_score(val_str):
    if not val_str or not val_str.strip():
        return None, "Vui lòng nhập một số."

    val_clean = val_str.strip().replace(",", ".")
    try:
        score = float(val_clean)
        if score < 0 or score > 10:
            return None, "Điểm phải từ 0 đến 10."
        return score, None
    except ValueError:
        return None, "Vui lòng nhập một số."


@app.route("/", methods=["GET", "POST"])
def tinh_diem():
    values = {}
    errors = {}
    result = None

    if request.method == "POST":

        values = request.form

        score_cc, err_cc = validate_score(values.get("cc", ""))
        score_gk, err_gk = validate_score(values.get("gk", ""))
        score_ck, err_ck = validate_score(values.get("ck", ""))

        if err_cc:
            errors["cc"] = err_cc
        if err_gk:
            errors["gk"] = err_gk
        if err_ck:
            errors["ck"] = err_ck

        if not errors:
            dtb = score_cc * 0.1 + score_gk * 0.3 + score_ck * 0.6
            dtb_rounded = round(dtb, 1)

            if score_ck < 1:
                diem_chu = "F (điểm thi dưới 1)"
            elif dtb_rounded >= 8.5:
                diem_chu = "A"
            elif dtb_rounded >= 7.0:
                diem_chu = "B"
            elif dtb_rounded >= 5.5:
                diem_chu = "C"
            elif dtb_rounded >= 4.0:
                diem_chu = "D"
            else:
                diem_chu = "F"

            result = f"{dtb_rounded} · {diem_chu}"

    return render_template(
        "Bai2.html", values=values, errors=errors, result=result
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
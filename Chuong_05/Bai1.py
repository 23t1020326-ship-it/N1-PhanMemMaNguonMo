from flask import Flask, render_template, request

app = Flask(__name__)


def parse_number(val_str):

    if not val_str or not val_str.strip():
        return None, "Vui lòng nhập một số."

    val_clean = val_str.strip().replace(",", ".")
    try:
        num = float(val_clean)
        if num.is_integer():
            return int(num), None
        return num, None
    except ValueError:
        return None, "Vui lòng nhập một số."


@app.route("/", methods=["GET", "POST"])
def calculator():
    values = {}
    errors = {}
    result = None

    if request.method == "POST":
        values = request.form

        num_a, err_a = parse_number(values.get("a", ""))
        num_b, err_b = parse_number(values.get("b", ""))
        op = values.get("op", "+")

        if err_a:
            errors["a"] = err_a
        if err_b:
            errors["b"] = err_b

        valid_ops = ["+", "-", "*", "/"]
        if op not in valid_ops:
            errors["op"] = "Phép toán không hợp lệ."

        if not errors:
            if op == "+":
                res_val = num_a + num_b
            elif op == "-":
                res_val = num_a - num_b
            elif op == "*":
                res_val = num_a * num_b
            elif op == "/":
                if num_b == 0:
                    errors["b"] = "Không thể chia cho 0."
                else:
                    res_val = num_a / num_b

            if not errors:
                res_clean = (
                    int(res_val)
                    if isinstance(res_val, float) and res_val.is_integer()
                    else res_val
                )
                result = f"{num_a} {op} {num_b} = {res_clean}"

    return render_template(
        "Bai1.html", values=values, errors=errors, result=result
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
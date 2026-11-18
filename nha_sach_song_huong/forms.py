from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, RadioField, SubmitField
from wtforms.validators import DataRequired, Optional, Email, Regexp, Length

class CheckoutForm(FlaskForm):
    customer_name = StringField(
        "Họ tên",
        validators=[
            DataRequired(message="Vui lòng nhập họ tên người nhận."),
            Length(max=150, message="Họ tên tối đa 150 ký tự.")
        ]
    )
    customer_phone = StringField(
        "Số điện thoại",
        validators=[
            DataRequired(message="Vui lòng nhập số điện thoại."),
            Regexp(r"^0\d{9}$", message="Số điện thoại gồm 10 chữ số và bắt đầu bằng 0.")
        ]
    )
    customer_email = StringField(
        "Email",
        validators=[
            Optional(),
            Email(message="Địa chỉ email không đúng định dạng."),
            Length(max=150)
        ]
    )
    shipping_address = StringField(
        "Địa chỉ giao hàng",
        validators=[
            DataRequired(message="Vui lòng nhập địa chỉ giao hàng."),
            Length(max=255, message="Địa chỉ tối đa 255 ký tự.")
        ]
    )
    note = StringField(
        "Ghi chú",
        validators=[Optional(), Length(max=500)]
    )
    payment_method = RadioField(
        "Thanh toán",
        choices=[
            ("Tiền mặt khi nhận hàng", "Tiền mặt khi nhận hàng"),
            ("Chuyển khoản", "Chuyển khoản")
        ],
        default="Tiền mặt khi nhận hàng",
        validators=[DataRequired(message="Vui lòng chọn phương thức thanh toán.")]
    )
    submit = SubmitField("Xác nhận đặt hàng")
import qrcode
import io
import base64

def generate_qr_code_image(url):
    """生成二维码图片并返回 base64 数据"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    # 添加数据到二维码
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    # 将图片转为 base64 数据
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_base64

if __name__ == "__main__":
    print(generate_qr_code_image("https://example.com"))
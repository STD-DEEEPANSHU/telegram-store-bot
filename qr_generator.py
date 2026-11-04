import io
import qrcode
from PIL import Image
from config import PAYTM_UPI_ID, PAYEE_NAME
import database as db

def generate_upi_qr(amount_inr: float, order_ref: str) -> io.BytesIO:
    """
    Generates a high-quality UPI QR Code for any UPI App (Paytm, GPay, PhonePe, BHIM)
    """
    active_upi = db.get_setting("paytm_upi_id", PAYTM_UPI_ID)
    active_payee = db.get_setting("payee_name", PAYEE_NAME)
    upi_payload = f"upi://pay?pa={active_upi}&pn={active_payee}&am={amount_inr:.2f}&cu=INR&tn={order_ref}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

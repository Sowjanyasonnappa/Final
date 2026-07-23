from io import BytesIO

from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


def generate_invoice(order):

    buffer = BytesIO()

    pdf = canvas.Canvas(buffer)

    pdf.setTitle("Invoice")

    pdf.setFont("Helvetica-Bold",18)

    pdf.drawString(
        200,
        800,
        "INVOICE",
    )

    pdf.setFont("Helvetica",12)

    pdf.drawString(
        40,
        760,
        f"Invoice No : INV-{order.id}",
    )

    pdf.drawString(
        40,
        740,
        f"Order ID : {order.id}",
    )

    pdf.drawString(
        40,
        720,
        f"Customer : {order.user.email}",
    )

    pdf.drawString(
        40,
        700,
        f"Status : {order.status}",
    )

    pdf.drawString(
        40,
        680,
        f"Payment : {order.payment_status}",
    )

    pdf.drawString(
        40,
        660,
        f"Shipping : {order.shipping_address}",
    )

    y = 610

    pdf.setFont("Helvetica-Bold",12)

    pdf.drawString(40,y,"Product")

    pdf.drawString(260,y,"Qty")

    pdf.drawString(340,y,"Price")

    y -= 25

    pdf.setFont("Helvetica",12)

    total = 0

    for item in order.items:

        pdf.drawString(
            40,
            y,
            item.product.name,
        )

        pdf.drawString(
            260,
            y,
            str(item.quantity),
        )

        amount = item.quantity * item.price_at_purchase

        pdf.drawString(
            340,
            y,
            f"₹ {amount}",
        )

        total += amount

        y -= 20

    y -= 30

    pdf.setFont("Helvetica-Bold",14)

    pdf.drawString(
        40,
        y,
        f"Total : ₹ {order.total_amount}",
    )

    pdf.save()

    buffer.seek(0)

    return buffer
def order_confirmation(user, order):

    return f"""
    <h2>Order Confirmation</h2>

    <p>Hello {user.email}</p>

    <p>Your Order #{order.id} has been placed successfully.</p>

    <p>Total Amount : ₹ {order.total_amount}</p>

    <p>Status : {order.status}</p>

    <br>

    Thank you for shopping with us.
    """


def payment_success(user, payment):

    return f"""
    <h2>Payment Successful</h2>

    <p>Hello {user.email}</p>

    <p>Payment of ₹ {payment.amount} completed.</p>

    <p>Transaction ID:</p>

    <b>{payment.transaction_id}</b>
    """


def shipped(user, order):

    return f"""
    <h2>Your Order is Shipped</h2>

    <p>Hello {user.email}</p>

    <p>Order #{order.id} has been shipped.</p>
    """


def delivered(user, order):

    return f"""
    <h2>Order Delivered</h2>

    <p>Hello {user.email}</p>

    <p>Order #{order.id} delivered successfully.</p>
    """


def cancelled(user, order):

    return f"""
    <h2>Order Cancelled</h2>

    <p>Hello {user.email}</p>

    <p>Your order #{order.id} has been cancelled.</p>
    """
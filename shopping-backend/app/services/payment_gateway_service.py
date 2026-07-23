"""
Payment Gateway Integration Service
Supports: Stripe, Razorpay, PayPal
"""

from typing import Dict, Optional
from uuid import UUID
from decimal import Decimal
from enum import Enum
import logging
import os
import json

logger = logging.getLogger(__name__)


class PaymentProvider(str, Enum):
    """Supported payment providers"""
    STRIPE = "stripe"
    RAZORPAY = "razorpay"
    PAYPAL = "paypal"


class StripePaymentGateway:
    """Stripe payment integration"""
    
    def __init__(self):
        try:
            import stripe
            self.stripe = stripe
            self.client = stripe
            self.api_key = os.getenv("STRIPE_API_KEY")
            if self.api_key:
                stripe.api_key = self.api_key
        except ImportError:
            logger.warning("Stripe SDK not installed")
            self.client = None
    
    def create_payment_intent(
        self,
        amount: float,
        currency: str = "USD",
        order_id: str = None,
        customer_email: str = None
    ) -> Dict:
        """Create Stripe payment intent"""
        try:
            if not self.client:
                return {"error": "Stripe not configured"}
            
            # Stripe uses smallest currency unit (cents for USD)
            amount_cents = int(amount * 100)
            
            intent = self.client.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                description=f"Order {order_id}" if order_id else "Payment",
                receipt_email=customer_email
            )
            
            return {
                "payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status,
                "amount": amount,
                "currency": currency
            }
            
        except Exception as e:
            logger.error(f"Stripe error creating intent: {str(e)}")
            return {"error": str(e)}
    
    def confirm_payment(self, payment_intent_id: str) -> Dict:
        """Confirm payment intent"""
        try:
            if not self.client:
                return {"error": "Stripe not configured"}
            
            intent = self.client.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                "status": intent.status,
                "amount": intent.amount / 100,  # Convert back to dollars
                "currency": intent.currency,
                "confirmed": intent.status == "succeeded"
            }
            
        except Exception as e:
            logger.error(f"Stripe error confirming payment: {str(e)}")
            return {"error": str(e)}
    
    def refund(self, payment_intent_id: str, amount: float = None) -> Dict:
        """Process Stripe refund"""
        try:
            if not self.client:
                return {"error": "Stripe not configured"}
            
            amount_cents = int(amount * 100) if amount else None
            
            refund = self.client.Refund.create(
                payment_intent=payment_intent_id,
                amount=amount_cents
            )
            
            return {
                "refund_id": refund.id,
                "status": refund.status,
                "amount": refund.amount / 100,
                "reason": refund.reason
            }
            
        except Exception as e:
            logger.error(f"Stripe error processing refund: {str(e)}")
            return {"error": str(e)}


class RazorpayPaymentGateway:
    """Razorpay payment integration"""
    
    def __init__(self):
        try:
            import razorpay
            self.razorpay = razorpay
            self.client = razorpay.Client(
                auth=(
                    os.getenv("RAZORPAY_KEY"),
                    os.getenv("RAZORPAY_SECRET")
                )
            )
        except ImportError:
            logger.warning("Razorpay SDK not installed")
            self.client = None
    
    def create_payment_order(
        self,
        amount: float,
        currency: str = "INR",
        order_id: str = None,
        customer_email: str = None
    ) -> Dict:
        """Create Razorpay order"""
        try:
            if not self.client:
                return {"error": "Razorpay not configured"}
            
            # Razorpay uses smallest currency unit (paise for INR)
            amount_paise = int(amount * 100)
            
            order = self.client.order.create(
                amount=amount_paise,
                currency=currency,
                receipt=order_id or f"order_{int(amount)}"
            )
            
            return {
                "order_id": order["id"],
                "status": order["status"],
                "amount": amount,
                "currency": currency
            }
            
        except Exception as e:
            logger.error(f"Razorpay error creating order: {str(e)}")
            return {"error": str(e)}
    
    def verify_payment(self, payment_id: str, signature: str, order_id: str) -> bool:
        """Verify Razorpay payment signature"""
        try:
            if not self.client:
                return False
            
            # Verify signature
            body = f"{order_id}|{payment_id}"
            expected_signature = self.client.utility.verify_payment_signature({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Razorpay signature verification failed: {str(e)}")
            return False
    
    def refund(self, payment_id: str, amount: float = None) -> Dict:
        """Process Razorpay refund"""
        try:
            if not self.client:
                return {"error": "Razorpay not configured"}
            
            amount_paise = int(amount * 100) if amount else None
            
            refund = self.client.payment.refund(
                payment_id,
                amount=amount_paise
            )
            
            return {
                "refund_id": refund["id"],
                "status": refund["status"],
                "amount": refund.get("amount", amount),
                "receipt": refund.get("receipt")
            }
            
        except Exception as e:
            logger.error(f"Razorpay error processing refund: {str(e)}")
            return {"error": str(e)}


class PayPalPaymentGateway:
    """PayPal payment integration"""
    
    def __init__(self):
        try:
            import paypalrestsdk
            self.paypal = paypalrestsdk
            self.paypal.configure({
                "mode": os.getenv("PAYPAL_MODE", "sandbox"),
                "client_id": os.getenv("PAYPAL_CLIENT_ID"),
                "client_secret": os.getenv("PAYPAL_SECRET")
            })
        except ImportError:
            logger.warning("PayPal SDK not installed")
            self.paypal = None
    
    def create_payment(
        self,
        amount: float,
        currency: str = "USD",
        order_id: str = None,
        return_url: str = None,
        cancel_url: str = None
    ) -> Dict:
        """Create PayPal payment"""
        try:
            if not self.paypal:
                return {"error": "PayPal not configured"}
            
            payment = self.paypal.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": return_url or "http://localhost:3000/payment/success",
                    "cancel_url": cancel_url or "http://localhost:3000/payment/cancel"
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": f"Order {order_id}",
                            "sku": order_id,
                            "price": str(amount),
                            "currency": currency,
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": str(amount),
                        "currency": currency,
                        "details": {
                            "subtotal": str(amount)
                        }
                    },
                    "description": f"Payment for order {order_id}"
                }]
            })
            
            if payment.create():
                return {
                    "payment_id": payment.id,
                    "status": payment.state,
                    "approval_url": next(
                        (link.href for link in payment.links if link.rel == "approval_url"),
                        None
                    )
                }
            else:
                logger.error(f"PayPal payment creation failed: {payment.error}")
                return {"error": payment.error.get("message", "Unknown error")}
            
        except Exception as e:
            logger.error(f"PayPal error creating payment: {str(e)}")
            return {"error": str(e)}
    
    def execute_payment(self, payment_id: str, payer_id: str) -> Dict:
        """Execute PayPal payment"""
        try:
            if not self.paypal:
                return {"error": "PayPal not configured"}
            
            payment = self.paypal.Payment.find(payment_id)
            
            if payment.execute({"payer_id": payer_id}):
                return {
                    "status": payment.state,
                    "transaction_id": payment.transactions[0].related_resources[0].sale.id,
                    "amount": payment.transactions[0].amount.total
                }
            else:
                logger.error(f"PayPal execution failed: {payment.error}")
                return {"error": payment.error.get("message", "Unknown error")}
            
        except Exception as e:
            logger.error(f"PayPal error executing payment: {str(e)}")
            return {"error": str(e)}
    
    def refund(self, sale_id: str, amount: str = None) -> Dict:
        """Process PayPal refund"""
        try:
            if not self.paypal:
                return {"error": "PayPal not configured"}
            
            sale = self.paypal.Sale.find(sale_id)
            
            refund_dict = {}
            if amount:
                refund_dict["amount"] = {
                    "total": str(amount),
                    "currency": "USD"
                }
            
            refund = sale.refund(refund_dict)
            
            if refund.success():
                return {
                    "refund_id": refund.id,
                    "status": refund.state,
                    "amount": refund.amount.total if refund.amount else None
                }
            else:
                logger.error(f"PayPal refund failed: {refund.error}")
                return {"error": refund.error.get("message", "Unknown error")}
            
        except Exception as e:
            logger.error(f"PayPal error processing refund: {str(e)}")
            return {"error": str(e)}


class PaymentGatewayFactory:
    """Factory for creating payment gateway instances"""
    
    _gateways = {
        PaymentProvider.STRIPE: StripePaymentGateway,
        PaymentProvider.RAZORPAY: RazorpayPaymentGateway,
        PaymentProvider.PAYPAL: PayPalPaymentGateway
    }
    
    @staticmethod
    def get_gateway(provider: PaymentProvider):
        """Get payment gateway instance"""
        gateway_class = PaymentGatewayFactory._gateways.get(provider)
        if not gateway_class:
            raise ValueError(f"Unknown payment provider: {provider}")
        return gateway_class()
    
    @staticmethod
    def get_default_gateway():
        """Get default payment gateway"""
        provider = os.getenv("DEFAULT_PAYMENT_PROVIDER", "stripe")
        try:
            return PaymentGatewayFactory.get_gateway(PaymentProvider(provider))
        except ValueError:
            logger.warning(f"Default payment provider {provider} not found, using Stripe")
            return StripePaymentGateway()


class PaymentService:
    """High-level payment service"""
    
    def __init__(self, provider: PaymentProvider = PaymentProvider.STRIPE):
        self.gateway = PaymentGatewayFactory.get_gateway(provider)
        self.provider = provider
    
    async def process_payment(
        self,
        amount: float,
        currency: str,
        order_id: str,
        customer_email: str = None
    ) -> Dict:
        """Process payment with appropriate gateway"""
        
        if self.provider == PaymentProvider.STRIPE:
            return self.gateway.create_payment_intent(
                amount=amount,
                currency=currency,
                order_id=order_id,
                customer_email=customer_email
            )
        
        elif self.provider == PaymentProvider.RAZORPAY:
            return self.gateway.create_payment_order(
                amount=amount,
                currency=currency,
                order_id=order_id,
                customer_email=customer_email
            )
        
        elif self.provider == PaymentProvider.PAYPAL:
            return self.gateway.create_payment(
                amount=amount,
                currency=currency,
                order_id=order_id
            )
    
    async def process_refund(
        self,
        transaction_id: str,
        amount: float = None
    ) -> Dict:
        """Process refund"""
        return self.gateway.refund(transaction_id, amount)

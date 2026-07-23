"""
Customer Analytics & Segmentation Service
Analyzes customer behavior and segments them by value and engagement
"""

from typing import List, Dict, Optional
from uuid import UUID
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
import logging

logger = logging.getLogger(__name__)


class CustomerAnalyticsService:
    """
    Analytics engine for customer segmentation and behavior analysis
    Segments: HIGH_VALUE, REGULAR, AT_RISK, NEW, VIP
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def calculate_customer_metrics(self, user_id: UUID) -> dict:
        """
        Calculate comprehensive metrics for a customer
        Returns: lifetime value, purchase frequency, avg order value, churn risk
        """
        try:
            from app.database.order_model import Order
            from app.database.user_model import User
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            # Get orders
            orders = self.db.query(Order).filter(
                and_(
                    Order.user_id == user_id,
                    Order.status == "COMPLETED"
                )
            ).all()
            
            # Calculate metrics
            lifetime_value = sum(
                float(order.total) for order in orders if order.total
            )
            
            purchase_count = len(orders)
            
            # Purchase frequency (orders in last 90 days)
            ninety_days_ago = datetime.now() - timedelta(days=90)
            recent_orders = [
                o for o in orders
                if o.created_at > ninety_days_ago
            ]
            purchase_frequency_90d = len(recent_orders)
            
            # Average order value
            avg_order_value = (
                lifetime_value / purchase_count if purchase_count > 0 else 0
            )
            
            # Days since last purchase
            if orders:
                last_purchase = max(o.created_at for o in orders)
                days_since_purchase = (datetime.now() - last_purchase).days
            else:
                days_since_purchase = (datetime.now() - user.created_at).days
            
            # Account age in days
            account_age = (datetime.now() - user.created_at).days
            
            # Customer since (months)
            months_as_customer = account_age / 30
            
            # Churn risk calculation
            churn_risk = self._calculate_churn_risk(
                days_since_purchase=days_since_purchase,
                purchase_frequency=purchase_frequency_90d,
                lifetime_value=lifetime_value,
                account_age=account_age
            )
            
            # Purchase trend (increasing/decreasing/stable)
            purchase_trend = self._calculate_purchase_trend(orders)
            
            return {
                "lifetime_value": Decimal(str(lifetime_value)),
                "purchase_count": purchase_count,
                "purchase_frequency_90d": purchase_frequency_90d,
                "average_order_value": Decimal(str(avg_order_value)),
                "days_since_last_purchase": days_since_purchase,
                "account_age_days": account_age,
                "months_as_customer": months_as_customer,
                "churn_risk": churn_risk,
                "purchase_trend": purchase_trend,
                "total_spent": Decimal(str(lifetime_value)),
                "order_count": purchase_count
            }
            
        except Exception as e:
            logger.error(f"Error calculating customer metrics: {str(e)}")
            return {}
    
    def _calculate_churn_risk(
        self,
        days_since_purchase: int,
        purchase_frequency: int,
        lifetime_value: float,
        account_age: int
    ) -> float:
        """
        Calculate churn risk (0-1 probability)
        Higher = higher risk of not purchasing again
        """
        risk_score = 0.0
        
        # Recency factor (40% weight) - Most important
        if days_since_purchase > 180:
            risk_score += 0.4  # 6+ months since purchase
        elif days_since_purchase > 90:
            risk_score += 0.2  # 3-6 months
        elif days_since_purchase > 30:
            risk_score += 0.1  # 1-3 months
        
        # Frequency factor (30% weight)
        if purchase_frequency == 0:
            risk_score += 0.3  # No purchases in 90 days
        elif purchase_frequency == 1:
            risk_score += 0.15  # Only 1 purchase
        elif purchase_frequency >= 4:
            risk_score -= 0.15  # Regular buyer (reduce risk)
        
        # Value factor (20% weight)
        if lifetime_value < 100:
            risk_score += 0.1  # Low spender
        elif lifetime_value > 5000:
            risk_score -= 0.2  # High value customer (reduce risk)
        
        # Account age factor (10% weight)
        if account_age < 30:
            risk_score -= 0.1  # New customer (reduce risk)
        elif account_age > 365:
            risk_score -= 0.05  # Long-term customer (reduce risk)
        
        return max(0.0, min(risk_score, 1.0))  # Clamp to 0-1
    
    def _calculate_purchase_trend(self, orders: List) -> str:
        """
        Calculate purchase trend: INCREASING, DECREASING, STABLE
        """
        if len(orders) < 2:
            return "STABLE"
        
        # Get orders from last 180 days
        six_months_ago = datetime.now() - timedelta(days=180)
        recent_orders = [o for o in orders if o.created_at > six_months_ago]
        
        if len(recent_orders) < 2:
            return "STABLE"
        
        # Calculate trend
        recent_orders.sort(key=lambda x: x.created_at)
        
        # Split into two halves
        mid = len(recent_orders) // 2
        first_half = recent_orders[:mid]
        second_half = recent_orders[mid:]
        
        avg_first = sum(float(o.total) for o in first_half) / len(first_half)
        avg_second = sum(float(o.total) for o in second_half) / len(second_half)
        
        # Calculate percentage change
        pct_change = ((avg_second - avg_first) / avg_first) * 100 if avg_first > 0 else 0
        
        if pct_change > 20:
            return "INCREASING"
        elif pct_change < -20:
            return "DECREASING"
        else:
            return "STABLE"
    
    async def segment_customer(self, user_id: UUID) -> str:
        """
        Segment customer into one of: HIGH_VALUE, REGULAR, AT_RISK, NEW, VIP
        """
        try:
            metrics = await self.calculate_customer_metrics(user_id)
            
            if not metrics:
                return "UNKNOWN"
            
            lifetime_value = float(metrics.get("lifetime_value", 0))
            purchase_frequency = metrics.get("purchase_frequency_90d", 0)
            avg_order_value = float(metrics.get("average_order_value", 0))
            days_since_purchase = metrics.get("days_since_last_purchase", 0)
            account_age = metrics.get("account_age_days", 0)
            purchase_trend = metrics.get("purchase_trend", "STABLE")
            
            # VIP: High value + frequent + recent + increasing trend
            if (lifetime_value > 10000 and
                purchase_frequency >= 5 and
                days_since_purchase < 30 and
                purchase_trend == "INCREASING"):
                return "VIP"
            
            # HIGH_VALUE: Significant spend, consistent purchases
            if (lifetime_value > 5000 and
                purchase_frequency >= 3 and
                days_since_purchase < 60):
                return "HIGH_VALUE"
            
            # REGULAR: Moderate spend, occasional purchases
            if (lifetime_value > 500 and
                purchase_frequency >= 1 and
                days_since_purchase < 90):
                return "REGULAR"
            
            # AT_RISK: Was customer but inactive OR low engagement
            if ((lifetime_value > 100 and days_since_purchase > 90 and days_since_purchase < 180) or
                (days_since_purchase > 180 and account_age < 365)):
                return "AT_RISK"
            
            # NEW: Recent account (< 30 days)
            if account_age <= 30:
                return "NEW"
            
            # Default to AT_RISK if inactive for too long
            if days_since_purchase > 180:
                return "AT_RISK"
            
            return "REGULAR"
            
        except Exception as e:
            logger.error(f"Error segmenting customer: {str(e)}")
            return "UNKNOWN"
    
    async def update_customer_segment(self, user_id: UUID):
        """Update customer segment in database"""
        try:
            from app.database.ecommerce_extension_model import CustomerSegment
            from app.database.user_model import User
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return
            
            # Get metrics and segment
            metrics = await self.calculate_customer_metrics(user_id)
            segment_type = await self.segment_customer(user_id)
            churn_risk = metrics.get("churn_risk", 0.5)
            
            # Check if segment exists
            existing_segment = self.db.query(CustomerSegment).filter(
                CustomerSegment.user_id == user_id
            ).first()
            
            segment_data = {
                "segment_type": segment_type,
                "lifetime_value": metrics.get("lifetime_value", Decimal(0)),
                "purchase_frequency": metrics.get("purchase_count", 0),
                "average_order_value": metrics.get("average_order_value", Decimal(0)),
                "last_purchase_date": None,
                "churn_risk": churn_risk,
                "updated_at": datetime.now()
            }
            
            if existing_segment:
                for key, value in segment_data.items():
                    setattr(existing_segment, key, value)
            else:
                new_segment = CustomerSegment(
                    user_id=user_id,
                    **segment_data
                )
                self.db.add(new_segment)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating customer segment: {str(e)}")
            self.db.rollback()
    
    async def bulk_segment_update(self) -> dict:
        """
        Update segments for all users
        Typically run as a scheduled job (daily)
        """
        try:
            from app.database.user_model import User
            
            users = self.db.query(User).all()
            
            updated_count = 0
            for user in users:
                try:
                    await self.update_customer_segment(user.id)
                    updated_count += 1
                except Exception as e:
                    logger.error(f"Error updating user {user.id}: {str(e)}")
                    continue
            
            logger.info(f"Updated segments for {updated_count} users")
            return {
                "status": "success",
                "updated_count": updated_count,
                "total_users": len(users)
            }
            
        except Exception as e:
            logger.error(f"Error in bulk segment update: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_segment_analytics(self, segment_type: Optional[str] = None) -> dict:
        """
        Get analytics for a segment or all segments
        """
        try:
            from app.database.ecommerce_extension_model import CustomerSegment
            
            query = self.db.query(CustomerSegment)
            
            if segment_type:
                query = query.filter(CustomerSegment.segment_type == segment_type)
            
            segments = query.all()
            
            if not segments:
                return {}
            
            # Group by segment type
            by_segment = {}
            for segment in segments:
                seg_type = segment.segment_type
                if seg_type not in by_segment:
                    by_segment[seg_type] = []
                by_segment[seg_type].append(segment)
            
            # Calculate analytics per segment
            analytics = {}
            for seg_type, seg_list in by_segment.items():
                analytics[seg_type] = {
                    "count": len(seg_list),
                    "avg_lifetime_value": sum(
                        float(s.lifetime_value) for s in seg_list
                    ) / len(seg_list),
                    "total_lifetime_value": sum(
                        float(s.lifetime_value) for s in seg_list
                    ),
                    "avg_churn_risk": sum(s.churn_risk for s in seg_list) / len(seg_list),
                    "high_risk_count": len([s for s in seg_list if s.churn_risk > 0.7])
                }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting segment analytics: {str(e)}")
            return {}
    
    async def get_at_risk_customers(self) -> List[dict]:
        """Get list of at-risk customers for re-engagement"""
        try:
            from app.database.ecommerce_extension_model import CustomerSegment
            from app.database.user_model import User
            
            at_risk = self.db.query(
                CustomerSegment
            ).filter(
                and_(
                    CustomerSegment.segment_type == "AT_RISK",
                    CustomerSegment.churn_risk > 0.6
                )
            ).order_by(
                desc(CustomerSegment.churn_risk)
            ).limit(100).all()
            
            return [
                {
                    "user_id": str(segment.user_id),
                    "segment_type": segment.segment_type,
                    "lifetime_value": float(segment.lifetime_value),
                    "churn_risk": segment.churn_risk,
                    "last_purchase_date": segment.last_purchase_date
                }
                for segment in at_risk
            ]
            
        except Exception as e:
            logger.error(f"Error getting at-risk customers: {str(e)}")
            return []
    
    async def get_vip_customers(self) -> List[dict]:
        """Get list of VIP customers for special treatment"""
        try:
            from app.database.ecommerce_extension_model import CustomerSegment
            
            vip = self.db.query(
                CustomerSegment
            ).filter(
                CustomerSegment.segment_type == "VIP"
            ).order_by(
                desc(CustomerSegment.lifetime_value)
            ).limit(50).all()
            
            return [
                {
                    "user_id": str(segment.user_id),
                    "segment_type": segment.segment_type,
                    "lifetime_value": float(segment.lifetime_value),
                    "purchase_frequency": segment.purchase_frequency,
                    "average_order_value": float(segment.average_order_value)
                }
                for segment in vip
            ]
            
        except Exception as e:
            logger.error(f"Error getting VIP customers: {str(e)}")
            return []

"""
AI Product Recommendations Service
Implements collaborative filtering, content-based, and popularity-based recommendations
"""

from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
import numpy as np
from math import sqrt
import logging

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Product recommendation engine using multiple algorithms:
    1. Collaborative Filtering (user-based)
    2. Content-Based (product attributes)
    3. Popularity-based (trending products)
    4. Frequently Bought Together
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_recommendations(
        self,
        user_id: UUID,
        limit: int = 10,
        exclude_purchased: bool = True
    ) -> List[dict]:
        """
        Get personalized recommendations for user
        Combines multiple algorithms with weighted scores
        """
        try:
            recommendations = []
            
            # 1. Get collaborative filtering recommendations (40% weight)
            collab_recs = await self._collaborative_filtering(user_id, limit * 2)
            recommendations.extend([
                {**rec, "algorithm": "collaborative", "weight": 0.4}
                for rec in collab_recs
            ])
            
            # 2. Get content-based recommendations (30% weight)
            content_recs = await self._content_based_recommendations(user_id, limit * 2)
            recommendations.extend([
                {**rec, "algorithm": "content", "weight": 0.3}
                for rec in content_recs
            ])
            
            # 3. Get frequently bought together (20% weight)
            bought_together = await self._frequently_bought_together(user_id, limit)
            recommendations.extend([
                {**rec, "algorithm": "bought_together", "weight": 0.2}
                for rec in bought_together
            ])
            
            # 4. Get trending products (10% weight)
            trending = await self._trending_products(limit)
            recommendations.extend([
                {**rec, "algorithm": "trending", "weight": 0.1}
                for rec in trending
            ])
            
            # Exclude already purchased products
            if exclude_purchased:
                purchased_ids = await self._get_user_purchased_products(user_id)
                recommendations = [
                    r for r in recommendations
                    if r["product_id"] not in purchased_ids
                ]
            
            # Aggregate scores for duplicate products
            final_recs = await self._aggregate_scores(recommendations)
            
            # Sort by final score and return top N
            final_recs.sort(key=lambda x: x["final_score"], reverse=True)
            
            return final_recs[:limit]
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []
    
    async def _collaborative_filtering(self, user_id: UUID, limit: int) -> List[dict]:
        """
        User-based collaborative filtering
        Find similar users and recommend their purchases
        """
        try:
            from app.database.user_model import User
            from app.database.order_model import Order, OrderItem
            from app.database.models import Product
            
            # Get current user's purchase history
            user_purchases = self.db.query(OrderItem).join(
                Order, Order.id == OrderItem.order_id
            ).filter(
                Order.user_id == user_id,
                Order.status == "COMPLETED"
            ).all()
            
            user_product_ids = {item.product_id for item in user_purchases}
            
            if not user_product_ids:
                return []
            
            # Find similar users (who bought similar products)
            similar_users = self.db.query(
                User.id,
                func.count(OrderItem.id).label("common_products")
            ).join(
                Order, Order.user_id == User.id
            ).join(
                OrderItem, OrderItem.order_id == Order.id
            ).filter(
                User.id != user_id,
                Order.status == "COMPLETED",
                OrderItem.product_id.in_(user_product_ids)
            ).group_by(
                User.id
            ).order_by(
                desc("common_products")
            ).limit(5).all()
            
            if not similar_users:
                return []
            
            similar_user_ids = [u[0] for u in similar_users]
            
            # Get products purchased by similar users but not by current user
            recommendations = self.db.query(
                Product.id,
                Product.name,
                Product.price,
                Product.image_url,
                func.count(OrderItem.id).label("purchase_count")
            ).join(
                OrderItem, OrderItem.product_id == Product.id
            ).join(
                Order, Order.id == OrderItem.order_id
            ).filter(
                Order.user_id.in_(similar_user_ids),
                Order.status == "COMPLETED",
                Product.id.notin_(user_product_ids)
            ).group_by(
                Product.id,
                Product.name,
                Product.price,
                Product.image_url
            ).order_by(
                desc("purchase_count")
            ).limit(limit).all()
            
            return [
                {
                    "product_id": rec[0],
                    "name": rec[1],
                    "price": float(rec[2]),
                    "image_url": rec[3],
                    "score": min(rec[4] / 10, 1.0)  # Normalize to 0-1
                }
                for rec in recommendations
            ]
            
        except Exception as e:
            logger.error(f"Collaborative filtering error: {str(e)}")
            return []
    
    async def _content_based_recommendations(self, user_id: UUID, limit: int) -> List[dict]:
        """
        Content-based recommendations
        Find products similar to user's view history
        """
        try:
            from app.database.models import Product
            from app.database.ecommerce_extension_model import ProductViewHistory
            
            # Get user's view history
            viewed_products = self.db.query(
                ProductViewHistory.product_id,
                Product.category_id,
                Product.price
            ).join(
                Product, Product.id == ProductViewHistory.product_id
            ).filter(
                ProductViewHistory.user_id == user_id,
                ProductViewHistory.last_viewed_at > datetime.now() - timedelta(days=30)
            ).order_by(
                desc(ProductViewHistory.view_count)
            ).limit(10).all()
            
            if not viewed_products:
                return []
            
            # Extract category and price range preferences
            viewed_categories = [p[1] for p in viewed_products if p[1]]
            viewed_prices = [float(p[2]) for p in viewed_products if p[2]]
            
            if viewed_prices:
                avg_price = sum(viewed_prices) / len(viewed_prices)
                price_range = (avg_price * 0.5, avg_price * 1.5)
            else:
                price_range = (0, 100000)
            
            # Get products in similar categories and price range
            recommendations = self.db.query(
                Product.id,
                Product.name,
                Product.price,
                Product.image_url,
                func.avg(OrderItem.quantity).label("avg_quantity")
            ).join(
                OrderItem, OrderItem.product_id == Product.id, isouter=True
            ).filter(
                Product.category_id.in_(viewed_categories) if viewed_categories else True,
                Product.price.between(price_range[0], price_range[1]),
                Product.id.notin_([p[0] for p in viewed_products])
            ).group_by(
                Product.id,
                Product.name,
                Product.price,
                Product.image_url
            ).order_by(
                desc(func.avg(OrderItem.quantity))
            ).limit(limit).all()
            
            return [
                {
                    "product_id": rec[0],
                    "name": rec[1],
                    "price": float(rec[2]),
                    "image_url": rec[3],
                    "score": 0.8  # High confidence for category/price match
                }
                for rec in recommendations
            ]
            
        except Exception as e:
            logger.error(f"Content-based recommendation error: {str(e)}")
            return []
    
    async def _frequently_bought_together(self, user_id: UUID, limit: int) -> List[dict]:
        """
        Frequently bought together
        Find products commonly purchased with user's past purchases
        """
        try:
            from app.database.models import Product
            from app.database.order_model import Order, OrderItem
            
            # Get user's purchase history
            user_purchase_ids = self.db.query(
                OrderItem.product_id
            ).join(
                Order, Order.id == OrderItem.order_id
            ).filter(
                Order.user_id == user_id,
                Order.status == "COMPLETED"
            ).all()
            
            user_product_ids = [p[0] for p in user_purchase_ids]
            
            if not user_product_ids:
                return []
            
            # Find products frequently bought with user's products
            recommendations = self.db.query(
                Product.id,
                Product.name,
                Product.price,
                Product.image_url,
                func.count(OrderItem.id).label("co_purchase_count")
            ).join(
                OrderItem, OrderItem.product_id == Product.id
            ).join(
                Order, Order.id == OrderItem.order_id
            ).filter(
                OrderItem.product_id.notin_(user_product_ids),
                Order.id.in_(
                    self.db.query(Order.id).join(
                        OrderItem, OrderItem.order_id == Order.id
                    ).filter(
                        OrderItem.product_id.in_(user_product_ids)
                    )
                )
            ).group_by(
                Product.id,
                Product.name,
                Product.price,
                Product.image_url
            ).order_by(
                desc("co_purchase_count")
            ).limit(limit).all()
            
            return [
                {
                    "product_id": rec[0],
                    "name": rec[1],
                    "price": float(rec[2]),
                    "image_url": rec[3],
                    "score": min(rec[4] / 5, 1.0)  # Normalize
                }
                for rec in recommendations
            ]
            
        except Exception as e:
            logger.error(f"Frequently bought together error: {str(e)}")
            return []
    
    async def _trending_products(self, limit: int) -> List[dict]:
        """
        Trending products
        Most viewed/purchased in last 7 days
        """
        try:
            from app.database.models import Product
            from app.database.ecommerce_extension_model import ProductViewHistory
            
            seven_days_ago = datetime.now() - timedelta(days=7)
            
            recommendations = self.db.query(
                Product.id,
                Product.name,
                Product.price,
                Product.image_url,
                func.sum(ProductViewHistory.view_count).label("total_views")
            ).join(
                ProductViewHistory, ProductViewHistory.product_id == Product.id
            ).filter(
                ProductViewHistory.last_viewed_at > seven_days_ago
            ).group_by(
                Product.id,
                Product.name,
                Product.price,
                Product.image_url
            ).order_by(
                desc("total_views")
            ).limit(limit).all()
            
            return [
                {
                    "product_id": rec[0],
                    "name": rec[1],
                    "price": float(rec[2]),
                    "image_url": rec[3],
                    "score": 0.7  # Moderate confidence for trending
                }
                for rec in recommendations
            ]
            
        except Exception as e:
            logger.error(f"Trending products error: {str(e)}")
            return []
    
    async def _get_user_purchased_products(self, user_id: UUID) -> set:
        """Get set of products already purchased by user"""
        try:
            from app.database.order_model import Order, OrderItem
            
            purchased = self.db.query(
                OrderItem.product_id
            ).join(
                Order, Order.id == OrderItem.order_id
            ).filter(
                Order.user_id == user_id,
                Order.status == "COMPLETED"
            ).all()
            
            return {p[0] for p in purchased}
        except Exception as e:
            logger.error(f"Error getting purchased products: {str(e)}")
            return set()
    
    async def _aggregate_scores(self, recommendations: List[dict]) -> List[dict]:
        """
        Aggregate scores for duplicate products
        Final score = weighted average of all algorithm scores
        """
        product_scores = {}
        
        for rec in recommendations:
            product_id = rec["product_id"]
            
            if product_id not in product_scores:
                product_scores[product_id] = {
                    "product_id": product_id,
                    "name": rec["name"],
                    "price": rec["price"],
                    "image_url": rec["image_url"],
                    "scores": [],
                    "algorithms": []
                }
            
            product_scores[product_id]["scores"].append(
                rec["score"] * rec["weight"]
            )
            product_scores[product_id]["algorithms"].append(rec["algorithm"])
        
        # Calculate final scores
        final_recs = []
        for product_id, data in product_scores.items():
            final_score = sum(data["scores"])  # Already weighted
            final_recs.append({
                "product_id": data["product_id"],
                "name": data["name"],
                "price": data["price"],
                "image_url": data["image_url"],
                "final_score": final_score,
                "algorithms_used": list(set(data["algorithms"])),
                "confidence": final_score
            })
        
        return final_recs
    
    async def track_view(self, user_id: UUID, product_id: UUID):
        """Track product view for recommendations"""
        try:
            from app.database.ecommerce_extension_model import ProductViewHistory
            from app.database.models import Product
            
            # Check if product exists
            product = self.db.query(Product).filter(
                Product.id == product_id
            ).first()
            
            if not product:
                return
            
            # Check if view already exists
            existing_view = self.db.query(ProductViewHistory).filter(
                and_(
                    ProductViewHistory.user_id == user_id,
                    ProductViewHistory.product_id == product_id
                )
            ).first()
            
            if existing_view:
                # Update existing view
                existing_view.view_count += 1
                existing_view.last_viewed_at = datetime.now()
            else:
                # Create new view
                new_view = ProductViewHistory(
                    user_id=user_id,
                    product_id=product_id,
                    view_count=1,
                    last_viewed_at=datetime.now(),
                    time_spent_seconds=0
                )
                self.db.add(new_view)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error tracking view: {str(e)}")
            self.db.rollback()

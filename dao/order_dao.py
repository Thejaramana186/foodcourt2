from db import db
from models.order import Order, OrderItem
from models.restaurant import Restaurant
from models.user import User
from sqlalchemy import and_, func, desc
from datetime import datetime, timedelta

class OrderDAO:
    def create_order(self, order):
        """Create a new order"""
        try:
            db.session.add(order)
            db.session.commit()
            return order.id
        except Exception as e:
            db.session.rollback()
            print(f"Error creating order: {e}")
            return None

    def get_order_by_id(self, order_id):
        """Fetch order by ID"""
        try:
            return db.session.get(Order, order_id)  # ✅ SQLAlchemy 2.0 compatible
        except Exception as e:
            print(f"Error fetching order by id {order_id}: {e}")
            return None

    def update_order(self, order):
        """Update an existing order"""
        try:
            db.session.commit()
            return order
        except Exception as e:
            db.session.rollback()
            print(f"Error updating order: {e}")
            return None

    def get_orders_by_user(self, user_id, page=1, per_page=10, status_filter=""):
        """Get all orders placed by a user"""
        query = Order.query.filter_by(customer_id=user_id)
        if status_filter:
            query = query.filter_by(status=status_filter)

        query = query.order_by(desc(Order.created_at))

        try:
            return query.paginate(page=page, per_page=per_page, error_out=False)
        except Exception as e:
            print(f"Error fetching orders: {e}")

            class EmptyPagination:
                def __init__(self):
                    self.items = []
                    self.total = 0
                    self.pages = 0
                    self.page = page
                    self.per_page = per_page
                    self.has_prev = False
                    self.has_next = False
                    self.prev_num = None
                    self.next_num = None

                def iter_pages(self):
                    return []

            return EmptyPagination()

    def get_orders_by_restaurant(self, restaurant_id, page=1, per_page=10, status_filter=""):
        """Get all orders for a single restaurant"""
        query = Order.query.filter_by(restaurant_id=restaurant_id)
        if status_filter:
            query = query.filter_by(status=status_filter)
        return query.order_by(desc(Order.created_at)).paginate(page=page, per_page=per_page, error_out=False)

    def get_orders_by_restaurants(self, restaurant_ids, page=1, per_page=15, status_filter=""):
        """Get orders for multiple restaurants"""
        query = Order.query.filter(Order.restaurant_id.in_(restaurant_ids))
        if status_filter:
            query = query.filter_by(status=status_filter)
        return query.order_by(desc(Order.created_at)).paginate(page=page, per_page=per_page, error_out=False)

    def get_orders_by_delivery_person(self, delivery_person_id, page=1, per_page=10, status_filter=""):
        """Get all orders assigned to a delivery person"""
        query = Order.query.filter_by(delivery_person_id=delivery_person_id)

        if status_filter == "assigned":
            query = query.filter(Order.status.in_(["out_for_delivery"]))
        elif status_filter:
            query = query.filter_by(status=status_filter)

        return query.order_by(desc(Order.created_at)).paginate(page=page, per_page=per_page, error_out=False)

    def get_available_orders_for_delivery(self, page=1, per_page=15):
        query = Order.query.filter(
        and_(
            func.lower(Order.status) == 'ready_for_pickup',
            Order.delivery_person_id.is_(None)
        )
    )
        return query.order_by(Order.created_at).paginate(
        page=page, per_page=per_page, error_out=False
    )
    def get_all_orders(self, page=1, per_page=20, status_filter=""):
        """Get all orders in the system"""
        query = Order.query
        if status_filter:
            query = query.filter_by(status=status_filter)
        return query.order_by(desc(Order.created_at)).paginate(page=page, per_page=per_page, error_out=False)

    def get_user_statistics(self, user_id):
        """Get stats for a customer"""
        orders = Order.query.filter_by(customer_id=user_id).all()
        total_orders = len(orders)
        total_spent = sum(order.total_amount for order in orders if order.status == "delivered")
        favorite_cuisine = None

        if orders:
            cuisine_counts = {}
            for order in orders:
                cuisine = order.restaurant.cuisine
                cuisine_counts[cuisine] = cuisine_counts.get(cuisine, 0) + 1
            if cuisine_counts:
                favorite_cuisine = max(cuisine_counts, key=cuisine_counts.get)

        return {"total_orders": total_orders, "total_spent": total_spent, "favorite_cuisine": favorite_cuisine}

    def get_restaurant_statistics(self, restaurant_id):
        """Get stats for a restaurant"""
        orders = Order.query.filter_by(restaurant_id=restaurant_id).all()
        total_orders = len(orders)
        total_revenue = sum(order.total_amount for order in orders if order.status == "delivered")
        pending_orders = len([o for o in orders if o.status in ["pending", "confirmed", "preparing"]])
        return {"total_orders": total_orders, "total_revenue": total_revenue, "pending_orders": pending_orders}

    def get_delivery_person_statistics(self, delivery_person_id):
        """Get stats for a delivery person"""
        orders = Order.query.filter_by(delivery_person_id=delivery_person_id).all()
        total_deliveries = len([o for o in orders if o.status == "delivered"])
        pending_deliveries = len([o for o in orders if o.status == "out_for_delivery"])
        return {
            "total_deliveries": total_deliveries,
            "pending_deliveries": pending_deliveries,
            "success_rate": (total_deliveries / len(orders) * 100) if orders else 0,
        }

    def get_total_order_count(self):
        """Get total number of orders"""
        return Order.query.count()

    def get_total_revenue(self):
        """Get total revenue from delivered orders"""
        result = db.session.query(func.sum(Order.total_amount)).filter_by(status="delivered").scalar()
        return result or 0

    def get_recent_orders(self, limit=10):
        """Get most recent orders"""
        return Order.query.order_by(desc(Order.created_at)).limit(limit).all()

    def get_daily_statistics(self, date):
        """Get orders & revenue for a specific day"""
        start_date = datetime.combine(date, datetime.min.time())
        end_date = start_date + timedelta(days=1)

        orders = Order.query.filter(and_(Order.created_at >= start_date, Order.created_at < end_date)).all()
        revenue = sum(order.total_amount for order in orders if order.status == "delivered")

        return {"orders": len(orders), "revenue": revenue}

    def get_delivery_earnings(self, delivery_person_id):
        """Get earnings for a delivery person"""
        delivered_orders = Order.query.filter_by(delivery_person_id=delivery_person_id, status="delivered").all()
        total_earnings = sum(order.total_amount * 0.1 for order in delivered_orders)  # 10% commission
        return {
            "total_earnings": total_earnings,
            "total_deliveries": len(delivered_orders),
            "recent_deliveries": delivered_orders[-10:],  # last 10 deliveries
        }

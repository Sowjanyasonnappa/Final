# StreamSentinel Shopping Backend

## Run locally

1. Start PostgreSQL and create a database named `shopping_db`.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Start the API:
   - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

## Main endpoints

- Auth: `/auth/register`, `/auth/login`
- Products: `/products/`
- Cart: `/cart/`
- Orders: `/orders/checkout`
- Wishlist: `/wishlist/`
- Categories: `/categories/`
- Coupons: `/coupons/`
- Admin: `/admin/dashboard`
- Search: `/search/`

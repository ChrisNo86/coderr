# Coderr Backend

REST API for **Coderr**, a freelancer marketplace where business users offer
services in three tiers (basic, standard, premium) and customers order and
review them. Built with Django and Django REST framework. The matching vanilla
JavaScript frontend is provided separately by the Developer Akademie and is
**not** part of this repository.

## Features

- Registration and login with username and password (token authentication)
- Two user types: `customer` and `business`, each with an editable profile
  incl. profile picture
- Offers with exactly three details, filtering, search, ordering and
  pagination
- Orders created from an offer detail, status handling by the business user
- Reviews (one per customer and business user)
- Platform statistics for the landing page
- Django admin for all models

## Requirements

- Python 3.10 or newer
- pip

## Getting started

```bash
# 1. Clone the repository
git clone https://github.com/ChrisNo86/coderr.git
cd coderr

# 2. Create and activate a virtual environment
python -m venv env
# Windows
env\Scripts\activate
# macOS / Linux
source env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create the database
python manage.py migrate

# 5. Create the guest accounts used by the frontend's guest login buttons
python manage.py create_guest_users

# 6. (Optional) Create an admin account for http://127.0.0.1:8000/admin/
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/api/`.

### Connecting the frontend

The frontend expects the API at `http://127.0.0.1:8000/api/` and loads
uploaded images from `http://127.0.0.1:8000/` (see
`shared/scripts/config.js` in the frontend project). Start the frontend with
the VS Code **Live Server** extension (port 5500). CORS is enabled for
`http://127.0.0.1:5500` and `http://localhost:5500` in `core/settings.py`;
add your origin there if you use a different port.

### Guest accounts

`python manage.py create_guest_users` creates the two accounts configured in
the frontend:

| Type | Username | Password |
|---|---|---|
| customer | `andrey` | `asdasd` |
| business | `kevin` | `asdasd24` |

These are demo credentials for local development only.

## Project structure

```
core/            Project settings and central URL routing
auth_app/        Registration, login, create_guest_users command
profile_app/     UserProfile model, profile endpoints, user type permissions
offers_app/      Offers and offer details (filters, pagination)
orders_app/      Orders and order counts
reviews_app/     Reviews
base_info_app/   Platform statistics
```

Every app keeps its API code (serializers, views, urls, permissions) in an
`api/` package.

## API overview

All endpoints except registration, login, the offer list and base info
require the header `Authorization: Token <token>`.

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/api/registration/` | Register customer or business user | open |
| POST | `/api/login/` | Log in, returns token | open |
| GET | `/api/profile/{pk}/` | Profile of a user | authenticated |
| PATCH | `/api/profile/{pk}/` | Update profile (multipart for `file`) | profile owner |
| GET | `/api/profiles/business/` | All business profiles | authenticated |
| GET | `/api/profiles/customer/` | All customer profiles | authenticated |
| GET | `/api/offers/` | Paginated offer list with filters | open |
| POST | `/api/offers/` | Create offer with three details | business user |
| GET | `/api/offers/{id}/` | Single offer | authenticated |
| PATCH | `/api/offers/{id}/` | Update offer / details by `offer_type` | offer creator |
| DELETE | `/api/offers/{id}/` | Delete offer | offer creator |
| GET | `/api/offerdetails/{id}/` | Single offer detail | authenticated |
| GET | `/api/orders/` | Orders of the user (customer or business) | authenticated |
| POST | `/api/orders/` | Order an offer detail | customer user |
| PATCH | `/api/orders/{id}/` | Update order status | business user of the order |
| GET | `/api/order-count/{business_user_id}/` | Orders `in_progress` | authenticated |
| GET | `/api/completed-order-count/{business_user_id}/` | Orders `completed` | authenticated |
| GET | `/api/reviews/` | Reviews (filter + ordering) | authenticated |
| POST | `/api/reviews/` | Create review | customer user |
| PATCH | `/api/reviews/{id}/` | Update rating / description | review creator |
| DELETE | `/api/reviews/{id}/` | Delete review | review creator |
| GET | `/api/base-info/` | Platform statistics | open |

### Query parameters

- `/api/offers/`: `creator_id`, `min_price`, `max_delivery_time`, `search`
  (title, description), `ordering` (`updated_at`, `min_price`, prefix `-`
  for descending), `page`, `page_size` (default 6). Empty parameters are
  ignored, invalid values return `400`.
- `/api/reviews/`: `business_user_id`, `reviewer_id`, `ordering`
  (`updated_at`, `rating`).

## Special notes

- **Profiles** are created automatically on registration. Text fields
  (`first_name`, `last_name`, `location`, `tel`, `description`,
  `working_hours`) are never `null` but an empty string. `first_name`,
  `last_name` and `email` are stored on Django's `User` model.
- **Offer details:** `revisions = -1` means unlimited revisions,
  `delivery_time_in_days` must be at least 1, `price` accepts numbers and
  numeric strings. On PATCH a detail is identified by its `offer_type`; its
  id stays the same.
- **Offer detail URLs:** the offer list returns relative paths
  (`/offerdetails/{id}/`), the single offer returns absolute URLs, as shown
  in the API documentation.
- **Orders** copy title, price, features etc. from the offer detail at the
  time of ordering, so later changes to the offer do not change existing
  orders. Only `status` can be updated (`in_progress`, `completed`,
  `cancelled`); any other field returns `400`.
- **Reviews:** a customer can review each business user only once; a second
  review returns `400`. Only `rating` (1–5) and `description` can be changed,
  other fields are ignored on PATCH.
- **Media:** uploaded files are stored in `media/` (not part of the
  repository) and served by Django while `DEBUG` is `True`.
- **Secret key / debug:** for local development defaults are used. For any
  deployment set the environment variables `DJANGO_SECRET_KEY` and
  `DJANGO_DEBUG=False`.
- The SQLite database is **not** part of the repository; run
  `python manage.py migrate` after cloning.

## Running the tests

```bash
python manage.py test
```

With coverage report:

```bash
pip install coverage
coverage run --source=. --omit="*/migrations/*,*/tests/*,manage.py" manage.py test
coverage report
```

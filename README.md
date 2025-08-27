# Django POS - Extended
Features added:
- Barcode input on New Sale (works with keyboard barcode scanners)
- Item-level discounts, sale-level discount and tax percent
- REST API (DRF) for products/customers/sales/payments
- Sales report page (date filter)
- User permission enforcement for create/edit/delete on products/customers
- Print-friendly receipt

After pulling code:
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

import logging
from flask import Flask, request

from . import odoo
from . import settings


_logger = logging.getLogger(__name__)


def create_app():
    ODOO_PARAMETERS = {
        'user': settings.USER,
        'password': settings.PASSWORD,
        'host': settings.HOST,
        'port': settings.PORT,
        'database': settings.DATABASE
    }
    api = odoo.JsonApi(**ODOO_PARAMETERS)
    api._authenticate()

    app = Flask(__name__)

    @app.route("/")
    def home():
        return "Welcome"

    @app.route("/create_order", methods=["POST"])
    def create_order():
        item_id = request.json['item_id']
        customer_name = request.json['customer_name']
        quantity = request.json['qty']

        customer = api.process('res.partner', 'search_read', ([['display_name', '=', customer_name]]))
        if not customer['result']:
            return "Customer Doesn't Exist"

        customer_id = customer['result'][0]['id']

        final_product = api.process('product.product', 'search_read', ([['id', '=', item_id]]))
        if not final_product:
            return "Product with that Item ID doesn't Exist"

        final_product_id = final_product['result'][0]['id']

        order_line_vals = {
            'product_id': final_product_id,
            'product_uom_qty': int(quantity)
        }

        order_vals = {
            'partner_id': customer_id,
            'order_line': [(0, 0, order_line_vals)]
        }

        order = api.process('sale.order', 'create', [order_vals])

        return order

    @app.route("/confirm_order", methods=["POST"])
    def confirm_order():
        order_id = request.json['order_id']

        confirm = api.process('sale.order', 'action_confirm', [order_id])
        return 'The Order is confirmed'

    return app

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

        # Get customer, if not present create the customer
        customer = api.process('res.partner', 'search_read', (([['display_name', '=', customer_name]]),))
        if not customer['result']:
            customer = api.process('res.partner', 'create', [{'name': 'Bob'}])
            customer_id = customer['result'][0]
        else:
            customer_id = customer['result'][0]['id']

        final_product = api.process('product.product', 'search_read', (([['id', '=', item_id]]),))
        if not final_product:
            return "Product with that Item ID doesn't Exist, get the correct item id of the product"

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
        serial_no = request.json['serial']
        is_confirmed = api.process('sale.order', 'action_confirm', [order_id])

        if is_confirmed['result'] is not True:
            return 'There was an error confirming the order, kindly contact customer care'

        lot = api.process('stock.production.lot', 'search_read', ([(['name', '=', serial_no])],))
        if not lot['result']:
            return "Invalid Serial No", 500

        lot_id = lot['result'][0]['id']

        order = api.process('sale.order', 'search_read', [[['id', '=', order_id]]])
        picking_id = order['result'][0]['picking_ids']
        picking = api.process('stock.picking', 'search_read', [[['id', '=', picking_id]]])
        move_id = picking['result'][0]['move_line_ids']
        move = api.process('stock.move.line', 'search_read', [[['id', '=', move_id]]])
        product_qty = move['result'][0]['product_qty']
        api.process('stock.move.line', 'write', [move_id, {'lot_id': lot_id, 'qty_done': product_qty}])

        is_picking_validated = api.process('stock.picking', 'button_validate', (picking_id,))

        return 'The Order is confirmed'

    return app

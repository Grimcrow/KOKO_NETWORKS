from odoo import models, fields, api, _


class KokoMrp(models.Model):
    _name = 'koko.mrp.products'

    product_id = fields.Many2one('product.product')
    used_products = fields.One2many('koko.mrp.products.used', 'koko_mrp_products_id')

    @api.multi
    def create_log(self, mrp_id):
        mrp = self.env['mrp.production'].search([('id', '=', mrp_id)])
        move_line_ids = mrp.finished_move_line_ids

        line_vals = []

        for move_line_id in move_line_ids:
            vals = (0, 0, {
                'product_id': move_line_id.product_id.id,
                'lot_id': move_line_id.lot_id.id
            })

            line_vals.append(vals)

        mrp_vals = {
            'product_id': mrp.product_id.id,
            'used_products':  line_vals
        }
        super(KokoMrp, self).create(mrp_vals)


class KokoMrpLines(models.Model):
    _name = 'koko.mrp.products.used'

    koko_mrp_products_id = fields.Many2one('koko.mrp.products')
    product_id = fields.Many2one('product.product')
    lot_id = fields.Many2one('stock.production.lot')


class CustomMrp(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def button_mark_done(self):
        res = super(CustomMrp, self).button_mark_done()
        self.env['koko.mrp.products'].create_log(self.id)
        return res

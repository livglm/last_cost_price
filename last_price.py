# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 ISA s.r.l. (<http://www.isa.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, workflow, _, exceptions
import openerp.addons.decimal_precision as dp


class product_last_price(models.Model):

    _inherit = 'product.product'
    _description = "Product extension for last price"

    last_purchase_price = fields.Float(compute = '_last_purchase_price', store=True,
        digits_compute=dp.get_precision('Product Price'))

    @api.one
    @api.depends('standard_price')
    def _last_purchase_price(self):

        print "qqqq"
        if self._context.get('shop', False):
            self.env.cr.execute('select warehouse_id from sale_shop where id=%s', (int(self._ccontext['shop']),))
            res2 = self.env.cr.fetchone()
            if res2:
                self._ccontext['warehouse'] = res2[0]

        if self._ccontext.get('warehouse', False):
            self.env.cr.execute('select lot_stock_id from stock_warehouse where id=%s', (int(self._ccontext['warehouse']),))
            res2 = self.env.cr.fetchone()
            if res2:
                self._ccontext['location'] = res2[0]

        if self._ccontext.get('location', False):
            if type(self._ccontext['location']) == type(1):
                location_ids = [self._ccontext['location']]
            elif type(self._ccontext['location']) in (type(''), type(u'')):
                location_ids = self.env['stock.location'].search([('name','ilike',self._ccontext['location'])])
            else:
                location_ids = self._ccontext['location']
        else:
            location_ids = []
            wids = self.env['stock.warehouse'].search([])
            for w in self.env['stock.warehouse'].browse(wids):
                location_ids.append(w.lot_stock_id.id)


        where = [tuple(location_ids),tuple(location_ids),tuple(ids)]
        query="""select id,price_unit
            from stock_move
            where location_id NOT IN %s
            and location_dest_id IN %s
            and product_id IN %s
            and state IN ('confirmed', 'done')
            and price_unit is not null
            order by id desc"""
        self.env.cr.execute(query , tuple(where))
        results = self.env.cr.fetchall()
        res={}.fromkeys(self.env.ids, 0.0)
        if results:
            res[ids[0]]=results[0][1]

        self.standard_price = res
        #import pdb; pdb.set_trace()
        print res
        return res


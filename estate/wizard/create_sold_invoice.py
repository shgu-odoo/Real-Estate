from odoo import models,fields,api

class CreateSoldInvoice(models.Model) :
    _name = "create.sold.invoice"
    _description = "Create Sold Invoice"


    partner_id = fields.Many2one('res.partner')

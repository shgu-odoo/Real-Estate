from odoo import models,fields,api

class AddOffer(models.Model) :
    _name = "property.offer.wizard"
    _description = "Property Offer Wizard"

    price = fields.Char()
    partner = fields.Many2one('res.partner')
    status = fields.Selection([('accepted' , 'Accepted') , ('refuse' , 'Refuse')])


    def action_make_offer(self) :
        self.ensure_one()
        Offer = self.env['estate.property.offer']
        activeIds = self.env.context.get('active_ids')
        data = {
            'price' : self.price,
            'partner_id' : self.partner.id,
            'status' : self.status 
        }

        for property in self.env['estate.property.myproperty'].browse(activeIds) :
            data['property_id'] = property.id
            Offer.create(data)
from odoo import models,fields,api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError,ValidationError



class MyProperty(models.Model) :
    _name = 'estate.property.myproperty'
    _description = 'My Property'


    def _get_description(self) :
        if self.env.context.get('is_my_property') :
            return self.env.user.name + "'s property"
            

    name = fields.Char(string = "Property Name",default="Unknown",required=True,filter="1")
    description = fields.Text(default=_get_description)
    postcode = fields.Char()
    date_availability = fields.Date(default = lambda self: fields.Datetime.now(),copy=False)
    expected_price = fields.Float(required=True) 
    selling_price = fields.Float(copy=False,readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([
        ('north' , 'North'),
        ('south' , 'South'),
        ('east' , 'East'),
        ('west' , 'West')
        ])
    active = fields.Boolean(default=True)
    image = fields.Image()
    state = fields.Selection([
        ('new' , 'New'),
        ('sold' , 'Sold'),
        ('cancel' , 'Cancel')], default = 'new')

    date_deadline = fields.Date()

    salesman_id = fields.Many2one('res.users')
    buyer_id = fields.Many2one('res.partner', default=lambda self: self.env.user.partner_id.id)

    property_offer_ids = fields.One2many('estate.property.offer','property_id')


    def action_sold(self) :
            #print("\n\n In Action Sold")   
            # for record in self :
            #     if record.state == 'cancel' :
            #         raise UserError("Cancel Property Cannot be Sold")
            #     record.state = 'sold'
        return self.write({'state' : 'sold'})


    def action_cancel(self) :
        # for record in self :
        #     if record.state =='sold' :
        #         raise UserError("Sold Property Cannot be Canceled")
        #     record.state = 'cancel'
        return self.write({'state' : 'cancel'})

    # Kanban view show all offers click on offer button

    def open_offers(self):
        view_id_all = self.env.ref('estate.estate_property_myproperty_offer_tree').id
        return {
            "name":"Offers",
            "type":"ir.actions.act_window",
            "res_model":"estate.property.myproperty.offer",
            "views":[[view_id_all, 'tree']],
            "target":"new",
            "domain": [('property_id', '=', self.id)]
            }
    
    # Kanban view show all confirm offers click on confirm offer button


    def open_confirm_offers(self):
        view_id_accept = self.env.ref('estate.estate_property_myproperty_offer_tree').id
        return {
            "name":"Offers",
            "type":"ir.actions.act_window",
            "res_model":"estate.property.myproperty.offer",
            "views":[[view_id_accept, 'tree']],
            "domain": [('property_id', '=', self.id),('status','=','accepted')]
            }

class EstatePropertyOffer(models.Model) :
    _name = 'estate.property.myproperty.offer'
    _description = 'Estate Property Offer'
    _order = 'price desc'

    price = fields.Float()
    status = fields.Selection([('accepted' , 'Accepted'),('refused' , 'Refused')])
    partner_id = fields.Many2one('res.partner')
    property_id = fields.Many2one('estate.property')
    
    # Related Field
    property_type_id = fields.Many2one(related = 'property_id.property_type_id', store=True)

    @api.depends("offer_date" , "valid_days")
    def _valid_till_date(self) :
        for record in self :
            record.valid_tills = record.offer_date + Datetime.timedelta(days = record.valid_days)
    

    def action_accepted(self) :
        for record in self :
            record.status = 'accepted'
            # Set buyer and Selling price
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id


    def action_refused(self) :
        for record in self :
            record.status = "refused"


    
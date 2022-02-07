from odoo import models,fields,api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError,ValidationError


class EstatePropertyType(models.Model) :
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _sql_constraints = [('unique_property_type1_name','unique(name)','Type cannot be duplicate ')]
    _order = 'name desc'

    name = fields.Char()
    property_ids = fields.One2many('estate.property' , 'property_type_id')
    offer_ids = fields.One2many('estate.property.offer' , 'property_type_id')
    offer_count = fields.Integer(compute = '_compute_offer_count')

    @api.depends('offer_ids')
    def _compute_offer_count(self) :
        for record in self :
            record.offer_count = len(record.offer_ids)



class EstatePropertyTag(models.Model) :
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'
    _sql_constraints = [('unique_property_tag_name','unique(name)','Tag cannot be duplicate ')]
    _order = 'name desc'

    name = fields.Char()
    color = fields.Integer()




class EstatePropertyOffer(models.Model) :
    _name = 'estate.property.offer'
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




class EstateProperty(models.Model) :

    _name = 'estate.property'
    _description = 'Estate Property'
    _sql_constraints = [('positive_price','CHECK(expected_price >= 0)','Enter Positive value')]
    _order = "expected_price desc"   


    def _get_description(self) :
        if self.env.context.get('is_my_property') :
            return self.env.user.name + "'s property" 
    

    name = fields.Char(string = "Property Name",default="Unknown",required=True)
    description = fields.Text(default =_get_description)
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
        

    property_type_id = fields.Many2one('estate.property.type')
    salesman_id = fields.Many2one('res.users')
    buyer_id = fields.Many2one('res.partner')
    #currency_id = fields.Many2one('res.currency' ,default=lambda self : self.env.company.currency_id)

    property_tag_ids = fields.Many2many('estate.property.tag')
    
    property_offer_ids = fields.One2many('estate.property.offer','property_id')

    total_area = fields.Integer(compute = "_compute_area" , inverse="_inverse_area")
    best_price = fields.Float(compute="_compute_best_price")

    validity = fields.Integer(default = 7 , compute="_compute_validity" , inverse = "_inverse_validity")
    date_deadline = fields.Date()


    @api.onchange('garden') 
    def _onchange_garden(self) :
        for record in self :
            if record.garden :
                record.garden_area = 10
                record.garden_orientation = 'north'
            else :
                record.garden_area = 0
                record.garden_orientation = None


   # @api.depends('validity')
   # def _compute_date_deadline(self) :
    #    for record in self :
     #       record.date_deadline = fields.Date.add(record.date_availability, days = record.validity)
    
    @api.depends('date_deadline')
    def _inverse_validity(self):
        for record in self:
            record.date_deadline = record.date_availability + relativedelta(days=record.validity)

    @api.depends('date_availability', 'date_deadline')     
    def _compute_validity(self):        
         for record in self:            
              if record.date_deadline and record.date_availability:                 
                  diff = record.date_deadline - record.date_availability                 
                  record.validity = diff.days            
              else:                 
                 record.validity = 7

        
    @api.depends('living_area' , 'garden_area')
    def _compute_area(self) :
        for record in self :
            record.total_area = record.living_area + record.garden_area

    
    @api.depends('property_offer_ids.price')
    def _compute_best_price(self) :
        for record in self :
            max_price = 0
            for offer in record.property_offer_ids :
                if offer.price > max_price :
                    max_price = offer.price
            record.best_price = max_price

    
    def _inverse_area(self) :
        for record in self:
            record.living_area = record.garden_area = record.total_area / 2


    @api.constrains('living_area' , 'garden_area')
    def _check_garden_area(self) :
        for record in self :
            if record.living_area < record.garden_area :
                raise ValidationError("Garden cannot be bigger than living area")

    
    def action_sold(self) :
        #print("\n\n In Action Sold")   
        for record in self :
            if record.state == 'cancel' :
                raise UserError("Cancel Property Cannot be Sold")
            record.state = 'sold'


    def action_cancel(self) :
        for record in self :
            if record.state =='sold' :
                raise UserError("Sold Property Cannot be Canceled")
            record.state = 'cancel'

    
    # Kanban view show all offers click on offer button

    def open_offers(self):
        view_id_all = self.env.ref('estate.estate_property_offer_tree').id
        return {
            "name":"Offers",
            "type":"ir.actions.act_window",
            "res_model":"estate.property.offer",
            "views":[[view_id_all, 'tree']],
            "target":"new",
            "domain": [('property_id', '=', self.id)]
            }
    
    # Kanban view show all confirm offers click on confirm offer button


    def open_confirm_offers(self):
        view_id_accept = self.env.ref('estate.estate_property_offer_tree').id
        return {
            "name":"Offers",
            "type":"ir.actions.act_window",
            "res_model":"estate.property.offer",
            "views":[[view_id_accept, 'tree']],
            "domain": [('property_id', '=', self.id),('status','=','accepted')]
            }
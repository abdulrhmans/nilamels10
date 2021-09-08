from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, date
import calendar
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

FETCH_RANGE = 2000


class ProductProfitReport(models.TransientModel):
    _name = "product.profit.report"
    
    @api.model
    def _get_default_company(self):
        return self.env.user.company_id
    
    @api.model
    def _get_date_from(self):
        date = datetime.today()
        date = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
        return date
    
    @api.model
    def _get_date_to(self):
        date = datetime.today()
#        date = datetime(date.year, 12, 31).strftime("%Y-%m-%d")
        return date

    product_ids = fields.Many2many('product.product', string='Product')
    category_ids = fields.Many2many('product.category', string='Category')
    location_id = fields.Many2one('stock.location', string='Store', domain=[('usage', '=', 'internal')])
    salesman_id = fields.Many2one('res.users', string='Salesman')
    division_id = fields.Many2one('customer.division', string='Division')
    department_id = fields.Many2one('customer.department', string='Department')
    date_from = fields.Date(string='From date', default=_get_date_from)
    date_to = fields.Date(string='To date', default=_get_date_to)
    
    show_profit_cost_ratio = fields.Boolean(string='Show Profit/Cost Ratio')
    show_profit_sales_ratio = fields.Boolean(string='Show Profit/Sales Ratio')
    show_balance = fields.Boolean(string='Show Balance')
    show_balance_value = fields.Boolean(string='show Balance Value')
    show_last_price = fields.Boolean(string='Show Last Price')
    show_last_cost = fields.Boolean(string='Show Last Cost')
    show_bonus_and_bonus_cost = fields.Boolean(string='Show Bonus and Bonus Cost')
    show_profit_margin = fields.Boolean(string='Show Profit Margin',readonly=True)
    
    show_arabic_name = fields.Boolean(string='Show Arabic Name')
    show_product_code = fields.Boolean(string='Product Code', default='True')
    show_product_name = fields.Boolean(string='Product Name', default='True')
    show_quantity = fields.Boolean(string='Quantity', default='True')
    show_unit = fields.Boolean(string='Unit', default='True')
    show_barcode_field = fields.Boolean(string='Barcode Field')
    show_price = fields.Boolean(string='Price', default='True')
    show_categ = fields.Boolean(string='Category')
    show_brand = fields.Boolean(string='Brand')
#    account_id = fields.Many2one('account.account', string='Account', domain=['|',('type', 'in', ('receivable',)),('group_account','=',True)])
    account_id = fields.Many2one('account.account', string='Account', domain=['|',('type', 'in', ('receivable',)),('user_type_id.name','=','Asset View')])
    
    group_by = fields.Selection(
        [('category', 'Category')],
        string='Group by', default=''
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=_get_default_company
    )
    sort_by = fields.Selection(
        [('product', 'Product'),
        ('qty', 'Qty'),
        ('sales', 'Sales'),
        ('profit', 'Profit')],
        string='Sort by', default='product'
    )
    based_on = fields.Selection(
        [('sales_and_returns', 'Sales and Returns'),
        ('sales', 'Sales'),
        ('returns', 'Returns')],
        string='Based On', default='sales_and_returns'
    )
    state = fields.Selection(
        [('all', 'All'),
        ('posted', 'Posted'),
        ('not_posted', 'Not Posted')],
        string='State', default='all'
    )
    
    
    @api.model
    def create(self, vals):
        ret = super(ProductProfitReport, self).create(vals)
        return ret

    @api.multi
    def write(self, vals):
        ret = super(ProductProfitReport, self).write(vals)
        return ret
    
    
    def validate_data(self):
        if self.date_from > self.date_to:
            raise ValidationError(_('"Date from" must be less than or equal to "Date to"'))
        return True
    
    def get_filters(self, default_filters={}):
        
        products = self.product_ids if self.product_ids else self.env['product.product'].search([])
        
        all_sub_categ = []
        category_ids = self.category_ids.ids or []
        print"category_ids: ",category_ids
        if category_ids:
            categs = self.env['product.category'].browse(category_ids)
            for categ in categs:
                for sub_categ_id in categ.search([('id', 'child_of', categ.id)]).ids:
                    all_sub_categ.append(sub_categ_id)
        print"all_sub_categ: ",all_sub_categ
        category_ids = list(set(all_sub_categ))
        
        product_list_new = ['All Products']
        if len(self.product_ids):
            product_list_new = [p.name for p in self.product_ids]
            
        category_list = ['All Categories']
        if self.category_ids:
            category_list = [c.name for c in self.category_ids]        
#        if len(category_ids):
#            category_list = [c.name for c in self.env['product.category'].browse(category_ids)]
            
        location = 'All'
        if self.location_id:
            location = self.location_id.name
            
        salesman = 'All'
        if self.salesman_id:
            salesman = self.salesman_id.name
            
        division = 'All'
        if self.division_id:
            division = self.division_id.name
            
        department = 'All'
        if self.department_id:
            department = self.department_id.name
        
        filter_dict= {
            'product_ids': self.product_ids.ids,
#            'category_ids': self.category_ids.ids,
            'category_ids': category_ids,
            'location_id': self.location_id or False,
            'salesman_id': self.salesman_id or False,
            'division_id': self.division_id or False,
            'department_id': self.department_id or False,
            'date_from': self.date_from or '2020-01-01',
            'date_to': self.date_to or '2030-01-01',
            'show_arabic_name': self.show_arabic_name or False,
            'show_profit_cost_ratio': self.show_profit_cost_ratio or False,
            'show_profit_sales_ratio': self.show_profit_sales_ratio or False,
            'show_balance': self.show_balance or False,
            'show_balance_value': self.show_balance_value or False,
            'show_bonus_and_bonus_cost': self.show_bonus_and_bonus_cost or False,
            'show_last_price': self.show_last_price or False,
            'show_last_cost': self.show_last_cost or False,
            'show_price': self.show_price or False,
            'show_barcode_field': self.show_barcode_field or False,
            'show_categ': self.show_categ or False,
            'show_brand': self.show_brand or False,
            'based_on': self.based_on or False,
            'sort_by': self.sort_by or False,
            'state': self.state or 'all',
            'group_by': self.group_by or 'all',
            'account': self.account_id and self.account_id.name or '',
            'account_id': self.account_id and self.account_id.id or False,
            
            # For Js widget only
            'product_list': [(p.id, p.name) for p in products],
            
            'product_list_new': product_list_new,
            'category_list': category_list,
            'location': location,
            'salesman': salesman,
            'division': division,
            'department': department,
        }
        filter_dict.update(default_filters)
#        print"filter_dict: ",filter_dict
        return filter_dict
    
    def process_filters(self):
        ''' To show on report headers'''
        
        data = self.get_filters(default_filters={})
        filters = {}
        
        if data.get('product_ids', []):
            filters['products'] = self.env['product.product'].browse(data.get('product_ids', [])).mapped('name')
        else:
            filters['products'] = ['All']
            
        if data.get('category_ids', []):
            filters['categories'] = self.env['product.category'].browse(data.get('category_ids', [])).mapped('name')
        else:
            filters['categories'] = ['All']

        # For Js framework
#        filters['journals_list'] = data.get('journals_list')
        filters['show_arabic_name'] = self.show_arabic_name or False
        filters['show_profit_cost_ratio'] = self.show_profit_cost_ratio or False
        filters['show_profit_sales_ratio'] = self.show_profit_sales_ratio or False
        filters['show_balance'] = self.show_balance or False
        filters['show_balance_value'] = self.show_balance_value or False
        filters['show_last_price'] = self.show_last_price or False
        filters['show_last_cost'] = self.show_last_cost or False
        filters['show_bonus_and_bonus_cost'] = self.show_bonus_and_bonus_cost or False
        filters['show_price'] = self.show_price or False
        filters['show_barcode_field'] = self.show_barcode_field or False
        filters['show_categ'] = self.show_categ or False
        filters['show_brand'] = self.show_brand or False
        
        filters['date_from'] = data.get('date_from')
        filters['date_to'] = data.get('date_to')
        filters['state'] = data.get('state')
        filters['group_by'] = data.get('group_by')
        
        filters['product_list'] = data.get('product_list')
        
        filters['product_list_new'] = data.get('product_list_new')
        filters['category_list'] = data.get('category_list')
        filters['salesman'] = data.get('salesman')
        filters['division'] = data.get('division')
        filters['location'] = data.get('location')
        filters['department'] = data.get('department')
        filters['customer'] = data.get('customer')
        filters['based_on'] = data.get('based_on')
        filters['sort_by'] = data.get('sort_by')
        filters['account'] = data.get('account')
        filters['account_id'] = data.get('account_id')

        return filters
    
    def process_data(self):
        '''
        It is the method for showing summary details of each accounts. Just basic details to show up
        Three sections,
        1. Initial Balance
        2. Current Balance
        3. Final Balance
        :return:
        '''
        data = self.get_filters(default_filters={})
#        print"filter data: ",data
        print"data.get('category_ids'): ",data.get('category_ids')
        
        show_arabic_name = data.get('show_arabic_name',False)
        show_profit_cost_ratio = data.get('show_profit_cost_ratio',False)
        show_profit_sales_ratio = data.get('show_profit_sales_ratio',False)
        show_balance = data.get('show_balance',False)
        show_balance_value = data.get('show_balance_value',False)
        show_last_price = data.get('show_last_price',False)
        show_last_cost = data.get('show_last_cost',False)
        show_bonus_and_bonus_cost = data.get('show_bonus_and_bonus_cost',False)
        show_price = data.get('show_price',False)
        show_barcode_field = data.get('show_barcode_field',False)
        show_categ = data.get('show_categ',False)
        show_brand = data.get('show_brand',False)


        date_from = data.get('date_from','2020-01-01')
        date_to = data.get('date_to','2030-01-01')
        domain = [('invoice_id.date_invoice', '>=', date_from),
                ('invoice_id.date_invoice', '<=', date_to)]
        
        based_on = data.get('based_on','sales_and_returns')
        if based_on == 'sales_and_returns':
            domain.append(('invoice_id.type', 'in', ('out_invoice','out_refund')))
        if based_on == 'sales':
            domain.append(('invoice_id.type', '=', 'out_invoice'))
        if based_on == 'returns':
            domain.append(('invoice_id.type', '=', 'out_refund'))
            
        state = data.get('state','all')
        if state== 'all':
            domain.append(('invoice_id.state', '!=', 'cancel'))
        if state== 'posted':
            domain.append(('invoice_id.state', 'not in', ('cancel','draft')))
        if state== 'not_posted':
            domain.append(('invoice_id.state', '=', 'draft'))
            
        if data.get('location_id'):
            location_id = data.get('location_id')
            domain.append(('invoice_id.location_id','=',location_id.id))
        if data.get('salesman_id'):
            salesman_id = data.get('salesman_id')
            domain.append(('invoice_id.user_id','=',salesman_id.id))
        if data.get('division_id'):
            division_id = data.get('division_id')
            domain.append(('invoice_id.division_id','=',division_id.id))
        if data.get('department_id'):
            department_id = data.get('department_id')
            domain.append(('invoice_id.department_id','=',department_id.id))
        if data.get('product_ids'):
            domain.append(('product_id', 'in', data.get('product_ids')))
        if data.get('category_ids'):
            domain.append(('product_id.categ_id', 'in', data.get('category_ids')))
#        print"process_data domainnnn: ",domain
        
        print"data.get('account_id'): ",data.get('account_id')
        if data.get('account_id'):
            accounts = [self.env['account.account'].browse(data.get('account_id'))]
#            accounts = [data.get('account_id')]
            if accounts[0].type == 'view':
                child_account_ids = self.env['account.account'].search([('parent_id', 'child_of', accounts[0].ids)])
                if len(child_account_ids):
                    accounts = child_account_ids.ids
                domain.append(('invoice_id.account_id','in',accounts))
            else:
                domain.append(('invoice_id.account_id','=',accounts[0].id))
        print"domain999999999999999999999999999999999999: ",domain
        

#        invoice_line_ids = self.env['account.invoice.line'].search(domain)
#        print"len(invoice_line_ids): ",len(invoice_line_ids)
        
        
        # query
#        COALESCE(ail.cost_price,0) as cost_price,
#        1/ COALESCE(uom.factor,1) * COALESCE(ail.cost_price,0) as cost_price,
        qry = """
            SELECT ail.id as id,
            COALESCE(ail.free_qty,0) as free_qty,
            COALESCE(ail.commission_share,0) as commission_share,
            1/ COALESCE(uom.factor,1) * COALESCE(ail.cost_price,0) as cost_price,
            ail.price_subtotal as price_subtotal,
            ail.discount_share as discount_share,
            ail.quantity as quantity,
            COALESCE(ai.exchange_rate, 1.0) as exchange_rate,
            ai.refund_without_invoice as refund_without_invoice,
            ai.id as invoice_id,
            ai.number as number,
            ai.date_invoice as date_invoice,
            ai.partner_id as partner_id,
            rp.name as partner_name,
            ai.type as type,
            uom.name as uom,
            pt.categ_id as categ_id,
            pp.id as product_id
            FROM account_invoice_line ail
            JOIN account_invoice ai ON (ai.id = ail.invoice_id)
            JOIN res_partner rp ON(rp.id = ai.partner_id) 
            JOIN product_product pp ON (pp.id=ail.product_id)
            JOIN product_template pt ON (pt.id=pp.product_tmpl_id)
            JOIN product_uom uom ON (uom.id=ail.uom_id)
            WHERE ai.date_invoice BETWEEN '%s' AND '%s'
        """ %(date_from,date_to)
        
        based_on = data.get('based_on','sales_and_returns')
        if based_on == 'sales_and_returns':
            qry += " AND ai.type IN ('out_invoice','out_refund')"
        elif based_on == 'sales':
            qry += " AND ai.type = 'out_invoice'"
        elif based_on == 'returns':
            qry += " AND ai.type = 'out_refund'"
        state = data.get('state','all')
 
        if state== 'all':
            qry += " AND ai.state != 'cancel'"
        elif state== 'posted':
            qry += " AND ai.state NOT IN ('cancel','draft')"
        elif state== 'not_posted':
            qry += " AND ai.state = 'draft'"
 
        if data.get('location_id'):
            location_id = data.get('location_id')
            qry += " AND ai.location_id = '%s'"%location_id.id
        if data.get('salesman_id'):
            salesman_id = data.get('salesman_id')
            qry += " AND ai.user_id = '%s'"%salesman_id.id
        if data.get('partner_id'):
            partner_id = data.get('partner_id')
            qry += " AND ai.partner_id = '%s'"%partner_id.id
        if data.get('category_ids',[]):
            category_ids = list(set(data.get('category_ids')))
            qry += " AND pt.categ_id IN (%s)"%",".join(map(str,category_ids))
        if data.get('product_ids',[]):
            product_ids = list(set(data.get('product_ids')))
            qry += " AND pp.id IN (%s)"%",".join(map(str,product_ids))

        print"data.get Account: ",data.get('account_id')
        if data.get('account_id'):
            accounts = [data.get('account_id')]
            if accounts[0].type == 'view':
                child_account_ids = self.env['account.account'].search([('parent_id', 'child_of', accounts[0].ids)])
                if len(child_account_ids):
                    accounts = child_account_ids.ids
            else:
                accounts = [accounts[0].id]
            qry += " AND ai.account_id IN (%s)"%",".join(map(str,accounts))
        
        self.env.cr.execute(qry)
        invoice_line_ids = self.env.cr.dictfetchall()
#        print"invoice_line_ids Query: ",invoice_line_ids        

        
        print"if data.get('category_ids'):: ",data.get('category_ids')
        category_ids = data.get('category_ids',[])
        if not len(category_ids):
            category_ids = [ l['categ_id'] for l in invoice_line_ids ]
#            for l in invoice_line_ids:
#                if not l.product_id.categ_id:continue
#                category_ids.append(l.product_id.categ_id.id)
        category_ids = list(set(category_ids))
        print"category idsss: ",category_ids
        all_categ = self.env['product.category'].browse(category_ids)
        
        product_ids = data.get('product_ids',[])
        if not len(product_ids):
            product_ids = [ l['product_id'] for l in invoice_line_ids ]
#            for l in invoice_line_ids:
#                if not l.product_id:continue
#                product_ids.append(l.product_id.id)
        product_ids = list(set(product_ids))
        print"product idsss: ",product_ids
        all_products = self.env['product.product'].browse(product_ids)
        
        final_res = {}
        all_qty,all_free_qty, all_sales, all_cost, all_free_cost, all_profit = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        for categ in all_categ:
            header_d = {}
            lines = []
            total_qty,total_free_qty, total_sales, total_cost,total_free_cost, total_profit = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            for each_product in all_products:
                if not each_product.categ_id:
                    continue
                if each_product.categ_id.id != categ.id:
                    continue
                
                v = {}
                cost, price, profit, qty,  = 0.0, 0.0, 0.0, 0.0
                free_qty, free_qty_cost = 0.0, 0.0
                unit = False
                for l in invoice_line_ids:
                    if l.get('product_id') != each_product.id:
                        continue
                    
#                    invoice = l.invoice_id
#                    currency = invoice.currency_id
#                    exchange_rate = 1.0
#                    if currency.name!='KWD':
#                        exchange_rate = invoice.exchange_rate
                    exchange_rate = l.get('exchange_rate',1.0)
                    if exchange_rate == 0:
                        exchange_rate = 1.0

                    if l.get('type') == 'out_refund':
#                        this_discount_share = l.this_discount_share or 0.0
                        this_discount_share = l.get('discount_share',0.0)
                        if this_discount_share:
                            this_discount_share = this_discount_share / exchange_rate
                        this_commission_share = l.get('commission_share', 0.0)
                        if this_commission_share:
                            this_commission_share = this_commission_share / exchange_rate
                        this_price = (l.get('price_subtotal') / exchange_rate) - this_discount_share - this_commission_share
                        this_cost = l.get('cost_price') * (l.get('quantity') + l.get('free_qty'))

                        this_profit = this_price - this_cost
                        cost -= this_cost
                        price -= this_price
                        profit -= this_profit
                        
                        qty -= l.get('quantity')
                        free_qty -= l.get('free_qty')
                        free_qty_cost -= (l.get('cost_price') * l.get('free_qty'))
                        if not unit:
                            unit = l.get('uom')
#                            unit = l.uom_id.name or ''
                    else:
                        this_discount_share = l.get('discount_share',0.0)
                        if this_discount_share:
                            this_discount_share = this_discount_share / exchange_rate
                        this_commission_share = l.get('commission_share', 0.0)
                        if this_commission_share:
                            this_commission_share = this_commission_share / exchange_rate
                        
                        this_price = (l.get('price_subtotal')/ exchange_rate) - this_discount_share - this_commission_share
                        this_cost = l.get('cost_price') * (l.get('quantity') + l.get('free_qty'))
                        
                        this_profit = this_price - this_cost
                        cost += this_cost
                        price += this_price
                        profit += this_profit
                        
                        qty += l.get('quantity')
                        free_qty += l.get('free_qty')
                        free_qty_cost += (l.get('cost_price') * l.get('free_qty'))
                        if not unit:
                            unit = l.get('uom')
#                            unit = l.uom_id.name or ''
                
                if not show_bonus_and_bonus_cost:
                    qty += free_qty
                    
                cost = float(round(cost,10))

                v['product_id'] = each_product.id
                v['product_code'] = each_product.default_code or ''
                v['product_name'] = each_product.name or ''
                v['arabic_name'] = each_product.name or ''
                v['barcode'] = each_product.barcode or ''
                v['category'] = each_product.categ_id.name
                v['brand'] = each_product.product_brand_id and each_product.product_brand_id.name or ''
#                v['unit'] = unit
                v['unit'] = each_product.uom_id.name
                v['qty'] = qty
                v['price'] = '{:.3f}'.format(price)
                v['price_f'] = price
                v['cost'] = '{:.3f}'.format(cost)
                v['profit'] = '{:.3f}'.format(profit)
                v['profit_f'] = profit
                v['show_arabic_name'] = show_arabic_name
                v['show_profit_cost_ratio'] = show_profit_cost_ratio
                v['show_profit_sales_ratio'] = show_profit_sales_ratio
                v['show_balance'] = show_balance
                v['show_balance_value'] = show_balance_value
                v['show_last_price'] = show_last_price
                v['show_last_cost'] = show_last_cost
                v['show_bonus_and_bonus_cost'] = show_bonus_and_bonus_cost
                v['show_price'] = show_price
                v['show_barcode_field'] = show_barcode_field
                v['show_categ'] = show_categ
                v['show_brand'] = show_brand
                
                v['free_qty'] = free_qty
                v['free_qty_cost'] = '{:.3f}'.format(free_qty_cost)
                
                d_cost = cost
                if d_cost == 0.0:
                    d_cost = 1.0
                    
                d_price = price
                if d_price == 0.0:
                    d_price = 1.0
                
                v['profit_cost_ratio'] = '{:.3f}'.format((profit / d_cost) * 100.0)
                v['profit_sales_ratio'] = '{:.3f}'.format((profit / d_price) * 100.0)
                
                balance = each_product.qty_available
                standard_price = each_product.standard_price
                
                v['balance'] = balance
                v['balance_value'] = '{:.3f}'.format(balance * standard_price)
                v['last_price'] = '{:.3f}'.format(each_product.lst_price)
                v['last_cost'] = '{:.3f}'.format(standard_price)

                lines.append(v)
                total_qty += qty
                total_free_qty += free_qty
                total_sales += price
                total_cost += cost
                total_profit += profit
                total_free_cost += free_qty_cost

                
                
            header_d['id'] = categ.id
            header_d['name'] = categ.name
            header_d['qty'] = total_qty
            header_d['free_qty'] = total_free_qty
            header_d['sales'] = '{:.3f}'.format(total_sales)
            header_d['cost'] = '{:.3f}'.format(total_cost)
            header_d['free_cost'] = '{:.3f}'.format(total_free_cost)
            header_d['profit'] = '{:.3f}'.format(total_profit)
            
            sort_by = self.sort_by or 'product'
            if sort_by == 'product':
                sort_by = 'product_name'
#                lines = sorted(lines,key=lambda x:lines[x][sort_by])
                lines = sorted(lines, key=lambda i: i[sort_by])
            if sort_by == 'sales':
                sort_by = 'price_f'
                lines = sorted(lines, key=lambda i: i[sort_by], reverse=True)
            if sort_by == 'profit':
                sort_by = 'profit_f'
                lines = sorted(lines, key=lambda i: i[sort_by], reverse=True)
            if sort_by == 'qty':
                sort_by = 'qty'
                lines = sorted(lines, key=lambda i: i[sort_by], reverse=True)

            header_d['lines'] = lines
            header_d['single_page'] = True
            header_d['count'] = len(lines)
                
            final_res[categ.id] = header_d
            
            # for totals
            all_qty += total_qty
            all_free_qty += total_free_qty
            all_sales += total_sales
            all_cost += total_cost
            all_free_cost += total_free_cost
            all_profit += total_profit
#            if show_bonus_and_bonus_cost:
#                all_profit -= total_free_cost
        
        
        final_res.update({'Total': {}})
        final_res['Total']['qty'] = all_qty
        final_res['Total']['free_qty'] = all_free_qty
        final_res['Total']['sales'] = '{:.3f}'.format(all_sales)
        final_res['Total']['cost'] = '{:.3f}'.format(all_cost)
        final_res['Total']['free_cost'] = '{:.3f}'.format(all_free_cost)
        final_res['Total']['profit'] = '{:.3f}'.format(all_profit)
        final_res['Total']['profit_f'] = all_profit
            
#        sort_by = self.sort_by or 'product'
#        if sort_by == 'product':
#            sort_by = 'name'
#            final_res = sorted(final_res,key=lambda x:final_res[x][sort_by])
#        else:
#            final_res = sorted(final_res,key=lambda x:final_res[x][sort_by], reverse=True)
            
        
#        print"final_res \n\n\n",len(final_res)
        return final_res
    
    def build_detailed_move_lines(self, offset=0, categ_id=0, fetch_range=FETCH_RANGE):
        data = self.get_filters(default_filters={})
#        print"filter data: ",data
        offset_count = offset * fetch_range
        
        date_from = data.get('date_from','2020-01-01')
        date_to = data.get('date_to','2030-01-01')
        domain = [('invoice_id.date_invoice', '>=', date_from),
                ('invoice_id.date_invoice', '<=', date_to)]
                
                
        based_on = data.get('based_on','sales_and_returns')
        if based_on == 'sales_and_returns':
            domain.append(('invoice_id.type', 'in', ('out_invoice','out_refund')))
        if based_on == 'sales':
            domain.append(('invoice_id.type', '=', 'out_invoice'))
        if based_on == 'returns':
            domain.append(('invoice_id.type', '=', 'out_refund'))
            
        state = data.get('state','all')
        if state== 'all':
            domain.append(('invoice_id.state', '!=', 'cancel'))
        if state== 'posted':
            domain.append(('invoice_id.state', 'not in', ('cancel','draft')))
        if state== 'not_posted':
            domain.append(('invoice_id.state', '=', 'draft'))

        if data.get('location_id'):
            location_id = data.get('location_id')
            domain.append(('invoice_id.location_id','=',location_id.id))
        if data.get('salesman_id'):
            salesman_id = data.get('salesman_id')
            domain.append(('invoice_id.user_id','=',salesman_id.id))
        if data.get('division_id'):
            division_id = data.get('division_id')
            domain.append(('invoice_id.division_id','=',division_id.id))
        if data.get('department_id'):
            department_id = data.get('department_id')
            domain.append(('invoice_id.department_id','=',department_id.id))
        if data.get('product_ids'):
            domain.append(('product_id', 'in', data.get('product_ids')))
        if data.get('category_ids'):
            domain.append(('product_id.categ_id', 'in', data.get('category_ids')))
        print"build_detailed_move_lines domainnnn: ",domain

#        invoice_line_ids = self.env['account.invoice.line'].search(domain)
#        print"build_detailed_move_lines len(invoice_line_ids): ",len(invoice_line_ids)
        
        
        # query
#        COALESCE(ail.cost_price,0) as cost_price,
#        1/ COALESCE(uom.factor,1) * COALESCE(ail.cost_price,0) as cost_price,
        qry = """
            SELECT ail.id as id,
            COALESCE(ail.free_qty,0) as free_qty,
            COALESCE(ail.commission_share,0) as commission_share,
            1/ COALESCE(uom.factor,1) * COALESCE(ail.cost_price,0) as cost_price,
            ail.price_subtotal as price_subtotal,
            ail.discount_share as discount_share,
            ail.quantity as quantity,
            COALESCE(ai.exchange_rate, 1.0) as exchange_rate,
            ai.refund_without_invoice as refund_without_invoice,
            ai.id as invoice_id,
            ai.number as number,
            ai.date_invoice as date_invoice,
            ai.partner_id as partner_id,
            rp.name as partner_name,
            ai.type as type,
            uom.name as uom,
            pt.categ_id as categ_id,
            pp.id as product_id
            FROM account_invoice_line ail
            JOIN account_invoice ai ON (ai.id = ail.invoice_id)
            JOIN res_partner rp ON(rp.id = ai.partner_id) 
            JOIN product_product pp ON (pp.id=ail.product_id)
            JOIN product_template pt ON (pt.id=pp.product_tmpl_id)
            JOIN product_uom uom ON (uom.id=ail.uom_id)
            WHERE ai.date_invoice BETWEEN '%s' AND '%s'
        """ %(date_from,date_to)
        
        based_on = data.get('based_on','sales_and_returns')
        if based_on == 'sales_and_returns':
            qry += " AND ai.type IN ('out_invoice','out_refund')"
        elif based_on == 'sales':
            qry += " AND ai.type = 'out_invoice'"
        elif based_on == 'returns':
            qry += " AND ai.type = 'out_refund'"
        state = data.get('state','all')
 
        if state== 'all':
            qry += " AND ai.state != 'cancel'"
        elif state== 'posted':
            qry += " AND ai.state NOT IN ('cancel','draft')"
        elif state== 'not_posted':
            qry += " AND ai.state = 'draft'"
 
        if data.get('location_id'):
            location_id = data.get('location_id')
            qry += " AND ai.location_id = '%s'"%location_id.id
        if data.get('salesman_id'):
            salesman_id = data.get('salesman_id')
            qry += " AND ai.user_id = '%s'"%salesman_id.id
        if data.get('partner_id'):
            partner_id = data.get('partner_id')
            qry += " AND ai.partner_id = '%s'"%partner_id.id
        if data.get('category_ids',[]):
            category_ids = list(set(data.get('category_ids')))
            qry += " AND pt.categ_id IN (%s)"%",".join(map(str,category_ids))
        if data.get('product_ids',[]):
            product_ids = list(set(data.get('product_ids')))
            qry += " AND pp.id IN (%s)"%",".join(map(str,product_ids))

        print"data.get Account: ",data.get('account_id')
        if data.get('account_id'):
            accounts = [data.get('account_id')]
            if accounts[0].type == 'view':
                child_account_ids = self.env['account.account'].search([('parent_id', 'child_of', accounts[0].ids)])
                if len(child_account_ids):
                    accounts = child_account_ids.ids
            else:
                accounts = [accounts[0].id]
            qry += " AND ai.account_id IN (%s)"%",".join(map(str,accounts))
        
        self.env.cr.execute(qry)
        invoice_line_ids = self.env.cr.dictfetchall()
#        print"invoice_line_ids Query: ",invoice_line_ids
        
        
        product_ids = data.get('product_ids',[])
        if not len(product_ids):
            product_ids = [ l['product_id'] for l in invoice_line_ids ]
#            for l in invoice_line_ids:
#                if not l.product_id:continue
#                product_ids.append(l.product_id.id)
        product_ids = list(set(product_ids))
        all_products = self.env['product.product'].browse(product_ids)

        show_arabic_name = data.get('show_arabic_name',False)
        show_profit_cost_ratio = data.get('show_profit_cost_ratio',False)
        show_profit_sales_ratio = data.get('show_profit_sales_ratio',False)
        show_balance = data.get('show_balance',False)
        show_balance_value = data.get('show_balance_value',False)
        show_last_price = data.get('show_last_price',False)
        show_last_cost = data.get('show_last_cost',False)
        show_bonus_and_bonus_cost = data.get('show_bonus_and_bonus_cost',False)
        show_price = data.get('show_price',False)
        show_barcode_field = data.get('show_barcode_field',False)
        show_categ = data.get('show_categ',False)
        show_brand = data.get('show_brand',False)
#        print"domainnnnnnnn: ",domain
        
#        invoice_ids = self.env['account.invoice'].sudo().search(domain,order='date_invoice')
        
#        all_products = []
        all_categ = [self.env['product.category'].browse(categ_id)]
        final_res = []
        for categ in all_categ:
            for each_product in all_products:
                if not each_product.categ_id:
                    continue
                if each_product.categ_id.id != categ.id:
                    continue
                
                v = {}
                cost, price, profit, qty,  = 0.0, 0.0, 0.0, 0.0
                free_qty, free_qty_cost = 0.0, 0.0
                unit = False
                for l in invoice_line_ids:
                    if l.get('product_id') != each_product.id:
                        continue
                    
                    exchange_rate = l.get('exchange_rate',1.0)
                    if exchange_rate == 0:
                        exchange_rate = 1.0                    

                    if l.get('type') == 'out_refund':
                        this_discount_share = l.get('discount_share') or 0.0
                        if this_discount_share:
                            this_discount_share = this_discount_share / exchange_rate
                        this_commission_share = l.get('commission_share', 0.0)
                        if this_commission_share:
                            this_commission_share = this_commission_share / exchange_rate
                        
                        this_price = (l.get('price_subtotal') / exchange_rate) - this_discount_share - this_commission_share
                        if not show_bonus_and_bonus_cost:
                            this_cost = l.get('cost_price') * (l.get('quantity') + l.get('free_qty'))
                        else:
                            this_cost = l.get('cost_price') * l.get('quantity')
                        this_profit = this_price - this_cost
                        cost -= this_cost
                        price -= this_price
                        profit -= this_profit
                        
                        qty -= l.get('quantity')
                        free_qty -= l.get('free_qty')
                        free_qty_cost -= (l.get('cost_price') * l.get('free_qty'))
                        if not unit:
                            unit = l.get('uom')
#                            unit = l.uom_id.name or ''
                    else:
                        this_discount_share = l.get('discount_share', 0.0)
                        if this_discount_share:
                            this_discount_share = this_discount_share / exchange_rate
                        this_commission_share = l.get('commission_share', 0.0)
                        if this_commission_share:
                            this_commission_share = this_commission_share / exchange_rate
                        
#                        this_price = l.price_subtotal - l.discount_share - l.commission_share
                        this_price = (l.get('price_subtotal') / exchange_rate) - this_discount_share - this_commission_share
                        if not show_bonus_and_bonus_cost:
                            this_cost = l.get('cost_price') * (l.get('quantity') + l.get('free_qty'))
                        else:
                            this_cost = l.get('cost_price') * l.get('quantity')
                        this_profit = this_price - this_cost
                        cost += this_cost
                        price += this_price
                        profit += this_profit
                        
                        qty += l.get('quantity')
                        free_qty += l.get('free_qty')
                        free_qty_cost += (l.get('cost_price') * l.get('free_qty'))
                        if not unit:
                            unit = l.get('uom')
#                            unit = l.uom_id.name or ''
                
                if not show_bonus_and_bonus_cost:
                    qty += free_qty
                    
                cost = float(round(cost,10))

                v['product_id'] = each_product.id
                v['product_code'] = each_product.default_code or ''
                v['product_name'] = each_product.name or ''
                v['arabic_name'] = each_product.name or ''
                v['barcode'] = each_product.barcode or ''
                v['category'] = each_product.categ_id.name
                v['brand'] = each_product.product_brand_id and each_product.product_brand_id.name or ''
#                v['unit'] = unit
                v['unit'] = each_product.uom_id.name
                v['qty'] = qty
                v['price'] = '{:.3f}'.format(price)
                v['cost'] = '{:.3f}'.format(cost)
                v['profit'] = '{:.3f}'.format(profit)
                v['profit_f'] = profit
                v['show_arabic_name'] = show_arabic_name
                v['show_profit_cost_ratio'] = show_profit_cost_ratio
                v['show_profit_sales_ratio'] = show_profit_sales_ratio
                v['show_balance'] = show_balance
                v['show_balance_value'] = show_balance_value
                v['show_last_price'] = show_last_price
                v['show_last_cost'] = show_last_cost
                v['show_bonus_and_bonus_cost'] = show_bonus_and_bonus_cost
                v['show_price'] = show_price
                v['show_barcode_field'] = show_barcode_field
                v['show_categ'] = show_categ
                v['show_brand'] = show_brand
                
                v['free_qty'] = free_qty
                v['free_qty_cost'] = '{:.3f}'.format(free_qty_cost)
                
                d_cost = cost
                if d_cost == 0.0:
                    d_cost = 1.0
                d_price = price
                if d_price == 0.0:
                    d_price = 1.0
                
                v['profit_cost_ratio'] = '{:.3f}'.format((profit / d_cost) * 100.0)
                v['profit_sales_ratio'] = '{:.3f}'.format((profit / d_price) * 100.0)
                
                balance = each_product.qty_available
                standard_price = each_product.standard_price
                
                v['balance'] = balance
                v['balance_value'] = '{:.3f}'.format(balance * standard_price)
                v['last_price'] = '{:.3f}'.format(each_product.lst_price)
                v['last_cost'] = '{:.3f}'.format(standard_price)
                v['profit_f'] = profit

                final_res.append(v)
                
        sort_by = self.sort_by or 'product'
        if sort_by == 'product':
            sort_by = 'product_name'
            final_res = sorted(final_res, key=lambda i: i[sort_by])
        else:
            if sort_by == 'sales': sort_by = 'price'
            final_res = sorted(final_res, key=lambda i: i[sort_by], reverse=True)
        
#        final_res = sorted(final_res, key=lambda i: i[sort_by])
        count = len(final_res)
#        print"count: ",count
#        print"offset_count: ",offset_count
#        print"final_res: ",final_res
        return count, offset_count, final_res
    
        
    def get_report_datas(self, default_filters={}):
        '''
        Main method for pdf, xlsx and js calls
        :param default_filters: Use this while calling from other methods. Just a dict
        :return: All the datas for GL
        '''
        if self.validate_data():
            filters = self.process_filters()
#            filters={}
            filters['show_arabic_name'] = self.show_arabic_name or False
            filters['show_profit_cost_ratio'] = self.show_profit_cost_ratio or False
            filters['show_profit_sales_ratio'] = self.show_profit_sales_ratio or False
            filters['show_balance'] = self.show_balance or False
            filters['show_balance_value'] = self.show_balance_value or False
            filters['show_last_price'] = self.show_last_price or False
            filters['show_last_cost'] = self.show_last_cost or False
            filters['show_bonus_and_bonus_cost'] = self.show_bonus_and_bonus_cost or False
            filters['show_price'] = self.show_price or False
            filters['show_barcode_field'] = self.show_barcode_field or False
            filters['show_categ'] = self.show_categ or False
            filters['show_brand'] = self.show_brand or False
            
            account_lines = self.process_data()
            return filters, account_lines
        
    def get_report_datas_wg(self, default_filters={}):
        '''
        Main method for pdf, xlsx and js calls
        :param default_filters: Use this while calling from other methods. Just a dict
        :return: All the datas for GL
        '''
        if self.validate_data():
            filters = self.process_filters()
#            filters={}
            filters['show_arabic_name'] = self.show_arabic_name or False
            filters['show_profit_cost_ratio'] = self.show_profit_cost_ratio or False
            filters['show_profit_sales_ratio'] = self.show_profit_sales_ratio or False
            filters['show_balance'] = self.show_balance or False
            filters['show_balance_value'] = self.show_balance_value or False
            filters['show_last_price'] = self.show_last_price or False
            filters['show_last_cost'] = self.show_last_cost or False
            filters['show_bonus_and_bonus_cost'] = self.show_bonus_and_bonus_cost or False
            filters['show_price'] = self.show_price or False
            filters['show_barcode_field'] = self.show_barcode_field or False
            filters['show_categ'] = self.show_categ or False
            filters['show_brand'] = self.show_brand or False
            
            account_lines = self.process_data_wg()
            return filters, account_lines

    def action_pdf(self):
#        raise UserError(_('This feature is under development.'))
        if self.group_by=='category':
            filters, account_lines = self.get_report_datas()
        else:
            filters, account_lines = self.get_report_datas_wg()
        return self.env['report'].with_context({'landscape': 1}).get_action(
            self, 'account_dynamic_reports.product_profit', data={'Ledger_data': account_lines,
                        'Filters': filters
                        })

    def action_xlsx(self):
        raise UserError(_('This feature is under development.'))

    def action_view(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'PPR View',
#            'tag': 'dynamic.ppr',
            'context': {'wizard_id': self.id},
        }
        if self.group_by == 'category':
            res['tag'] = 'dynamic.ppr'
        else:
            res['tag'] = 'dynamic.pprwg'
            
        return res
    
    
    
    def process_data_wg(self):
        '''
        It is the method for showing summary details of each accounts. Just basic details to show up
        Three sections,
        1. Initial Balance
        2. Current Balance
        3. Final Balance
        :return:
        '''
        data = self.get_filters(default_filters={})
        
        show_arabic_name = data.get('show_arabic_name',False)
        show_profit_cost_ratio = data.get('show_profit_cost_ratio',False)
        show_profit_sales_ratio = data.get('show_profit_sales_ratio',False)
        show_balance = data.get('show_balance',False)
        show_balance_value = data.get('show_balance_value',False)
        show_last_price = data.get('show_last_price',False)
        show_last_cost = data.get('show_last_cost',False)
        show_bonus_and_bonus_cost = data.get('show_bonus_and_bonus_cost',False)
        show_price = data.get('show_price',False)
        show_barcode_field = data.get('show_barcode_field',False)
        show_categ = data.get('show_categ',False)
        show_brand = data.get('show_brand',False)


        date_from = data.get('date_from','2020-01-01')
        date_to = data.get('date_to','2030-01-01')
        domain = [('invoice_id.date_invoice', '>=', date_from),
                ('invoice_id.date_invoice', '<=', date_to)]
        
        based_on = data.get('based_on','sales_and_returns')
        if based_on == 'sales_and_returns':
            domain.append(('invoice_id.type', 'in', ('out_invoice','out_refund')))
        if based_on == 'sales':
            domain.append(('invoice_id.type', '=', 'out_invoice'))
        if based_on == 'returns':
            domain.append(('invoice_id.type', '=', 'out_refund'))
            
        state = data.get('state','all')
        if state== 'all':
            domain.append(('invoice_id.state', '!=', 'cancel'))
        if state== 'posted':
            domain.append(('invoice_id.state', 'not in', ('cancel','draft')))
        if state== 'not_posted':
            domain.append(('invoice_id.state', '=', 'draft'))
            
        if data.get('location_id'):
            location_id = data.get('location_id')
            domain.append(('invoice_id.location_id','=',location_id.id))
        if data.get('salesman_id'):
            salesman_id = data.get('salesman_id')
            domain.append(('invoice_id.user_id','=',salesman_id.id))
        if data.get('product_ids'):
            domain.append(('product_id', 'in', data.get('product_ids')))
        if data.get('category_ids'):
            domain.append(('product_id.categ_id', 'in', data.get('category_ids')))
            
        if data.get('account_id'):
            accounts = [self.env['account.account'].browse(data.get('account_id'))]
            if accounts[0].type == 'view':
                child_account_ids = self.env['account.account'].search([('parent_id', 'child_of', accounts[0].ids)])
                if len(child_account_ids):
                    accounts = child_account_ids.ids
                domain.append(('invoice_id.account_id','in',accounts))
            else:
                domain.append(('invoice_id.account_id','=',accounts[0].id))
        print"process_data domainnnn wg: ",domain

#        invoice_line_ids = self.env['account.invoice.line'].search(domain)
#        print"len(invoice_line_ids)wg: ",len(invoice_line_ids)
        
        # query
#        COALESCE(ail.cost_price,0) as cost_price,
#        1/ COALESCE(uom.factor,1) * COALESCE(ail.cost_price,0) as cost_price,
        qry = """
            SELECT ail.id as id,
            COALESCE(ail.free_qty,0) as free_qty,
            COALESCE(ail.commission_share,0) as commission_share,
            1/ COALESCE(uom.factor,1) * COALESCE(ail.cost_price,0) as cost_price,
            ail.price_subtotal as price_subtotal,
            COALESCE(ail.discount_share,0.0) as discount_share,
            ail.quantity as quantity,
            COALESCE(ai.exchange_rate, 1.0) as exchange_rate,
            ai.refund_without_invoice as refund_without_invoice,
            ai.id as invoice_id,
            ai.number as number,
            ai.date_invoice as date_invoice,
            ai.partner_id as partner_id,
            rp.name as partner_name,
            ai.type as type,
            uom.name as uom,
            pt.categ_id as categ_id,
            pp.id as product_id
            FROM account_invoice_line ail
            JOIN account_invoice ai ON (ai.id = ail.invoice_id)
            JOIN res_partner rp ON(rp.id = ai.partner_id) 
            JOIN product_product pp ON (pp.id=ail.product_id)
            JOIN product_template pt ON (pt.id=pp.product_tmpl_id)
            JOIN product_uom uom ON (uom.id=ail.uom_id)
            WHERE ai.date_invoice BETWEEN '%s' AND '%s'
        """ %(date_from,date_to)
        
        based_on = data.get('based_on','sales_and_returns')
        if based_on == 'sales_and_returns':
            qry += " AND ai.type IN ('out_invoice','out_refund')"
        elif based_on == 'sales':
            qry += " AND ai.type = 'out_invoice'"
        elif based_on == 'returns':
            qry += " AND ai.type = 'out_refund'"
        state = data.get('state','all')
 
        if state== 'all':
            qry += " AND ai.state != 'cancel'"
        elif state== 'posted':
            qry += " AND ai.state NOT IN ('cancel','draft')"
        elif state== 'not_posted':
            qry += " AND ai.state = 'draft'"
 
        if data.get('location_id'):
            location_id = data.get('location_id')
            qry += " AND ai.location_id = '%s'"%location_id.id
        if data.get('salesman_id'):
            salesman_id = data.get('salesman_id')
            qry += " AND ai.user_id = '%s'"%salesman_id.id
        if data.get('partner_id'):
            partner_id = data.get('partner_id')
            qry += " AND ai.partner_id = '%s'"%partner_id.id
        if data.get('category_ids',[]):
            category_ids = list(set(data.get('category_ids')))
            qry += " AND pt.categ_id IN (%s)"%",".join(map(str,category_ids))
        if data.get('product_ids',[]):
            product_ids = list(set(data.get('product_ids')))
            qry += " AND pp.id IN (%s)"%",".join(map(str,product_ids))

        print"data.get Account: ",data.get('account_id')
        if data.get('account_id'):
            accounts = [data.get('account_id')]
            if accounts[0].type == 'view':
                child_account_ids = self.env['account.account'].search([('parent_id', 'child_of', accounts[0].ids)])
                if len(child_account_ids):
                    accounts = child_account_ids.ids
            else:
                accounts = [accounts[0].id]
            qry += " AND ai.account_id IN (%s)"%",".join(map(str,accounts))
        
        self.env.cr.execute(qry)
        invoice_line_ids = self.env.cr.dictfetchall()
#        print"invoice_line_ids Query: ",invoice_line_ids
        
        print"if data.get('category_ids')wg:: ",data.get('category_ids')
        category_ids = data.get('category_ids',[])
        if not len(category_ids):
            category_ids = [ l['categ_id'] for l in invoice_line_ids ]
#            for l in invoice_line_ids:
#                if not l.product_id.categ_id:continue
#                category_ids.append(l.product_id.categ_id.id)
        category_ids = list(set(category_ids))
        print"category idssswg: ",category_ids
        all_categ = self.env['product.category'].browse(category_ids)
        
        product_ids = data.get('product_ids',[])
        if not len(product_ids):
            product_ids = [ l['product_id'] for l in invoice_line_ids ]
#            for l in invoice_line_ids:
#                if not l.product_id:continue
#                product_ids.append(l.product_id.id)
        product_ids = list(set(product_ids))
        print"product idssswg: ",product_ids
        all_products = self.env['product.product'].browse(product_ids)
        
        final_res = []
        total_qty, total_sales, total_cost, total_free_cost, total_free_qty, total_profit = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        for each_product in all_products:
            if not each_product.categ_id:
                continue
            v = {}
            cost, price, profit, qty,  = 0.0, 0.0, 0.0, 0.0
            free_qty, free_qty_cost = 0.0, 0.0
            unit = False
            for l in invoice_line_ids:
                if l.get('product_id') != each_product.id:
                    continue
                
#                invoice_id = l.get('invoice_id')
#                currency = invoice_id.currency_id
#                exchange_rate = 1.0
#                if currency.name!='KWD':
#                    exchange_rate = invoice_id.exchange_rate
                exchange_rate = l.get('exchange_rate',1.0)
                if exchange_rate == 0:
                    exchange_rate = 1.0
                    
                if l.get('type') == 'out_refund':
                    this_discount_share = l.get('discount_share', 0.0)
                    if this_discount_share:
                        this_discount_share = this_discount_share / exchange_rate
                    this_commission_share = l.get('commission_share', 0.0)
                    if this_commission_share:
                        this_commission_share = this_commission_share / exchange_rate
                    
                    this_price = (l.get('price_subtotal') / exchange_rate) - this_discount_share - this_commission_share
                    if not show_bonus_and_bonus_cost:
                        this_cost = l.get('cost_price') * (l.get('quantity') + l.get('free_qty'))
                    else:
                        this_cost = l.get('cost_price') * l.get('quantity')
                    this_profit = this_price - this_cost
                    cost -= this_cost
                    price -= this_price
                    profit -= this_profit                    

                    qty -= l.get('quantity')
                    free_qty -= l.get('free_qty')
                    free_qty_cost -= (l.get('cost_price') * l.get('free_qty'))
                    if not unit:
                        unit = l.get('uom')
                else:
                    this_discount_share = l.get('discount_share', 0.0)
                    if this_discount_share:
                        this_discount_share = this_discount_share / exchange_rate
                    this_commission_share = l.get('commission_share', 0.0)
                    if this_commission_share:
                        this_commission_share = this_commission_share / exchange_rate
                    
                    this_price = (l.get('price_subtotal') / exchange_rate) - this_discount_share - this_commission_share
                    if not show_bonus_and_bonus_cost:
                        this_cost = l.get('cost_price') * (l.get('quantity') + l.get('free_qty'))
                    else:
                        this_cost = l.get('cost_price') * l.get('quantity')
                    this_profit = this_price - this_cost
                    cost += this_cost
                    price += this_price
                    profit += this_profit

                    qty += l.get('quantity')
                    free_qty += l.get('free_qty')
                    free_qty_cost += (l.get('cost_price') * l.get('free_qty'))
                    if not unit:
                        unit = l.get('uom')

            if not show_bonus_and_bonus_cost:
                qty += free_qty
            
            cost = float(round(cost,10))
            print"cost11: ",cost

            v['product_id'] = each_product.id
            v['name'] = each_product.name
            v['product_code'] = each_product.default_code or ''
            v['product_name'] = each_product.name or ''
            v['arabic_name'] = each_product.name or ''
            v['barcode'] = each_product.barcode or ''
            v['category'] = each_product.categ_id.name
            v['brand'] = each_product.product_brand_id and each_product.product_brand_id.name or ''
#            v['unit'] = unit
            v['unit'] = each_product.uom_id.name
            v['qty'] = qty
            v['price'] = '{:.3f}'.format(price)
            v['price_f'] = price
            v['cost'] = '{:.3f}'.format(cost)
            v['profit'] = '{:.3f}'.format(profit)
            v['profit_f'] = profit
            v['show_arabic_name'] = show_arabic_name
            v['show_profit_cost_ratio'] = show_profit_cost_ratio
            v['show_profit_sales_ratio'] = show_profit_sales_ratio
            v['show_balance'] = show_balance
            v['show_balance_value'] = show_balance_value
            v['show_last_price'] = show_last_price
            v['show_last_cost'] = show_last_cost
            v['show_bonus_and_bonus_cost'] = show_bonus_and_bonus_cost
            v['show_price'] = show_price
            v['show_barcode_field'] = show_barcode_field
            v['show_categ'] = show_categ
            v['show_brand'] = show_brand
            v['is_line'] = True

            v['free_qty'] = free_qty
            v['free_qty_cost'] = '{:.3f}'.format(free_qty_cost)

            d_cost = cost
            if d_cost == 0.0:d_cost = 1.0

            d_price = price
            if d_price == 0.0:d_price = 1.0

            v['profit_cost_ratio'] = '{:.3f}'.format((profit / d_cost) * 100.0)
            v['profit_sales_ratio'] = '{:.3f}'.format((profit / d_price) * 100.0)

            balance = each_product.qty_available
            standard_price = each_product.standard_price

            v['balance'] = balance
            v['balance_value'] = '{:.3f}'.format(balance * standard_price)
            v['last_price'] = '{:.3f}'.format(each_product.lst_price)
            v['last_cost'] = '{:.3f}'.format(standard_price)

            final_res.append(v)
            total_qty += qty
            total_sales += price
            total_cost += cost
            total_free_cost += free_qty_cost
            total_free_qty += free_qty
            total_profit += profit
            if show_bonus_and_bonus_cost:
                total_profit -= free_qty_cost
            ######

        sort_by = self.sort_by or 'product'
        if sort_by == 'product':
            sort_by = 'product_name'
            final_res = sorted(final_res, key=lambda i: i[sort_by])
        else:
            if sort_by == 'sales': sort_by = 'price_f'
            if sort_by == 'profit': sort_by = 'profit_f'
            final_res = sorted(final_res, key=lambda i: i[sort_by], reverse=True)
        
            
        d1 = {'name': 'Total',
            'qty': total_qty,
            'free_qty': total_free_qty,
            'sales': '{:.3f}'.format(total_sales),
            'cost': '{:.3f}'.format(total_cost),
            'free_cost': '{:.3f}'.format(total_free_cost),
            'profit': '{:.3f}'.format(total_profit),
        }
        final_res.append(d1)
        
#        print"final_res \n\n\n",final_res
        return final_res
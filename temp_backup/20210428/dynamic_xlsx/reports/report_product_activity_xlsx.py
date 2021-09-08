# _*_ coding: utf-8
from odoo import models, fields, api, _

from datetime import datetime
try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
    from xlsxwriter.utility import xl_rowcol_to_cell
except ImportError:
    ReportXlsx = object

DATE_DICT = {
    '%m/%d/%Y' : 'mm/dd/yyyy',
    '%Y/%m/%d' : 'yyyy/mm/dd',
    '%m/%d/%y' : 'mm/dd/yy',
    '%d/%m/%Y' : 'dd/mm/yyyy',
    '%d/%m/%y' : 'dd/mm/yy',
    '%d-%m-%Y' : 'dd-mm-yyyy',
    '%d-%m-%y' : 'dd-mm-yy',
    '%m-%d-%Y' : 'mm-dd-yyyy',
    '%m-%d-%y' : 'mm-dd-yy',
    '%Y-%m-%d' : 'yyyy-mm-dd',
    '%f/%e/%Y' : 'm/d/yyyy',
    '%f/%e/%y' : 'm/d/yy',
    '%e/%f/%Y' : 'd/m/yyyy',
    '%e/%f/%y' : 'd/m/yy',
    '%f-%e-%Y' : 'm-d-yyyy',
    '%f-%e-%y' : 'm-d-yy',
    '%e-%f-%Y' : 'd-m-yyyy',
    '%e-%f-%y' : 'd-m-yy'
}

class ProductActivityXlsx(ReportXlsx):
    _name = 'report.dynamic_xlsx.product_activity_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def _define_formats(self, workbook):
        """ Add cell formats to current workbook.
        Available formats:
         * format_title
         * format_header
        """
        self.format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 12,
            'font': 'Arial',
            'border': False
        })
        self.format_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
            #'border': True
        })
        self.format_header_right = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'right',
            'font': 'Arial',
            'text_wrap': True,
            'font': 'Arial',
            'valign': 'top'            
            #'border': True
        })
        self.content_header = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'border': True,
            'font': 'Arial',
        })
        self.content_header_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'border': True,
            'align': 'center',
            'font': 'Arial',
        })
        self.line_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'bottom': True,
            'font': 'Arial',
        })
        self.line_header_light = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'text_wrap': True,
            'font': 'Arial',
            'valign': 'top'
        })
        self.line_header_light_right = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'right',
            'text_wrap': True,
            'font': 'Arial',
            'valign': 'top'
        })
        self.line_header_light_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
        })
        self.line_header_light_initial = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'bottom': True,
            'font': 'Arial',
            'valign': 'top'
        })
        self.line_header_light_ending = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'font': 'Arial',
            'valign': 'top'
        })

    def prepare_report_filters(self, filter):
        """It is writing under second page"""
#        print"filtererrrrr ",filter
        self.row_pos_2 += 2
        if filter:
            date_from = filter.get('date_from',False)
            if not date_from:
                filter['date_from'] = '2020-01-01'
            date_to = filter.get('date_to',False)
            if not date_to:
                filter['date_to'] = '2020-01-01'
            filter['product_code'] = 'True'
                
            # Date from
            self.sheet_2.write_string(self.row_pos_2, 0, _('Date from'),
                                    self.format_header)
            self.sheet_2.write_datetime(self.row_pos_2, 1, self.convert_to_date(str(filter['date_from']) or ''),
                                    self.content_header_date)

            self.row_pos_2 += 1
            self.sheet_2.write_string(self.row_pos_2, 0, _('Date to'),
                                    self.format_header)
            self.sheet_2.write_datetime(self.row_pos_2, 1, self.convert_to_date(str(filter['date_to']) or ''),
                                    self.content_header_date)
                                    
            self.row_pos_2 += 1
            self.sheet_2.write_string(self.row_pos_2, 0, _('Product'),
                                    self.format_header)
            self.sheet_2.write_string(self.row_pos_2, 1, (str(filter['product']) or ''), 
                                    self.line_header_light)                                    
                                    
            self.row_pos_2 += 1
            self.sheet_2.write_string(self.row_pos_2, 0, _('Store'),
                                    self.format_header)
            self.sheet_2.write_string(self.row_pos_2, 1, (str(filter['location']) or ''), 
                                    self.line_header_light)
                                    
            self.row_pos_2 += 1
            self.sheet_2.write_string(self.row_pos_2, 0, _('Salesman'),
                                    self.format_header)
            self.sheet_2.write_string(self.row_pos_2, 1, (str(filter['salesman']) or ''), 
                                self.line_header_light)
                                
            self.row_pos_2 += 1
            self.sheet_2.write_string(self.row_pos_2, 0, _('SortBy'),
                                    self.format_header)
            self.sheet_2.write_string(self.row_pos_2, 1, (str(filter['sort_by']) or ''), 
                    self.line_header_light)
                    
            self.row_pos_2 += 1
            self.sheet_2.write_string(self.row_pos_2, 0, _('Customer'),
                                    self.format_header)
            self.sheet_2.write_string(self.row_pos_2, 1, (str(filter['customer']) or ''), 
                            self.line_header_light)
                            
            self.row_pos_2 += 1
            self.sheet_2.write_string(self.row_pos_2, 0, _('State'),
                                    self.format_header)
            self.sheet_2.write_string(self.row_pos_2, 1, (str(filter['state']) or ''), 
                        self.line_header_light)
                                    
                                            
                                            
#    def prepare_report_contents_wg(self, data, acc_lines, filter):
    def prepare_report_contents(self, data, acc_lines, filter):
        data = data[0]
        self.row_pos += 3
        
#        print"prepare_report_contents acc_lines: \n\n\n",acc_lines

        self.sheet.write_string(self.row_pos, 0, _('Ref No'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 1, _('Date'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 2, _('Description'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 3, _('Customer'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 4, _('Source'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 5, _('Destination'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 6, _('QtyIn'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 7, _('QtyOut'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 8, _('Price'),
                                self.format_header)
#        self.sheet.write_string(self.row_pos, 9, _('Discount'),
#                                self.format_header)
        self.sheet.write_string(self.row_pos, 9, _('Cost'),
                                self.format_header)
        self.sheet.write_string(self.row_pos, 10, _('Balance'),
                                self.format_header)
                                
        if acc_lines:
            for sub_line in acc_lines:
                self.row_pos += 1
                if sub_line.get('ref_no')!='Total':

                    self.sheet.write_string(self.row_pos, 0, sub_line.get('ref_no'),
                                            self.line_header_light)
                    self.sheet.write_string(self.row_pos, 1, sub_line.get('date'),
                                            self.line_header_light)
                    self.sheet.write_string(self.row_pos, 2, sub_line.get('desc'),
                                            self.line_header_light)
                    self.sheet.write_string(self.row_pos, 3, sub_line.get('customer'),
                                            self.line_header_light)
                    self.sheet.write_string(self.row_pos, 4, sub_line.get('source'),
                                            self.line_header_light)
                    self.sheet.write_string(self.row_pos, 5, sub_line.get('destination'),
                                            self.line_header_light)                                            
                    self.sheet.write_number(self.row_pos, 6,
                                            float(sub_line.get('qty_in')),self.line_header_light_right)
                    self.sheet.write_number(self.row_pos, 7,
                                            float(sub_line.get('qty_out')),self.line_header_light_right)
                    self.sheet.write_number(self.row_pos, 8,
                                            float(sub_line.get('price')),self.line_header_light_right)
#                    self.sheet.write_number(self.row_pos, 9,
#                                            float(sub_line.get('discount')),self.line_header_light_right)
                    self.sheet.write_number(self.row_pos, 9,
                                            float(sub_line.get('cost')),self.line_header_light_right)
                    self.sheet.write_number(self.row_pos, 10,
                                            float(sub_line.get('balance')),self.line_header_light_right)
                # total line
                if sub_line.get('ref_no')=='Total':

                    self.sheet.write_string(self.row_pos, 0, '',
                                            self.format_header_right)
                    self.sheet.write_string(self.row_pos, 1, '',
                                            self.format_header_right)
                    self.sheet.write_string(self.row_pos, 2, '',
                                            self.format_header_right)
                    self.sheet.write_string(self.row_pos, 5, sub_line.get('name'),
                                            self.format_header_right)
                    self.sheet.write_number(self.row_pos, 6,
                                            float(sub_line.get('total_qty_in')),self.format_header_right)
                    self.sheet.write_number(self.row_pos, 7,
                                            float(sub_line.get('total_qty_out')),self.format_header_right)
                    self.sheet.write_number(self.row_pos, 8,
                                            float(sub_line.get('total_price')),self.format_header_right)
#                    self.sheet.write_number(self.row_pos, 9,
#                                            float(sub_line.get('total_discount')),self.format_header_right)
                    self.sheet.write_number(self.row_pos, 9,
                                            float(sub_line.get('total_cost')),self.format_header_right)
                    self.sheet.write_number(self.row_pos, 10,
                                            float(sub_line.get('total_balance')),self.format_header_right)



    def _format_float_and_dates(self, currency_id, lang_id):

        self.line_header.num_format = currency_id.excel_format
        self.line_header_light.num_format = currency_id.excel_format
        self.line_header_light_initial.num_format = currency_id.excel_format
        self.line_header_light_ending.num_format = currency_id.excel_format


        self.line_header_light_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')
        self.content_header_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')

    def convert_to_date(self, datestring=False):
        if datestring:
            datestring = fields.Date.from_string(datestring).strftime(self.language_id.date_format)
            return datetime.strptime(datestring, self.language_id.date_format)
        else:
            return False

    def generate_xlsx_report(self, workbook, data, record):
#        print"generate_xlsx_report called"
#        print"generate_xlsx_report called data: ",data
#        print"generate_xlsx_report called record: ",record

        self._define_formats(workbook)
        self.row_pos = 0
        self.row_pos_2 = 0

        self.record = record # Wizard object

        self.sheet = workbook.add_worksheet('Product Activity Report')
        self.sheet_2 = workbook.add_worksheet('Filters')
        self.sheet.set_column(0, 0, 12)
        self.sheet.set_column(1, 1, 12)
        self.sheet.set_column(2, 2, 15)
        self.sheet.set_column(3, 3, 30)
        self.sheet.set_column(4, 4, 10)
        self.sheet.set_column(5, 5, 10)
        self.sheet.set_column(6, 6, 10)
        self.sheet.set_column(7, 7, 10)

        self.sheet_2.set_column(0, 0, 35)
        self.sheet_2.set_column(1, 1, 25)
        self.sheet_2.set_column(2, 2, 25)
        self.sheet_2.set_column(3, 3, 25)
        self.sheet_2.set_column(4, 4, 25)
        self.sheet_2.set_column(5, 5, 25)
        self.sheet_2.set_column(6, 6, 25)

        self.sheet.freeze_panes(4, 0)

        self.sheet.screen_gridlines = False
        self.sheet_2.screen_gridlines = False
        self.sheet_2.protect()

        # For Formating purpose
        lang = self.env.user.lang
        self.language_id = self.env['res.lang'].search([('code','=',lang)])[0]
        self._format_float_and_dates(self.env.user.company_id.currency_id, self.language_id)

        if record:
            data = record.read()
            self.sheet.merge_range(0, 0, 0, 8, 'Product Activity Report'+' - '+data[0]['company_id'][1], self.format_title)
            self.dateformat = self.env.user.lang
            filters, account_lines = record.get_report_datas()
#            # Filter section
            self.prepare_report_filters(filters)
#            # Content section
            self.prepare_report_contents(data, account_lines, filters)

ProductActivityXlsx('report.dynamic_xlsx.product_activity_xlsx','product.activity.report')
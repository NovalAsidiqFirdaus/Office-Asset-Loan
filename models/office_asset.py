# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class OfficeAsset(models.Model):
    _name = 'office.asset'
    _description = 'Office Asset'
    _order = 'code asc, name asc'

    name = fields.Char(string='Asset Name', required=True)
    code = fields.Char(string='Asset Code', required=True, copy=False, index=True)
    category = fields.Selection([
        ('electronics', 'Electronics'),
        ('furniture', 'Furniture'),
        ('vehicle', 'Vehicle'),
        ('other', 'Other'),
    ], string='Category', default='electronics', required=True)
    purchase_date = fields.Date(string='Purchase Date')
    condition = fields.Selection([
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('damaged', 'Damaged'),
    ], string='Condition', default='good', required=True)
    note = fields.Text(string='Note')
    active = fields.Boolean(string='Active', default=True)

    loan_ids = fields.One2many(
        comodel_name='office.asset.loan',
        inverse_name='asset_id',
        string='Loans',
    )
    is_available = fields.Boolean(
        string='Available',
        compute='_compute_is_available',
        search='_search_is_available',
        store=False,
    )
    loan_count = fields.Integer(
        string='Loan Count',
        compute='_compute_loan_count',
        store=False,
    )

    _code_unique = models.Constraint(
        'UNIQUE(code)',
        'Asset code must be unique! This code is already in use by another asset.',
    )

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for record in self:
            if record.code:
                record.display_name = f"[{record.code}] {record.name}"
            else:
                record.display_name = record.name or ''

    @api.depends('loan_ids.state')
    def _compute_is_available(self):
        for asset in self:
            asset.is_available = not any(loan.state == 'borrowed' for loan in asset.loan_ids)

    def _search_is_available(self, operator, value):
        if operator not in ('=', '!='):
            return []
        borrowed_loans = self.env['office.asset.loan'].sudo().search([('state', '=', 'borrowed')])
        borrowed_asset_ids = borrowed_loans.mapped('asset_id').ids
        is_true = (operator == '=' and bool(value)) or (operator == '!=' and not bool(value))
        if is_true:
            return [('id', 'not in', borrowed_asset_ids)]
        return [('id', 'in', borrowed_asset_ids)]

    @api.depends('loan_ids')
    def _compute_loan_count(self):
        for asset in self:
            asset.loan_count = len(asset.loan_ids)

    def action_view_loans(self):
        self.ensure_one()
        return {
            'name': _('Loans for %s', self.display_name),
            'type': 'ir.actions.act_window',
            'res_model': 'office.asset.loan',
            'view_mode': 'list,form',
            'domain': [('asset_id', '=', self.id)],
            'context': {'default_asset_id': self.id},
        }

# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class OfficeAssetLoan(models.Model):
    _name = 'office.asset.loan'
    _description = 'Office Asset Loan'
    _order = 'loan_date desc, id desc'

    name = fields.Char(
        string='Loan Number',
        readonly=True,
        copy=False,
        default=lambda self: _('New'),
    )
    asset_id = fields.Many2one(
        comodel_name='office.asset',
        string='Asset',
        required=True,
        ondelete='restrict',
    )
    borrower_id = fields.Many2one(
        comodel_name='res.users',
        string='Borrower',
        required=True,
        default=lambda self: self.env.user,
    )
    loan_date = fields.Date(
        string='Loan Date',
        required=True,
        default=fields.Date.context_today,
    )
    due_date = fields.Date(
        string='Due Date',
        required=True,
    )
    return_date = fields.Date(
        string='Return Date',
        readonly=True,
    )
    purpose = fields.Char(string='Purpose')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, index=True)

    duration_days = fields.Integer(
        string='Duration (Days)',
        compute='_compute_duration_days',
        store=False,
    )
    is_overdue = fields.Boolean(
        string='Is Overdue',
        compute='_compute_is_overdue',
        store=False,
    )

    @api.depends('loan_date', 'due_date')
    def _compute_duration_days(self):
        for record in self:
            if record.loan_date and record.due_date:
                record.duration_days = (record.due_date - record.loan_date).days
            else:
                record.duration_days = 0

    @api.depends('state', 'due_date')
    def _compute_is_overdue(self):
        today = fields.Date.context_today(self)
        for record in self:
            record.is_overdue = bool(
                record.state == 'borrowed'
                and record.due_date
                and record.due_date < today
            )

    @api.constrains('loan_date', 'due_date')
    def _check_due_date(self):
        for record in self:
            if record.loan_date and record.due_date and record.due_date < record.loan_date:
                raise ValidationError(_(
                    'Due date cannot be earlier than loan date.'
                ))

    @api.onchange('loan_date')
    def _onchange_loan_date(self):
        if self.loan_date:
            if not self.due_date or self.due_date < self.loan_date:
                self.due_date = self.loan_date + timedelta(days=7)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('office.asset.loan') or _('New')
        return super().create(vals_list)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_draft_or_cancelled(self):
        for record in self:
            if record.state in ('borrowed', 'returned'):
                raise UserError(_(
                    'You cannot delete a loan that is currently in "%s" status. '
                    'Only draft or cancelled loans can be deleted.',
                    dict(self._fields['state'].selection).get(record.state, record.state)
                ))

    def action_borrow(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Only draft loans can be processed for borrowing.'))
            if record.asset_id.condition == 'damaged':
                raise UserError(_(
                    'Cannot borrow asset "%s" because its condition is Damaged.',
                    record.asset_id.name
                ))

            # Check if asset is already borrowed by another loan
            active_loans = self.sudo().search([
                ('id', '!=', record.id),
                ('asset_id', '=', record.asset_id.id),
                ('state', '=', 'borrowed'),
            ], limit=1)
            if active_loans:
                raise UserError(_(
                    'Asset "%s" is currently borrowed by another loan (%s). '
                    'Please wait until it is returned.',
                    record.asset_id.name,
                    active_loans.name,
                ))

            record.state = 'borrowed'

    def action_return(self):
        for record in self:
            if record.state != 'borrowed':
                raise UserError(_('Only borrowed loans can be returned.'))
            record.return_date = fields.Date.context_today(record)
            record.state = 'returned'

    def action_cancel(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Only draft loans can be cancelled.'))
            record.state = 'cancelled'

    def action_draft(self):
        for record in self:
            if record.state not in ('returned', 'cancelled'):
                raise UserError(_('Only returned or cancelled loans can be reset to Draft.'))
            record.return_date = False
            record.state = 'draft'

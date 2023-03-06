# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, models
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _check_lock_to_dates(self):
        """Prevent moves that are on or before lock to date.

        Advisors have more freedom then other users and are only constrained
        by the ficalyear_lock_to_date.
        Other users will also be restricted by the period_lock_to_date.
        """
        is_advisor = self.user_has_groups("account.group_account_manager")
        for move in self:
            advisor_lock_to_date = move.company_id.fiscalyear_lock_to_date
            user_lock_to_date = move.company_id.period_lock_to_date
            if is_advisor:
                lock_to_date = advisor_lock_to_date or False
            
            else:
                lock_to_date = (
                    max(user_lock_to_date, advisor_lock_to_date)
                    if user_lock_to_date and advisor_lock_to_date
                    else user_lock_to_date or advisor_lock_to_date or False
                )
            if lock_to_date and move.date <= lock_to_date:
                if is_advisor:
                    message = _(
                        "You cannot add/modify entries before and "
                        "inclusive of the lock to date %s"
                    ) % (lock_to_date)
                else:
                    message = _(
                        "You cannot add/modify entries before and "
                        "inclusive of the lock to date %s. "
                        "Check the company settings or ask someone "
                        "with the 'Adviser' role"
                    ) % (lock_to_date)
                raise ValidationError(message)
    
    def post(self):
        self._check_lock_to_dates()
        return super().post()
    
    def action_post(self):
        self._check_lock_to_dates()
        return super().action_post()

    def button_cancel(self):
        self._check_lock_to_dates()
        return super().button_cancel()

    def button_draft(self):
        self._check_lock_to_dates()
        return super().button_draft()

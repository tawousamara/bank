from odoo import models, api
import pandas as pd
import os

#! Downloading Pandas 


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def assign_arabic_names_from_excel(self):
        # module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        # #print(module_path)
        # excel_path = os.path.join(module_path, 'static/files', 'user.xlsx')

        # print('Loading .................')
        # try:
        #     df = pd.read_excel(excel_path)
        # except Exception as e:
        #     print(f"Failed to read Excel file: {str(e)}")
        #     return False

        # print('########### Iteration #############')
        # for index, row in df.iterrows():
        #     email = row.get('تسجيل الدخول')
        #     arabic_name = row.get('الاسم')

        #     if not email or not arabic_name:
        #         print(f"Missing data in row {index}. Email or Arabic name is missing.")
        #         continue 

        #     print('Search by email .................')
        #     user = self.search([('email', '=', email)], limit=1)

        #     if user:
        #         try:
        #             #print('assign')
        #             user.partner_id.write({'nom_arabe': arabic_name})
        #             print(f"Updated user {email} with Arabic name: {arabic_name}")
        #         except Exception as e:
        #             print(f"Failed to update user {email}: {str(e)}")
        #     else:
        #         print(f"*** The User with email: {email} doesnt exist ***")

        return True

from odoo import http
from odoo.http import request
import base64
List_items = [('1','هل العميل شخص مقرب سياسيا؟'),
              ('2','هل أحد الشركاء/المساهمين/مسير مقرب سياسيا؟'),
              ('3','هل العميل أو أحد الشركاء/المساهمين/مسير مقرب من البنك؟'),
              ('4','هل للعميل شركات زميلة / مجموعة؟'),
              ('5','المتعامل / أحد الشركاء مدرج ضمن القوائم السوداء'),
              ('6','المتعامل / أحد الشركاء مدرج ضمن قائمة الزبائن المتعثرين بمركزية المخاطر لبنك الجزائر')]
LIST = [('1', 'طلب التسهيلات ممضي من طرف المفوض القانوني عن الشركة'),
          ('2', 'الميزانيات لثلاث سنوات السابقة مصادق عليها من طرف المدقق المحاس'),
          ('3',
           ' الميزانية الافتتاحية و الميزانية المتوقعة للسنة المراد تمويلها موقعة من طرف الشركة (حديثة النشأة)'),
          ('4', 'مخطط تمويل الاستغلال مقسم الى أرباع السنة للسنة المراد تمويلها'),
          ('5',
           ' المستندات و الوثائق المتعلقة بنشاط الشركة ( عقود، صفقات ،  طلبيات ، ... )'),
          ('6', 'محاضر الجمعيات العادية و الغير العادية للأشخاص المعنويين'),
          ('7', 'نسخة مصادق عليها من السجل التجاري'),
          ('8', 'نسخة مصادق عليها من القانون الأساسي للشركة'),
          ('9', 'مداولة الشركاء أو مجلس الإدارة لتفويض المسير لطلب القروض البنكية'),
          ('10', 'نسخة مصادق عليها من النشرة الرسمية للإعلانات القانونية'),
          ('11', 'نسخة طبق الأصل لعقد ملكية أو استئجار المحلات ذات الاستعمال المهني'),
          ('12',
           ' نسخة طبق الأصل للشهادات الضريبية و شبه الضريبية حديثة (أقل من ثلاثة أشهر)'),
          ('13', 'استمارة كشف مركزية المخاطر ممضية من طرف ممثل الشركة (نموذج مرفق)'),
          ('14', 'آخر تقرير مدقق الحسابات'),
          ('15', 'Actif, Passif, TCR (N, N-1)'),
          ('16', 'Actif, Passif, TCR (N-2, N-3)')
          ]

list_situation = [
    ('1', 'حقوق الملكية'),
    ('2', 'مجموع الميزانية'),
    ('3', 'رقم الأعمال'),
    ('4', 'صافي الارباح')
]


class OpportunityController(http.Controller):

    @http.route('/opportunity/delete_apropos', type='json', auth='user', methods=['POST'], csrf=True)
    def delete_apropos(self):
        try:
            print('###############################################""')
            print('"""""""""""""""""""""""""""""""""""""')
            apropos_id = request.jsonrequest.get('apropos_id')
            print(apropos_id)
            print("000000000000000000000000000000000000000000")
            record = request.env['wk.partenaire'].sudo().browse(int(apropos_id))
            print('555555555555555555555555555')
            print(record)
            if record.exists():
                record.unlink()
                print("SUCCESS")
                return {'success': True}
            else:
                return {'success': False, 'error': 'Record not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @http.route(['/opportunity/form'], type='http', auth='public', website=True, csrf=True)
    def opportunity_form(self, **kwargs):
        step = kwargs.get('step', 'step1')
        opportunity_id = kwargs.get('opportunity_id', 0)
        activities = request.env['wk.activite'].search([])
        classifications = request.env['wk.classification'].search([])
        demandes = request.env['wk.type.demande'].search([])
        forme_jurs = request.env['wk.forme.jur'].search([])
        apropos_ids = request.env['wk.partenaire'].search([('lead_id', '=', int(opportunity_id))])
        gestion_ids = request.env['wk.gestion'].search([('lead_id', '=', int(opportunity_id))])
        taille_ids = request.env['wk.taille'].search([('lead_id', '=', int(opportunity_id))])
        situation_ids = request.env['wk.situation'].search([('lead_id', '=', int(opportunity_id))])
        fournisseur_ids = request.env['wk.fournisseur'].search([('lead_id', '=', int(opportunity_id))])
        client_ids = request.env['wk.client'].search([('lead_id', '=', int(opportunity_id))])
        company_ids = request.env['wk.companies'].search([('lead_id', '=', int(opportunity_id))])
        nationalites = request.env['res.country'].search([('to_show', '=', False)])
        garanties = request.env['wk.garanties'].search([])
        type_demande_ids = request.env['wk.product'].search([('for_branch', '=', True)])
        banque_ids = request.env['wk.banque'].search([])
        type_fin_ids = request.env['wk.fin.banque'].search([])
        type_payment_ids = request.env['wk.type.payment'].search([])
        if opportunity_id != 0:
            opportunity = request.env['crm.lead'].browse(int(opportunity_id))
        else:
            opportunity = False
        situation_fin = request.env['wk.situation.fin'].search([('lead_id', '=', int(opportunity_id))])

        values = {
            'step': opportunity.stage if opportunity else 'step1',
            'opportunity_id': opportunity_id if opportunity_id else 0,
            'activities': activities,
            'nationalites': nationalites,
            'classifications': classifications,
            'demandes': demandes,
            'forme_jurs': forme_jurs,
            'banque_ids': banque_ids,
            'type_fin_ids': type_fin_ids,
            'apropos_ids': apropos_ids,
            'gestion_ids': gestion_ids,
            'taille_ids': taille_ids,
            'kyc_ids': List_items,
            'situation_ids': situation_ids,
            'fournisseur_ids': fournisseur_ids,
            'client_ids': client_ids,
            'company_ids': company_ids,
            'garanties': garanties,
            'answers': [('oui', 'نعم'),
                        ('non', 'لا')],
            'type_demande_ids': type_demande_ids,
            'type_payment_ids': type_payment_ids,
        }

        for index, fin in enumerate(situation_fin):
            values[f'fin{index+1}_1'] = fin.year1
            values[f'fin{index+1}_2'] = fin.year2
            values[f'fin{index+1}_3'] = fin.year3
        return request.render('portal_salam.opportunity_form', values)

    @http.route('/opportunity/submit', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def opportunity_submit(self, **post):
        # Handle form submission and move to the next step
        opportunity_id = post.get('opportunity_id', 0)
        step = post.get('step', 'step1')
        if opportunity_id:
            opportunity = request.env['crm.lead'].browse(int(opportunity_id))
        else:
            opportunity = False
        if step == 'step1':
            if not opportunity:
                post['stage'] = post.get('step')
                post.pop('step')
                post.pop('opportunity_id')
                opportunity = request.env['crm.lead'].create(post)
            opportunity.write({
                'stage': 'step2'
            })
        elif step == 'step2':
            vals = post
            answers = {}
            details = {}
            infos = {}
            list_items_dict = {item[0]: item[1] for item in List_items}
            # Parcourir toutes les clés dans 'post'
            for key, value in post.items():
                if key.startswith('answer_'):
                    try:
                        # Extraire l'ID de la clé
                        record_id = int(key.split('_')[1])
                        answers[record_id] = value
                    except ValueError:
                        continue
                elif key.startswith('detail_'):
                    try:
                        # Extraire l'ID de la clé
                        record_id = int(key.split('_')[1])
                        details[record_id] = value
                    except ValueError:
                        continue
                elif key.startswith('info_'):
                    try:
                        # Extraire l'ID de la clé
                        record_id = int(key.split('_')[1])
                        infos[record_id] = value
                    except ValueError:
                        continue

            # Liste pour stocker les enregistrements à créer
            records_to_create = []

            # Assurez-vous que les IDs correspondent entre les réponses, les détails et les informations
            for record_id in answers.keys():
                record = {
                    'answer': answers[record_id],
                    'detail': details.get(record_id, ''),
                    'info': list_items_dict.get(str(record_id), ''),
                    'lead_id': opportunity.id
                }
                records_to_create.append(record)
            if records_to_create:
                request.env['wk.kyc.details'].create(records_to_create)

                opportunity.write({
                    'stage': 'step3'
                })
        elif step == 'step3':
            request.env['wk.situation.fin'].search([('lead_id', '=', opportunity.id)]).unlink()
            for i in range(1, 5):
                element = request.env['wk.situation.fin'].search([('lead_id', '=', opportunity.id),
                                                                  ('sequence', '=', i+1)])
                # Loop through fin1, fin2, fin3, fin4
                record_vals = {
                    'type': post.get(f'description_{i}'),
                    'sequence': i+1,
                    'year1': post.get(f'fin{i}_1'),
                    'year2': post.get(f'fin{i}_2'),
                    'year3': post.get(f'fin{i}_3'),
                    'lead_id': opportunity.id,
                }
                if not element:
                    request.env['wk.situation.fin'].create(record_vals)
                else:
                    request.env['wk.situation.fin'].write(record_vals)
            opportunity.write({
                'stage': 'step4'
            })
        elif step == 'step4':
            documents = []
            document_dict = {item[0]: item[1] for item in LIST}
            # Parcourir toutes les clés dans 'post'
            for key, value in post.items():
                if key.startswith('document_'):
                    try:
                        # Extraire l'ID de la clé
                        document_id = int(key.split('_')[1])
                        file = value
                        documents.append({
                            'list_document': str(document_id),
                            'list_doc': document_dict.get(str(document_id), ''),
                            'document': base64.b64encode(file.read()) if file else False,
                            'lead_id': opportunity.id
                        })
                    except ValueError:
                        continue
            if documents:
                # Créer les enregistrements dans le modèle cible
                if not opportunity.documents:
                    request.env['wk.document.check'].create(documents)
                else:
                    for doc in documents:
                        exist_doc = opportunity.documents.filtered(lambda l: l.list_document == doc['list_document'])
                        exist_doc.write(doc)
            opportunity.write({
                'stage': 'step5'
            })
        return request.redirect('/opportunity/form?opportunity_id=%d&step=%s' % (opportunity.id, opportunity.stage))

    @http.route('/create/apropos', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def create_apropos(self, **post):
        # Handle form submission and move to the next step
        opportunity_id = int(post.get('opportunity_id', 0))
        step = post.get('step', 'step1')
        post['lead_id'] = opportunity_id  # Ensure that the opportunity ID is correctly set
        vals = post
        vals.pop('opportunity_id')
        vals.pop('step')
        apropos_line = request.env['wk.partenaire'].create(vals)
        opportunity = request.env['crm.lead'].browse(int(opportunity_id))
        return request.redirect('/opportunity/form?opportunity_id=%d&step=%s' % (opportunity_id, opportunity.stage))

    @http.route('/create/gestion', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def create_gestion(self, **post):
        # Handle form submission and move to the next step
        opportunity_id = int(post.get('opportunity_id', 0))
        step = post.get('step', 'step1')
        post['lead_id'] = opportunity_id  # Ensure that the opportunity ID is correctly set
        vals = post
        vals.pop('opportunity_id')
        vals.pop('step')
        gestion_line = request.env['wk.gestion'].create(vals)
        opportunity = request.env['crm.lead'].browse(int(opportunity_id))
        return request.redirect('/opportunity/form?opportunity_id=%d&step=%s' % (opportunity_id, opportunity.stage))

    @http.route('/create/taille', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def create_taille(self, **post):
        # Handle form submission and move to the next step

        opportunity_id = int(post.get('opportunity_id', 0))
        step = post.get('step', 'step1')
        post['lead_id'] = opportunity_id  # Ensure that the opportunity ID is correctly set
        vals = post
        selected_garanties = post.get('garanties')

        selected_garanties = []
        delete_keys = []
        for key, value in post.items():
            if key.startswith('garantie_'):
                try:
                    # Extraire l'ID de la clé
                    delete_keys.append(key)
                    garantie_id = int(key.split('_')[1])
                    selected_garanties.append(garantie_id)
                except ValueError:
                    # Ignorer les clés qui ne peuvent pas être converties en entier
                    continue
        for item in delete_keys:
            vals.pop(item)
        if selected_garanties:
            vals['garanties'] = [(6, 0, selected_garanties)]
        vals.pop('opportunity_id')
        vals.pop('step')
        gestion_line = request.env['wk.taille'].create(vals)
        opportunity = request.env['crm.lead'].browse(int(opportunity_id))
        return request.redirect('/opportunity/form?opportunity_id=%d&step=%s' % (opportunity_id, opportunity.stage))

    @http.route('/create/situation', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def create_situation(self, **post):
        # Handle form submission and move to the next step

        opportunity_id = int(post.get('opportunity_id', 0))
        step = post.get('step', 'step1')
        post['lead_id'] = opportunity_id  # Ensure that the opportunity ID is correctly set
        vals = post
        vals.pop('opportunity_id')
        vals.pop('step')
        situation_line = request.env['wk.situation'].create(vals)
        opportunity = request.env['crm.lead'].browse(int(opportunity_id))
        return request.redirect('/opportunity/form?opportunity_id=%d&step=%s' % (opportunity_id, opportunity.stage))

    @http.route('/create/fournisseur', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def create_fournisseur(self, **post):
        # Handle form submission and move to the next step

        opportunity_id = int(post.get('opportunity_id', 0))
        step = post.get('step', 'step1')
        post['lead_id'] = opportunity_id  # Ensure that the opportunity ID is correctly set
        vals = post
        selected_payment = []
        delete_keys = []
        for key, value in post.items():
            if key.startswith('payment_'):
                try:
                    # Extraire l'ID de la clé
                    delete_keys.append(key)
                    garantie_id = int(key.split('_')[1])
                    selected_payment.append(garantie_id)
                except ValueError:
                    # Ignorer les clés qui ne peuvent pas être converties en entier
                    continue
        for item in delete_keys:
            vals.pop(item)
        if selected_payment:
            vals['type_payment'] = [(6, 0, selected_payment)]
        vals.pop('opportunity_id')
        vals.pop('step')
        situation_line = request.env['wk.fournisseur'].create(vals)
        opportunity = request.env['crm.lead'].browse(int(opportunity_id))
        return request.redirect('/opportunity/form?opportunity_id=%d&step=%s' % (opportunity_id, opportunity.stage))

    @http.route('/create/client', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def create_client(self, **post):
        # Handle form submission and move to the next step
        opportunity_id = int(post.get('opportunity_id', 0))
        step = post.get('step', 'step1')
        post['lead_id'] = opportunity_id  # Ensure that the opportunity ID is correctly set
        vals = post
        selected_payment = []
        delete_keys = []
        for key, value in post.items():
            if key.startswith('payment_'):
                try:
                    # Extraire l'ID de la clé
                    delete_keys.append(key)
                    garantie_id = int(key.split('_')[1])
                    selected_payment.append(garantie_id)
                except ValueError:
                    # Ignorer les clés qui ne peuvent pas être converties en entier
                    continue
        for item in delete_keys:
            vals.pop(item)
        if selected_payment:
            vals['type_payment'] = [(6, 0, selected_payment)]
        vals.pop('opportunity_id')
        vals.pop('step')
        situation_line = request.env['wk.client'].create(vals)
        opportunity = request.env['crm.lead'].browse(int(opportunity_id))
        return request.redirect('/opportunity/form?opportunity_id=%d&step=%s' % (opportunity.id, opportunity.stage))


    @http.route('/create/company', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def create_company(self, **post):
        # Handle form submission and move to the next step

        opportunity_id = int(post.get('opportunity_id', 0))
        step = post.get('step', 'step1')
        post['lead_id'] = opportunity_id  # Ensure that the opportunity ID is correctly set
        vals = post
        vals.pop('opportunity_id')
        vals.pop('step')
        situation_line = request.env['wk.companies'].create(vals)
        opportunity = request.env['crm.lead'].browse(int(opportunity_id))
        return request.redirect('/opportunity/form?opportunity_id=%d&step=%s' % (opportunity_id, opportunity.stage))

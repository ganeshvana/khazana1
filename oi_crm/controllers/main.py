# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
from werkzeug.exceptions import Forbidden, NotFound
from werkzeug.urls import url_decode, url_encode, url_parse
import werkzeug

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.fields import Command
from odoo.http import request
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.addons.website.controllers import main
from odoo.addons.website.controllers.form import WebsiteForm
from odoo.osv import expression
from odoo.tools.json import scriptsafe as json_scriptsafe
_logger = logging.getLogger(__name__)
import hashlib
from odoo import http, models, _
from werkzeug.urls import url_encode, url_join
# import MySQLdb
# import MySQLdb.cursors

class WebsiteSale(http.Controller):
    
    @http.route('/shop/payment/validate', type='http', auth="public", website=True, sitemap=False)
    def shop_payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        print(request, "request-----")
        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        if transaction_id:
            tx = request.env['payment.transaction'].sudo().browse(transaction_id)
            assert tx in order.transaction_ids()
        elif order:
            tx = order.get_portal_last_transaction()
        else:
            tx = None

        if not order or (order.amount_total and not tx):
            return request.redirect('/shop')

        if order and not order.amount_total and not tx:
            order.with_context(send_email=False).action_confirm()
            return request.redirect(order.get_portal_url())

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset()
        if tx and tx.state == 'draft':
            return request.redirect('/shop')
        if request.env.user.crm_id and order:
            order.opportunity_id = request.env.user.crm_id.id
            order.partner_id = request.env.user.crm_id.partner_id.id
            order.state = 'draft'
            addr = request.env.user.crm_id.partner_id.address_get(['delivery', 'invoice'])
            order.partner_invoice_id = addr['invoice']
            order.partner_shipping_id = addr['delivery']
        PaymentPostProcessing.remove_transactions(tx)
        return request.redirect('/shop/confirmation')
    
    @http.route(['/on_click_eterna_home'], type='http', auth="public", website=True)
    def al_eterna_home_redirect(self, line_id=None, add_partner=None, **kw):
        # cr, uid, context , pool = request.cr, request.uid, request.context , request.registry
        uid = 0
        print(request, "request======")
        cart_id = 25
        user_name = 'blau_user'
        pwd = 'blau@123'
        user_obj = request.env['res.users']
        searched_id = user_obj.search([('id','=',uid)])
        mail = None
        name = None
        phone = None
        user_val = None
        if searched_id:
            user_val = user_obj.browse(searched_id[0].id)
            mail = user_val.partner_id.email
            if mail == None or mail == False:
                mail = user_val.login
            name = user_val.partner_id.name 
            phone = user_val.partner_id.phone
            if phone == None or phone == False:
                phone = user_val.partner_id.mobile
        m = hashlib.md5()
        m.update(user_name.encode('utf-8'))
        md5username = m.hexdigest()
        # company = pool.get('ir.model.data').get_object_reference(cr, SUPERUSER_ID, 'base', 'main_company')
        return_url = ''
        try:
            return_url = 'http://localhost:8069/'
            request.session['req_lead_id'] = cart_id
        except:
            pass
        # if user_val:
        #     if user_val.company_id.id == company[1]:
        #         return http.redirect_with_hash("http://blau60.com/stagging/token-confirm.php?cart_id=%s&username=%s&email=%s&name=%s&ph=%s" %(cart_id,md5username,mail,name,phone))
        # return {
        #         'type': 'ir.actions.act_url',
        #         'name': "Blau",
        #         'target': '_blank',
        #         'url': "http://blau60.com/token-confirm.php?cart_id=25455&username=21232f297a57a5a743894a0e4a801fc3&email=info@khazanagroup.in&name=Administrator&ph=9949594004"
        #     }
        return werkzeug.utils.redirect("https://blau60.com/token-confirm.php?cart_id=25455&username=21232f297a57a5a743894a0e4a801fc3&email=info@khazanagroup.in&name=Administrator&ph=9949594004")

    @http.route(['/fetch_from_eterna_home','/fetch_from_eterna_home/<model("crm.lead"):lead>'], type='http', auth="public")
    def al_fetch_details_from_eterna(self, line_id=None,**kw):
        # cr, uid, context , pool = request.cr, request.uid, request.context , request.registry
        cart_id = 25455
        categ_obj= request.env['product.public.category']
        lead_obj = request.env['crm.lead']
        prod_tmpl_obj = request.env['product.template']
        product_obj = request.env['product.product']
        # config_obj = request.env['sale.advance.settings']
        # config_ids = config_obj.search([])
        server_ip = None
        server_ip = "166.62.27.58"
        #server_ip = "166.62.27.58"
        print("======sssssssssss")
        try:
            connection = MySQLdb.connect("172.104.35.195","admin","admin@blau123", "blauliving")
        except Exception as e:
            return "Exception : DB Access Failed<br>"+str(e)
        #connection = MySQLdb.connect(host = str(server_ip), user = "odoouser", passwd = "T6gXt33d", db = "eterna_home",cursorclass=MySQLdb.cursors.DictCursor)
        cursor = connection.cursor ()
        cursor.execute ("SET SESSION sql_mode = ''")
        #cursor.execute ("select id as id,oid as oid,uwid as uwid,cart_id as lead_id,title as product_name,qty as qty,amount as price,description as description,exterior_images as img1 ,customized_images as img2 from eterna_line_item where cart_id =%s and sync=0",[cart_id])
        cursor.execute ("select sync as is_updated, id as id,oid as oid,uwid as uwid,cart_id as lead_id,title as product_name,qty as qty,amount as price,description as description,exterior_images as img1 ,customized_images as img2 from eterna_line_item where cart_id =%s",[cart_id])
        data = cursor.fetchall()
        print(data, "=====data")
        #img_path='/www.blauliving.com/'
        img_path='/www.blau60.com/'
        if not data:
            _logger.info("*****Fetch Details are not found*****")
        if data!=None:
            for val in data:
                _logger.info("product line details : %s,%s",val['id'],val['is_updated'])
                lead_line_val={}
                eterna_line_id=False
                eterna_order_id=False
                specification_id=False
                product_name=False
                description=''
                exterior_img=None
                cutomized_img=None
                quantity=0
                description1=''
                size=''
                price=0.0
                if val['is_updated']==1:
                    if val['id']:
                        eterna_line_id=val['id']
                        if eterna_line_id!=None:
                            lead_line_val['eterna_line_id']=eterna_line_id
                    if val['qty']:
                        quantity=val['qty']
                        lead_line_val['product_uom_qty']=quantity
                    if val['lead_id']:
                        lead_id=val['lead_id']
                        if lead_id!=None and lead_id!=False:
                            lead_line_val['product_lead_id']=lead_id
                    if val['price']:
                        price=val['price']
                        lead_line_val['price_unit']=price
                else:    
                    if val['id']:
                        eterna_line_id=val['id']
                        if eterna_line_id!=None:
                            lead_line_val['eterna_line_id']=eterna_line_id
                    if val['oid']:
                        eterna_order_id=val['oid']
                        if eterna_order_id!=None and eterna_order_id!=False:
                            lead_line_val['eterna_order_id']=eterna_order_id
                    if val['lead_id']:
                        lead_id=val['lead_id']
                        if lead_id!=None and lead_id!=False:
                            lead_line_val['product_lead_id']=lead_id
                    if val['uwid']:
                        eterna_uwid=val['uwid']
                        if eterna_uwid!=None:
                            lead_line_val['eterna_uwid']=eterna_uwid
                    if val['product_name']:
                        categ_name=''
                        product_name=''
                        categ_id=''
                        combine_name=val['product_name']
                        combine_name=combine_name.split('&')
                        for value in combine_name:
                            value1=value.split('=')
                            if value1[0]=='room_name':
                                categ_name=value1[1]
                                categ_name=str(categ_name.replace('+',' ')).strip()
                            elif value1[0]=='title':
                                product_name1=value1[1]
                                product_name+=str(product_name1.replace('+',' ')).strip()
                            else:
                                if value1[0]=='wardrobe_type':
                                    wardrobe_type=value1[1]
                                    wardrobe_type=str(wardrobe_type.replace('+',' ')).strip()
                                    lead_line_val['eterna_wardrobe_type']=wardrobe_type
                                    
                                    product_name=str(wardrobe_type)+' '+str(product_name)
                                if value1[0]=='room_id':
                                    categ_id=value1[1]
                        searched_categ_id=categ_obj.search(cr,uid,[('eterna_categ_id','=',int(categ_id))],context=context)
                        if not searched_categ_id:
                            searched_id=categ_obj.search(cr,uid,[('name','ilike',str(categ_name).strip())],context=context)
                            if searched_id:
                                specification_id=searched_id[0]
                                lead_line_val['specification_id']=specification_id
                                categ_obj.write(cr,SUPERUSER_ID,searched_id[0],{'eterna_categ_id':int(categ_id)},context=context)
                        else:
                            specification_id=searched_categ_id[0]
                            lead_line_val['specification_id']=specification_id
                        if product_name!='':
                            product_name=product_name.replace('%2B','+')
                            searched_product=prod_tmpl_obj.search(cr,uid,[('name','=',product_name),('type','=','consu')],context=context)
                            taxes_id = []
                            company_ids = pool['res.company'].search(cr, SUPERUSER_ID, [])
                            company_data = pool['res.company'].browse(cr, SUPERUSER_ID, company_ids)
                            ir_values = pool['ir.values']
                            for company in company_data:
                                taxes_id += ir_values.get_default(cr, SUPERUSER_ID, 'product.template', 'taxes_id', company_id = company.id)
                            if searched_product:
                                lead_line_val['product_template_id']=searched_product[0]
                                prod_id=product_obj.search(cr,uid,[('product_tmpl_id','=',searched_product[0])],context=context)
                                if prod_id:
                                    for pro_val in product_obj.browse(cr,uid,prod_id,context=context):
                                        if pro_val.website_published==True:
                                            if taxes_id:
                                                product_obj.write(cr, SUPERUSER_ID, pro_val.id, {'website_published':False,'tax_id':[[6, False, taxes_id]]})
                                            else:
                                                product_obj.write(cr,SUPERUSER_ID,pro_val.id,{'website_published':False})
                                    lead_line_val['product_id']=prod_id[0]
                            else:
                                if taxes_id:
                                    created_id=prod_tmpl_obj.create(cr,SUPERUSER_ID,{'is_blau_product':True,'website_published':False,'name':product_name, 'taxes_id':[[6, False, taxes_id]],'type':'consu'},context=context)
                                else:
                                    created_id=prod_tmpl_obj.create(cr,SUPERUSER_ID,{'is_blau_product':True,'website_published':False,'name':product_name,'type':'consu'},context=context)
                                lead_line_val['product_template_id']=created_id
                                prod_id=product_obj.search(cr,uid,[('product_tmpl_id','=',created_id)],context=context)
                                for pro_val in product_obj.browse(cr,uid,prod_id,context=context):
                                    product_obj.write(cr,SUPERUSER_ID,pro_val.id,{'website_published':False})
                                product_id=prod_id[0]
                                if product_id:
                                    lead_line_val['product_id']=product_id
                        else:
                            lead_line_val['product_id']=False
                    if val['qty']:
                        quantity=val['qty']
                        lead_line_val['product_uom_qty']=quantity
                    if val['price']:
                        price=val['price']
                        lead_line_val['price_unit']=price
                    #if val['description']:
                        #description=val['description']
                        #descrip=''
                        #describe=description.replace('<p>','')
                        #dimension=describe.split('</p>')
                        #description1=describe.replace('</p>','\n')
                        #lead_line_val['eterna_description']=description1
                    if val['description']:
                        description=val['description']
                        descrip=''
                        describe=description.replace('<p>','')
                        dimension=describe.split('</p>')
                        new_describe=''
                        for dime in dimension:
                            new_dime=''
                            new_dime1=''
                            dime1=dime.split(':')
                            #print dime1,dime1[1],dime[0]
                            if dime1[0].strip()=='Dimension':
                                new_dime1=dime1[1][0:15]
                                new_dime=dime1[0]+':'+new_dime1
                            else:
                                if len(dime1)>1:
                                    new_dime=dime1[0]+':'+dime1[1]
                                else:
                                    new_dime=dime1[0]
                            new_describe+=str(new_dime)+'\n'
                        description1=describe.replace('</p>','\n')
                        lead_line_val['eterna_description']=new_describe
                    if val['img1']:
                        try:
                            #img_path='http://'+str(server_ip)+'/elevate/'
                            #img_path='http://www.blauliving.com/'
                            img_path='http://www.blau60.com/'
                            img_path=img_path+str(val['img1'])
                            exterior_img=base64.encodestring(urllib2.urlopen(img_path).read())
                            #product_obj.write(cr,SUPERUSER_ID,[lead_line_val['product_id']],{'image_medium':exterior_img},context=context)
                            lead_line_val['eterna_image']=exterior_img
                        except Exception as a:
                            _logger.info("Getting Image details Failed: %s",a)
                            try:
                                #img_path='http://eternahome.com/elevate/'
                                #img_path='http://www.blauliving.com/'
                                img_path='http://www.blau60.com/'
                                img_path=img_path+str(val['img1'])
                                exterior_img=base64.encodestring(urllib2.urlopen(img_path).read())
                                lead_line_val['eterna_image']=exterior_img
                                #product_obj.write(cr,SUPERUSER_ID,[lead_line_val['product_id']],{'image_medium':exterior_img},context=context)
                            except Exception as c:
                                _logger.info("Second time Getting Image details Failed: %s",c)
                                exterior_img=None
                    if val['img2']:
                        try:
                            #img_path='http://localhost/elevate/'
                            #img_path='http://'+str(server_ip)+'/elevate/'
                            #img_path='http://www.blauliving.com/'
                            img_path='http://www.blau60.com/'
                            img_path=img_path+str(val['img2'])
                            cutomized_img=base64.encodestring(urllib2.urlopen(img_path).read())
                            cutomized_img=tools.image_resize_image_medium(rec.cutomized_img)
                            lead_line_val['eterna_custom_image']=cutomized_img
                            #product_obj.write(cr,SUPERUSER_ID,[lead_line_val['product_id']],{'eterna_image':cutomized_img},context=context)
                        except Exception as i:
                            _logger.info("Getting Image-22 details Failed: %s",i)
                            try:
                                #img_path='http://eternahome.com/elevate/'
                                #img_path='http://www.blauliving.com/'
                                img_path='http://www.blau60.com/'
                                img_path=img_path+str(val['img2'])
                                cutomized_img=base64.encodestring(urllib2.urlopen(img_path).read())
                                lead_line_val['eterna_custom_image']=cutomized_img
                                #product_obj.write(cr,SUPERUSER_ID,[lead_line_val['product_id']],{'eterna_image':cutomized_img},context=context)
                            except Exception as i2:
                                _logger.info("Second time Getting Image-22 details Failed: %s",i2)
                                cutomized_img=None
                if lead_line_val:
                    if val['is_updated']==1:
                        searched_line=pool.get('product.lead').search(cr,uid,[('product_lead_id','=',lead_line_val['product_lead_id']),('eterna_line_id','=',lead_line_val['eterna_line_id'])],context=context)
                        if searched_line!=[]:
                            browse_val=pool.get('product.lead').browse(cr,uid,searched_line[0],context=context)
                            if browse_val.product_uom_qty!=lead_line_val['product_uom_qty'] or browse_val.price_unit!=lead_line_val['price_unit']:
                                _logger.info("Successfully Updated eterna product details")
                                pool.get('product.lead').write(cr,uid,[browse_val.id],lead_line_val,context=context)
                    else:
                        if lead_line_val['product_id']!=False:
                            searched_line=pool.get('product.lead').search(cr,uid,[('product_id','=',lead_line_val['product_id']),('product_lead_id','=',lead_line_val['product_lead_id']),('eterna_line_id','=',lead_line_val['eterna_line_id'])],context=context)
                            if searched_line==[]:
                                pool.get('product.lead').create(cr,uid,lead_line_val,context=context)
                                _logger.info("Successfully fetched eterna product details")
                                product_obj.write(cr,SUPERUSER_ID,[lead_line_val['product_id']],{'product_code':size},context=context)
                                cursor.execute ("update eterna_line_item set sync =%s , cart_status=%s where id =%s ",[int(1),'updated',int(lead_line_val['eterna_line_id'])])
                                connection.commit()
                            #if exterior_img!=None and cutomized_img!=None:
                                #product_obj.write(cr,SUPERUSER_ID,[lead_line_val['product_id']],{'image_medium':exterior_img,'eterna_image':cutomized_img,'price_extra_custom':lead_line_val['price_unit'],'description_sale':description1},context=context)
                            #else:
                            #if exterior_img!=None:
                                #product_obj.write(cr,SUPERUSER_ID,[lead_line_val['product_id']],{'image_medium':exterior_img},context=context)
                            #if cutomized_img!=None:
                                #product_obj.write(cr,SUPERUSER_ID,[lead_line_val['product_id']],{'eterna_image':cutomized_img},context=context)
                            #product_obj.write(cr,SUPERUSER_ID,[lead_line_val['product_id']],{'price_extra_custom':lead_line_val['price_unit'],'description_sale':description1},context=context)
                    
                    #return http.redirect_with_hash("http://localhost/elevate/logout.php")
        return http.redirect_with_hash("/shop/cart")

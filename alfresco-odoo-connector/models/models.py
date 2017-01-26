# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import os
import base64
import cmis_integration
from odoo.exceptions import UserError, ValidationError

root_path = os.path.dirname(os.path.abspath(__file__))


class alfrescoupload(models.Model):
    _name = 'alfresco.upload'
    directory_name = fields.Char(string='Directory Name')
    upload_file_data = fields.Many2many('ir.attachment', 'class_ir_attachments_rel', 'class_id', 'attachment_id', 'Attachments')
    user_name = fields.Many2one('alfresco.credentials', string='Username',required=True,default=lambda self: self.env['alfresco.credentials'].search([('name', '!=', [])], limit=1))

    @api.model
    def create(self, vals):
        res = super(alfrescoupload, self).create(vals)
        alfresco_user_name = res.user_name.name
        alfresco_url =  res.user_name.url
        alfresco_pwd = res.user_name.pass_word
        cms_obj = cmis_integration.CMISController(alfresco_url, alfresco_user_name, alfresco_pwd)
        for each in res.upload_file_data:
            attach_file_name = each.name
            attach_file_data = each.sudo().read(['datas_fname', 'datas'])
            directory_path = os.path.join(root_path, "files")
            if not os.path.isdir(directory_path):
                    os.mkdir(directory_path)
            file_path = os.path.join("files", attach_file_name)
            complete_path = os.path.join(root_path, file_path)
            with open(complete_path , "w") as text_file:
                text_file.write(str(base64.decodestring(attach_file_data[0]['datas'])))
            if res.directory_name==False:
                out_put_flag = cms_obj.upload_file(complete_path , overwrite_flag = True)
                if out_put_flag==False:
                    raise ValidationError(_('Some error occured while connecting with alfresco.'))
            else:
                out_put_flag = cms_obj.create_directory(res.directory_name)
                if out_put_flag==False:
                    raise ValidationError(_('Some error occured while connecting with alfresco.'))
                out_put_flag = cms_obj.upload_file(complete_path,directory_name = res.directory_name, overwrite_flag=True)
                if out_put_flag==False:
                    raise ValidationError(_('Some error occured while connecting with alfresco.'))

        return res

    @api.multi
    def unlink(self):
        for each in self:
            alfresco_user_name = each.user_name.name
            alfresco_url =  each.user_name.url
            alfresco_pwd = each.user_name.pass_word
            cms_obj = cmis_integration.CMISController(alfresco_url, alfresco_user_name, alfresco_pwd)
            directory_id = each.id
            direct_name = self.env['alfresco.upload'].search([('id','=',directory_id)]).directory_name
            out_put_flag = cms_obj.delete_complete_folder(direct_name)
            if out_put_flag==False:
                raise ValidationError(_('Some error occured while connecting with alfresco.'))

        return models.Model.unlink(self)


    @api.multi
    def write(self,vals):


        change_keys_array =  vals.keys()
        directory_change_flag = False
        directory_to_be_deleted = self.directory_name
        if 'directory_name' in change_keys_array:
            directory_change_flag = True
        old_files_array = []
        old_file_ids = self.read()[0]['upload_file_data']
        for each in old_file_ids:
            file_name_get = self.env['ir.attachment'].search([('id','=',each)]).name
            old_files_array.append(file_name_get)
        res = super(alfrescoupload, self).write(vals)
        new_files_attach_array = []
        for each in self.upload_file_data:
            file_name_get = each.name
            new_files_attach_array.append(file_name_get)
        alfresco_user_name = self.user_name.name
        alfresco_url =  self.user_name.url
        alfresco_pwd = self.user_name.pass_word
        cms_obj = cmis_integration.CMISController(alfresco_url, alfresco_user_name, alfresco_pwd)
        if directory_change_flag:
            out_put_flag = cms_obj.delete_complete_folder(directory_to_be_deleted)
            if out_put_flag==False:
                raise ValidationError(_('Some error occured while connecting with alfresco.'))

        for file_name in old_files_array:
            out_put_flag = cms_obj.remove_file_instance(directory_to_be_deleted,file_name)
            if out_put_flag==False:
                raise ValidationError(_('Some error occured while connecting with alfresco.'))

        for each in self.upload_file_data:
            attach_file_name = each.name
            if attach_file_name in new_files_attach_array:
                attach_file_data = each.sudo().read(['datas_fname', 'datas'])
                directory_path = os.path.join(root_path, "files")
                if not os.path.isdir(directory_path):
                    os.mkdir(directory_path)
                file_path = os.path.join("files", attach_file_name)

                complete_path = os.path.join(root_path, file_path)
                with open(complete_path , "w") as text_file:
                    text_file.write(str(base64.decodestring(attach_file_data[0]['datas'])))
                if self.directory_name==False:
                    out_put_flag = cms_obj.upload_file(complete_path , overwrite_flag = True)
                    if out_put_flag==False:
                        raise ValidationError(_('Some error occured while connecting with alfresco.'))

                else:
                    out_put_flag = cms_obj.create_directory(self.directory_name)
                    if out_put_flag==False:
                        raise ValidationError(_('Some error occured while connecting with alfresco.'))
                    out_put_flag = cms_obj.upload_file(complete_path,directory_name = self.directory_name, overwrite_flag=True)
                    if out_put_flag==False:
                        raise ValidationError(_('Some error occured while connecting with alfresco.'))

        return res

class alfrescocredentials(models.Model):
    _name = 'alfresco.credentials'
    url = fields.Char(string='URL',required=True)
    name = fields.Char(string='Username', required=True)
    pass_word = fields.Char(string='Password', required=True)
    _sql_constraints = [
                     ('field_unique', 
                      'unique(user_name)',
                      'Choose another value - it has to be unique!')]



###############################################################################
#
# Copyright (C) 2007-TODAY Tiny ERP Pvt Ltd. All Rights Reserved.
# Modified by Raphael Alla
#
# $Id$
#
# Developed by Tiny (http://openerp.com) and Axelor (http://axelor.com).
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the 
# Free Software Foundation, Inc., 59 Temple Place - Suite 330, 
# Boston, MA  02111-1307, USA.
#
###############################################################################

import time
import math

from openobject.tools import expose, validate, redirect
from openerp import validators

import cherrypy

from openobject import tools
from openerp.utils import common
from openobject.i18n import format

#from openerp.tinyres import TinyResource
from openerp.utils import rpc, TinyDict
from openerp.controllers.form import Form
import openerp.widgets as tw

class BI_Form(Form):
    _cp_path = '/designer/bi_form'
       
    def create_form(self, params, tg_errors=None):
        if tg_errors:
            return cherrypy.request.terp_form

        params.offset = params.offset or 0
        params.limit = params.limit or 20
        params.count = params.count or 0
        params.view_type = params.view_type or params.view_mode[0]
        if not params.has_key('_terp_bi_type'):
            params['_terp_bi_type'] = 'false'
            
        form = tw.form_view.ViewForm(params, name="view_form", action="/bi_form/save")
        if 'remember_notebook' in cherrypy.session:
            cherrypy.session.pop('remember_notebook')
        else:
            self.del_notebook_cookies()
        return form

    @expose(template="/tinybi/widgets/templates/designer_view_popup.mako")
    def create(self, params, tg_errors=None):

        params.view_type = params.view_type or params.view_mode[0]
        if params.view_type == 'tree':
            params.editable = True

        form = self.create_form(params, tg_errors)
        
        editable = form.screen.editable
        mode = form.screen.view_type
        id = form.screen.id
        ids = form.screen.ids

        buttons = TinyDict()    # toolbar
        links = TinyDict()      # bottom links (customise view, ...)
        
        buttons.new = not editable or mode == 'tree'
        buttons.edit = not editable and mode == 'form'
        buttons.save = editable and mode == 'form'
        buttons.cancel = editable and mode == 'form'
        buttons.delete = not editable and mode == 'form'
        buttons.pager =  mode == 'form' # Pager will visible in edit and non-edit mode in form view.

        buttons.search = 'tree' in params.view_mode and mode != 'tree'
        buttons.graph = 'graph' in params.view_mode and mode != 'graph'
        buttons.form = 'form' in params.view_mode and mode != 'form'
        buttons.calendar = 'calendar' in params.view_mode and mode != 'calendar'
        buttons.gantt = 'gantt' in params.view_mode and mode != 'gantt'
        buttons.can_attach = id and mode == 'form'
        buttons.has_attach = buttons.can_attach # and self._has_attachments(params.model, id, mode)
        buttons.i18n = not editable and mode == 'form'

        target = params.context.get('_terp_target')
        buttons.toolbar = target != 'new' and not form.is_dashboard

        links.view_manager = True
        links.workflow_manager = False
        
        proxy = rpc.RPCProxy('workflow')
        wkf_ids = proxy.search([('osv', '=', params.model)], 0, 0, 0, rpc.session.context)
        links.workflow_manager = (wkf_ids or False) and wkf_ids[0]
        
        pager = None
        if buttons.pager:
            pager = tw.pager.Pager(id=form.screen.id, ids=form.screen.ids, offset=form.screen.offset, 
                                   limit=form.screen.limit, count=form.screen.count, view_type=params.view_type)

        if not params.load_counter:
            params.load_counter=1
        return dict(form=form, params=params,pager=pager, buttons=buttons, links=links, show_header_footer=False)

    @expose()
    def edit(self, model, id=False, type = 'false', ids=None, view_ids=None, view_mode=['form', 'tree'], 
             source=None, domain=[], context={}, offset=0, limit=20, count=0, search_domain=None):

        params, data = TinyDict.split({'_terp_model': model,
                                       '_terp_id' : id,
                                       '_terp_ids' : ids,
                                       '_terp_view_ids' : view_ids,
                                       '_terp_view_mode' : view_mode,
                                       '_terp_source' : source,
                                       '_terp_domain' : domain,
                                       '_terp_context' : context,
                                       '_terp_offset': offset,
                                       '_terp_limit': limit,
                                       '_terp_count': count,
                                       '_terp_search_domain': search_domain,
                                       '_terp_bi_type': type})
        params.editable = True
        params.view_type = 'form'

        if params.view_mode and 'form' not in params.view_mode:
            params.view_type = params.view_mode[-1]
            
        if params.view_type == 'tree':
            params.view_type = 'form'

        # On New O2M
        if params.source:
            current = TinyDict()
            current.id = False
            params[params.source] = current
        
        return self.create(params)
    
    def get_form(self):
        params, data = TinyDict.split(cherrypy.request.params)

        # bypass validations, if saving from button in non-editable view
        if params.button and not params.editable and params.id:
            return None

        cherrypy.request.terp_validators = {}
        params.nodefault = True
        
        form = self.create_form(params)
        cherrypy.request.terp_form = form

        vals = cherrypy.request.terp_validators
        schema = validators.Schema(**vals)

        form.validator = schema

        return form
    
    @expose()
    @validate(form=get_form)
    def save(self, terp_save_only=False, tg_source=None, tg_errors=None, tg_exceptions=None, **kw):
        """Controller method to save/button actions...

        @param tg_errors: TG special arg, used durring validation
        @param kw: keyword arguments

        @return: form view
        """
        params, data = TinyDict.split(kw)
        # remember the current notebook tab
        cherrypy.session['remember_notebook'] = True
        if tg_errors:
            return self.create(params, tg_errors=tg_errors)

        # bypass save, for button action in non-editable view
        if not (params.button and not params.editable and params.id):

            proxy = rpc.RPCProxy(params.model)

            if not params.id:
                id = proxy.create(data, params.context)
                cherrypy.session['_bi_terp_id'] = id
                params.ids = (params.ids or []) + [int(id)]
                params.id = int(id)
                params.count += 1
            else:
                params['_terp_bi_type'] = 'true'
                id = proxy.write([params.id], data, params.context)
        button = params.button

        # perform button action
        if params.button:
            res = self.button_action(params)
            if res:
                return res

        current = params.chain_get(params.source or '')
        if current:
            current.id = None
            if not params.id:
                params.id = int(id)
        elif not button:
            params.editable = False

        if terp_save_only:
            params.load_counter = 2
            return dict(params=params, data=data)
        
        args = {'model': params.model,
                'id': params.id,
                'ids': ustr(params.ids),
                'view_ids': ustr(params.view_ids),
                'view_mode': ustr(params.view_mode),
                'domain': ustr(params.domain),
                'context': ustr(params.context),
                'offset': params.offset,
                'limit': params.limit,
                'count': params.count,
                'search_domain': ustr(params.search_domain)}

        if params.editable or params.source or params.return_edit:
            raise redirect(self.path + '/edit', source=params.source, **args)       
        
        params.load_counter = 2
        return self.create(params)
    
    @expose()
    def delete_bi(self, **kw): 
        
        proxy = rpc.RPCProxy('olap.schema')
        proxy_cube = rpc.RPCProxy('olap.cube')
        proxy_dimension = rpc.RPCProxy('olap.dimension')
        proxy_hierarchy = rpc.RPCProxy('olap.hierarchy')
        proxy_level = rpc.RPCProxy('olap.level')
        proxy_measure = rpc.RPCProxy('olap.measure')
        proxy_fact_table = rpc.RPCProxy('olap.database.tables')
        proxy_app_table = rpc.RPCProxy('olap.application.table')
        proxy_app_field = rpc.RPCProxy('olap.application.field')
        
        
        if str(kw.get('model')) == 'olap.measure':
            res = proxy_measure.unlink([int(kw.get('id'))])
            
        elif str(kw.get('model')) == 'olap.level':
            res = proxy_level.unlink([int(kw.get('id'))])
            
        elif str(kw.get('model')) == 'olap.hierarchy':
            level_ids = proxy_level.search([('hierarchy_id','=',int(kw.get('id')))])
            
            for l_id in level_ids:
                res = proxy_level.unlink([int(l_id)])
            res = proxy_hierarchy.unlink([int(kw.get('id'))])
            
        elif str(kw.get('model')) == 'olap.dimension':
            hierarchy_ids=proxy_hierarchy.search([('dimension_id','=',int(kw.get('id')))])
            
            for h_id in hierarchy_ids:
                level_ids=proxy_level.search([('hierarchy_id','=',int(h_id))])
                
                for l_id in level_ids:
                    res = proxy_level.unlink([int(l_id)])
                res = proxy_hierarchy.unlink([int(h_id)])
            res = proxy_dimension.unlink([int(kw.get('id'))])
            
        elif str(kw.get('model')) == 'olap.cube':
            dimension_ids = proxy_dimension.search([('cube_id','=',int(kw.get('id')))])
            
            for d_id in dimension_ids:
                hierarchy_ids = proxy_hierarchy.search([('dimension_id','=',int(d_id))])
                
                for h_id in hierarchy_ids:
                    level_ids = proxy_level.search([('hierarchy_id','=',int(h_id))])
                    
                    for l_id in level_ids:
                        res = proxy_level.unlink([int(l_id)])
                    res = proxy_hierarchy.unlink([int(h_id)])
                res = proxy_dimension.unlink([int(d_id)])
            measure_id = proxy_measure.search([('cube_id','=',int(kw.get('id')))])
            
            for m_id in measure_id:
                res=proxy_measure.unlink([int(m_id)])
            res = proxy_cube.unlink([int(kw.get('id'))])
            
            
        elif str(kw.get('model')) == 'olap.schema':
            
            id = proxy.search([('id','=',int(kw.get('id')))])
            search = proxy.read(id,['database_id'])[0]
            
            cube_ids = proxy_cube.search([('schema_id','=',int(kw.get('id')))])
            for c_id in cube_ids:
                dimension_ids = proxy_dimension.search([('cube_id','=',int(c_id))])
                
                for d_id in dimension_ids:
                    hierarchy_ids = proxy_hierarchy.search([('dimension_id','=',int(d_id))])
                    
                    for h_id in hierarchy_ids:
                        level_ids = proxy_level.search([('hierarchy_id','=',int(h_id))])
                        
                        for l_id in level_ids:
                            res = proxy_level.unlink([int(l_id)])
                        res = proxy_hierarchy.unlink([int(h_id)])
                    res = proxy_dimension.unlink([int(d_id)])
                    
                measure_id = proxy_measure.search([('cube_id','=',int(c_id))])
                for m_id in measure_id:
                    res = proxy_measure.unlink([int(m_id)])
                res = proxy_cube.unlink([int(c_id)])
                
            ids = proxy.search([('database_id','=',search['database_id'][0])])
            if len(ids) == 1:
                table_ids = proxy_fact_table.search([('fact_database_id','=',search['database_id'][0])])
                for t_id in table_ids:
                    res = proxy_fact_table.unlink([int(t_id)])
                res = proxy.unlink([int(kw.get('id'))])
            else:
                res = proxy.unlink([int(kw.get('id'))])
                return dict(success='false')
            
        return dict(success='true')
    
    def del_notebook_cookies(self):
        names = cherrypy.request.cookie.keys()

        for n in names:
            if n.endswith('_notebookTGTabber'):
                cherrypy.response.cookie[n] = 0

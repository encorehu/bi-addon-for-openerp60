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

from openobject.tools import expose

import cherrypy

from openerp.utils import rpc
from openobject import tools
from openerp.utils import common
from openobject.i18n import format

#from openerp.tinyres import TinyResource
from openerp.utils import TinyDict
from openerp.controllers import SecuredController

#from openerp.subcontrollers.form import Form
from tinybi.widgets.designer_view_popup import BI_Form
import openerp.widgets as tw

    
class Designer(SecuredController):
    
    bi_form = BI_Form()
    _cp_path = '/designer'
    
    @expose(template='/tinybi/controllers/templates/designer.mako')
    def index(self, **kw):
        model = 'olap.schema'
        view_type = 'tree'
        parent_id = ''
        key_name=''
        params,data = TinyDict.split(kw)
        if params.model:
            model=params.model
        if params.parent_id:
            parent_id=params.parent_id
        if params.key_name:
            key_name=params.key_name
        headers = [{'string' : '', 'name' : 'string', 'type' : 'char'},
                   {'string' : '', 'name': 'edit', 'type' : 'image', 'width': 2},
                   {'string' : '', 'name': 'delete', 'type' : 'image', 'width': 2}]

        treewidget = tw.treegrid.TreeGrid('view_tree', model=model, headers=headers, ids=['2'], url='/designer/get_subtree', key_name=key_name, parent_id=parent_id)
        treewidget.showheaders = True
        treewidget.expandall = False
        treewidget.onbuttonclick = 'onButtonClick'           
        
        return dict(tree=treewidget)
        
    
    def tree_parser(self,items={},id='',action='',children=[],icon=None,drag=False,in_query=False,in_slicer=False):
        res = {}
        res['target'] = None
        res['items'] = items
        res['id'] = id
        res['action'] = action
        res['children'] = children
        res['icon'] = icon
        res['draggable'] = drag
        res['in_query'] = in_query
        res['in_slicer'] = in_slicer
        return res    
    
    @expose('json')
    def get_subtree(self, model, key_name='', parent_id='', **kw):
        tree=[]
        cont={}

        proxy = rpc.RPCProxy(model)
        if parent_id:
            parent_id = map(lambda x: str(x),parent_id.split(','))
            ids = proxy.search([(key_name,'in',parent_id)])
        else:
            ids = proxy.search([])
        
        datas = proxy.read(ids,['id','name'])
        
        mapper = {
                  'olap.schema':['olap.cube','schema_id',['id','name']],
                  'olap.cube':['olap.dimension','cube_id',['id','name']],
                  'olap.dimension':['olap.hierarchy','dimension_id',['id','name']],
                  'olap.hierarchy':['olap.level','hierarchy_id',['id','name']],
                  'olap.level':['','',[]],
                  'olap.measure':['','',[]]
                  }
        
#		This will be now java script function that will open the pop ups
#        action='/designer/bi_form/edit?model='+model
#        action = "javascript:make_try(view_tree)"
    
#        context = '{"schema_id":1}'

        if parent_id:
            cont[key_name]=parent_id[0]
        else:
            cont[key_name]=0
        
        action = 'javascript:open_form_popup("%s","%s")' % (model,cont)
        
        add_name = 'New'+model.split('.')[1]
        add_string = 'Add New '+model.split('.')[1]
        add_id = 'new'+model.split('.')[1]
#        cont[''] = ''
        add_new = self.tree_parser({'name': add_name, 'string': add_string}, add_id, action , [],'/openerp/static/images/stock/gtk-new.png')
        for data in datas:
            items = {
                     'edit': '/tinybi/static/images/edit_inline.gif',
                     'delete': '/tinybi/static/images/delete_inline.gif', 
                     'name': data['name'], 'string': data['name']
                     }
            
            action = 'javascript:open_form_popup("%s","%s","%s")' % (model,cont,data['id'])
            
#            items['edit'].update({'Edit':'/tinybi/static/images/edit_inline.gif','onclick':action})
#            action='/designer/bi_form/edit?model=%s&id=%s'%(model,data['id'])
            id=data['id']
            icon='/tinybi/static/images/tree_img/close_folder.png'
            children=mapper[model][2]
            params= {'model': mapper[model][0], 'parent_id':data['id'], 'key_name':mapper[model][1]}
            
            action = 'javascript:open_form_popup("%s","%s","%s")' % (model,cont,data['id'])
            print "The mapper model",mapper[model][1],data['id']
            if model=='olap.cube':
                static_children=[]
                c_items = {
                           'name': 'Dimension', 'string': 'Dimension'
                           }
                c_parent_id=parent_id
                c_action=''
                c_icon='/tinybi/static/images/tree_img/close_folder.png'
                c_id='dimension_root'
                c_params= {'model': 'olap.dimension',  'parent_id':data['id'], 'key_name':'cube_id'}
                res=self.tree_parser(c_items, c_id, c_action, children,c_icon)
                res['params']=params
                static_children.append(res)

                c_items = {
                           'name': 'Measure', 'string': 'Measure'
                           }
                c_id='measure_root'
                params= {'model': 'olap.measure',  'parent_id':data['id'], 'key_name':'cube_id' }
                res=self.tree_parser(c_items, c_id, c_action, children,c_icon)
                res['params']=params
                static_children.append(res)
                
                res=self.tree_parser(items, id, action, static_children,icon)
                res['params']=params
            else:
               
                res=self.tree_parser(items, id, action, children,icon)
                res['params']=params
            tree.append(res)
        tree.append(add_new)
        
        return dict(records=tree)

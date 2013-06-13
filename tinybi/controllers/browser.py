
###############################################################################
#
# Copyright (C) 2007-TODAY Tiny ERP Pvt Ltd. All Rights Reserved.
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

import sqlalchemy
import cherrypy
import datetime
import locale
from openobject.tools import expose
from openobject.tools import redirect

#from openerp.tinyres import TinyResource
from openerp.utils import rpc,TinyDict
from openerp.controllers import SecuredController


import openerp.widgets as tw
import tinybi.widgets as widgets

from openerp.controllers.form import Form
from openerp.controllers.tree import Tree as bi_tree

import cube_engine, mdx_bi

class Browser(SecuredController):
#    mdx_main = mdx_bi.mdx_query()
    mdx = mdx_bi.mdx_mapper()
    form = Form()
    cubEngine = cube_engine.CubeEngine()
    result_format = widgets.result_format.Result_Format()
    error = None
#    graph = widgets.Graph.Bar_Stack()
    _cp_path = '/browser'

    @expose( template = "/tinybi/controllers/templates/browser.mako" )
    def index( self, **kw ):
        id = 1
        desc = 'Cube Browser'

        view_ids = rpc.RPCProxy( "ir.ui.view" ).search( [( 'model', '=', 'olap.dimension' )] )
        params = TinyDict()
        params.model = 'olap.dimension'
        params.view_mode = ['tinybi']
        params.view_ids = view_ids
        params.domain = [( 'res_model', '=', 'olap.dimension' ), ( 'res_id', '=', int( '1' ) )]

        screen = tw.screen.Screen( params, selectable = 1 )
        #screen.widget.pageable = False
        if cherrypy.session.has_key( 'saved_model' ) and cherrypy.session.has_key( 'saved_query_id' ):
            model = str( cherrypy.session.get( 'saved_model' ) )
            id = cherrypy.session.get( 'saved_query_id' )
            execute = rpc.RPCProxy( model ).read( id, [] )[0]

            selected_query = execute['query']
            self.mdx.parseMDX( selected_query )
            slice_list = self.mdx.fetch_all_slicer()
            cross_row = self.mdx.cross_list( 0 )
            cross_col = self.mdx.cross_list( 1 )
            screen = widgets.browser_view.Browser( slice_list, cross_row, cross_col )

            return dict( screen = screen )
        else:
            return dict( screen = screen )

    @expose()
    def make_view( self ):
        id = rpc.RPCProxy( "ir.ui.menu" ).search( [( 'name', '=', 'Olap Saved Query' )] )[0]
        raise redirect( '/tree/open', {'model': 'ir.ui.menu', 'id' :id} )

    def tree_parser( self, items = {}, id = '', action = '', children = [], icon = None, drag = False, in_query = False, in_slicer = False ):
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

    @expose( 'json' )
    def cube_select( self, **kw ):
        display = {}
        cube = kw.get( 'combo_cube' )
        widget_cube = {}
        if cube == 'Select Cube':
            cherrypy.session['bi_cubeid'] = ''
            cherrypy.session['bi_cube'] = ''
            cherrypy.session['bi_schema'] = ''
        else:
            cube_name = rpc.RPCProxy( 'olap.cube' ).read( [cube], ['name'] )
            selectedCube = str( cube_name[0]['name'] )
            dimensions_ids = rpc.RPCProxy( 'olap.dimension' ).search( [( 'cube_id', '=', int( cube ) )] )
            hierarchies_ids = rpc.RPCProxy( 'olap.hierarchy' ).search( [( 'dimension_id', 'in', dimensions_ids )] )
            hierarchies = rpc.RPCProxy( 'olap.hierarchy' ).read( hierarchies_ids )
            hier_level = {}
            for hier in hierarchies:
                levels_ids = rpc.RPCProxy( 'olap.level' ).search( [( 'hierarchy_id', '=', hier['id'] )] )
                hier_level[str( hier['name'] )] = len( levels_ids )
            cherrypy.session['hier_level'] = hier_level
            if cherrypy.session.has_key( 'saved_model' ):
                self.mdx.make_cube( selectedCube )
                cherrypy.session.pop( 'saved_model' )
            else:
                self.mdx.add_cube( selectedCube )
            ids = rpc.RPCProxy( 'olap.cube' ).read( [cube], ['schema_id'] )
            proxy = rpc.RPCProxy( "olap.schema" )
            res = proxy.read( ids[0]['schema_id'][0], ['id', 'name', 'database_id'] )
            schema = str( res['name'] )
            if cherrypy.session.has_key( '_designer' ) and cherrypy.session['_designer'] == 'on':
                cherrypy.session['bi_cubeid_d'] = cube
            else:
                cherrypy.session['bi_cubeid'] = cube
            cherrypy.session['bi_cube'] = selectedCube
            cherrypy.session['bi_schema'] = schema
        return dict()

    @expose( 'json' )
    def schema_select( self, **kw ):
        display = {}
        schema = kw.get( 'combo_schema' )
        record = {}
        widget_schema = {}
        cube_list = []
        if schema == 'Select Schema':
            cherrypy.session['bi_schemaid'] = ''
            cherrypy.session['bi_schema'] = ''
            record['schema'] = ''
            record['schemaID'] = ''
            return dict( cube_list = [] , error = None )
        else:
            schema_name = rpc.RPCProxy( 'olap.schema' ).read( [schema], ['name', 'database_id'] )
            selectedSchema = str( schema_name[0]['name'] )
            database_details = rpc.RPCProxy( 'olap.fact.database' ).read( [str( schema_name[0]['database_id'][0] )], [] )
            host = "host=%s" % ( str( database_details[0]['db_host'] ) )
            port = "port=%s" % ( str( database_details[0]['db_port'] ) )
            name = "dbname=%s" % ( str( database_details[0]['db_name'] ) )
            user = "user=%s" % ( str( database_details[0]['db_login'] ) )
            password = "password=%s" % ( str( database_details[0]['db_password'] ) )
            if str( database_details[0]['type'] ) == 'postgres':
                import psycopg2
                try:
                    psycopg2.connect( '%s %s %s %s %s' % ( host, port, name, user, password ) )
                    proxy = rpc.RPCProxy( "olap.cube" )
                    cube_ids = proxy.search( [( 'schema_id', '=', int( schema ) )] )
                    res = proxy.read( cube_ids, ['id', 'name'] )
                    for i in res:
                        cube_list.append( ( i['id'], i['name'] ) )
                    self.mdx.add_schema( selectedSchema )
                    cherrypy.session['bi_schemaid'] = schema
                    cherrypy.session['bi_schema'] = selectedSchema
                    record['schema'] = selectedSchema
                    record['schemaID'] = schema
                    return dict( cube_list = cube_list , error = None )
                except Exception , e:
                    self.error = e
                    return dict( error = self.error.message )

    def maxdepth( self, cubeEngine, hierarchy_name, max ):
        res = []
        if len( hierarchy_name.split( "." ) ) > max:
            return res
        textquery = "select {" + hierarchy_name + ".children } on rows from " + cherrypy.session['bi_cube']
        axis, data, error, last_query = cubeEngine.execute_mdx( '', cherrypy.session['bi_schema'], textquery, 'True' )
        if axis:
            for x in axis[0]:
                datax = x[1]
                if( type( datax ) <> type( False ) ):
                    if( type( datax ) == type( 0.0 ) ):
                        datax = int( datax )
#                    elif datax.__contains__( '\x' ):
#                        pass
                    items = {"slicer": "/tinybi/static/images/filter.png", "name":   datax  , "string":   datax}
                    action = None
                    hierarchy_name = hierarchy_name + ".[" +  datax  + "]"
                    id = hierarchy_name
                    icon = "/tinybi/static/images/tree_img/draggable.png"
                    children = self.maxdepth( cubeEngine, hierarchy_name, max )
                    drag = True
                    in_query = True
                    in_slicer = True
                    hierarchy_name = hierarchy_name.split( "." )
                    hierarchy_name = '.'.join( hierarchy_name[:len( hierarchy_name ) - 1] )
                    res.append( self.tree_parser( items, id, action, children, icon, drag, in_slicer ) )
                    
        return res

    @expose( 'json' )
    def data_browser( self, ids, model, fields = [], domain = [], context = {}, key_name = '', parent_id = '', **kw ):
        pid = parent_id
        schematree = []
        cubedimtree = []
        cubemsrtree = []
        dimtree = []
        msrtree = []
        tree = []
        cont = {}
        if cherrypy.session.has_key( 'bi_cubeid' ) and cherrypy.session['bi_cubeid']:
            cubeEngine = cube_engine.CubeEngine()
            fieldstr = ['id', 'name']
            tree = []
            proxy = rpc.RPCProxy( model )
            dimtree = []
            mapper = {
                      'olap.dimension':['olap.hierarchy', 'dimension_id', ['id', 'name']],
                      'olap.hierarchy':['olap.level', 'hierarchy_id', ['id', 'name']],
                      'olap.level':['olap.level.child', 'level_id', ['id', 'name']],
                      'olap.measure':['', '', []]
                      }

            if model != 'olap.level.child':
                if parent_id:
                    parent_id = map( lambda x: str( x ), parent_id.split( ',' ) )
                    ids = proxy.search( [( key_name, 'in', parent_id )] )
                    datas = proxy.read( ids, fieldstr )
                else:
                    key_name = 'cube_id'
                    parent_id = cherrypy.session['bi_cubeid']

            else:
                datas = {}
                datas = eval( parent_id )
                for lvl in datas:
                    items = lvl['items']
                    params = {'model': 'olap.level.child', 'parent_id':lvl['id'], 'key_name':lvl['items']['name']}
                    id = lvl['id']
                    action = None
                    drag = True
                    in_query = True
                    in_slicer = True
                    children = []
                    icon = lvl['icon']
                    res = lvl
                    if lvl['children']:
                         children = ['id', 'name']
                         params = {'model': 'olap.level.child', 'parent_id':str( lvl['children'] ), 'key_name':lvl['children'][0]['items']['name']}
                    res = self.tree_parser( items, id, action, children, icon, drag, in_query, in_slicer )
                    res['params'] = params
                    tree.append( res )
                return dict( records = tree )


            if model == 'olap.cube':
                id = 'New'
                params = {'model': 'olap.dimension', 'parent_id':parent_id, 'key_name':key_name}
                static_children = []
                c_items = {
                        "name": 'Dimension',
                        "string": 'Dimension'
                           }
                c_parent_id = parent_id
                children = ['id', 'name']
                c_action = None
                c_icon = '/tinybi/static/images/tree_img/close_folder.png'
                c_id = 'dimension_root'
                c_params = {'model': 'olap.dimension', 'parent_id':parent_id, 'key_name':key_name}
                res = self.tree_parser( c_items, c_id, c_action, children, c_icon )
                res['params'] = params
                tree.append( res )
                c_items = {
                           'name': 'Measures', 'string': 'Measures'
                           }
                c_id = 'measure_root'
                children = ['id', 'name']
                params = {'model': 'olap.measure', 'parent_id':parent_id, 'key_name':key_name }
                res = self.tree_parser( c_items, c_id, c_action, children, c_icon )
                res['params'] = params

                static_children.append( res )
                res = self.tree_parser( c_items, id, c_action, children, c_icon )
                res['params'] = params
                tree.append( res )
                return dict( records = tree )

            action = None
            drag = True
            in_query = True
            in_slicer = True

            for data in datas:
                items = {"name": data['name'], "string": data['name']}
                icon = "/tinybi/static/images/tree_img/draggable.png"
                params = {'model': mapper[model][0], 'parent_id':data['id'], 'key_name':mapper[model][1]}
                id = "[" + data['name'] + "].[all]"
                children = mapper[model][2]

                if model == 'olap.level':
                    h_ids = []
                    h_id = pid
                    h_ids.append( h_id )
                    proxy = rpc.RPCProxy( 'olap.hierarchy' )
                    h_name_id = proxy.search( [( 'id', '=', h_id )] )
                    h_name = proxy.read( h_name_id, ['id', 'name'] )
                    lvltree = self.maxdepth( cubeEngine, "[" + h_name[0]['name'] + "]", len( ids ) )
                    lvltree = lvltree
                    id = "[" + data['name'] + "].[all]"
                    children = lvltree
                    for lvl in lvltree:
                        items = lvl['items']
                        id = lvl['id']
                        if lvl['children']:
                             children = ['id', 'name']
                             params = {'model': 'olap.level.child', 'parent_id': str( lvl['children'] ) , 'key_name':lvl['children'][0]['items']['name']}
                        else:
                            children = []
                        res = self.tree_parser( items, id, action, children, icon, drag, in_query, in_slicer )
                        res['params'] = params
                        tree.append( res )
                    return dict( records = tree )

                if model == 'olap.hierarchy':
                    items = {"name": data['name'], "string": data['name']}

                if model == 'olap.dimension':
                    items = {
                            "query": " ",
                            "name": data['name'], "string": data['name']
                             }
                    cherrypy.session['dim_name'] = data['name']
                    cherrypy.session['dim_id'] = data['id']
                    icon = "/tinybi/static/images/tree_img/close_folder.png"

                if model == 'olap.measure':
                    items = {
                            "query": " ",
                            "name": data['name'], "string": data['name']
                             }
                    id = "[measures].[" + data['name'] + "]"

                res = self.tree_parser( items, id, action, children, icon, drag, in_query, in_slicer )
                res['params'] = params
                tree.append( res )
        else:
            items = {"query": "", "slicer": "", "name": 'No Cube Selected', "string": 'No Cube Selected'}
            id = "_d"
            icon = "/tinybi/static/images/tree_img/close_folder.png"
            action = None
            children = []
            tree.append( self.tree_parser( items, id, action, children, icon ) )
        return dict( records = tree )


    @expose( template = '../widgets/templates/mdx_output.mako' )
    def exe( self, *args, **kw ):
        print "+=================================+"
        textquery = kw.get( 'textquery' )
        print 'textquery', textquery

        frompane = kw.get( 'frompane' )
        if kw.has_key( 'from' ) and kw.get( 'from' ) == '1':
            self.mdx.parseMDX( textquery )
        set = {}
        error = False
        result_set = []
        axis, data, error, last_query = self.cubEngine.execute_mdx( '', cherrypy.session['bi_schema'], textquery, frompane )
        cherrypy.session['axis'] = axis
        
        cherrypy.session['data'] = data
        
        set['axis'] = axis
        set['data'] = data
        result_set.append( set )
        if last_query:
            print "==>Roll back"
            self.mdx.parseMDX( cherrypy.session['last_success_query'] )
            error = False
        if not error:
            flag = False
            result = self.result_format.result_format( axis, data, None, flag, textquery )

            rows = result[0]
            cols = result[1]
            data = result[2]
            pages = result[3]
            cols_cross_drill = result[4]
            slicers = []
            fetch_slicers = self.mdx.fetch_all_slicer()

            if fetch_slicers:
                st_counter = 0
                for filter in fetch_slicers:
                    slicers.append( [st_counter, ','.join( map( lambda x: x , filter ) ), '.'.join( map( lambda x: "["+str(x)+"]" , filter) )] )
                    st_counter = st_counter + 1
            else:
                slicers = []
        print "cols", cols
        print "rows", rows
        print "pages", pages
        print "slicers", slicers
        print "cols_cross_drill", cols_cross_drill
        print "data", data
        print "+=================================+"
        return dict( rows = rows, cols = cols, data = data, pages = pages, slicers = slicers,cols_cross_drill = cols_cross_drill)

    @expose( 'json' )
    def undo( self, **kw ):
        if kw.get('query'):
            if cherrypy.session.has_key( 'mdx_query' ):
                if cherrypy.session['mdx_query'].__contains__(str(kw.get('query'))):
                    if cherrypy.session['mdx_query'].index(str(kw.get('query'))) -1 < 0:
                        return dict(error = "Not Perform This Operation")
#                    if cherrypy.session['mdx_query'].index(str(kw.get('query'))) == cherrypy.session['mdx_query'].index(cherrypy.session['mdx_query'][-1]) and len(cherrypy.session['mdx_query']) <=1:
#                        return dict(error = "Not Perform This Operation")
                    else:
                        undo_query = str(cherrypy.session['mdx_query'][cherrypy.session['mdx_query'].index(str(kw.get('query'))) -1])
                        return dict( query = undo_query )
        else:
            error = "Not Perform This Operation"
            return dict( error = error )
    
    @expose( 'json' )
    def redo( self, **kw ):
        if kw.get('query'):
            if cherrypy.session.has_key( 'mdx_query' ):
                if cherrypy.session['mdx_query'].__contains__(str(kw.get('query'))):
                    if cherrypy.session['mdx_query'].index(str(kw.get('query'))) == cherrypy.session['mdx_query'].index(cherrypy.session['mdx_query'][-1]):
                        return dict(error = "Not Perform This Operation")
                    else:
                        redo_query = str(cherrypy.session['mdx_query'][cherrypy.session['mdx_query'].index(str(kw.get('query'))) + 1])
                        return dict( query = redo_query )
        else:
            error = "Not Perform This Operation"
            return dict( error = error )
        
#    @expose('json')
#    def undo(self, **kw):
#        index = ''
#        if kw.get( 'query' ):
#            if cherrypy.session.has_key( 'mdx_query' ):
#                for i in cherrypy.session['mdx_query']:
#                    if i['query'] == kw['query']:
#                        index = int( i['index'] - 1 )
#                        break;
#
#                for j in cherrypy.session['mdx_query']:
#                    if index > 0:
#                        if j['index'] == index:
#                            query = j['query']
#                    else:
#                        query = j['query']
#                        break;
#            return dict( query = query )
##                        query = 'select   from Sales'
#        else:
#            if cherrypy.session.has_key( 'mdx_query' ):
#                max = len( cherrypy.session['mdx_query'] ) - 1
#                query = cherrypy.session['mdx_query'][max]['query']
#                return dict( query = query )
#            else:
#                error = "Not Perform This Operation"
#                return dict( error = error )



#    @expose( 'json' )
#    def redo( self, **kw ):
#        index = ''
#        query = ''
#        if kw.get( 'query' ):
#            if cherrypy.session.has_key( 'mdx_query' ):
#                for i in cherrypy.session['mdx_query']:
#                    if i['query'] == kw['query']:
#                        index = int( i['index'] + 1 )
#                        break;
#
#                for j in cherrypy.session['mdx_query']:
#                    if j['index'] == index:
#                        query = j['query']
#                        break;
#                        return dict( query = query )
#            return dict( query = query )
#
#        else:
#            if cherrypy.session.has_key( 'mdx_query' ):
#                max = len( cherrypy.session['mdx_query'] ) - 1
#                query = cherrypy.session['mdx_query'][max]['query']
#                return dict( query = query )
#            else:
#                error = "Not Perform This Operation"
#                return dict( error = error )

    @expose( template = '../widgets/templates/graph.mako' )
    def graph( self, **kw ):
        return dict( name = str( kw.get( 'name' ) ), width = int( kw.get( 'width' ) ), height = int( kw.get( 'height' ) ), url = str( kw.get( 'url' ) ) )
    
    @expose('json')
    def check_condtiotion(self, **kw):
        axis = cherrypy.session.get( 'axis' )
        data = cherrypy.session.get( 'data' )
        locale.setlocale(locale.LC_ALL, '')
        
        if len(axis)>2: 
            flag = False
            result = self.result_format.result_format( axis,data,None,flag ,str(kw.get('query')))
            row = result[0]
            col = result[1]
            datas = result[2]
            page = result[3]
            page_d = []
            locale.setlocale(locale.LC_ALL, '')
            if kw.has_key('Pie'):
                if len(col) > 1:
                    for p in range(len(page)):
                        row_data = []
                        for r in range(len(row)):
                            if row[r][1]['parent'] is None:
                                col_data = []
                                for d in range(len(datas[r][1])):
                                    if datas[r][1][d][1][p].__contains__(' '):
                                            datas[r][1][d][1][p] = datas[r][1][d][1][p][:datas[r][1][d][1][p].index(' ')]
                                            datas[r][1][d][1][p] = locale.atof(datas[r][1][d][1][p])
                                    col_data.append((col[d][1]['text'], datas[r][1][d][1][p]))
                                row_data.append((row[r][1]['text'], col_data))
                        page_d.append((page[p][1]['text'], row_data))
                    return dict(page_cols = page_d)
                else:
                    for p in range(len(page)):
                        row_data = []
                        for r in range(len(row)):
                            if row[r][1]['parent'] is None:
                                col_data = []
                                for d in range(len(datas[r][1])):
                                    if datas[r][1][d][1][p].__contains__(' '):
                                            datas[r][1][d][1][p] = datas[r][1][d][1][p][:datas[r][1][d][1][p].index(' ')]
                                            datas[r][1][d][1][p] = locale.atof(datas[r][1][d][1][p])
                                    col_data.append((col[d][1]['text'], datas[r][1][d][1][p]))
                                row_data.append((row[r][1]['text'], col_data))
                        page_d.append((page[p][1]['text'], row_data))

                    return dict(data = page_d)
            else:
                for p in range(len(page)):
                    row_data = []
                    for r in range(len(row)):
                        if row[r][1]['parent'] is None:
                            col_data = []
                            for d in range(len(datas[r][1])):
                                if datas[r][1][d][1][p].__contains__(' '):
                                        datas[r][1][d][1][p] = datas[r][1][d][1][p][:datas[r][1][d][1][p].index(' ')]
                                        datas[r][1][d][1][p] = locale.atof(datas[r][1][d][1][p])
                                col_data.append((col[d][1]['text'], datas[r][1][d][1][p]))
                            row_data.append((row[r][1]['text'], col_data))
                    page_d.append((page[p][1]['text'], row_data))
                return dict(data = page_d)
        else:
            if kw.has_key('Pie'):
                flag = True
                result = self.result_format.result_format( axis,data,None,flag ,str(kw.get('query')))
                row = result[0]
                col = result[1]
                datas = result[2]
                cols_d = []
                dd = datas.values()[0]
                if col:
                    for key,val in col.items():
                        if val['parent'] is None:
                            cols_d.append((val['key_value'], dd[key]))
                    return dict(cols = cols_d)
                else:
                    return dict(error = 'Pie Chart Does not show any information.(No Measurement on cols)')
            else:
                result = self.result_format.result_format( axis,data,None,True ,str(kw.get('query')))
                row = result[0]
                col = result[1]
                datas = result[2]
                if not col:
                    return dict(error = 'Bar Chart Does not show any information.(No Measurement on cols)')
                else:
                    return dict()
    
    @expose( 'json' )
    def stack_bar( self,**kw ):
        ChartColors = ["#CD1076","#DC143C","#FFB90F","#9932CC","#68228B","#9BCD9B","#228B22","#FF4040","#98F5FF","#8B7355","#F8F8FF","#FFD700","#DCDCDC","#EE6A50"]
        elements = {}
        elements["elements"] = []
        elements["title"] = {}
        elements["x_axis"] = {}
        elements["y_axis"] = {}
        elements["tooltip"] = {}
        elements["bg_colour"] = "#FFFFFF"
        axis = cherrypy.session.get( 'axis' )
        data = cherrypy.session.get( 'data' )
        locale.setlocale(locale.LC_ALL, '')
        if len(axis)>2:
            for e in data:
                for item in range(len(e)):
                    for dt in range(len(e[item])):
                        if type(e[item][dt])!= type(0.0):
                            if e[item][dt][0].__contains__(' '):
                                e[item][0] = e[item][dt][0][:e[item][dt][0].index(' ')]
                                e[item][0] = locale.atof(e[item][0])
                            else:
                                e[item][0] = float(e[item][dt][0])
                        else:
                            e[item][0] = float(e[item][dt])
        else:
            for element in data:
                for item in element:
                    if type(item[0])!= type(0.0):
                        if item[0].__contains__(' '):
                            item[0] = item[0][:item[0].index(' ')]
                            item[0] = locale.atof(item[0])
                        else:
                            item[0] = float(item[0])
        query = str(kw.get('query'))
        flag = True
        result = self.result_format.result_format( axis,data,None,flag ,query)
        rows = result[0]
        cols = result[1]
        datas = result[2]
        x_axis_label = []
        x_values = []
        y_vals = []
        keys = []
        if cols:
            for tt in range( len( cols ) ):
                x_values.append( [] )
        else:
            x_values.append( [] )
        for key,value in rows.items():
            if value['parent'] == None:
                x_axis_label.append( value['text'] )
                count = 0
                y_vals.append( datas[key].values() )
                for header in datas[key].keys():
                    key_val = ','.join( map( lambda x:str( x ),value['key_value'] ) )
                    
                    if cols:
                        tip= str(value['text'])+ "\n"+ str(cols[header]['text']+" "+ str(datas[key][header])) 
                        x_values[count].append( [{"colour": ChartColors[count],"val": datas[key][header],"on-click": "Graph('"+'event'+"', '" + str( '.'.join(map(lambda x: str(x), cols[header]['key_value'])) ) + "','" + key_val + "','" + str( datas[key][header] ) + "')", "tip": tip}] )
                        keys.append( [{"colour": ChartColors[count],"text": cols[header]['text'],"font-size": 12,"on-click": ""}] )
                    else:
                        tip= str(value['text'])+ "\n"+ str(datas[key][header])
                        x_values[count].append( [{"colour": ChartColors[count],"val": datas[key][header], "tip": tip}] )
                        keys.append( [{"colour": ChartColors[count],"text": ""}] )
                    count = count + 1
        if cols:
            y_max = max(map( lambda x: max( x ),y_vals ))
            
            
        else:
            y_max = 10
        for elem in range( len( x_values ) ):
            elements["elements"].append( {"type": "bar_stack","values": x_values[elem],"keys": keys[elem]} )
        y_max = float(y_max)
        
        if int(y_max) % 2 == 0:
            if y_max > 0 and y_max > 1000:
                yy_max = y_max + 1000.0
            elif y_max > 0 and y_max < 1000 :
                yy_max = y_max + 50
            else:
                yy_max = y_max
        else:
            y = int(y_max) -2
            yy_max = int(y_max) + y
        elements["title"] = {"text":""}
        elements["legend"] = {"position": "right"}
        elements["x_axis"] = {"3d":5,"colour":"#909090","grid-colour": "#FFFFFF","labels":{"rotate": 270, "colour": "#ADB5C7","size": 13,"labels": x_axis_label}}
        elements["y_axis"] = { "min": 0,"max": yy_max,"steps": int(yy_max) / 10 }
        elements["tooltip"] = {"mouse": 2, "colour": "#6E604F","background": "#edf7fd","title": "{font-size: 12px; color: #edf7fd;}","body": "{font-size: 12px; color: #2e3436;}" }
        return elements
    
    @expose('json')
    def page_stack_bar(self, **kw):
        ChartColors = ["#CD1076","#DC143C","#FFB90F","#9932CC","#68228B","#9BCD9B","#228B22","#FF4040","#98F5FF","#8B7355","#F8F8FF","#FFD700","#DCDCDC","#EE6A50"]
        elements = {}
        elements["elements"] = []
        elements["title"] = {}
        elements["x_axis"] = {}
        elements["y_axis"] = {}
        elements["tooltip"] = {}
        elements["bg_colour"] = "#FFFFFF"
        
        data_page = str(kw.get('data')).split("*")
        dt_page = data_page[1].split(">")
        
        axis = cherrypy.session.get( 'axis' )
        data = cherrypy.session.get( 'data' )
        query = str(kw.get('query'))
        
        flag = True
        result = self.result_format.result_format( axis,data,None,flag ,query)
        locale.setlocale(locale.LC_ALL, '')
        for e in range(len(dt_page)):
            if dt_page[e].__contains__(' '):
                dt_page[e] = dt_page[e][:dt_page[e].index(' ')]
                dt_page[e] = locale.atof(dt_page[e])
            dt_page[e] = float(dt_page[e])
        
        rows = result[0]
        cols = result[1]
        datas = result[2]
        x_axis_label = []
        x_values = []
        y_vals = []
        keys = []
        
        if cols:
            for tt in range( len( cols ) ):
                x_values.append( [] )
        else:
            x_values.append( [] )
        for key,value in rows.items():
            if value['parent'] == None:
                x_axis_label.append( str(value['text'] +"\n"+"("+data_page[0]+")") )
                count = 0
                y_vals.append( dt_page)
                
                key_val = ','.join( map( lambda x:str( x ),value['key_value'] ) )
                c = cols.keys()
                c.sort()
                n_cols = []
                for i in c:
                    n_cols.append({i: cols[i]})
                cols_text = []
                cols_header = []
                for col_s in n_cols:
                    for col_key,col_value in col_s.items():
                       cols_text.append('.'.join(col_value['key_value'])) 
                       cols_header.append(col_value['text'])
                       
                for t in range(len(cols_text)):
                    tip = str(value['text']) + "\n" + str(cols_text[t].split(".")[1])+ " " +str(dt_page[t])
                    x_values[count].append( [{"colour": ChartColors[count],"val": dt_page[t],"on-click": "Graph('"+'event'+"','" + str( cols_text[t] ) + "','" + key_val + "','" + str( dt_page[t] ) + "')", "tip": tip}] )
                    keys.append( [{"colour": ChartColors[count],"text": cols_header[t],"font-size": 12,"on-click": ""}] )
                    count = count + 1
        
        for elem in range( len( x_values ) ):
            elements["elements"].append( {"type": "bar_stack","values": x_values[elem],"keys": keys[elem]} )
        y_max = max(map( lambda x: max( x ),y_vals ))
        
        if int(y_max) % 2 == 0:
            if y_max > 0 and y_max > 1000:
                yy_max = y_max + 1000.0
            elif y_max > 0 and y_max < 1000 :
                yy_max = y_max + 50
            else:
                yy_max = y_max
        else:
            y = int(y_max) -2
            yy_max = int(y_max) + y
        elements["title"] = {"text":""}
        elements["legend"] = {"position": "right"}
        elements["x_axis"] = {"3d":5,"colour":"#909090","grid-colour": "#FFFFFF","labels":{"rotate": 270, "colour": "#ADB5C7","size": 13,"labels": x_axis_label}}
        if y_max<1:
            elements["y_axis"] = { "min": y_max,"max": y_max,"steps": y_max}
        else:
            elements["y_axis"] = { "min": 0,"max": yy_max,"steps": int(yy_max) / 10 }
        elements["tooltip"] = {"mouse": 2, "colour": "#6E604F","background": "#edf7fd","title": "{font-size: 12px; color: #edf7fd;}","body": "{font-size: 12px; color: #2e3436;}" }
        return elements
    
    @expose( 'json' )
    def stack_by_element( self, **kw ):
        ChartColors = ["#FEF0C9", "#8B8378", "#DEB887", "#D2691E", "#FF7F24", "#DC143C", "#CD661D", "#66CD00", "#9932CC", "#68228B", "#9BCD9B", "#228B22", "#FF4040", "#98F5FF", "#8B7355", "#DCDCDC", "#EE6A50", "#FEF0C9", "#8B8378", "#DEB887", "#D2691E", "#FF7F24", "#DC143C", "#CD661D", "#66CD00", "#9932CC", "#FEF0C9", "#8B8378", "#DEB887", "#D2691E", "#FF7F24", "#DC143C", "#CD661D", "#8B8378", "#9932CC"]
        ChartColors.reverse()
        rows = str( kw.get( "rows" ) )
        p_elem =  rows.split(',')
        parent_elem = map(lambda x: "["+x+"]", p_elem)
        qr = []
        counter = 1
        for x in parent_elem:
            if counter == 1 :
                qr.append(x+".[all]")
            else:
                qr.append('.'.join(parent_elem[0:counter]))
            counter = counter + 1
        
        cols = str( kw.get( "columns" ) )
        cube = str( kw.get( "cube" ) )
        elements = {}
        x_axis_label = []
        elements["elements"] = []
        x_axis_label.append( rows.replace(',','\n') )
        f = False
        query = "select {"
        if rows.__contains__( 'measures' ):
            rows = "[measures].[" + rows.split( "." )[1] + "]"
        else:
            rows = rows.split( "," )
            
            element = rows
            element = '.'.join(map(lambda x : "[" + x+"]",element))
            a=[]
            if cherrypy.session.has_key('temp_child'):
                for k in cherrypy.session['temp_child']:
                    a.append(k.keys()[0])
                if not element in a:
                    query = "select {" +element +'.children} on rows from ' + cherrypy.session['bi_cube']
                    schema = cherrypy.session['bi_schema']
                    axis, data = rpc.RPCProxy( 'olap.schema' ).request( schema, query)
                    child_len = len(axis[0])
                    cherrypy.session['temp_child'].append({element: child_len})
            else:
                query = "select {" +element +'.children} on rows from ' + cherrypy.session['bi_cube']
                schema = cherrypy.session['bi_schema']
                axis, data = rpc.RPCProxy( 'olap.schema' ).request( schema, query)
                child_len = len(axis[0])
                cherrypy.session['temp_child'] = [{element: child_len}]

            if len( rows ) == cherrypy.session.get( 'hier_level' )[str( rows[0] )]:
                f = True
            
            rows = '.'.join( map( lambda x:"[" + str( x ) + "]", rows ) ) + ".children"
        if cols.__contains__( 'measures' ):
            x_col = cols
            cols = "[measures].[" + cols.split( "." )[1] + "]"
        else:
            cols = ( cols.split( "." ) )
            if len( cols ) == cherrypy.session.get( 'hier_level' )[str( cols[0] )]:
                f = True
            cols = '.'.join( map( lambda x:"[" + str( x ) + "]", cols ) ) + ".children"
        query = "select {"
        
        query = query + ','.join(qr)+ ','+rows + "} on rows , {" + cols + "} on columns from " + " " + cube
        axis, data = rpc.RPCProxy( 'olap.schema' ).request( str( kw.get( "schema" ) ), query )
        locale.setlocale(locale.LC_ALL, '')
        for element in data:
            for item in element:
                if type(item[0])!= type(0.0):
                    if item[0].__contains__(' '):
                        item[0] = item[0][:item[0].index(' ')]
                        item[0] = locale.atof(item[0])
                    else:
                        item[0] = float(item[0])

        result = self.result_format.result_format( axis, data, None, True, query )
        row = result[0]
        col = result[1]
        datas = result[2]
         

        x_values = []
        y_vals = []
        keys = []
        count = 0
        
        for key, val in row.items():
            if val['parent']!= None:
                if not  datas[key].values().__contains__('0.0') or datas[key].values().__contains__(0.0) or datas[key].values().__contains__(0) or datas[key].values().__contains__('0'):
                    y_vals.append( datas[key].values() )
                    key_val = ','.join( map( lambda x: x .split( "." )[0], val['key_value'] ) )
                    keys.append( {"colour": ChartColors[count], "text": val['text'], "font-size": 12} )
                    val_data = [d for d in datas[key].values()][0]
                    tip = val['text']+ "\n"+ x_col.split(".")[1]+ " " + val_data
                    if f:
                        x_values.append( {"colour": ChartColors[count], "val": float(val_data), "tip": tip} )
                    else:
                        x_values.append( {"colour": ChartColors[count], "val": float(val_data), "on-click": "Graph('"+'event'+"', '" + x_col + "','" + key_val + "','" +  val_data  + "')", "tip": tip} )
                    count = count + 1
        y_max = float( kw.get( 'y_max' ) )
        
        if int(y_max) % 2 == 0:
            if y_max > 0 and y_max > 1000:
                yy_max = y_max + 1000.0
            elif y_max > 0 and y_max < 1000 :
                yy_max = y_max + 50
            else:
                yy_max = y_max
        else:
            y = int(y_max) -2
            yy_max = int(y_max) + y
        
        elements["elements"] = [{"type": "bar_stack", "values": [x_values], "keys": keys}]
        elements["menu"] = {"colour":"#E0E0ff", "outline_colour":"#707070", "values": [{"type": "text", "text": "Back", "javascript-function":"Graph"}]}
        elements["bg_colour"] = "#FFFFFF"
        elements["title"] = {"text":""}
        elements["legend"] = {"position": "right"}
        elements["x_axis"] = {"3d":5, "colour":"#909090", "grid-colour": "#FFFFFF", "labels":{"rotate": 270, "step":2, "colour": "#ADB5C7", "size": 13, "labels": x_axis_label}}
        elements["y_axis"] = { "min": 0, "max": yy_max, "steps": int(yy_max) / 10 }
        elements["tooltip"] = {"mouse": 2, "colour": "#6E604F","background": "#edf7fd","title": "{font-size: 12px; color: #edf7fd;}","body": "{font-size: 12px; color: #2e3436;}" }
        return elements
    
    @expose('json')
    def pie_chart(self, *args, **kw):
        Chartcolors = ["#CD8162","#8B008B","#8B1C62","#9370DB","#000080","#FF4500","#E6E6FA","#8B864E","#F0E68C","#8B3A3A","#CD6090"]
        Chartcolors.reverse()
        
        elements = {}
        locale.setlocale(locale.LC_ALL, '')
        if args:
            query = str( args[0] )
            schema = str( args[1] )
        if kw:
            query = str( kw.get( 'query' ) )
            schema = str( kw.get( 'schema' ) )
            c_column = str(kw.get( 'cols_d' )).split("*")[0]
            c_data =  str(kw.get( 'cols_d' )).split("*")[1]
            
            if c_data.__contains__(' '):
                print
                c_data = c_data[:c_data.index(' ')]
                c_data = locale.atof(c_data)
            else:
                c_data = float(c_data)
            
        axis,data = rpc.RPCProxy( 'olap.schema' ).request( schema,query )
        
        for element in data:
            for item in element:
                if type(item[0])!= type(0.0):
                    if item[0].__contains__(' '):
                        item[0] = item[0][:item[0].index(' ')]
                        item[0] = locale.atof(item[0])
                    else:
                        item[0] = float(item[0])
        result = self.result_format.result_format( axis,data,None,True, query )
            
            
        rows = result[0]
        cols = result[1]
        datas = result[2]
        elements["bg_colour"] = "#FFFFFF"
        elements["title"] = {"text": ""}
        elements["legend"] = {"position": "top","visible": 1,"bg_colour" : "#FFFFFF"}
        elements["elements"] = [{"type": "pie","values": [],"colours":Chartcolors,"alpha":0.5,"start_angle":35, "animate": [ { "type": "fade" }]}]
#        elements["menu"] = {"colour":"#E0E0ff", "outline_colour":"#707070", "values": [{"type": "text", "text": "Back", "javascript-function":"Graph"}]}
        elements["tooltip"] = { "colour": "#6E604F","background": "#edf7fd","title": "{font-size: 10px; color: #edf7fd;}","body": "{font-size: 10px; color: #2e3436;}" }
        
        for key,value in rows.items():
            if not args:
                if value['parent'] is None:
                    elem = '.'.join( map( lambda x:"[" + str( x ) + "]",value['key_value'] ) ) + ".children"
                    if cols:
                        column = ".".join(map(lambda x: "["+str(x)+"]", c_column.split(",")))
                        tip_col = c_column.split(",")[1]
                    else:
                        col = ''
                        tip_col = ''
                        column = ''
#                    val = [d for d in datas[key].values()][0]
                    val = c_data
                    if len( value['key_value'] ) > cherrypy.session.get( 'hier_level' )[str( value['key_value'][0] )]:
                        elements["elements"][0]["values"].append( {"tip": str( val ) + " " + tip_col + " By \n" + str( value['text'] ),"value": float(val),"text": str( value['text'] )} )
                    else:
                        elements["elements"][0]["values"].append( {"tip": str( val ) + " " + tip_col + " By \n" + str( value['text'] ),"value": float(val),"text": str( value['text'] ),"on-click": "Pie('"+'event'+"','" + elem + "', '" + column + "')","key-on-click": "Pie('"+'event'+"','" + elem + "', '" + column + "')"} )
            else:
                if value['parent'] != None:
                    elem = '.'.join( map( lambda x:"[" + str( x ) + "]",value['key_value'] ) ) + ".children"
                    if cols:
                        col = [v['key_value'] for k,v in cols.items()][0]
                        tip_col = [v['text'] for k,v in cols.items()][0]
                        column = ".".join( map( lambda x: "[" + str( x ) + "]",col ) )
                        
                    else:
                        col = ''
                        tip_col = ''
                        column = ''
                    
                    dt = [d for d in datas[key].values()]
                    if not  dt.__contains__('0.0') or dt.__contains__(0.0) or dt.__contains__(0) or dt.__contains__('0'):
                        val = [d for d in datas[key].values()][0]
                        if len( value['key_value'] ) > cherrypy.session.get( 'hier_level' )[str( value['key_value'][0] )]:
                            elements["elements"][0]["values"].append( {"tip": str( value['text'] ) + "\n " + tip_col + " " + str( val ),"value": float(val),"text": str( value['text'] )} )
                        else:
                            elements["elements"][0]["values"].append( {"tip": str( value['text'] ) + "\n " + tip_col + " " + str( val ),"value": float(val),"text": str( value['text'] ),"on-click": "Pie('"+'event'+"','" + elem + "', '" + column + "')","key-on-click": "Pie('"+'event'+"','" + elem + "', '" + column + "')"} )
        return elements
    
    @expose('json')
    def page_pie_chart(self, **kw):
        Chartcolors = ["#CD8162","#8B008B","#8B1C62","#9370DB","#000080","#FF4500","#E6E6FA","#8B864E","#F0E68C","#8B3A3A","#CD6090"]
        Chartcolors.reverse()
        elements = {}
        elements["bg_colour"] = "#FFFFFF"
        elements["title"] = {"text": ""}
        elements["legend"] = {"position": "right","visible": 1,"bg_colour" : "#FFFFFF"}
        elements["elements"] = [{"type": "pie","values": [],"colours":Chartcolors,"alpha":0.5,"start_angle":35, "animate": [ { "type": "fade" }]}]
        elements["tooltip"] = { "colour": "#6E604F","background": "#edf7fd","title": "{font-size: 10px; color: #edf7fd;}","body": "{font-size: 10px; color: #2e3436;}" }
        data_page = str(kw.get('data')).split("*")
        
        dt_page = data_page[1].split(">")
        
        axis = cherrypy.session.get( 'axis' )
        data = cherrypy.session.get( 'data' )
        query = str(kw.get('query'))
        flag = True
        result = self.result_format.result_format( axis,data,None,flag ,query)
        locale.setlocale(locale.LC_ALL, '')
        for e in range(len(dt_page)):
            if dt_page[e].__contains__(' '):
                dt_page[e] = dt_page[e][:dt_page[e].index(' ')]
                dt_page[e] = locale.atof(dt_page[e])
            dt_page[e] = float(dt_page[e])
            
        rows = result[0]
        cols = result[1]
        datas = result[2]
        x_axis_label = []
        x_values = []
        y_vals = []
        keys = []
        
        if cols:
            for tt in range( len( cols ) ):
                x_values.append( [] )
        else:
            x_values.append( [] )
        for key,value in rows.items():
            if value['parent'] == None:
                count = 0
                y_vals.append( dt_page)
                
                key_val = ','.join( map( lambda x:str( x ),value['key_value'] ) )
                c = cols.keys()
                c.sort()
                n_cols = []
                
                for i in c:
                    n_cols.append({i: cols[i]})
                cols_text = []
                cols_header = []
                for col_s in n_cols:
                    for col_key,col_value in col_s.items():
                       cols_text.append(col_value['key_value']) 
                       cols_header.append(col_value['text'])
               
                elem = "[" + value['text'] + "].children"
                if kw.has_key('column_d'):
                    if cols_header.__contains__(str(kw.get('column_d'))):
                        tip_col = cols_header[cols_header.index(str(kw.get('column_d')))]
                        column = '.'.join(map(lambda x: "[" + str(x)+ "]", cols_text[cols_header.index(str(kw.get('column_d')))]))
                else:
                    column = '.'.join(map(lambda x: "[" + str(x)+ "]", cols_text[0]))
                    tip_col = cols_header[0]
                val = dt_page[0]
                
                if len( value['key_value'] ) > cherrypy.session.get( 'hier_level' )[str( value['key_value'][0] )]:
                    elements["elements"][0]["values"].append( {"tip": str( value['text'] ) + "\n" + tip_col+ " "+ str( val ),"value": float(val),"text": str(value['text'] +"\n"+"("+data_page[0]+")")} )
                else:
                    elements["elements"][0]["values"].append( {"tip": str( value['text'] ) + "\n" + tip_col+ " "+ str( val ),"value": float(val),"text": str(value['text'] +"\n"+"("+data_page[0]+")"),"on-click": "Pie('"+'event'+"','" + elem + "', '" + column + "')","key-on-click": "Pie('"+'event'+"','" + elem + "', '" + column + "')"} )
        return elements
    
    @expose( 'json' )
    def pie_chart1( self,*args,**kw ):
        Chartcolors = ["#CD8162","#8B008B","#8B1C62","#9370DB","#000080","#FF4500","#E6E6FA","#8B864E","#F0E68C","#8B3A3A","#CD6090","#8B3A62"]
        Chartcolors.reverse()
        elements = {}
        if args:
            query = str( args[0] )
            schema = str( args[1] )
        if kw:
            query = str( kw.get( 'query' ) )
            schema = str( kw.get( 'schema' ) )

        axis,data = rpc.RPCProxy( 'olap.schema' ).request( schema,query )
        locale.setlocale(locale.LC_ALL, '')
        for element in data:
            for item in element:
                if type(item[0])!= type(0.0):
                    if item[0].__contains__(' '):
                        item[0] = item[0][:item[0].index(' ')]
                        item[0] = locale.atof(item[0])
                    else:
                        item[0] = float(item[0])
        result = self.result_format.result_format( axis,data,None,True, query )

        rows = result[0]
        cols = result[1]
        datas = result[2]
        elements["bg_colour"] = "#FFFFFF"
        elements["title"] = {"text": ""}
#        elements["is_decimal_separator_comma"] = 0
        elements["legend"] = {"position": "right","visible": 1,"bg_colour" : "#FFFFFF"}
        elements["elements"] = [{"type": "pie","values": [],"colours":Chartcolors,"alpha":0.5,"start_angle":35, "animate": [ { "type": "fade" }]}]
#        elements["menu"] = {"colour":"#E0E0ff", "outline_colour":"#707070", "values": [{"type": "text", "text": "Back", "javascript-function":"Graph"}]}
        elements["tooltip"] = { "colour": "#6E604F","background": "#edf7fd","title": "{font-size: 10px; color: #edf7fd;}","body": "{font-size: 10px; color: #2e3436;}" }
        
        for key,value in rows.items():
            if not args:
                if value['parent'] is None:
                    elem = '.'.join( map( lambda x:"[" + str( x ) + "]",value['key_value'] ) ) + ".children"
                    if cols:
                        col = [v['key_value'] for k,v in cols.items()][0]
                        tip_col = [v['text'] for k,v in cols.items()][0]
                        column = ".".join( map( lambda x: "[" + str( x ) + "]",col ) )
                    else:
                        col = ''
                        tip_col = ''
                        column = ''
                    val = [d for d in datas[key].values()][0]
                    if len( value['key_value'] ) > cherrypy.session.get( 'hier_level' )[str( value['key_value'][0] )]:
                        elements["elements"][0]["values"].append( {"tip": str( val ) + " " + tip_col + " By \n" + str( value['text'] ),"value": float(val),"text": str( value['text'] )} )
                    else:
                        elements["elements"][0]["values"].append( {"tip": str( val ) + " " + tip_col + " By \n" + str( value['text'] ),"value": float(val),"text": str( value['text'] ),"on-click": "Pie('"+'event'+"','" + elem + "', '" + column + "')","key-on-click": "Pie('"+'event'+"','" + elem + "', '" + column + "')"} )
            else:
                if value['parent'] != None:
                    elem = '.'.join( map( lambda x:"[" + str( x ) + "]",value['key_value'] ) ) + ".children"
                    if cols:
                        col = [v['key_value'] for k,v in cols.items()][0]
                        tip_col = [v['text'] for k,v in cols.items()][0]
                        column = ".".join( map( lambda x: "[" + str( x ) + "]",col ) )
                        
                    else:
                        col = ''
                        tip_col = ''
                        column = ''
                    
                    dt = [d for d in datas[key].values()]
                    if not  dt.__contains__('0.0') or dt.__contains__(0.0) or dt.__contains__(0) or dt.__contains__('0'):
                        val = [d for d in datas[key].values()][0]
                        if len( value['key_value'] ) > cherrypy.session.get( 'hier_level' )[str( value['key_value'][0] )]:
                            elements["elements"][0]["values"].append( {"tip": str( val ) + " " + tip_col + " By \n" + str( value['text'] ),"value": float(val),"text": str( value['text'] )} )
                        else:
                            elements["elements"][0]["values"].append( {"tip": str( val ) + " " + tip_col + " By \n" + str( value['text'] ),"value": float(val),"text": str( value['text'] ),"on-click": "Pie('" + elem + "', '" + column + "')","key-on-click": "Pie('" + elem + "', '" + column + "')"} )
        return elements

    @expose( 'json' )
    def pie_by_element( self, **kw ):
        schema = str( kw.get( 'schema' ) )
        cube = str( kw.get( 'cube' ) )
        rows = str( kw.get( 'rows' ) )
        column = str( kw.get( 'columns' ) )
        element = rows.split('.')[:-1]
        a=[]
        if cherrypy.session.has_key('temp_child'):
            for k in cherrypy.session['temp_child']:
                a.append(k.keys()[0])

            if not element in a:
                query = "select {" +'.'.join(map(lambda x: str(x), element)) +'.children} on rows from ' + cherrypy.session['bi_cube']
                
                schema = cherrypy.session['bi_schema']
                axis, data = rpc.RPCProxy( 'olap.schema' ).request( schema, query)
                child_len = len(axis[0])
                cherrypy.session['temp_child'].append({'.'.join(map(lambda x: str(x), element)): child_len})
        else:
            query = "select {" +'.'.join(map(lambda x: str(x), element)) +'.children} on rows from ' + cherrypy.session['bi_cube']
            schema = cherrypy.session['bi_schema']
            axis, data = rpc.RPCProxy( 'olap.schema' ).request( schema, query)
            child_len = len(axis[0])
            cherrypy.session['temp_child'] = [{'.'.join(map(lambda x: str(x), element)): child_len}]
        
        p_elem = rows.split(".")
        qr = []
        p_elem.pop(-1)
        counter = 1
        for x in p_elem:
            if counter == 1 :
                qr.append(x+".[all]")
            else:
                qr.append('.'.join(p_elem[0:counter]))
            counter = counter + 1
        query = "select {" + ','.join(qr)+',' +rows + "} on rows , {" + column + "} on columns from " + " " + cube
        elements = self.pie_chart( query, schema )
        elem = elements.replace( 'null', 'None' )
        elements = eval( elem )
        if elements.has_key( 'tg_flash' ):
            elements.pop( 'tg_flash' )
        return elements

    @expose( 'json' )
    def save_query( self, **kw ):
        flag = False
        name = str( kw.get( 'name' ) )
        query = str( kw.get( 'query' ) )
        schema = str( kw.get( 'schema' ) )
        cube = str( kw.get( 'cube' ) )
        if kw.get( 'overwrite' ):
            flag = str( kw.get( 'overwrite' ) )
        user_id = rpc.session.uid
        model = 'olap.saved.query'
        proxy = rpc.RPCProxy( model )
        times = str( datetime.datetime.now() )
        parse_qry = self.result_format.parse_query(query)
        rws = parse_qry[0][0]
        cls = parse_qry[0][1]
        pages = parse_qry[0][2]
        details = [[], [], []]
        
        for r in range(len(rws)):
            if rws[r].split(".")[-1] == 'children':
                parent = '.'.join(map(lambda x: x,rws[r].split(".")[:-1]))
                qry = "select {" +parent +'.children } on rows from ' + cherrypy.session['bi_cube']
                sch = cherrypy.session['bi_schema']
                rw_axis, data = rpc.RPCProxy( 'olap.schema' ).request( sch, qry, {'log': False})
                for ch in range(len(rw_axis[0])):
                    details[0].append(rws[r])
            else:
                details[0].append(rws[r])
        
        for c in range(len(cls)):
            if cls[c].split(".")[-1] == 'children':
                parent = '.'.join(map(lambda x: x,cls[c].split(".")[:-1]))
                col_qry = "select {" +parent +'.children } on rows from ' + cherrypy.session['bi_cube']    
                col_sch = cherrypy.session['bi_schema']
                cl_axis, cl_data = rpc.RPCProxy( 'olap.schema' ).request( col_sch, col_qry, {'log': False})
                for ch in range(len(cl_axis[0])):
                    details[1].append(cls[c])
            else:
                details[1].append(cls[c])
        if flag:
            id = cherrypy.session['saved_query_id']
            save_query = proxy.write( id , {'user_id': user_id, 'query': query, 'time':times, 'axis_keys': details} )
        else:
            save_query = proxy.create( {'name':name, 'user_id': user_id, 'query': query, 'cube_id': cube, 'schema_id': schema, 'time':times, 'axis_keys': details} )
        
        return dict()

    @expose( 'json' )
    def load_saved_query( self, **kw ):
        user_id = rpc.session.uid
        q_id = rpc.RPCProxy( 'olap.saved.query' ).search( [( 'user_id', '=', user_id )] )
        search_query = rpc.RPCProxy( 'olap.saved.query' ).read( q_id, ['name'] )
        qry_ids = [id['id'] for id in search_query]
        queries = [qry['name'] for qry in search_query]
        return dict( queries = queries, qry_ids = qry_ids )

    @expose( 'json' )
    def execute_saved_query( self, **kw ):
        qry_id = [int( kw.get( 'id' ) )]
        query = rpc.RPCProxy( 'olap.saved.query' ).read( qry_id, ['query'] )[0]['query']
        return dict( query = query )

    @expose( template = "/tinybi/widgets/templates/cube_firstdrop.mako" )
    def initial_view( self, **kw ):
        return dict()
    @expose( template = "/tinybi/widgets/templates/testing.mako" )
    def testing(self):
        return dict()

# vim: ts=4 sts=4 sw=4 si et

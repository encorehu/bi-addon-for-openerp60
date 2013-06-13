import time
import datetime
import calendar

import cherrypy
#from openobject.tools import widgets, mochikit

from openobject import tools
from openerp.widgets import TinyWidget # interface
from openerp.widgets import treegrid
from openerp.utils import rpc, TinyDict
from cube_view import schema_select_combo
from cube_view import mdx_query_output
from tinybi.widgets import result_format
from openobject.widgets import Form, JSLink, locations, CSSLink


#class Browser( tg.widgets.CompoundWidget, interface.TinyWidget ):
class Browser( TinyWidget ):
    template = "/tinybi/widgets/templates/browser_view.mako"
    params = ["widget_cube", "tree", "error"]
    member_widgets = ['screen', ]
    javascript = [
                  JSLink( "openerp", "javascript/treegrid.js", location = locations.bodytop ),
                  JSLink( "openerp", "javascript/form.js", location = locations.bodytop ),
                  #widgets.JSLink( "openerp", "javascript/Resize.js", location = tg.widgets.js_location.bodytop ),
                  JSLink( "tinybi", "javascript/popup.js", location = locations.bodytop ),
                  JSLink( "tinybi", "javascript/mdx_toolbar.js", location = locations.bodytop ),
                  JSLink( "tinybi", "javascript/browser_view.js", location = locations.bodytop ),
                  JSLink( "tinybi", "javascript/swfobject.js", location = locations.bodytop ),
                  JSLink( "openobject", "javascript/MochiKit/DragAndDrop.js", location = locations.bodytop ),
                  JSLink( "openerp", "javascript/dashboard.js", location = locations.bodytop )
                  ]
    css = [
            CSSLink( "openerp", "css/treegrid.css" ),
            CSSLink( "openerp", "css/style.css" ),
            CSSLink( "openerp", "css/dashboard.css" )
           ]

    res = result_format.Result_Format()
    def __init__( self, *args,**kw ):
        super(Browser, self).__init__(name="BI Browser")
        rows = []
        cols = []
        cols_cross_drill = []
        data = []
        pages = []
        pages_element = []
        slicers = []
        selected_schema = ''
        selected_cube = ''
        selected_query = ''
        widget_cube = {}
        cubes = []
        selectedCube = []
        schema = []
        sample = []
        header = ["___", "head1", "head2"]
        cubed = []
        proxy = rpc.RPCProxy( "olap.cube" )
        d_ids = proxy.search( [] )
        res = proxy.read( d_ids, ['id', 'name'] )
        for i in res:
            cubed.append( ( i['id'], str( i['name'] ) ) )
        cherrypy.session['cubes'] = cubed

        sch_proxy = rpc.RPCProxy( 'olap.schema' )
        sch_id = sch_proxy.search( [] )
        sch_res = sch_proxy.read( sch_id, ['id', 'name'] )
        for i in sch_res:
            schema.append( ( i['id'], str( i['name'] ) ) )

        cherrypy.session['schemas'] = schema

        if cherrypy.session.has_key( 'saved_model' ) and cherrypy.session.has_key( 'saved_query_id' ):
            
            model = str( cherrypy.session.get( 'saved_model' ) )
            id = cherrypy.session.get( 'saved_query_id' )
            execute = rpc.RPCProxy( model ).read( id, [] )[0]
            n_schema = execute['schema_id'][1]
            cube = execute['cube_id'][1]
            if cherrypy.session.has_key( 'bi_cube' ) and cherrypy.session['bi_cube'] != cube:
                cherrypy.session['hier_level'] = ''
                cherrypy.session['bi_cube'] = cube
                cherrypy.session['bi_cubeid'] = execute['cube_id'][0]
                cherrypy.session['bi_schema'] = n_schema
            else:
                cherrypy.session['bi_cube'] = cube
                cherrypy.session['bi_cubeid'] = execute['cube_id'][0]
                cherrypy.session['bi_schema'] = n_schema
            selected_query = execute['query']

            axis, data = rpc.RPCProxy( 'olap.schema' ).request( n_schema, selected_query )

            result = self.res.result_format( axis, data, execute['cube_id'][0], False, str(selected_query) )
            rows = result[0]
            cols = result[1]
            data = result[2]
            pages = result[3]
            cols_cross_drill = result[4]
            selected_schema = n_schema
            selected_cube = cube
            proxy = rpc.RPCProxy( "olap.cube" )
            cube_ids = proxy.search( [( 'schema_id', '=', int( execute['schema_id'][0] ) )] )
            res = proxy.read( cube_ids, ['id', 'name'] )

            for i in res:
                sample.append( ( i['id'], i['name'] ) )
            
            if args:
                slicer_list = args[0]
                if slicer_list:
                    st_counter = 0
                    for filter in slicer_list:
                        slicers.append( [st_counter, ','.join(map(lambda x: str(x),filter)), '.'.join(map(lambda x: "["+str(x)+"]",filter))] )
                        st_counter = st_counter + 1
    

        widget_cube['combo_schema'] = schema_select_combo( firsttext = "Select Schema",
                                                           name = "schema",
                                                           onselect = "_combo_select_schema(event,this.value);",
                                                           list = schema,
                                                           selected_schema = selected_schema,
                                                           sample = sample,
                                                           selected_cube = selected_cube,
                                                           selected_query = selected_query,
                                                           error = None )

        
        widget_cube['mdx_output'] = mdx_query_output( rows = rows,
                                                      cols = cols,
                                                      cols_cross_drill = cols_cross_drill,
                                                      data = data,
                                                      pages = pages,
                                                      slicers = slicers )

        model = 'olap.cube'
        params, data = TinyDict.split( kw )
        if params.model:
            model = params.model
        if params.parent_id:
            parent_id = params.parent_id
        if params.key_name:
            key_name = params.key_name

        headers = [
                       {'string' : 'Main tree', 'name' : 'string', 'type' : 'char'},
                       {'string' : 'S', 'name': 'slicer', 'type' : 'image', 'width': 2}
                   ]

        treewidget = treegrid.TreeGrid( 'view_tree',
                                        model = model,
                                        headers = headers,
                                        ids = ['2'],
                                        url = "/browser/data_browser",
                                        key_name = '',
                                        parent_id = '' )

        treewidget.showheaders = False
        treewidget.expandall = False
        treewidget.onbuttonclick = 'browser_onButtonClick'

        self.widget_cube = widget_cube
        self.tree = treewidget
        self.string = 'BI Browser View'
        self.error = None

# vim: ts=4 sts=4 sw=4 si et

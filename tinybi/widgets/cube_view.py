import openobject.tools as tg
import cherrypy
from openobject.tools import expose
#from openobject.tools import validators
from openerp.widgets import TinyWidget

class schema_select_combo( TinyWidget ):
    template = "/tinybi/widgets/templates/schema_select_combo.mako"
    params = ["firsttext",
              "schemalist",
              "onselect",
              "selected_schema",
              "sample",
              "selected_cube",
              "selected_query", "error"]
    def __init__( self, list = [], **kw ):
        super(schema_select_combo, self).__init__(name=kw.get('name'))
        self.cube_name = kw.get( 'second_name' )
        if kw.get( "list" ):
            self.schemalist = kw.get( "list" )
        else:
            self.schemalist = list
        self.error = kw.get( 'error' )
        self.onselect = kw.get( 'onselect' )
        self.firsttext = kw.get( "firsttext" )
        self.selected_schema = kw.get( 'selected_schema' )
        self.sample = kw.get( 'sample' )
        self.selected_cube = kw.get( 'selected_cube' )
        self.selected_query = kw.get( 'selected_query' )

class mdx_query_output( TinyWidget ):
    template = "/tinybi/widgets/templates/mdx_output.mako"
    params = ["rows", "cols", "data", "pages", "pages_element", "slicers","cols_cross_drill"]
    def __init__( self, **kw ):
        self.rows = kw.get( 'rows' )
        self.cols = kw.get( 'cols' )
        self.data = kw.get( 'data' )
        self.pages = kw.get( 'pages' )
        self.cols_cross_drill = kw.get('cols_cross_drill')
        self.slicers = kw.get( 'slicers' )

class cube_firstdrop( TinyWidget ):
    template = "/tinybi/widgets/templates/cube_firstdrop.mako"

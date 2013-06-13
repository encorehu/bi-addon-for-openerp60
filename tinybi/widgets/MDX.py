import time
import datetime
import calendar

import cherrypy
import openobject.tools as tg

from openobject import tools

from openerp.utils import rpc,TinyDict
from openobject.tools import redirect
from openerp.widgets import TinyWidget
from openerp.widgets import Form, JSLink, locations, CSSLink

class MDX_View( TinyWidget ):
    template = 'widgets.templates.mdx'
    javascript = [JSLink( "tinybi", "javascript/mdx_view.js" )]
    css = [
	       CSSLink( "tinybi", "css/mdx_view.css" ),
            ]
    params = ["header", "rows", "filters", "query", "schema"]

    def __init__( self, **attrs ):
        if attrs.get( 'ids' ):
            self.query = []
            self.schema = []
            self.filters = []
            self.rows = []
            self.header = []
            error = False
            if attrs.get( 'ids' ):
                if attrs.get( 'model' ) == 'olap.saved.query':
                    cherrypy.session['saved_model'] = attrs.get( 'model' )
                    cherrypy.session['saved_query_id'] = attrs.get( 'ids' )
#                    cherrypy.session['hier_level'] = ''
                    raise redirect( '/browser', model = attrs.get( 'model' ) )
                else:
                    query_id = rpc.RPCProxy( attrs['model'] ).search( [( 'id', '=', attrs.get( 'ids' )[0] )] )[0]
                    query_logs_obj = rpc.RPCProxy( attrs['model'] ).read( [query_id] )[0]
                    self.query = [str( query_logs_obj['query'] )]
                    cube_obj = rpc.RPCProxy( 'olap.cube' ).read( [query_logs_obj['cube_id'][0]] )[0]
                    self.schema = [cube_obj['schema_id'][1]]
            else:
                error = True
            if not error:
                try:
                    temp = {}
                    filter = self.query[0].split( "where" )
                    if len( filter ) > 1:
                        temp = filter[1].split( "," )
                        temp[0] = temp[0].lstrip()[1:]
                        temp[-1] = temp[-1][:-1]
                        res = []
                        for t in range( len( temp ) ):
                            res.append( [t, temp[t]] )
                        self.filters = res
                    axis, data = rpc.RPCProxy( 'olap.schema' ).request( self.schema[0], self.query[0] )
                    temp = self.form_data( axis, data )
                    self.header = temp['header']
                    self.rows = temp['rows']
                except:
                    error = True
                    rows = False

    def axis_maker( self, axis ):
        space_counter = 0
        table_data = []
        key = {}
        index = 0
        first_space_counter = len( axis[0][0] )
        dimension = []
        dimensions = 0
        ids = []
        for axis_data in axis:
            temp = {}
            t_str = ''
            for data in axis_data[0]:
                t_str = t_str + '[' + str( data ) + ']' + '.'
            ids.append( t_str )
            if space_counter < len( axis_data[0] ):
                space_counter = len( axis_data[0] )
            if first_space_counter > len( axis_data[0] ):
                first_space_counter = len( axis_data[0] )
            temp[index] = axis_data[1]
            key[index] = axis_data[0]
            if axis_data[0][0] == 'measures':
                temp['before_space'] = 0
            else:
                if ( len( axis_data[0] ) - 1 - first_space_counter < 0 ):
                    temp['before_space'] = 0
                else:
                    temp['before_space'] = len( axis_data[0] ) - first_space_counter
            table_data.append( temp )
            index = index + 1
        if space_counter == first_space_counter:
            space_counter = 0
        else:
            space_counter = space_counter - 1
        final_result = []
        keys = []
        index = 0
        key_name = table_data[0]
        key_key = key[0]
        for i in key.keys():
            temp = []
            x = table_data[i]['before_space']
            for t in range( 0, table_data[i]['before_space'] ):
                temp.append( '' )
            temp.append( table_data[i][i] )
            for t in range( 0, space_counter - x ):
                temp.append( '' )
            final_result.append( temp )
        result = {}
        result['data'] = final_result
        result['actual_len'] = len( axis )
        result['key'] = key
        return result

    def form_data( self, ax, da ):
        axis = ax
        data = da
        table_data = []
        d = []
        for x in data:
            for i in x:
                if ( isinstance( i, float ) ):
                    d.append( float( i ) )
                else:
                    if ( type( i ) == type( [] ) ):
                        d.append( float( i[0] ) )
                    else:
                        d.append( float( i ) )

        for data in axis:
            table_data.append( self.axis_maker( data ) )

        l_data = []
        for rows in table_data[0]['data']:
            temp = []
            l_data.append( rows )
        header = ['']
        if 1 in range( len( table_data ) ):
            for i in range( len( l_data[0] ) - 1 ):
                header.append( '' )
        else:
             for i in range( len( l_data[0] ) - 1 ):
                header.append( '' )

        counter = 0
        for index in range( len( l_data ) ):
            if 1 in range( len( table_data ) ):
                for x in table_data[1]['data']:
                    l_data[index].append( d[counter] )
                    counter = counter + 1
            else:
                l_data[index].append( d[index] )
        if 1 in range( len( table_data ) ):
            for x in table_data[1]['data']:
                header.append( x )
        res = {}
        res['header'] = header
        res['rows'] = l_data
        return res

    def remove_filter( self, index ):
        pop_filter = self.filters.pop( index )
        self.query = self.query.split( "where" )[0] + '(' + ','.join( self.filters ) + ')'




# vim: ts=4 sts=4 sw=4 si et

from pyparsing import *

from openobject.tools import expose
import cherrypy
from openerp.utils import rpc
import tinybi.widgets as widgets
from openerp.controllers import SecuredController


class mdx_query( object ):

    def __init__( self ):
        self.axes = [[], [], []]
        self.drill = [{}, {}, {}]
        self.crossjoins = [[], [], []]
        self.conditions = []
        self.cube = ''
        self.lastadded = []
        self.make_child = []

    def clearCube( self ):
        self.axes = [[], [], []]
        self.drill = [{}, {}, {}]
        self.crossjoins = [[], [], []]
        self.conditions = []
        self.lastadded = []
        if cherrypy.session.has_key( 'last_success_query' ):
            cherrypy.session['last_success_query'] = None

    def add_schema( self, schema ):
        self.schema = schema
        self.axes = [[], [], []]
        self.drill = [{}, {}, {}]
        self.crossjoins = [[], [], []]
        self.conditions = []
        self.lastadded = []
        self.make_child = []
        return dict()

    def make_cube( self, cube ):
        self.cube = cube
        return {}

    def add_cube( self, cube ):
        self.cube = cube
        self.axes = [[], [], []]
        self.drill = [{}, {}, {}]
        self.crossjoins = [[], [], []]
        self.conditions = []
        self.lastadded = []
        self.make_child = []
        return dict()

    def get_cube( self ):
        return self.cube

    def maxdepth( self, hierarchy_name, cube, schema, max ):
        res = []
        if len( hierarchy_name.split( "." ) ) > max:
            return res
        if '[/]' in hierarchy_name.split( "." ):
            return res
        query = "select {" + hierarchy_name + ".children} on rows from " + cherrypy.session['bi_cube']
        axis, data = rpc.RPCProxy( 'olap.schema' ).request( schema, query, {'log': False} )
        res.append( hierarchy_name + ".children" )
        a = []
        if cherrypy.session.has_key('temp_child'):
            for k in cherrypy.session['temp_child']:
                a.append(k.keys()[0])
            if not hierarchy_name in a:
                child_len = len(axis[0])
                cherrypy.session['temp_child'].append({hierarchy_name: child_len})
        else:
            child_len = len(axis[0])
            cherrypy.session['temp_child'] = [{hierarchy_name: child_len}]
        
        

 #        axis, data, error, last_query = cubeEngine.execute_mdx( '', cherrypy.session['bi_schema'], textquery, 'True' )
        if axis:
            for x in axis[0]:
                datax = x[1]
                if( type( datax ) <> type( False ) ):
                    if( type( datax ) == type( 0.0 ) ):
                        datax = int( datax )
                    hierarchy_name = hierarchy_name + ".[" + str( datax ) + "]"
                    children = self.maxdepth( hierarchy_name, cube, schema, max )
                    for i in children:
                        res.append(i)
                    hierarchy_name = hierarchy_name.split( "." )
                    hierarchy_name = '.'.join( hierarchy_name[:len( hierarchy_name ) - 1] )
        return res

    def collapse_all(self):
        schema_name = None
        cube_name = self.get_cube()
        if cherrypy.session.has_key( 'bi_schema' ):
            schema_name = cherrypy.session['bi_schema']
        else:
            print "This is the error "
            return None
        for index in range( len( self.axes ) ):
            axis = self.axes[index]
            result = []
            if axis:
                element_count = 0
                temp_axis = []
                for ax in axis:
                    element = ax.mdx_get()
                    if element.endswith( 'children' ):
                        pass
                    elif element.startswith('[measures]'):
                        result.append(element)
                    else:
                        result.append(element)
            
            self.axes[index] = []

            for items in result:
                temp = items.split( "." )
                main = []
                for i in temp:
                    if i.endswith( "]" ):
                        i = i[1:-1]
                    main.append( i )
                self.axes[index].append( mdx_axes( main ) )
            
            # Making of the drill
            self.drill[index] = {}
        return None        

    def expand_all( self ):
        schema_name = None
        cube_name = self.get_cube()
        if cherrypy.session.has_key( 'bi_schema' ):
            schema_name = cherrypy.session['bi_schema']
        else:
            print "This is the error "
            return None
        for index in range( len( self.axes ) ):
            axis = self.axes[index]
            result = []
            if axis:
                element_count = 0
                temp_axis = []
                for ax in axis:
                    element = ax.mdx_get()
                    if element.endswith( 'children' ):
                        '''
                            This elements is to be removes and not be taken in to the consideration
                        '''
                        pass
                    elif element.startswith('[measures]'):
                        result.append(element)
                    else:
                        items = element.split( "." )
                        result.append( element )
                        if cherrypy.session.has_key( 'hier_level' ):
                            level_len = cherrypy.session['hier_level']
                            level_len = level_len[items[0][1:-1]]
                            if items[-1] == '[all]':
                                items.pop()
                            items = '.'.join(items)
                            res = self.maxdepth( items, cube_name, schema_name, level_len )
                            
                            for x in  res:
                                result.append( x )
                        else:
                            print " This is the case of the error "
                            return None
            self.axes[index] = []

            for items in result:
                temp = items.split( "." )
                main = []
                for i in temp:
                    if i.endswith( "]" ):
                        i = i[1:-1]
                    main.append( i )
                self.axes[index].append( mdx_axes( main ) )
            
            # Making of the drill
            for ax in self.axes[index]:
                element = ax.mdx_get()
                if element.endswith('children'):
                    element = element.split(".")
                    element = '.'.join(element [:-1])
                    self.drill[index][element] = True
        return None

    def make_str( self, clause ):
        clause = clause.rstrip().lstrip()
        if clause and clause[0] == "{":
            clause = clause[1:len( clause ) - 1]
        query_part = []
        for data in clause.split( "," ):
            add = []
            for items in data.split( "." ):
                if items and ( items[0] == '[' ):
                     items = items[1:len( items ) - 1]
                add.append( items )
            query_part.append( add )
        return query_part

    def parseMDX( self, qr ):
        # This will parse the query in to forms needed

        lrbrack, rrbrack = map( Suppress, "()" )
        comma = Suppress( "," )
        leftCurlBr, rightCurlBr = map( Suppress, "{}" )
        dot = Suppress( "." )
        crossToken = Literal( "crossjoin" ).suppress()
        selectToken = Keyword( "select", caseless = True ).suppress()
        fromToken = Keyword( "from", caseless = True ).suppress()
        whereToken = Keyword( "where", caseless = True ).suppress()

        scalar = Word( alphanums + "_" + " " )
        cube = Word( alphas + '_' )
        level_scalar = Word( alphanums + "_" + " " )
        level_filter = Suppress( "[" ) + level_scalar + Suppress( "]" )
        level_function = Keyword( "children", caseless = True )
        level_item = level_filter | level_function
        levels = Group( level_item + Optional( dot + delimitedList( level_item, ".", combine = False ) ) )
        axis_parser = delimitedList( levels, ",", combine = False )
        where_parse = lrbrack + Group( delimitedList( levels , ",", combine = False ) ) + rrbrack

        cross_parser = leftCurlBr + levels + rightCurlBr
        crossx = Forward()
        cross_mdx = crossx | leftCurlBr + axis_parser + rightCurlBr
        crossx << ( crossToken + lrbrack + cross_mdx + comma + Group( cross_parser.setResultsName( "cross" ) ) + rrbrack )

        rowsmdx = leftCurlBr + axis_parser + rightCurlBr
        colsmdx = leftCurlBr + axis_parser + rightCurlBr
        pagemdx = leftCurlBr + axis_parser + rightCurlBr
        row_mdx_axis = rowsmdx | crossx
        col_mdx_axis = colsmdx | crossx
        row_names = ["rows", "columns", "pages"]
        onToken = Keyword( "on", caseless = True ).suppress()
        page_name = oneOf( ' '.join( row_names ) ).suppress()

        query_parser = selectToken + Group( row_mdx_axis ) + onToken + page_name + Optional( comma + Group( col_mdx_axis ) + onToken + page_name ) \
                + Optional( comma + Group( pagemdx ) + onToken + page_name ) \
                + fromToken + cube.suppress() + Optional( whereToken + where_parse )
        print " The parser set "


        qr = qr.split("where")
        query = query_parser.parseString( qr[0] )
        if len(qr)>1:
            where = where_parse.parseString(qr[1])
            for i in where[0]:
                self.conditions.append( mdx_axes(i))
        print " This is the result of the parser ",query
        # This is assumed query will have rows and columns and where clause its still not fully for pages
        # Still need to be modified
        ax = 0
        for items in query:
            for i in items:
                if i.cross:
                    self.crossjoins[ax].append( mdx_axes( list( i[0] ) ) )
                else:
                    if 'children' in list( i ):
                        self.drill[ax][str( i[0] )] = True
                    self.axes[ax].append( mdx_axes( i ) )
            ax = ax + 1
        print " Done with the parser "
        return dict()


    def remove_conditions( self, pos ):
        self.conditions.pop( pos )


    def add_conditions( self, cond = [] ):
        self.conditions.append( mdx_axes( cond ) )

    def fetch_slicer( self ):
        slice = []
        if( self.conditions ):
            for condition in self.conditions:
                slicer = []
                for x in condition.elements.items:
                    slicer.append( x.name )
                slice.append( slicer )
        return slice
    
    def page_axis(self):
        page_elem = []
        if(self.axes[2]):
            for page in self.axes[2]:
                pager = []
                for x in self.axes[2]:
                    item = x.mdx_get()
                    pager.append(item )
                page_elem.append( pager )
        return page_elem
                    
    
    def fetch_query_items( self ):
        axs = []
        if( self.axes[0] ):
            for axis in self.axes[0]:
                axis_data = []
                for x in axis.elements.items:
                    axis_data.append( x.name )
                axs.append( axis_data )
        if( self.axes[1] ):
            for axis in self.axes[1]:
                axis_data = []
                for x in axis.elements.items:
                    axis_data.append( x.name )
                axs.append( axis_data )
        return axs

    def fetch_query_items_row( self ):
        axs_row = []
        if ( self.axes[0] ):
            for axis in self.axes[0]:
                axis_data = []
                for x in axis.elements.items:
                    axis_data.append( x.name )
                axs_row.append( axis_data )
        return axs_row

    def fetch_query_items_col( self ):
        axs_col = []
        if ( self.axes[1] ):
            for axis in self.axes[1]:
                axis_data = []
                for x in axis.elements.items:
                    axis_data.append( x.name )
                axs_col.append( axis_data )
        return axs_col


    def mdx_get( self ):
        query_str = 'select  '
        for data in range( len( self.axes ) ):
            if data == 0 and self.axes[data]:
                temp = []
                cross = []
                if len( self.crossjoins[data] ) > 0:
                    for el in self.axes[0]:
                        temp.append( el.mdx_get() )
                    query_axis = '{' + ','.join( temp ) + ' }'
                    cross_str = ''
                    count = 0
                    for elements in self.crossjoins[0]:
                        if count == 0:
                            cross_str = 'crossjoin (' + query_axis + " , {" + elements.mdx_get() + " } )"
                        else:
                            cross_str = 'crossjoin (' + cross_str + " , {" + elements.mdx_get() + " })"
                        count = count + 1
                    query_str = query_str + cross_str + ' on rows'
                elif self.axes[data]:
                    for elements in self.axes[0]:
                        temp.append( elements.mdx_get() )
                    query_str = query_str + '{' + ','.join( temp ) + ' } on rows'

            if data == 1 and self.axes[data]:
                temp = []
                if len( self.crossjoins[data] ) > 0:
                    for el in self.axes[1]:
                        temp.append( el.mdx_get() )
                    query_axis = '{' + ','.join( temp ) + ' }'
                    cross_str = ''
                    count = 0
                    for elements in self.crossjoins[1]:
                        if count == 0:
                            cross_str = 'crossjoin (' + query_axis + " , {" + elements.mdx_get() + " })"
                        else:
                            cross_str = 'crossjoin (' + cross_str + " , {" + elements.mdx_get() + " })"
                        count = count + 1
                    query_str = query_str + ',' + cross_str + ' on columns'

                else:
                    for elements in self.axes[1]:
                        temp.append( elements.mdx_get() )
                    query_str = query_str + ', {' + ','.join( temp ) + ' } on columns'
            if data == 2 and self.axes[data]:
                temp = []
                for elements in self.axes[2]:
                    temp.append( elements.mdx_get() )
                query_str = query_str + ', {' + ','.join( temp ) + ' } on pages'

        query_str = query_str + ' from ' + self.cube
        if self.conditions:
            slicer = []
            for conditions in self.conditions:
                slicer.append( conditions.mdx_get() )
            query_str = query_str + ' where (' + ','.join( slicer ) + ')'
        return query_str


    def swap( self ):
        temp = self.axes[0]
        self.axes[0] = self.axes[1]
        self.axes[1] = temp
        self.axes[2] = self.axes[2]
        temp = self.drill[0]
        self.drill[0] = self.drill[1]
        self.drill[1] = temp
        r_cross = self.crossjoins[0]
        self.crossjoins[0] = self.crossjoins[1]
        self.crossjoins[1] = r_cross


    def remove_element( self, element, ax ):
        make_len = len( element )
        i = 0
        k = 0
        flag = False
        temp = []
        pos = 0
        for axis in self.axes[ax]:
            axis_data = []
            for x in axis.elements.items:
                axis_data.append( x.name )
            make_len = len( axis_data )
            make_key = element[1]

            if element == axis_data:
                temp.append( pos )
            elif make_key == 'all' and element[0] == axis_data[0]:
                for test in axis_data:
                   testloop = test;
                if testloop == 'children':
                   temp.append( pos )
            pos = pos + 1
        if temp:
            data = temp[0]
            for i in temp:
                self.axes[ax].remove( self.axes[ax][data] )

    def query_element( self, axis_remove = [] ):
        a = 0;
        q_number = 0;
        if( self.axes[0] ):
            pos = 0
            temp = []
            make_key = ''
            make_len = 0
            for axis in self.axes[0]:
                axis_data = []
                for x in axis.elements.items:
                    axis_data.append( x.name )

                if axis_remove == axis_data:
                    temp.append( pos )
                    make_len = len( axis_data )
                    make_key = axis_remove[0]
                elif make_key and make_key == axis_remove[0] and ( len( axis_data ) > make_len or axis_data[1] == 'children' ):
                    temp.append( pos )
                elif make_key:
                    break

                pos = pos + 1

            if temp:
                data = temp[0]
                for i in temp:
                    self.axes[0].remove( self.axes[0][data] )

        if( self.axes[1] ):
            pos = 0
            for axis in self.axes[1]:
                axis_data = []
                for x in axis.elements.items:
                    axis_data.append( x.name )
                if axis_remove == axis_data:
                    self.axes[1].remove( self.axes[1][pos] )
                pos = pos + 1
        return {}

    def remove_cross_joins( self, ax, pos ):
        if self.crossjoins[ax]:
            self.crossjoins[ax].pop( pos )
    
    def remove_page_axis(self, ax, pos):
        self.axes[2].pop(pos)

    def del_element( self, pos, ax ):
        axs = int( ax )
        if self.axes[axs]:
            curr_pos = int( pos )
            temp = []
            for axis in self.axes[axs][int( pos ):]:
                axis_data = []
                for x in axis.elements.items:
                    axis_data.append( x.name )
                if curr_pos == int( pos ):
                    temp.append( curr_pos )
                    make_len = len( axis_data )
                    make_key = axis_data[0]
                elif make_key and make_key == axis_data[0] and ( len( axis_data ) > make_len or axis_data[-1] == 'children' ):
                    temp.append( curr_pos )
                elif make_key:
                    break
                curr_pos = curr_pos + 1
            if axs == 0:
               if len( self.axes[0] ) > len( temp ):
                   if temp:
                       data = temp[0]
                       for i in temp:
                           self.axes[0].remove( self.axes[0][data] )
            elif axs == 1:
                if temp:
                    data = temp[0]
                    for i in temp:
                        self.axes[axs].remove( self.axes[axs][data] )
                    
                    if len(self.axes[axs]) == 0:
                        if self.axes[axs+1]:
                            self.axes[axs+1] = []
            elif axs == 2:
                if temp:
                    data = temp[0]
                    for i in temp:
                        self.axes[axs].remove( self.axes[axs][data] )
                    
        if axs!=2 and len(self.axes[axs]) == 0:
            if self.crossjoins[axs]:
                self.crossjoins[axs] = []            
        return {}

    def add_axes_rows( self, pos, axis = [] ):
        print "\n\n This is the axis ", axis
        t = {}
        t['data'] = '.'.join( axis )
        t['pos'] = pos
        self.lastadded.append( t )
        self.axes[0].insert( pos, mdx_axes( axis ) )


    def add_axes_cross_joins( self, ax, cross_axis = [] ):
        self.crossjoins[ax].append( mdx_axes( cross_axis ) )

    def remove_cross( self, axis, pos = 0 ):
        self.crossjoins[axis].pop( pos )

    def add_axes_cols( self, pos, axis = [] ):
        t = {}
        t['data'] = '.'.join( axis )
        t['pos'] = pos
        self.lastadded.append( t )
        self.axes[1].insert( pos, mdx_axes( axis ) )

    def add_axes_pages( self, pos, axis = [] ):
        if self.axes[1]:
            self.axes[2].insert( pos, mdx_axes( axis ) )
            return False
        else:
            return True


    def drill_decide( self, ax, axis = [], pos = 0, drilling='' ):
        drill_result = drilling
        if drill_result == 'notdrilled':
            self.drill_down( ax, axis, pos )
        else:
            if drill_result == 'drilled':
                self.drill_up( ax, axis, pos )
        return {}


    def cross_drill( self, cross_ax, cross_axis = [], pos = 0 ):
        total_elem = cross_axis[0].split(',')
        element = self.crossjoins[cross_ax][pos]
        temp = '.'.join( map( lambda x:x.mdx_get(), element.elements.items ))
        ret = 0 # 0 is removal of children 1 if added children
        if temp.endswith( "[all]" ) and len(total_elem)<=2:
            temp = ( map( lambda x:x.name, element.elements.items ))
            temp[-1] = 'children'
            self.crossjoins[cross_ax].pop( pos )
            self.crossjoins[cross_ax].insert( pos, mdx_axes( temp ))
            ret = 1
        elif temp.endswith( ".children" ) and len(total_elem)<=2:
            temp = ( map( lambda x:x.name, element.elements.items ))
            temp[-1] = 'all'
            self.crossjoins[cross_ax].pop( pos )
            self.crossjoins[cross_ax].insert( pos, mdx_axes( temp ))
            ret = 0
        elif temp.endswith('children'):
            temp = ( map( lambda x:x.name, element.elements.items ))
            temp.pop()
            self.crossjoins[cross_ax].pop( pos )
            self.crossjoins[cross_ax].insert( pos, mdx_axes( temp ))
            ret = 0
        else:
            temp = ( map( lambda x:x.name, element.elements.items ))
            temp.append('children')
            self.crossjoins[cross_ax].pop( pos )
            self.crossjoins[cross_ax].insert( pos, mdx_axes( temp ))
            ret = 1
        return ret

    def page_drill(self, ax, axis , pos=0):
        total_elem = axis[0].split(',')
        element = self.axes[ax][pos]
        temp = '.'.join( map( lambda x:x.mdx_get(), element.elements.items ))
        ret = 0 # 0 is removal of children 1 if added children
        if temp.endswith( "[all]" ) and len(total_elem)<=2:
            temp = ( map( lambda x:x.name, element.elements.items ))
            temp[-1] = 'children'
            self.axes[ax].pop( pos )
            self.axes[ax].insert( pos, mdx_axes( temp ))
            ret = 1
        elif temp.endswith( ".children" ) and len(total_elem)<=2:
            temp = ( map( lambda x:x.name, element.elements.items ))
            temp[-1] = 'all'
            self.axes[ax].pop( pos )
            self.axes[ax].insert( pos, mdx_axes( temp ))
            ret = 0
        elif temp.endswith('children'):
            temp = ( map( lambda x:x.name, element.elements.items ))
            temp.pop()
            self.axes[ax].pop( pos )
            self.axes[ax].insert( pos, mdx_axes( temp ))
            ret = 0
        else:
            temp = ( map( lambda x:x.name, element.elements.items ))
            temp.append('children')
            self.axes[ax].pop( pos )
            self.axes[ax].insert( pos, mdx_axes( temp ))
            ret = 1
        return ret
    
    def drill_down( self, ax, axis = [], pos = 0 ):
        len_axis = len( axis )
        t = {}
        done = -1
        insert_pos = pos
        if 1 not in  range( len( self.axes[ax] ) ):

            axis.append( 'children' )
            if ax == 0:
                self.add_axes_rows( pos + 1, axis )
            elif ax == 1:
                self.add_axes_cols( pos + 1, axis )
            elif ax == 2:
                self.add_axes_pages( pos + 1, axis )
            done = 1
        else:
            for data in self.axes[ax][pos:]:
                done = 0
                temp_c = []
                if len( axis ) == 1:
                    len_cal = len_axis
                    cmp = axis
                else:
                    len_cal = len_axis - 1
                    cmp = axis[:1]
                for i in range( 0, len_cal ):
                    temp_c.append( data.elements.items[i].name )

                if temp_c != cmp and len( temp_c ) == len( cmp ):
                    axis.append( 'children' )
                    if ax == 0:
                        self.add_axes_rows( pos + 1, axis )
                    elif ax == 1:
                        self.add_axes_cols( pos + 1, axis )
                    elif ax == 2:
                        self.add_axes_pages( pos + 1, axis )
                    done = 1
                    break
                insert_pos = insert_pos + 1
        if done == 0 or done == -1:
            axis.append( 'children' )
            if ax == 0:
                self.add_axes_rows( pos + 1, axis )
            elif ax == 1:
                self.add_axes_cols( pos + 1, axis )
            elif ax == 2:
                self.add_axes_pages( pos + 1, axis )

    def cross_list( self, ax ):
         cross_ele = []
         for cross in range( len( self.crossjoins[ax] ) ):
             cross_ele.append( self.crossjoins[ax][cross].mdx_get() )
         return cross_ele

    def drill_up( self, ax, axis = [], pos = 0 ):
        t = {}
        len_axis = len( axis )
        del_pos = []
        count = pos + 1
        for data in self.axes[ax][pos + 1:]:
            temp_c = []
            if data.mdx_get().endswith('[all]'):
                break
            for i in range( 0, len_axis ):
                if not len( data.elements.items ) <= len_axis:
                    temp_c.append( data.elements.items[i].name )
            if temp_c and temp_c[0]==axis[0]:
                if temp_c == axis:
                    del_pos.append( count )
                count = count + 1
            else:
                break
        count = del_pos[0]
        for item in del_pos:
            self.axes[ax].remove( self.axes[ax][count] )

    def swap_cross(self):
        # Considering the cross join is possible only on the rows and columns 
        # Rows = 0 and columns = 1 so we swap using temp
        error = False
        if not self.axes[1]:
            error = True
        else: 
            temp = self.crossjoins[0]
            self.crossjoins[0] = self.crossjoins[1]
            self.crossjoins[1] = temp
        return error

class mdx_axes( object ):
    def __init__( self, elements = [] ):
        self.elements = mdx_element( elements )

    def mdx_get( self ):
        t = self.elements.mdx_get()
        return self.elements.mdx_get()

class mdx_element( object ):
    def __init__( self, items = [] ):
        self.items = []
        for t in items:
             self.items.append( mdx_item( t ) )

    def mdx_get( self ):
        t = []
        for x in self.items:
            t.append( str( x.mdx_get() ) )
        return str( '.'.join( t ) )

class mdx_item( object ):
    def __init__( self, name = '' ):
        self.name = name

    def mdx_get( self ):
        if self.name == 'children':
            return str( self.name )
        else:
            return '[' + str( self.name ) + ']'

if __name__ == '__main__':
    q = mdx_query()
    q.cube = 'sale_order_line'



    q.add_axes_rows( 0, ['partner_country','all'] )
    q.add_axes_cols( 0, ['measures','Items Sold'] )
    q.mdx_get()
    q.add_axes_cross_joins( 0, ['User','all'] )
    q.add_axes_cross_joins( 0, ['Date','all'] )
    q.add_axes_cross_joins( 1, ['measures','Total Sold'] )
    q.mdx_get()
    q.cross_drill( 0, ['Date'], 1 )
    q.mdx_get()
    q.remove_cross( 0, 0 )
    q.mdx_get()
    q.remove_cross( 1, 0 )
    q.mdx_get()


# Class to act interfaces between mdx_class controller and kid view

mdx = mdx_query()

class mdx_mapper( SecuredController ):
    res = widgets.result_format.Result_Format()
    @expose()
    def add_schema( self, schemaname = None, **kw ):
        if ( schemaname == None ):
            schemaname = kw.get( 'schemaname' );
        a = mdx.add_schema( schemaname );
        return dict()

    def make_cube( self, cubename = None ):
        mdx.make_cube( cubename )
        return dict()

    @expose()
    def add_cube( self, cubename = None, **kw ):
        if ( cubename == None ):
            cubename = kw.get( 'cubename' );
        a = mdx.add_cube( cubename );
        return dict()


    def mdx_get_main( self, **kw ):
        a = mdx.mdx_get();
        return a

    @expose()
    def mdx_get( self, **kw ):
        a = mdx.mdx_get();
        return dict( query = a )
    
    @expose()
    def add_axis_on_pages(self, **kw):
        x = str( kw.get( 'axis' ) ).split( "." )
        x = map( lambda x: x[1:len( x ) - 1], x )
        err = mdx.add_axes_pages( int( kw.get( 'pos' ) ), x )
        if err:
            error = "On pages is not possbile"
            return dict(error=error)
        else:
            a = mdx.mdx_get();
            return dict(query = a)
    
    @expose()
    def add_axis_on_rows( self, **kw ):
        print "><<<<<<<<<<<<<<<<<<<<<<<<"
        print "::: axis :::",str( kw.get( 'axis' ) )
        print "::: pos :::",int( kw.get( 'pos' ) )
        x = str( kw.get( 'axis' ) ).split( "." )
        x = map( lambda x: x[1:len( x ) - 1], x )
        mdx.add_axes_rows( int( kw.get( 'pos' ) ), x );
        a = mdx.mdx_get();
        return dict( query = a )

    @expose()
    def add_axis_on_cross_rows( self, **kw ):
        x = str( kw.get( 'axis' ) ).split( "." )
        x = map( lambda x: x[1:len( x ) - 1], x )
        mdx.add_axes_cross_joins( int( kw.get( 'pos' ) ), x )
        a = mdx.mdx_get();
        return dict( query = a )

    @expose()
    def add_axis_on_cols( self, **kw ):
        x = str( kw.get( 'axis' ) ).split( "." )
        x = map( lambda x: x[1:len( x ) - 1], x )
        mdx.add_axes_cols( int( kw.get( 'pos' ) ), x );
        a = mdx.mdx_get();
        return dict( query = a )

    def cross_list( self, ax ):
        cross_list = mdx.cross_list( int( ax ) )
        return cross_list
    @expose()
    def add_axis_on_cross( self, **kw ):
        x = str( kw.get( 'element' ) ).split( "." )
        x = map( lambda x: x[1:len( x ) - 1], x )
        mdx.add_axes_cross_joins( int( kw.get( 'axis' ) ), x )
        a = mdx.mdx_get()
        cross_list = mdx.cross_list( int( kw.get( 'axis' ) ) )
        return dict( query = a, cross_list = cross_list )


    @expose()
    def add_element_on_col( self, **kw ):
        mdx.add_element_on_col( int( kw.get( 'pos' ) ), int( kw.get( 'subpos' ) ), kw.get( 'element' ) );
        return dict()

    @expose()
    def add_element_on_row( self, **kw ):
        mdx.add_element_on_row( int( kw.get( 'pos' ) ), int( kw.get( 'subpos' ) ), kw.get( 'element' ) );
        return dict()

    @expose( template = 'openerp.widgets.templates.mdx_output' )
    def swap( self, **kw ):
        mdx.swap()
        query = mdx.mdx_get()
        print "Query:>>>>>>>>>>>>>>>>",query
        schema = str(cherrypy.session['bi_schema'])
        axis, data = rpc.RPCProxy( 'olap.schema' ).request( schema, query )
        result = self.res.result_format( axis, data, None, False, str(query) )
        rows = result[0]
        cols = result[1]
        data = result[2]
        pages = result[3]
        cols_cross_drill = result[4]
        fetch_slicers = self.fetch_all_slicer()
        slicers = []
                
        if fetch_slicers:
            st_counter = 0
            for filter in fetch_slicers:
                slicers.append( [st_counter, '.'.join(map(lambda x: "["+x+"]",filter))] )
                st_counter = st_counter + 1
        else:
            slicers = []
        return dict( rows = rows, cols = cols, data = data, pages = pages, slicers = slicers,cols_cross_drill = cols_cross_drill)
        
    def get_drill( self ):
        return mdx.drill
    
    @expose()
    def page_drill(self, **kw):
        ret = mdx.page_drill( int( kw.get( 'axis' ) ), [str( kw.get( 'element' ) )], int( kw.get( 'pos' ) ) )
        a_qry = mdx.mdx_get()
        page_list = mdx.page_axis()
        element = str( kw.get( 'element' ) ).split(",")
        element = '.'.join(map(lambda x : "[" + x+"]",element))
        a=[]
        if ret:
            if cherrypy.session.has_key('temp_child'):
                for k in cherrypy.session['temp_child']:
                    a.append(k.keys()[0])
                if not element in a:
                    qry = "select {" +element +'.children } on rows from ' + cherrypy.session['bi_cube']
                    schema = cherrypy.session['bi_schema']
                    axis, data = rpc.RPCProxy( 'olap.schema' ).request( schema, qry, {'log': False})
                    child_len = len(axis[0])
                    cherrypy.session['temp_child'].append({element: child_len})
            else:
                qry = "select {" +element +'.children } on rows from ' + cherrypy.session['bi_cube']
                schema = cherrypy.session['bi_schema']
                axis, data = rpc.RPCProxy( 'olap.schema' ).request( schema, qry, {'log': False})
                child_len = len(axis[0])
                cherrypy.session['temp_child'] = [{element: child_len}]
        return dict(query = a_qry, page_list = page_list)
    
    @expose()
    def drill( self, **kw ):
        y =  kw.get( 'element' ).encode('utf-8')
        element = y.split(",")
        element = '.'.join(map(lambda x : "[" + x+"]",element))
        a=[]
        if cherrypy.session.has_key('temp_child'):
            for k in cherrypy.session['temp_child']:
                a.append(k.keys()[0])
            if not element in a:
                query = "select {" +element +'.children } on rows from ' + cherrypy.session['bi_cube']
                schema = cherrypy.session['bi_schema']
                axis, data = rpc.RPCProxy( 'olap.schema' ).request( schema, query, {'log': False})
                child_len = len(axis[0])
                cherrypy.session['temp_child'].append({element: child_len})
        else:
            query = "select {" +element +'.children } on rows from ' + cherrypy.session['bi_cube']
            schema = cherrypy.session['bi_schema']
            axis, data = rpc.RPCProxy( 'olap.schema' ).request( schema, query, {'log': False})
            child_len = len(axis[0])
            cherrypy.session['temp_child'] = [{element: child_len}]
            
        data = []
        if y.split(",") :
            data = y.split(",")

        else:
            data.append( y )
        data_new = []

        for d in data:
            if d.split( "." ):
                temp = d.split( "." )
                data_new.append( temp[0] )
            else:
                data_new.append( d )
        mdx.drill_decide( int( kw.get( 'axis' ) ), data_new, int( kw.get( 'pos' ) ), str( kw.get( 'drilling' ) ) )
        a_query = mdx.mdx_get()
        return dict( query = a_query )

    @expose()
    def cross_drill( self, **kw ):
        ret = mdx.cross_drill( int( kw.get( 'axis' ) ), [str( kw.get( 'element' ) )], int( kw.get( 'pos' ) ) )
        a_qry = mdx.mdx_get()
        cross_list = mdx.cross_list( int( kw.get( 'axis' ) ) )
        cross_list = cross_list[int( kw.get( 'pos' ) )]
        element = str( kw.get( 'element' ) ).split(",")
        element = '.'.join(map(lambda x : "[" + x+"]",element))
        a=[]
        if ret:
            if cherrypy.session.has_key('temp_child'):
                for k in cherrypy.session['temp_child']:
                    a.append(k.keys()[0])
                if not element in a:
                    qry = "select {" +element +'.children } on rows from ' + cherrypy.session['bi_cube']
                    schema = cherrypy.session['bi_schema']
                    axis, data = rpc.RPCProxy( 'olap.schema' ).request( schema, qry, {'log': False})
                    child_len = len(axis[0])
                    cherrypy.session['temp_child'].append({element: child_len})
            else:
                qry = "select {" +element +'.children } on rows from ' + cherrypy.session['bi_cube']
                schema = cherrypy.session['bi_schema']
                axis, data = rpc.RPCProxy( 'olap.schema' ).request( schema, qry, {'log': False})
                child_len = len(axis[0])
                cherrypy.session['temp_child'] = [{element: child_len}]
        
        return dict( query = a_qry, cross_list = cross_list)

    @expose()
    def remove_cross_joins( self, **kw ):
        axis = int( kw.get( 'axis' ) )
        element = int( kw.get( 'element' ) )
        mdx.remove_cross_joins( axis, element )
        query = mdx.mdx_get()
        return dict( query = query )
    
    @expose()
    def remove_page_axis(self, **kw):
        axis = int( kw.get( 'axis' ) )
        element_index = int( kw.get( 'element_id' ) )
        mdx.remove_page_axis(axis, element_index)
        query = mdx.mdx_get()
        return dict(query = query)
    
    @expose()
    def slicer( self, **kw ):
        status = ''
        slicer_list = mdx.fetch_slicer()
        x = str( kw.get( 'elem' ) ).split( "." )
        x = map( lambda x: x[1:len( x ) - 1], x )

        if not ( x in slicer_list ):
            mdx.add_conditions( x )
            status = 'activated'
        a = mdx.mdx_get();
        return dict( query = a, status = status )


    def fetch_all_slicer( self ):
        slicer_list = mdx.fetch_slicer()
        return slicer_list
    
    def page_axis(self):
        page_list = mdx.page_axis()
        return page_list
    
    @expose()
    def remove_slicer( self, pos ):
        mdx.remove_conditions( int( pos ) )
        query = mdx.mdx_get();
        return dict( query = query )

    def listparser( self, list ):
        list_ret = []
        for l in list:
            tt = ''
            if 'children' in l:
                l.pop()
                tt = '[' + '].['.join( l ) + ']'
                tt = tt + '.children'
                list_ret.append( tt )
            else:
                tt = '[' + '].['.join( l ) + ']'
                list_ret.append( tt )
        return list_ret

    @expose()
    def listsliceritems( self, **kw ):
        list = mdx.fetch_slicer()
        list = self.listparser( list )
        return dict( list = list )

    @expose()
    def listqueryitems( self, **kw ):
        list = mdx.fetch_query_items()
        list = self.listparser( list )
        return dict( list = list )

 #   This is the new implementation for the removing query elements
    @expose()
    def remove_element( self, **kw ):
        elem = str( kw.get( 'elem' ) ).split( "." )
        axis = int( kw.get( 'axis' ) )
        flag = kw.get( 'flag_measure' );
        if flag == 'true':
            elem.insert( 0, 'measures' )
        elif len( elem ) == 1:
            elem.append( 'all' )
        mdx.remove_element( elem, axis )
        return dict()

    @expose()
    def query_element( self, **kw ):
        status = ''
        query_items_list_row = mdx.fetch_query_items_row()
        query_items_list_col = mdx.fetch_query_items_col()
        query_items_list = mdx.fetch_query_items()
        x = str( kw.get( 'elem' ) ).split( "." )
        x = map( lambda x: x[1:len( x ) - 1], x )
        axis = int( kw.get( 'axis' ) )
        a = 0;
        row_list = []
        for q_list_row in query_items_list_row:
            row_list.append( q_list_row )
            q_number = a;
            a = a + 1;
        col_list = []
        for q_list_col in query_items_list_col:
            col_list.append( q_list_col )
        if q_number > 0 or ( x in col_list ):
            mdx.query_element( x )
            status = 'de-activated';
        else:
            mdx.query_element( x )
            status = 'activated';
        query_str = mdx.mdx_get();
        return dict( query = query_str, status = status )



    @expose()
    def del_element( self, **kw ):
        pos = str( kw.get( 'pos' ) )
        ax = str( kw.get( 'ax' ) )
        status = ''
        mdx.del_element( pos, ax )
        a = mdx.mdx_get();
        return dict( query = a, pos = pos, ax = ax )

    @expose()
    def clearCube( self ):
        cube = mdx.get_cube()
        mdx.clearCube()
        mdx.add_cube( cube )
        if cherrypy.session.has_key( 'mdx_query' ):
            cherrypy.session.pop( 'mdx_query' )

        return {}

    @expose()
    def get_cube( self ):
        return mdx.get_cube()

    @expose()
    def parseMDX( self, query = None ):
        mdx.clearCube()
        mdx.parseMDX( query )

        return dict( query = mdx.mdx_get() )

    @expose()
    def expand_all( self ):
        mdx.expand_all()
        return dict( query = mdx.mdx_get() )

    @expose()
    def collapse_all( self ):
        mdx.collapse_all()
        return dict( query = mdx.mdx_get())
    
    @expose()
    def swap_cross(self):
        ret = mdx.swap_cross()
        if ret:
            error = " BI ERROR : You Should add cols to accomplish swap."
            return dict(error = error)
        else:
            a = mdx.mdx_get()
            print " This is the query to be return >>>>>>>>>>>",a
        return dict(query = a)
    
# vim: ts=4 sts=4 sw=4 si et    

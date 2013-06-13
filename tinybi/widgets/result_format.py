###############################################################################
#
# Copyright (C) 2007-TODAY Tiny ERP Pvt Ltd. All Rights Reserved.
# Modified by Raphael Alla <raphael@mitija.com>
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
import datetime
import math
import sqlalchemy
from openobject.tools import expose
from openerp.controllers import SecuredController

import cherrypy

from openobject import tools
from openobject.i18n import format

#from openerp.tinyres import TinyResource
from openerp.utils import rpc, common, TinyDict

import pyparsing
from pyparsing import *

class Result_Format( SecuredController ):

    #@expose()
    def parse_query(self, query):
        result = []
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
        level_scalar = Word( alphanums+alphas8bit.encode("utf-8") + "_" + " " )
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
                + Optional( comma + Group( pagemdx ) + onToken + page_name )\
                + fromToken + cube.suppress() + Optional( whereToken + Group(where_parse ))
        print " This is the query",query
        query = query.split("where")
        qr = query_parser.parseString(query[0])
        conditions = []

        axes = [[],[],[]]
        crossjoins=[[],[],[]]
        ax = 0
        for items in qr:
            for i in items:
                if i.cross:
                    if i[0][-1] == 'children':
                        crossjoins[ax].append( '.'.join(map(lambda x: "[" + x +"]",i[0][:-1]))+".children")
                    else:
                        crossjoins[ax].append( '.'.join(map(lambda x: "[" + x +"]",i[0])))
                else:
                    if i[-1] == 'children':
                        axes[ax].append( '.'.join(map(lambda x: "[" + x +"]",i[:-1]))+".children")
                    else:
                        axes[ax].append( '.'.join(map(lambda x: "[" + x +"]",i)))
            ax = ax + 1
        result.append(axes)
        result.append(crossjoins)
        return result    
    
    #@expose()
    def generate_position(self, axis = [], elem = []):
        ids = []
        axis_counter = 0
        element_key = ''
        element = {}
        id = 0
        for index in range(len(axis)):
            if index == 0:
                element_key = elem[index]

            elif elem[index]==element_key:
                id = id
            else:
                id = id + 1
                element_key = elem[index]
            key_value = axis[index][0][:axis[index][0].index(axis[index][1])+1]
            ids.append([str(axis_counter),{'text': axis[index][1].encode('utf-8'), 'key_value': key_value, 'id': id}])
            axis_counter = axis_counter + 1
        return ids
    
    #@expose()
    def result_format(self, axis, ax_datas, cube_id, flag, query):
        print "+++++++++++++++++++"
        print 'axis ', axis
        print 'ax_datas  ', ax_datas
        print 'cube_id ', cube_id
        print 'flag ', flag
        print ax_datas.__class__

        if len(axis) <=1:
            for ax_d in range(len(ax_datas)):
                if type(ax_datas[ax_d][0]) == type(False):
                    ax_datas[ax_d][0] = ''
        if flag == False:
            if cherrypy.session.has_key('mdx_query'):
                if not cherrypy.session['mdx_query'].__contains__(query):
                    cherrypy.session['mdx_query'].append(query)
            else:
                qry_list = []
                qry_list.append(query)
                cherrypy.session['mdx_query'] = qry_list
        res = self.parse_query(query)
        axes = res[0]
        crossjoins = res[1]
        rows_element = axes[0]
        cols_element = axes[1]
        pages_element = axes[2]
        cross_rows = crossjoins[0]
        cross_cols = crossjoins[1]
        rows = {}
        cols = {}
        pages = {}
        datas = {}
        count = 0
        res_key_ids = [[], [], []]
        items = []
        temps_keys =[]
        result = []
        main_count = 0
        x_elem = []
        col_x_elem = []
        page_x_elem = []
        
        for index in range(len(pages_element)):
            row = pages_element[index].split(".")
            if row[-1]=='[all]':
                page_x_elem.append(pages_element[index])
            elif row[-1]=='children':
                key_row = '.'.join(row[:-1])
                if cherrypy.session.has_key('temp_child'):
                    for lens in cherrypy.session['temp_child']:
                        if key_row in lens.keys():
                            to_append = lens[key_row]
                            for i in range(int(to_append)):
                                page_x_elem.append(pages_element[index])
            else:
                page_x_elem.append(pages_element[index])
                
        save_row_ids = []
        for index in range(len(rows_element)):
            row = rows_element[index].split(".")
            if row[-1]=='[all]':
                x_elem.append(rows_element[index])
                save_row_ids.append({index: rows_element[index]})
            elif row[-1]=='children':
                key_row = '.'.join(row[:-1])
                if cherrypy.session.has_key('temp_child'):
                    for lens in cherrypy.session['temp_child']:
                        if key_row in lens.keys():
                            to_append = lens[key_row]
                            for i in range(int(to_append)):
                                x_elem.append(rows_element[index])
                                save_row_ids.append({index: rows_element[index]})
                else:
                    model = 'olap.saved.query'
                    search_id = rpc.RPCProxy(model).search([('query','=',query)])
                    read_id = rpc.RPCProxy( model ).read( search_id )[0]
                    axis_keys = eval(read_id['axis_keys'])
                    for a_k in axis_keys[0]:
                        if '.'.join(row) == a_k:
                            x_elem.append(rows_element[index])
                            save_row_ids.append({index: a_k})
            else:
                x_elem.append(rows_element[index])
                save_row_ids.append({index: rows_element[index]})
                
        save_col_ids = []
        for index in range(len(cols_element)):
            row = cols_element[index].split(".")
            if row[-1]=='[all]':
                col_x_elem.append(cols_element[index])
                save_col_ids.append({index: cols_element[index]})
            elif row[-1]=='children':
                key_row = '.'.join(row[:-1])
                if cherrypy.session.has_key('temp_child'):
                    for lens in cherrypy.session['temp_child']:
                        if key_row in lens.keys():
                            to_append = lens[key_row]
                            for i in range(int(to_append)):
                                col_x_elem.append(cols_element[index])
                                save_col_ids.append({index: cols_element[index]})
#                        else:
#                            qry = "select {" +key_row +'.children} on rows from ' + cherrypy.session['bi_cube']
#                            schema = cherrypy.session['bi_schema']
#                            c_axis, c_data = rpc.RPCProxy( 'olap.schema' ).request( schema, qry, {'log': False})
#                            ch_len = len(c_axis[0])
#                            cherrypy.session['temp_child'].append({key_row: ch_len})
#                            for lens in cherrypy.session['temp_child']:
#                                if key_row in lens.keys():
#                                    to_append = lens[key_row]
#                                    for i in range(int(to_append)):
#                                        col_x_elem.append(cols_element[index])
#                                        save_col_ids.append({index: cols_element[index]})
#                else:
#                    query = "select {" +key_row +'.children} on rows from ' + cherrypy.session['bi_cube']
#                    schema = cherrypy.session['bi_schema']
#                    c_axis, c_data = rpc.RPCProxy( 'olap.schema' ).request( schema, query, {'log': False})
#                    child_len = len(c_axis[0])
#                    cherrypy.session['temp_child'] = [{key_row: child_len}]
#                    for lens in cherrypy.session['temp_child']:
#                        if key_row in lens.keys():
#                            to_append = lens[key_row]
#                            for i in range(int(to_append)):
#                                col_x_elem.append(cols_element[index])
#                                save_col_ids.append({index: cols_element[index]})
            else:
                col_x_elem.append(cols_element[index])
                save_col_ids.append({index: cols_element[index]})
        rev_row = x_elem[:]
        rows_ids = save_row_ids[:]
        drill= []
        for dt in cross_rows:
            rev_row = x_elem[:]
            data = dt.split(".")
            if data[-1]=='children':
                key_row = '.'.join(data[:-1])
                if cherrypy.session.has_key('temp_child'):
                     for lens in cherrypy.session['temp_child']:
                        if key_row in lens.keys():
                            to_append = lens[key_row]
                            for i in range(int(to_append)-1):
                                x_elem.extend(rev_row)
#                        else:
#                            qry = "select {" +key_row +'.children} on rows from ' + cherrypy.session['bi_cube']
#                            schema = cherrypy.session['bi_schema']
#                            r_axis, r_data = rpc.RPCProxy( 'olap.schema' ).request( schema, qry, {'log': False})
#                            ch_len = len(r_axis[0])
#                            cherrypy.session['temp_child'].append({key_row: ch_len})
#                            for lens in cherrypy.session['temp_child']:
#                                if key_row in lens.keys():
#                                    to_append = lens[key_row]
#                                    for i in range(int(to_append)):
#                                        x_elem.append(rows_element[index])
#                                        save_row_ids.append({index: rows_element[index]})
#                else:
#                    qry = "select {" +key_row +'.children} on rows from ' + cherrypy.session['bi_cube']
#                    schema = cherrypy.session['bi_schema']
#                    r_axis, r_data = rpc.RPCProxy( 'olap.schema' ).request( schema, qry, {'log': False})
#                    child_len = len(r_axis[0])
#                    cherrypy.session['temp_child'] = [{key_row: child_len}]
#                    for lens in cherrypy.session['temp_child']:
#                        if key_row in lens.keys():
#                            to_append = lens[key_row]
#                            for i in range(int(to_append)):
#                                x_elem.append(rows_element[index])
#                                save_row_ids.append({index: rows_element[index]})
        for x in range(int(len(x_elem)-1)):
            save_row_ids.extend(rows_ids)
        rev_col = col_x_elem[:]
        cols_ids = save_col_ids[:]
        for col_dt in cross_cols:
            rev_col = col_x_elem[:]
            data = col_dt.split(".")
            if data[-1]=='children':
                key_row = '.'.join(data[:-1])
                if cherrypy.session.has_key('temp_child'):
                     for lens in cherrypy.session['temp_child']:
                        if key_row in lens.keys():
                            to_append = lens[key_row]

                            for i in range(int(to_append)-1):
                                col_x_elem.extend(rev_col)
                                
#                        else:
#                            qry = "select {" +key_row +'.children} on rows from ' + cherrypy.session['bi_cube']
#                            schema = cherrypy.session['bi_schema']
#                            c_axis, c_data = rpc.RPCProxy( 'olap.schema' ).request( schema, qry, {'log': False})
#                            ch_len = len(c_axis[0])
#                            cherrypy.session['temp_child'].append({key_row: ch_len})
#                            for lens in cherrypy.session['temp_child']:
#                                if key_row in lens.keys():
#                                    to_append = lens[key_row]
#                                    for i in range(int(to_append)):
#                                        col_x_elem.append(cols_element[index])
#                                        save_col_ids.append({index: cols_element[index]})
#                else:
#                    qry = "select {" +key_row +'.children} on rows from ' + cherrypy.session['bi_cube']
#                    schema = cherrypy.session['bi_schema']
#                    c_axis, c_data = rpc.RPCProxy( 'olap.schema' ).request( schema, qry, {'log': False})
#                    child_len = len(c_axis[0])
#                    cherrypy.session['temp_child'] = [{key_row: child_len}]
#                    for lens in cherrypy.session['temp_child']:
#                        if key_row in lens.keys():
#                            to_append = lens[key_row]
#                            for i in range(int(to_append)):
#                                col_x_elem.append(cols_element[index])
#                                save_col_ids.append({index: cols_element[index]})
                    

        for x in range(int(len(col_x_elem)-1)):
            save_col_ids.extend(cols_ids)
            
        rev_col = col_x_elem[:]
        if page_x_elem:
            page_res = self.generate_position(axis[2], page_x_elem)
            page_ids = page_res
        else:
            page_ids = []
        
        main_c = 0
        child_c = 0
        
        for index in range(len(axis)):
            main_dict = {}
            main_c = 0
            keys_parent = []
            parent_q_elem = ''
            key_elem = ''
            for ax in range(len(axis[index])):
                element_key = ''
                element = {}
                items = None
                if index == 0 :
                    main_dict = rows
                    x_elem = x_elem
                elif index == 1:
                    main_dict = cols
                    x_elem = col_x_elem
                elif index == 2:
                    main_dict = pages
                    x_elem = page_x_elem
                
                find_element = x_elem[ax].split(".")
                
                if axis[index][ax][0][axis[index][ax][0].index(axis[index][ax][1])+1:]:
                    if axis[index][ax][0][axis[index][ax][0].index(axis[index][ax][1])+1:].__contains__(axis[index][ax][1]):
                        key_value = axis[index][ax][0][:axis[index][ax][0].index(axis[index][ax][1])+2]
                    else:
                        key_value = axis[index][ax][0][:axis[index][ax][0].index(axis[index][ax][1])+1]
                else:
                    key_value = axis[index][ax][0][:axis[index][ax][0].index(axis[index][ax][1])+1]
                
                if find_element[-1]=='[all]':
                    element_key = str(main_c)
                    keys_parent.append(('.'.join(axis[index][ax][0][:axis[index][ax][0].index(axis[index][ax][1])+1]),element_key))

                    main_c = main_c + 1
                    text = str(axis[index][ax][1])

                    drill_axis = axis[index][ax][0][axis[index][ax][0].index(axis[index][ax][1])+1:]
                    
                    cross_drills = None
                    if drill_axis:
                        cross_counter = 0
                        cross_drills = []
                        if index == 0:
                            cross_check = cross_rows
                        elif index == 1:
                            cross_check = cross_cols
                        for cross in range(len(drill_axis)):
                            if cross_check[cross].split(".")[-1] == 'children':
                                cross_class = 'drilled'
                            else:
                                cross_class = 'notdrilled'
                            cross_drills.append([str(cross_counter),','.join(map(lambda x: x.encode('utf-8'),drill_axis[cross])), cross_class])
                            cross_counter = cross_counter + 1
                    else:
                        cross_drills = None
                    
                    if index == 0:
                        on_remove = save_row_ids[ax].keys()[0]
                    elif index == 1:
                        on_remove = save_col_ids[ax].keys()[0]
                        
                    elif index == 2:
                        on_remove = page_ids[ax][1]['id']
                    
                    
                    element = {'text': text, 'parent': None, 'key_value': key_value, 'cross_drill': cross_drills, 'on_remove': on_remove}
                    parent_q_elem = ''

                elif find_element[-1]=='children':
                    temp = keys_parent[:]
                    temp.reverse()
                    if axis[index][ax][0].count(axis[index][ax][1])>1:
                        axis_counter = axis[index][ax][0].count(axis[index][ax][1]) -1
                        parent_key_compare = '.'.join(axis[index][ax][0][:axis[index][ax][0].index(axis[index][ax][1])+axis_counter])
                    else:
                        parent_key_compare = '.'.join(axis[index][ax][0][:axis[index][ax][0].index(axis[index][ax][1])])
                    if not parent_q_elem or parent_q_elem!=x_elem[ax]:
#                        if not temp:
#                            if not element_key:
#                                element_key = str(main_c)
#                            else:
#                                element_key = str(main_c)
#                            main_c = main_c + 1
                        for x in temp:
                            if x[0] == parent_key_compare:
                                parent_q_elem = x_elem[ax]
                                child_c = 0
                                key_elem = x[1]
                                element_key = x[1]+"."+str(child_c)
                                break
#                            else:
#                                element_key = str(main_c)
#                                main_c = main_c + 1
#                                break

                    elif parent_q_elem:
                        child_c = child_c +1
                        element_key = key_elem+"."+str(child_c)
                    text = axis[index][ax][1].encode("utf-8")
                    drill_axis = axis[index][ax][0][axis[index][ax][0].index(axis[index][ax][1])+axis[index][ax][0].count(axis[index][ax][1]):]
                    cross_drills = None
                    if drill_axis:
                        cross_counter = 0
                        cross_drills = []
                        if index == 0:
                            cross_check = cross_rows
                        elif index == 1:
                            cross_check = cross_cols
                            
                        for cross in range(len(drill_axis)):
                            if cross_check[cross].split(".")[-1] == 'children':
                                cross_class = 'drilled'
                            else:
                                cross_class = 'notdrilled'
                            cross_drills.append([str(cross_counter),','.join(map(lambda x: x.encode('utf-8'),drill_axis[cross])), cross_class])
                            cross_counter = cross_counter + 1
                    else:
                        cross_drills = None
                    if key_elem:
                        parent = key_elem
                    else:
                        parent = None
                    
                    if index == 0:
                        on_remove = save_row_ids[ax].keys()[0]
                    elif index == 1:
                        on_remove = save_col_ids[ax].keys()[0]
                    elif index == 2:
                        on_remove = page_ids[ax][1]['id']
                    element = {'text': text, 'parent': parent, 'key_value': key_value, 'cross_drill': cross_drills, 'on_remove': on_remove}
                    keys_parent.append(('.'.join(axis[index][ax][0][:axis[index][ax][0].index(axis[index][ax][1])+1]),element_key))

                else:

                    element_key = str(main_c)
                    keys_parent.append(('.'.join(axis[index][ax][0][:axis[index][ax][0].index(axis[index][ax][1])+1]),element_key))
                    main_c = main_c + 1
                    text = str(axis[index][ax][1])

                    drill_axis = axis[index][ax][0][axis[index][ax][0].index(axis[index][ax][1])+1:]
                    cross_drills = None
                    if drill_axis:
                        cross_counter = 0
                        cross_drills = []
                        
                        if index == 0:
                            cross_check = cross_rows
                        elif index == 1:
                            cross_check = cross_cols
                        
                        for cross in range(len(drill_axis)):
                            if cross_check[cross].split(".")[-1] == 'children':
                                cross_class = 'drilled'
                            else:
                                cross_class = 'notdrilled'
                            
                            cross_drills.append([str(cross_counter),','.join(map(lambda x: x.encode('utf-8'),drill_axis[cross])), cross_class])
                            cross_counter = cross_counter + 1
                    else:
                        cross_drills = None
                    
                    if index == 0:
                        on_remove = save_row_ids[ax].keys()[0]
                    elif index == 1:
                        on_remove = save_col_ids[ax].keys()[0]
                    elif index == 2:
                        on_remove = page_ids[ax][1]['id']
                        
                    element = {'text': text, 'parent': None, 'key_value': key_value, 'cross_drill': cross_drills, 'on_remove': on_remove}
                    parent_q_elem = ''

                if index == 0 :
                    res_key_ids[index].append(str(element_key))
                    rows[element_key] = element
                elif index == 1:
                    res_key_ids[index].append(str(element_key))
                    cols[element_key] = element
                elif index == 2:
                    res_key_ids[index].append(str(element_key))
                    pages[element_key] = element
        row_keys = rows.keys()
        temp_row = rows.keys()
        row_keys.sort()
        col_keys = cols.keys()
        temp_col = cols.keys()
        col_keys.sort()
        page_keys = pages.keys()
        temp_pages  = pages.keys()
        page_keys.sort()
        for d in range( len( ax_datas ) ):
            values = {}
            for t in range( len( ax_datas[d] ) ):
                if type( ax_datas[d][t] ) == type( [] ):
                    if type( ax_datas[d][t][0] ) == type( [] ):
                        values[res_key_ids[1][t]] = map(lambda x: str(x[0]), ax_datas[d][t] )
                    else:
                        if ax_datas[d][t][0]:
                            values[res_key_ids[1][t]] = ax_datas[d][t][0].encode("utf-8")
                        else:
                            values[res_key_ids[1][t]] = ''

                else:
                    values[str( t )] =  str( ax_datas[d][t] )
            datas[res_key_ids[0][d]] = values
        cherrypy.session['swap_cols'] = cols
        if flag == True:
            """
                For Graphs
            """
            result.append( rows )
            result.append( cols )
            result.append( datas )
            result.append(pages)
            return result
        else:
            """
                Add Class And Drill to the element(rows and cols)
                if drill possible class = undrilled and drill = true
            """
            
            hier_level = cherrypy.session.get( 'hier_level' )
            for key, value in rows.items():
                if value['key_value'].__contains__( 'measures' ):
                    value['class'] = 'undrilled'
                    value['drill'] = None
                    value['title'] = ""
                
                elif value['key_value'].__contains__('/'):
                    value['class'] = 'undrilled'
                    value['drill'] = None
                    value['title'] = ""

                else:
                    if hier_level:
                        if str( value['key_value'][0] ) in hier_level.keys():
                            hier = hier_level[str( value['key_value'][0] )]
                            if len( value['key_value'] ) <= hier:
                                value['class'] = 'notdrilled'
                                value['drill'] = False
                                value['title'] = "Click To Drill Down"
                            else:
                                value['class'] = 'undrilled'
                                value['drill'] = None
                                value['title'] = ""
                        else:
                            print " Not possible"
                    else:
                        if not cube_id:
                            cube_id = cherrypy.session['bi_cubeid']
                        dimensions_ids = rpc.RPCProxy( 'olap.dimension' ).search( [( 'cube_id', '=', int( cube_id ) )] )
                        hierarchies_ids = rpc.RPCProxy( 'olap.hierarchy' ).search( [( 'dimension_id', 'in', dimensions_ids )] )
#                        hierarchies_ids = rpc.RPCProxy( 'olap.hierarchy' ).search( [( 'name', '=', str( value['key_value'][0] ) )] )
                        hierarchies = rpc.RPCProxy( 'olap.hierarchy' ).read( hierarchies_ids )
                        hier_level = {}
                        for hier in hierarchies:
                            levels_ids = rpc.RPCProxy( 'olap.level' ).search( [( 'hierarchy_id', '=', hier['id'] )] )
                            hier_level[str( hier['name'] )] = len( levels_ids )
                        if str( value['key_value'][0] ) in hier_level.keys():
                            hier = hier_level[str( value['key_value'][0] )]
                            if len( value['key_value'] ) <= hier:
                                value['class'] = 'notdrilled'
                                value['drill'] = False
                                value['title'] = "Click To Drill Down"
                            else:
                                value['class'] = 'undrilled'
                                value['drill'] = None
                                value['title'] = ""
                        else:
                            print " Not possible"
            
            for page_k, page_val in pages.items():
                page_val['class'] = 'notdrilled'
                page_val['drill'] = False
                page_val['title'] = "Click To Drill Down"

            pages_keys = pages.keys()
            pages_keys.sort()
            pages_counter = 0
            pages_pos_dict = {}
            for p_k in pages_keys:
                print
                if len( p_k.split( "." ) ) == 1:
                    pages_pos_dict[p_k] = pages_counter
                    pages_counter = pages_counter + 1
                
                else:
                    page_temp_key = '.'.join( p_k.split( "." )[:-1] )
                    page_temp_len = len( p_k.split( "." ) )
                    m = filter( lambda x:( len( x.split( "." ) ) == page_temp_len and page_temp_key == '.'.join( x.split( "." )[:-1] ) ) , pages_keys )
                    s_f = 0
                    for x in m :
                        if not x in pages_pos_dict.keys():
                            pages_pos_dict[x] = pages_counter
                            s_f = 1
                    if m and s_f:
                        pages_counter = pages_counter + 1
            
            for x in pages_pos_dict.keys():
                pages[x]['pos'] = pages_pos_dict[x]
            
            for page_key, page_value in pages.items():
                if page_value['parent']:
                    pages[page_value['parent']]['drill'] = True
                    pages[page_value['parent']]['class'] = 'drilled'
                    pages[page_value['parent']]['title'] = 'Click To Drill Up'
                    
            
            for page_n_key, page_n_value in pages.items():
                page_n_value['key_value'] = ','.join( map( lambda x:  x.encode('utf-8'), page_n_value['key_value'] ) )

            page_temp = []
            for page_k, page_v in pages.items():
                page_temp.append( [page_k, page_v] )
            
            page_temp.sort()
            
            pos_key = rows.keys()
            pos_key.sort()
            counter = 0
            pos_dict = {}
            """
                Assign position to the element(rows)
            """
            for k in pos_key:
                if len( k.split( "." ) ) == 1:
                    pos_dict[k] = counter
                    counter = counter + 1
                else:
                    temp_key = '.'.join( k.split( "." )[:-1] )
                    temp_len = len( k.split( "." ) )
                    m = filter( lambda x:( len( x.split( "." ) ) == temp_len and temp_key == '.'.join( x.split( "." )[:-1] ) ) , pos_key )
                    s_f = 0
                    for x in m :
                        if not x in pos_dict.keys():
                            pos_dict[x] = counter
                            s_f = 1
                    if m and s_f:
                        counter = counter + 1

            for x in pos_dict.keys():
                rows[x]['pos'] = pos_dict[x]

            for key, value in rows.items():
                if value['parent']:
                    padd = value['parent'].split(".")
                    if len(padd) == 1:
                        value['padding-left'] = '15px'
                    elif len(padd) == 2:
                        value['padding-left'] = '30px'
                    elif len(padd) == 2:
                        value['padding-left'] = '35px'
                    elif len(padd) == 3:
                        value['padding-left'] = '44px'
                    elif len(padd) == 4:
                        value['padding-left'] = '52px'
                    elif len(padd) == 5:
                        value['padding-left'] = '60px'
                    elif len(padd) == 6:
                        value['padding-left'] = '68px'
                        
                    rows[value['parent']]['drill'] = True
                    rows[value['parent']]['class'] = 'drilled'
                    rows[value['parent']]['title'] = 'Click To Drill Up'
                else:
                    value['padding-left'] = ''
            
            
            for key, value in cols.items():
                if value['key_value'].__contains__( 'measures' ):
                    value['class'] = 'undrilled'
                    value['drill'] = None
                    value['title'] = ""
                else:
                    if hier_level:
                        if str( value['key_value'][0] ) in hier_level.keys():
                            hier = hier_level[str( value['key_value'][0] )]
                            if len( value['key_value'] ) <= hier:
                                value['class'] = 'notdrilled'
                                value['drill'] = False
                                value['title'] = "Click To Drill Down"
                            else:
                                value['class'] = 'undrilled'
                                value['drill'] = None
                                value['title'] = ""
                        else:
                            print " Not possible"
                    else:
                        if not cube_id:
                            cube_id = cherrypy.session['bi_cubeid']
                        dimensions_ids = rpc.RPCProxy( 'olap.dimension' ).search( [( 'cube_id', '=', int( cube_id ) )] )
                        hierarchies_ids = rpc.RPCProxy( 'olap.hierarchy' ).search( [( 'dimension_id', 'in', dimensions_ids )] )
#                        hierarchies_ids = rpc.RPCProxy( 'olap.hierarchy' ).search( [( 'name', '=', str( value['key_value'][0] ) )] )
                        hierarchies = rpc.RPCProxy( 'olap.hierarchy' ).read( hierarchies_ids )
                        hier_level = {}
                        for hier in hierarchies:
                            levels_ids = rpc.RPCProxy( 'olap.level' ).search( [( 'hierarchy_id', '=', hier['id'] )] )
                            hier_level[str( hier['name'] )] = len( levels_ids )
                        if str( value['key_value'][0] ) in hier_level.keys():
                            hier = hier_level[str( value['key_value'][0] )]
                            if len( value['key_value'] ) <= hier:
                                value['class'] = 'notdrilled'
                                value['drill'] = False
                                value['title'] = "Click To Drill Down"
                            else:
                                value['class'] = 'undrilled'
                                value['drill'] = None
                                value['title'] = ""
                        else:
                            print " Not possible"

            pos_key = cols.keys()
            pos_key.sort()
            counter = 0
            pos_dict = {}
            """
                Assign position to the element(cols)
            """
            for k in pos_key:
                if len( k.split( "." ) ) == 1:
                    pos_dict[k] = counter
                    counter = counter + 1
                else:
                    temp_key = '.'.join( k.split( "." )[:-1] )
                    temp_len = len( k.split( "." ) )
                    m = filter( lambda x:( len( x.split( "." ) ) == temp_len and temp_key == '.'.join( x.split( "." )[:-1] ) ) , pos_key )
                    s_f = 0
                    for x in m :
                        if not x in pos_dict.keys():
                            pos_dict[x] = counter
                            s_f = 1
                    if m and s_f:
                        counter = counter + 1

            for x in pos_dict.keys():
                cols[x]['pos'] = pos_dict[x]

            for key, value in cols.items():
                if value['parent']:
                    cols[value['parent']]['drill'] = True
                    cols[value['parent']]['class'] = 'drilled'
                    cols[value['parent']]['title'] = 'Click To Drill Up'

            for key, value in rows.items():
                value['key_value'] = ','.join( map( lambda x:  x.encode("utf-8"), value['key_value'] ) )

            row = []
            for key, value in rows.items():
                row.append( [key, value] )

            row.sort()
            
            cols_cross_drill = []
            for key, value in cols.items():
                value['key_value'] = ','.join( map( lambda x: x.encode("utf-8"), value['key_value'] ) )
                if value['cross_drill']:
                    cols_cross_drill.append(value['cross_drill'])
            col = []
            for key, value in cols.items():
                col.append( [key, value] )
            col.sort()
#            page_temp = []
#            for page_key,page_value in pages.items():
#                page_temp.append([page_key, page_value])
#            page_temp.sort()
            data = []
            for key, val in datas.items():
                dt_inner = []
                for k, v in val.items():
                    dt_inner.append( [k, v] )
                dt_inner.sort()
                data.append( [key, dt_inner] )
            
            
            data.sort()
            for d in range( len( data ) ):
                val = map( lambda x:x[1], data[d][1] )
                if pages:
                    for i in range(len(val[0])):
                        page_temp[i][1]['data'] = map(lambda x:x[i],val)
                    row[d][1]['data'] = val
                else:
                    row[d][1]['data'] = val    
            cherrypy.session['swap_rows'] = rows
            cherrypy.session['swap_datas'] = datas
            cherrypy.session['swap_pages'] = page_temp
            result = []
            result.append( row )
            result.append( col )
            result.append( data )
            result.append(page_temp)
            result.append(cols_cross_drill)
            return result

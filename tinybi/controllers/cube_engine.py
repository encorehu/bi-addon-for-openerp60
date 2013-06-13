import cherrypy

import optparse
import xmlrpclib
import time

from openerp.utils import rpc
from openerp.controllers import SecuredController

import mdx_bi
from mdx_bi import *

__version__ = '1.0'

class CubeEngine( SecuredController ):
    def execute_mdx( self, *args, **kw ):
        error = False
        error_from_pane = False
        last_query = False
        axis = []
        data = []
        try:
            if args[3] == 'False':
                axis, data = rpc.RPCProxy( 'olap.schema' ).request( args[1], args[2] , {'log':True})
                cherrypy.session['last_success_query'] = args[2]
            else:
                error_from_pane = True
                axis, data = rpc.RPCProxy( 'olap.schema' ).request( args[1], args[2], {'log':False })
        except:
            if error_from_pane == True:
                error = True
            else:
                if ( axis == [] )and ( data == [] ):
                    if cherrypy.session.get( 'last_success_query' ) == 'No query':
                        raise redirect( '/browser' )
                    else:
                        axis, data = rpc.RPCProxy( 'olap.schema' ).request( args[1], cherrypy.session.get( 'last_success_query' ) )
                        print "roll back in cube engine"
                        last_query = True
                    error = True
        return axis, data, error, last_query

# vim: ts=4 sts=4 sw=4 si et

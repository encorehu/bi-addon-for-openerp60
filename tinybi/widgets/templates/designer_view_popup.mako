<%inherit file="/openobject/controllers/templates/base.mako"/>
<%! show_header_footer=False %>
<%def name="header()">
    <title>${form.screen.string} </title>
    <script type="text/javascript">
        var form_controller = '/designer/bi_form';
    </script>

    <script type="text/javascript" src="/tinybi/static/javascript/designer.js"></script>
    <script type="text/javascript" src="/tinybi/static/javascript/tabber/tabber_cookie.js"></script>
    <script type="text/javascript" src="/tinybi/static/javascript/tabber/tabber.js"></script>
    
    <script type="text/javascript">
        
        MochiKit.DOM.addLoadEvent(function (evt){
            var lc = ${params._terp_load_counter}
            lc = parseInt(lc) || 0;
            
            var model = document.getElementById("_terp_model");
            model = model.value || '';
            
            if(model=='olap.schema') {
            
                if (lc  > 1) {
                    window.close();
                    window.opener.location.reload(true);
                }
                
            }
            
            else {
                var b_type = ${params._terp_bi_type};
                var id = document.getElementById("_terp_id");
                id = id.value || 'False';
                
                var context = document.getElementById("_terp_context");
                context = context.value || 0;
                 
                if (lc  > 1)  {
                    var tree = window.opener.view_tree;
                    var selected = tree.selection[0] || null;
                    var record = selected.record;
                    var data = record.items;
                    var pnode = selected.parentNode;
                    
                    var view_form = window.document.view_form;
                    var table = MochiKit.DOM.getElementsByTagAndClassName('table','fields',view_form);
                    
                    if(model == 'olap.measure') {
                        var row = table[0].rows[0];
                        var cols = MochiKit.DOM.getElementsByTagAndClassName('td','item',row);
                        var name = cols[0].childNodes[1].innerHTML;
                    }
                    
                    else {
                        var row = table[0].rows[1];
                        var cols = MochiKit.DOM.getElementsByTagAndClassName('td','item',row);
                        var name = cols[0].childNodes[1].innerHTML;
                        
                    }
                    change_view(tree,pnode,selected,record,name,id,model,context,b_type)
                }
               }
            });
    </script>	
</%def> 
<%def name="content()">
<body>

    <table class="view" cellspacing="5" border="0" width="100%">
        <tr>
            <td>
              
                <table width="100%" class="titlebar">
                    <tr>
                        <td width="32px" align="center">
                            <img src="/openerp/static/images/stock/gtk-edit.png"/>
                        </td>
                        <td width="100%" >${form.screen.string}
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td>${form.display()}</td>
        </tr>
        <tr>
            <td>
                <div class="toolbar">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <td width="100%">
                            </td>
                            <td>
                                <button type="button" onclick="window.close();">Close</button>
                                <button type="button" onclick="submit_form('save');">Save</button>
                            </td>
                        </tr>
                    </table>
                </div>
            </td>
        </tr>
    </table>
</body>
</%def>

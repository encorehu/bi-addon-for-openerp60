<%inherit file="/openobject/controllers/templates/base.mako"/>
<%def name="header()">
    <title>${tree.string}</title>
    <script type="text/javascript">

        function submit_form(action, src, data, target){
            
            var selection = MochiKit.DOM.getElement('tree_ids').value;

            
            if (!selection) {
                return alert('You must select at least one record.');
            }
            
            var form = document.forms['view_tree'];
            
            var args = {
                _terp_data: data ? data : null
            };
            
            args['_terp_selection'] = '[' + selection + ']';

            setNodeAttribute(form, 'action', getURL('/tree/' + action, args));
            form.method = 'post';
            form.submit();
        }

        function button_click(id){
            location.href = getURL('/tree', {id : id, model : $('_terp_model').value, domain: $('_terp_domain').value});
        }

    </script>
    <script type="text/javascript" src="/tinybi/static/javascript/master.js"></script>
    <script type="text/javascript" src="/tinybi/static/javascript/ajax.js"></script>
    <script type="text/javascript" src="/tinybi/static/javascript/designer.js"></script>
</%def>
<%def name="content()">

<table class="view" width="100%" border="0" cellpadding="0" cellspacing="0">
    <tr>
        <td width="100%" valign="top">
            <table cellpadding="0" cellspacing="0" border="0" width="100%">
                <tr>
                    <td colspan="2">
                        <table width="100%" class="titlebar">
                            <tr>
                                <td width="32px" align="center">
                                    <img src="/openerp/static/images/stock/gtk-find.png"/>
                                </td>
                                <td width="100%">Cube Designer</td>
                            </tr>
                         </table>
                     </td>
                 </tr>
                 <tr>
                    <td width="100%" valign="top">${tree.display()}</td>
                 </tr>
            </table>
        </td>
    </tr>
</table>
</%def>

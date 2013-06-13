<%inherit file="/openobject/controllers/templates/base.mako"/>
<%def name="header()">
    <title>Open Object BI</title>
 	<script type="text/javascript">
        var form_controller = '/browser';
    </script>
    <script type="text/javascript" src="/tinybi/static/javascript/master.js"></script>
    <script type="text/javascript" src="/tinybi/static/javascript/ajax.js"></script>
</%def> 
<%def name="content()">

    <table class="view" cellspacing="5" border="0" width="100%">
        <tr>
            <td>
                <textarea rows="2" cols="100" id="query" class="queryarea" name="textquery" style="width: 98%; border-color: #E3E3E3;display:none;"></textarea>
            </td>
        </tr>
        <tr>
            <td>${screen.display()}</td>
        </tr>
    </table>
</%def> 

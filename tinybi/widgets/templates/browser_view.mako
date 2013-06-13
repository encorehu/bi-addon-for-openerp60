<table cellpadding="0px" cellspacing="0px" width="100%">
    <tr>
        <td>
            <table>
                <tr>
                    <td align="center">
                        <img class="bi_toolbar" src="/tinybi/static/images/toolbar_img/clear.png" title="Clear" onclick="clear_query()"/>
                    </td>
                    <td align="center">
                        <img class="bi_toolbar" src="/tinybi/static/images/toolbar_img/Filesave.png" title="Save Current Query" onclick="save_query(event)"/>
                    </td>
                    <td>
                        <img class="bi_toolbar" src="/openerp/static/images/stock/gtk-open.png" title="View Saved Query" onclick="window.location.href='/browser/make_view'"/>
                    </td>
                    <td align="center" id="non_empty_view" style="display:none;">
                        <img class="bi_toolbar" src="/openerp/static/images/stock/gtk-remove.png" title="Remove Empty Records" onclick="switch_non_empty_view()"/>
                    </td>
                    <td align="center" id="empty_view" style="display:none;">
                        <img class="bi_toolbar" src="/openerp/static/images/stock/gtk-add.png" title="Display Empty Records" onclick="switch_empty_view()"/>
                    </td>
                    <td align="center"> 
                        <img id="undo" class="bi_toolbar"  src="/tinybi/static/images/toolbar_img/back.png" title="Undo Step" onclick="undo_step(event)"/>
                    </td>
                    <td align="center">
                        <img class="bi_toolbar" src="/tinybi/static/images/toolbar_img/forward.png" title="Redo Step" onclick="redo(event)"/>
                    </td>
                    <td align="center">
                        <img class="bi_toolbar" src="/tinybi/static/images/toolbar_img/expand.png" title="Expand All Parents" onclick="expand_all(event)"/>
                    </td>
                    <td align="center">
                        <img class="bi_toolbar" src="/tinybi/static/images/toolbar_img/collapse.png" title="Collapse All Parents" onclick="collapse_all(event)"/>
                    </td>
                    <td align="center">
                        <img class="bi_toolbar" src="/tinybi/static/images/toolbar_img/table.png" title="Table View" onclick="Table()"/>
            
                    </td>
                    <td align="center">
                        <img class="bi_toolbar" src="/tinybi/static/images/toolbar_img/chart.jpg" id="bar" title="Bar Chart View" onclick="Graph(event)"/>
                    </td>
                    <td align="center">
                        <img class="bi_toolbar" src="/tinybi/static/images/toolbar_img/pie.png" title="Pie Chart View" onclick="Pie(event)"/>
                    </td>
                    <td align="center">
                        <img class="bi_toolbar" src="/tinybi/static/images/mdx.png" title="MDX Query View" onclick="mdx_query(event)"/>
                    </td>
                </tr>
            </table>
        </td>
        <td style="display:none;" align="right">
            <button id="empty_view" onclick="switch_empty_view()" style="display:none;">Display Empty</button>
            <button  onclick="switch_non_empty_view()" >Remove Empty</button>
        </td>
    </tr>
    <tr>
        <td id="mainpane" colspan="1">
            <table id="browser" width="100%" cellpadding="0" cellspacing="0" align="center" style="border-top: 1px solid silver; border-bottom:1px solid silver;border-left:1px solid silver; border-right:1px solid silver;">
                <tr>
                    <td align="center" valign="top">
                        <img title = " Click to hide tree" id="grip_button" src="/tinybi/static/images/sidebar_show.gif" onclick="hide_show_tree()"/>
                    </td>
                    <td id="column_1" width="30%" style="vertical-align: top;">
                        ${widget_cube['combo_schema'].display()}
                        <div align="center" style=" width: 100%; height: auto;" width="100%">
                            ${tree.display()}
                            <script type="text/javascript">
                            {
                                MochiKit.DOM.addLoadEvent(function(evt){
                                if(view_tree) {
                                    MochiKit.Signal.connect(view_tree,'onNodeExpand',make_tree_draggable);
                                }
                                });
                            }
                            </script>
                        </div>
                    </td>
                    <td id="resizegrip" class="resizegrip"/>
                    <td valign="top" id="mdx_output" width="100%" align="center">
                        
                        <table>
                            <tr>
                                <td id="mdx_query_output">
                                    ${widget_cube['mdx_output'].display()}
                                </td>
                                
                            </tr>
                        </table>
                    </td>
                    <td id="mdx_graph" style="display:none; z-index: 1;" align="center">
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>

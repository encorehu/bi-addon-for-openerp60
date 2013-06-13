<div id="mdx_result_output" width="100%" align="left" style="width: 100%; height: auto;">
    <table cellspacing="5px">
        <tr style="height:25px;margin-bottom:10px;">
            % if slicers:
            <td class="filter_cross">
                <table  width="fixed" valign="top" >
                    <tbody id="Filter">
                        % for filter in slicers:
                        <tr id="${filter[0]}">
                            % if filter[0] == 0:
                            <td style="font-weight:bold;">
                                Filters :
                            </td>
                            % endif
                            % if filter[0] > 0:
                            <td style="font-weight:bold;">
                            </td>
                            % endif
                            <td>
                                ${filter[1]}
                            </td>
                            <td id="${filter[2]}">
                                <img src="/tinybi/static/images/delete_inline.gif" title="Click to Remove Filter"  height="10px" width="13px" style="cursor: pointer; vertical-align:middle;" onclick="clear_filter(this.parentNode.parentNode.id,this.parentNode.id)"/>
                            </td>
                        </tr>
                        % endfor
                    </tbody>
                </table>
            </td>
            % endif
        </tr>
    </table>
    <table id="result_format" width="100%">
        % if not rows:
        <tr id="initial_table">
            <td width="100%" align="center">
                
                <table id="dyt_temp" align="center" class="stats" width="100%">
                    <tr style="height: 100%">
                        <td class="adddim" align="center" width="100%">
                            <table width="100%">
                                <tr>
                                    <td width="100%" class="main_td" align="center">
                                        Select and insert items from the tree to fill in the report.
                                    </td>
                                </tr>
                                <tr>
                                    <td width="100%" id="drop_here" class="first_drop_here" title="DROP HERE TO START" align="center">
                                    </td>
                                </tr>
                                <tr>
                                    <td width="100%" class="main_td" align="left">
                                        Draggable elements  : With [ <img src="/tinybi/static/images/tree_img/draggable.png"/> ] on tree view left
                                    </td>
                                </tr>
                                <tr>
                                    <td width="100%" class = "main_td" align="left">
                                        Droppable place : With [ <span class="drop_hint" >Droppable</span> ] on hover on grid
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        % endif
        % if rows and pages:
        %   for page in range(len(pages)):

        <tr id="query_table" >
            <td width="100%">
                <table width="100%">
                    <tr>
                        <td align="center">
                            <div class="page_axis_style">
                                <span align="center" onclick="drill('2_${pages[page][0]}','${pages[page][1]['key_value']}','${pages[page][1]['pos']}','${pages[page][1]['class']}')">
                                    ${pages[page][1]['key_value']}
                                </span>
                                <span align="center">
                                    <img src="/tinybi/static/images/delete_inline.gif" title="Click to Remove Page Element"  height="10px" width="13px" style="cursor: pointer;" onclick="del_element('${pages[page][1]['on_remove']}','2')"/>
                                </span>
                            </div>
                        </td>
                    </tr>
                </table>
                <table>
                    <tr>
                        <td width="100%" valign="top" colspan="2">
                            <table width="100%" id="containertable" border="0" cellspacing="0" cellpadding="0">
                                <tr>
                                    % if pages[page][1]['parent'] is None and pages[page][1]['on_remove']==0:
                                    <td width="14px">
                                        <img align="right" src="/tinybi/static/images/swap_diagonal_right.gif" title="Click to Swap Crossjoins" style="height: 14px; cursor: pointer; padding-right:0px; display: none;" onclick="swap_cross()"/>
                                    </td>
                                    % endif
                                    % if len(cols) ==0 and pages[page][1]['parent'] is None:
                                    <td id="crosscol" width="99%" style="display: table-cell;" class="NewAxis" title="Drop to add in to cols ">
                                        <script type="text/javascript">
                                            makeDroppablecoll("crosscol");
                                            document.getElementById("mdx_output").align="left";
                                        </script>
                                    </td>
                                    % endif
                                    % if len(cols) > 0 and pages[page][1]['parent'] is None and pages[page][1]['on_remove']==0:
                                    <td id="crosscol" width="99%"  style="display: table-cell;" class="cross" title="Drop to make cross on cols">
                                        <script type="text/javascript">
                                            makeDroppablecoll_cross("crosscol");
                                        </script>
                                    </td>
                                    % endif
                                    % if len(cols) > 0 and not pages[page][1]['parent'] is None:
                                    <td id="crosscol" width="99%"  style="display: table-cell;">
                                    </td>
                                    % endif
                                </tr>
                                <tr>
                                    % if pages[page][1]['parent'] is None and pages[page][1]['on_remove']==0:
                                    <td width="14px" id="crossrow" style="display: table-cell;" class="cross" title="Drop to make cross on rows">
                                        <script type="text/javascript">
                                            makeDroppablerow_cross("crossrow");
                                        </script>
                                    </td>
                                    % endif
                                    % if not pages[page][1]['parent'] is None:
                                    <td width="14px" id="crossrow" style="display: table-cell">
                                    </td>
                                    % endif
                                    <td width="100%" style="background-color: #FFFFF2;">
                                        <table id="dytable" border="0" style="height: 100%; width;100%;" width="100%" class="stats" align="left" cellspacing="0" cellpadding="0">
                                            <tbody id="dyt" align="left" style="width:100%" width="100%">
                                                <tr id="col_0" style="background-color: #f6f6f6;">
                                                    <!-- THESE TDS ARE FOR SWAP AXIS (BASED ON CONDITION) -->
                                                    <%
                                                        if rows[0][1]['cross_drill']:
                                                            colspan = len(rows[0][1]['cross_drill'])+1
                                                        else:
                                                            colspan = 0
                                                    %>
                                                    % if pages[page][1]['parent'] is None:
                                                    <td colspan="${colspan}" align="center" class="swap_d" style="vertical-align: bottom;" id="swap_row_col">
                                                        % if pages[page][1]['on_remove'] == 0:
                                                        <img align="right" src="/tinybi/static/images/swap_diagonal_right.gif" title="Click to Swap Axis" style="height: 20px; cursor: pointer; padding-right:0px;" onclick="interchanged(event, '${cols}')"/>
                                                        % endif
                                                        % if pages[page][1]['on_remove'] > 0:
                                                        <img align="right" src="/tinybi/static/images/swap_diagonal_right.gif"/>
                                                        % endif
                                                    </td>
                                                    % endif
                                                    % if not pages[page][1]['parent'] is None:
                                                    <td colspan="${colspan}" align="center" class="swap_d" style="vertical-align: bottom;" id="swap_row_col">
                                                        <img align="right" src="/tinybi/static/images/swap_diagonal_right.gif"/>
                                                    </td>
                                                    % endif
                                                    <%
                                                        prev_col = 0
                                                        if pages:
                                                            col_colspan=len(pages)
                                                        else:
                                                            col_colspan=1
                                                    %>
                                                    <!-- THIS TD IS FOR COLUMN -->
                                                    % for col in cols:
                                                    <td width="100%" id="${col[0]}" style="font-weight: bold;background:#E0E0E0;">
                                                        <%
                                                            test_col=col[0].split('.')
                                                            len_col=len(test_col)
                                                            if len_col > 1:
                                                                class_col="column_style_child"
                                                            else:
                                                                class_col="column_style"
                                                        %>
                                                        <table align="top" class="${class_col}" width="100%" height="100%">
                                                            <tr>
                                                                <%
                                                                    if not col[1]['cross_drill'] is None:
                                                                        col[1]['cross_drill'] = col[1]['cross_drill']
                                                                    else:
                                                                        col[1]['cross_drill'] = []
                                                                %>
                                                                % if col and col[1]['parent'] is None and pages[page][1]['parent'] is None and pages[page][1]['on_remove'] == 0:
                                                                <td id="1_${col[1]['pos']}" style="display: table-cell;" class="dropeleCol" title="Drop to add in to cols">
                                                                    <script type="text/javascript">
                                                                        makeDroppablecol("1_${col[1]['pos']}");
                                                                        if(getElement('non_empty_view').style.display == 'none')
                                                                            getElement('non_empty_view').style.display = '';

                                                                        if(getElement('empty_view').style.display == ''|| getElement('empty_view').style.display == 'block' || getElement('non_empty_view').style.display == 'none') {
                                                                            getElement('empty_view').style.display = 'none';
                                                                            getElement('non_empty_view').style.display = '';
                                                                        }
                                                                    </script>
                                                                </td>
                                                                % endif
                                                                % if col and col[1]['parent'] is None and pages[page][1]['parent'] is None and pages[page][1]['on_remove'] == 0:
                                                                <td id="1_${col[1]['pos']}" style="display: table-cell;" class="dropeleCol_ch_page">
                                                                </td>
                                                                % endif
                                                                % if col and col[1]['parent'] is None and not pages[page][1]['parent'] is None:
                                                                <td id="1_${col[1]['pos']}" style="display: table-cell;" class="dropeleCol_ch_page">
                                                                </td>
                                                                % endif
                                                                
                                                                <td id="head" width="100%" align="center" class="headrow">
                                                                    <table id="mdx_result"  border="0" align="center" width="100%" height="100%" valign="top">
                                                                        % if col[1]['parent'] is None:
                                                                        <tr>
                                                                            <td width="100%" valign="top" style="white-space: nowrap;" align="center" >
                                                                                <div title="${col[1]['title']}" style="cursor: pointer; " id="1_${col[0]}" class="${col[1]['class']}" align="center" onclick="if('${col[1]['class']}' == 'notdrilled') {drill(this.id,'${col[1]['key_value']}', '${col[1]['on_remove']}','notdrilled')} else if('${col[1]['class']}' == 'drilled') {drill(this.id,'${col[1]['key_value']}','${col[1]['on_remove']}','drilled')}">
                                                                                    ${col[1]['text']}
                                                                                </div>
                                                                            </td>
                                                                            <td width="100%" valign="top">
                                                                                % if col[1]['parent'] is None:
                                                                                <img id="${col[1]['text']}_${col[0]}" height="10px" width="13px" style="height: 100%; cursor: pointer;" title="Click to Remove Element" src="/tinybi/static/images/delete_inline.gif" onclick="del_element('${col[1]['on_remove']}','1')"/>
                                                                                % endif
                                                                            </td>
                                                                        </tr>
                                                                        % endif
                                                                        % if not col[1]['parent'] is None:
                                                                        <tr>
                                                                            <td width="100%" valign="top">
                                                                            <%
                                                                                elem = col[1]['key_value'].split(",");
                                                                                elem.pop();
                                                                            %>
                                                                            <table width="100%" border="0">
                                                                                <tr>
                                                                                    <td>
                                                                                        % for length in elem:
                                                                                        <br />
                                                                                        % endfor
                                                                                        <div title="${col[1]['title']}" style="display: table-cell; white-space: nowrap; vertical-align: bottom;  cursor: pointer;" id="1_${col[0]}" class="${col[1]['class']}" align="left" onclick="if('${col[1]['class']}' == 'notdrilled') {drill(this.id,'${col[1]['key_value']}','${col[1]['on_remove']}','notdrilled')} else if('${col[1]['class']}' == 'drilled') {drill(this.id,'${col[1]['key_value']}','${col[1]['on_remove']}','drilled')}">
                                                                                            ${col[1]['text']}
                                                                                        </div>
                                                                                    </td>
                                                                                </tr>
                                                                            </table>
                                                                            </td>
                                                                        </tr>
                                                                        % endif
                                                                    </table>
                                                                </td>
                                                            </tr>
                                                        </table>
                                                        <%
                                                            prev_col = col[1]['pos']+ 1
                                                            max_col_pos = max([max_pos[1]['pos'] for max_pos in cols]) +1
                                                        %>
                                                    </td>
                                                    % endfor
                                                    % if cols and pages[page][1]['parent'] is None and pages[page][1]['on_remove'] == 0:
                                                    <td style="display: table-cell;" id="1_${max_col_pos}" class="dropeleColextra" title="Drop to add in to cols">
                                                        <script type="text/javascript">
                                                            getElement('1_${max_col_pos}').height = elementDimensions('swap_row_col').h;
                                                            makeDroppablecol('1_${max_col_pos}');
                                                        </script>
                                                    </td>
                                                    % endif
                                                    % if cols and pages[page][1]['parent'] is None and pages[page][1]['on_remove'] > 0:
                                                    <td style="display: table-cell;" id="1_${max_col_pos}" class="dropeleCol_ch_page">
                                                    </td>
                                                    % endif
                                                    % if cols and not pages[page][1]['parent'] is None:
                                                    <td style="display: table-cell;" id="1_${max_col_pos}" class="dropeleCol_ch_page">
                                                    </td>
                                                    % endif
                                                </tr>
                                                % if cols_cross_drill:
                                                <tr style="background: #E0E0E0 none repeat scroll 0 0;">
                                                    <%
                                                        if rows[0][1]['cross_drill']:
                                                            colspan = len(rows[0][1]['cross_drill'])+1
                                                        else:
                                                            colspan = 0
                                                    %>
                                                    <td colspan="${colspan}">
                                                    </td>
                                                    % for col_cross in cols_cross_drill:
                                                    <td width="100%" >
                                                        <table width="100%" class="column_style">
                                                            <tr>
                                                                % for col_c in col_cross:
                                                                <td width="100%">
                                                                    <table width="100%">
                                                                        <tr>
                                                                            <td width="87%">
                                                                                <div style="white-space: nowrap; cursor: pointer;" class="${col_c[2]}" onclick="cross_drill(1,'${col_c[1]}',${col_c[0]})">${col_c[1]}</div>
                                                                            </td>
                                                                            <td width="13%">
                                                                                <img title="Click to Remove Crossjoin from Columns" src="/tinybi/static/images/delete_inline.gif" height="10px" width="13px" style="cursor: pointer; vertical-align:middle;" onclick="remove_cross_joins(1,'${col_c[0]}')"/>
                                                                            </td>
                                                                        </tr>
                                                                    </table>
                                                                </td>
                                                                % endfor
                                                            </tr>
                                                        </table>
                                                    </td>
                                                    % endfor
                                                    <td>
                                                    </td>
                                                </tr>
                                                % endif
                                                <%
                                                    prev_row=0
                                                %>
                                                % for row in rows:
                                                <tr id="${row[0]}" class="row_axis">
                                                    <%
                                                        test_row=row[0].split('.')
                                                        len_row=len(test_row)
                                                        if len_row > 1:
                                                            class_row="row_style_child"
                                                        else:
                                                            class_row="row_style"
                                                        
                                                    %>
                                                    % if row[1]['parent'] is None:
                                                    <td width="100%" class="${class_row}">
                                                        <table width="100%">
                                                            <tr>
                                                                <td width="90%">
                                                                    % if row[1]['parent'] is None and pages[page][1]['parent'] is None and pages[page][1]['on_remove'] == 0:
                                                                    <div id="0_${row[1]['pos']}" class="dropeleRow" style="b" title="Drop to add in to rows"/>
                                                                    % endif    
                                                                    % if pages[page][1]['parent'] is None:
                                                                    <script type="text/javascript">
                                                                        makeDroppablerow("0_${row[1]['pos']}");
                                                                        document.getElementById("mdx_output").align="left"
                                                                    </script>
                                                                    % endif
                                                                    <div title="${row[1]['title']}" class="${row[1]['class']}" id="${row[0]}" style="white-space: nowrap; cursor: pointer;" onclick="if('${row[1]['class']}' == 'notdrilled') {drill('0_${row[0]}','${row[1]['key_value']}','${row[1]['on_remove']}','notdrilled')} else if('${row[1]['class']}' == 'drilled') {drill('0_${row[0]}','${row[1]['key_value']}','${row[1]['on_remove']}','drilled')}"> ${row[1]['text']}</div>
                                                                </td>
                                                                <td width="10%" align="right" valign="bottom">
                                                                    <img id="${row[1]['text']}_${row[0]}" title="Click to Remove Element" style="cursor: pointer;" height="10px" width="13px" src="/tinybi/static/images/delete_inline.gif" onclick="del_element('${row[1]['on_remove']}','0')"/>
                                                                </td>
                                                            </tr>
                                                        </table>
                                                    </td>
                                                    % endif
                                                    % if not row[1]['parent'] is None:
                                                    <td class="${class_row}" width="100%" style="white-space: nowrap; padding-left: ${row[1]['padding-left']};">
                                                        <table width="100%">
                                                            <tr>    
                                                                <td width="100%">
                                                                    <div title="${row[1]['title']}" class="${row[1]['class']}" id="${row[0]}" style="white-space: nowrap; cursor: pointer;" onclick="if('${row[1]['class']}' == 'notdrilled') {drill('0_${row[0]}','${row[1]['key_value']}','${row[1]['on_remove']}','notdrilled')} else if('${row[1]['class']}' == 'drilled') {drill('0_${row[0]}','${row[1]['key_value']}','${row[1]['on_remove']}','drilled')}"> ${row[1]['text']}</div>
                                                                </td>
                                                            </tr>
                                                        </table>
                                                    </td>
                                                    % endif
                                                    <%
                                                        if not row[1]['cross_drill'] is None:
                                                            row[1]['cross_drill'] = row[1]['cross_drill']
                                                        else:
                                                            row[1]['cross_drill'] = []
                                                    %>
                                                    % if not row[1]['cross_drill'] is None:
                                                    %   for cross in row[1]['cross_drill']:
                                                    <td class="cross_row_style" style="font-weight: bold; vertical-align:bottom;" align="left" width="100%">
                                                        <table align="left" width="100%">
                                                            <tr id="${cross[0]}">
                                                                <td align="left" width="90%">
                                                                    <div style="white-space: nowrap; cursor: pointer;" class="${cross[2]}" onclick="cross_drill(0,'${cross[1]}',${cross[0]})">${cross[1]}</div>
                                                                </td>
                                                                <td width="10%" align="right">
                                                                    <img title="Click to Remove Crossjoin from Rows" src="/tinybi/static/images/delete_inline.gif" height="10px" width="13px" style="cursor: pointer; " onclick="remove_cross_joins(0,'${cross[0]}')"/>
                                                                </td>
                                                            </tr>
                                                        </table>
                                                    </td>
                                                    %   endfor
                                                    % endif
                                                    % if len(pages) ==1:
                                                    %   for d in row[1]['data']:
                                                    <td width="100%" id="data" class="data" align="right">
                                                        <table width="100%">
                                                            <tr>
                                                                <td width="100%" >
                                                                    <div align="right" style="width: 100%;" width="100%" id="">
                                                                        <div class="nodropeleRow"/>
                                                                        <div align="right" class="mdx_data" id="" style="display: inline;">${d}</div>
                                                                    </div>
                                                                </td>
                                                            </tr>
                                                        </table>
                                                    </td>
                                                    %   endfor
                                                    % endif
                                                    % if len(pages) > 1:
                                                    %   for d in range(len(row[1]['data'])):
                                                    <td width="100%" id="data" class="data" align="right">
                                                        <table width="100%">
                                                            <tr>
                                                                <td width="100%" >
                                                                    <div align="right" style="width: 100%;" width="100%" id="">
                                                                        <div class="nodropeleRow"/>
                                                                        <div align="right" class="mdx_data" id="" style="display: inline;">${row[1]['data'][d][page]}</div>
                                                                    </div>
                                                                </td>
                                                            </tr>
                                                        </table>
                                                    </td>
                                                    %   endfor
                                                    % endif
                                                    <td style="background-color: #FFFFF2; border-top: 1px solid #D6D6D6;" width="100%">
                                                    </td>
                                                    <%
                                                        prev_row = row[1]['pos'] + 1
                                                        max_row_pos = max([max_pos[1]['pos'] for max_pos in rows]) +1
                                                    %>
                                                </tr>
                                                % endfor

                                                % if pages[page][1]['parent'] is None and pages[page][1]['on_remove'] == 0:
                                                <tr id="${max_row_pos}" style="background: #f6f6f6;">
                                                    <%
                                                        if rows[0][1]['cross_drill']:
                                                            colspan = len(rows[0][1]['cross_drill'])+1
                                                    %>
                                                    % if not rows[0][1]['cross_drill']:
                                                    <td width="100%">
                                                        <span align="left" style="width: 100%;">
                                                            <div id="0_${max_row_pos}" class="dropeleRowextra" style="" title="Drop to add in to rows"/>
                                                            <script type="text/javascript">
                                                                makeDroppablerow('0_${max_row_pos}');
                                                            </script>
                                                        </span>
                                                    </td>
                                                    % endif
                                                    % if rows[0][1]['cross_drill']:
                                                    <td colspan="${colspan}" width="100%">
                                                        <span align="left" style="width: 100%;">
                                                            <div id="0_${max_row_pos}" class="dropeleRowextra" style="" title="Drop to add in to rows"/>
                                                            <script type="text/javascript">
                                                                makeDroppablerow('0_${max_row_pos}');
                                                            </script>
                                                        </span>
                                                    </td>
                                                    % endif
                                                </tr>
                                                % endif
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                                % if pages[page][1]['parent'] is None:
                                <tr>
                                    <td >
                                        <script type="text/javascript">
                                            makeDroppablepage('thirdAxis');
                                        </script>
                                    </td>
                                    % if pages[page][1]['on_remove'] == 0:
                                    <td id="thirdAxis" class="thirdNewAxis" style="display: tablle-cell;" title="Drop to Add in Pages">
                                    </td>
                                    % endif
                                    % if pages[page][1]['on_remove'] > 0:
                                    <td id="thirdAxis" style="display: tablle-cell;" title="Drop to Add in Pages">
                                    </td>
                                    % endif
                                </tr>
                                % endif
                                % if not pages[page][1]['parent'] is None:
                                <tr>
                                    <td>
                                    </td>
                                    <td id="thirdAxis" style="display: tablle-cell;">
                                    </td>
                                </tr>
                                % endif
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        %   endfor
        % endif
        % if rows and not pages:
        <tr>
            <td width="100%" valign="top" colspan="2">
                <table width="100%" id="containertable" border="0" cellspacing="0" cellpadding="0">
                    <tr>
                        <td width="14px">
                        </td>
                        % if len(cols) == 0:
                        <td id="crosscol" width="100%" style="display: table-cell;" class="FirstNewAxis" title="Drop to add in to cols ">
                            <script type="text/javascript">
                                makeDroppablecoll("crosscol");
                                document.getElementById("mdx_output").align="left";
                            </script>
                        </td>
                        % endif
                        % if len(cols) > 0:
                        <td id="crosscol" width="100%"  style="display: table-cell;" class="cross" title="Drop to make cross on cols">
                            <script type="text/javascript">
                                makeDroppablecoll_cross("crosscol");
                            </script>
                        </td>
                        % endif
                    </tr>
                    <tr>
                        <td width="14px" id="crossrow" style="display: table-cell;" class="cross" title="Drop to make cross on rows">
                            <script type="text/javascript">
                                makeDroppablerow_cross("crossrow");
                            </script>
                        </td>
                        <td width="100%" style="background-color: #FFFFF2;">
                            <table id="dytable" border="0" style="height: 100%; width;100%;" width="100%" class="stats" align="left" cellspacing="0" cellpadding="0">
                                <tbody id="dyt" align="left" style="width:100%" width="100%">
                                    <tr id="col_0" style="background-color: #f6f6f6;">
                                        <%
                                            if rows[0][1]['cross_drill']:
                                                colspan = len(rows[0][1]['cross_drill'])+1
                                            else:
                                                colspan = 0
                                        %>
                                        <td colspan = "${colspan}" class="swap_d" id="swap_row_col" width="14px">
                                            <img src="/tinybi/static/images/swap_diagonal_right.gif" title="Click to Swap Axis" style="height: 14px; cursor: pointer; float:right; display: inline;" onclick="interchanged(event, '${cols}')"/>
                                        </td>
                                        
                                        % for col in cols:
                                        <td width="100%" id="${col[0]}" style="font-weight: bold;background:#E0E0E0;">
                                            <%
                                                test_col=col[0].split('.')
                                                len_col=len(test_col)
                                                if len_col > 1:
                                                    class_col="column_style_child"
                                                else:
                                                    class_col="column_style"
                                            %>
                                            <table align="top" class="${class_col}" width="100%" height="100%">
                                                <tr>
                                                    % if col and col[1]['parent'] is None:
                                                    <td id="1_${col[1]['pos']}" style="display: table-cell;" class="dropeleCol" title="Drop to add in to cols">
                                                        <script type="text/javascript">
                                                            makeDroppablecol("1_${col[1]['pos']}");
                                                            if(getElement('non_empty_view').style.display == 'none')
                                                            getElement('non_empty_view').style.display = '';

                                                            if(getElement('empty_view').style.display == ''|| getElement('empty_view').style.display == 'block' || getElement('non_empty_view').style.display == 'none') {
                                                                getElement('empty_view').style.display = 'none';
                                                                getElement('non_empty_view').style.display = '';
                                                            }
                                                        </script>
                                                    </td>
                                                    % endif
                                                    <td id="head" width="100%" align="center" class="headrow">
                                                        <table id="mdx_result" border="0" align="center" width="100%" height="100%" valign="top">
                                                            % if col[1]['parent'] is None:
                                                            <tr>
                                                                <td width="100%" valign="top" style="white-space: nowrap;" align="center" >
                                                                    <div title="${col[1]['title']}" style="cursor: pointer; " id="1_${col[0]}" class="${col[1]['class']}" align="center" onclick="if('${col[1]['class']}' == 'notdrilled') {drill(this.id,'${col[1]['key_value']}', '${col[1]['on_remove']}','notdrilled')} else if('${col[1]['class']}' == 'drilled') {drill(this.id,'${col[1]['key_value']}','${col[1]['on_remove']}','drilled')}">
                                                                            ${col[1]['text']}
                                                                    </div>
                                                                </td>
                                                                <td width="100%" valign="top">
                                                                    % if col[1]['parent'] is None:
                                                                    <img id="${col[1]['text']}_${col[0]}" height="10px" width="13px" style="cursor: pointer;" title="Click to Remove Element" src="/tinybi/static/images/delete_inline.gif" onclick="del_element('${col[1]['on_remove']}','1')"/>
                                                                    % endif
                                                                </td>
                                                            </tr>
                                                            % endif
                                                            % if not col[1]['parent'] is None:
                                                            <tr>
                                                                <td width="100%" valign="top">
                                                                    <%
                                                                        elem = col[1]['key_value'].split(",");
                                                                        elem.pop();
                                                                    %>
                                                                    <table width="100%" border="0">
                                                                        <tr>
                                                                            <td>
                                                                                % for length in elem:
                                                                                <br/>
                                                                                % endfor
                                                                                <div title="${col[1]['title']}" style="display: table-cell; white-space: nowrap; vertical-align: bottom;  cursor: pointer;" id="1_${col[0]}" class="${col[1]['class']}" align="left" onclick="if('${col[1]['class']}' == 'notdrilled') {drill(this.id,'${col[1]['key_value']}','${col[1]['on_remove']}','notdrilled')} else if('${col[1]['class']}' == 'drilled') {drill(this.id,'${col[1]['key_value']}','${col[1]['on_remove']}','drilled')}">
                                                                                    ${col[1]['text']}
                                                                                </div>
                                                                            </td>
                                                                        </tr>
                                                                    </table>
                                                                </td>
                                                            </tr>
                                                            % endif
                                                        </table>
                                                    </td>
                                                </tr>
                                            </table>
                                            <%
                                                prev_col = col[1]['pos']+ 1
                                                max_col_pos = max([max_pos[1]['pos'] for max_pos in cols]) +1
                                            %>
                                        </td>
                                        % endfor
                                        % if cols:
                                        <td style="display: table-cell;" id="1_${max_col_pos}" class="dropeleColextra" title="Drop to add in to cols">
                                            <script type="text/javascript">
                                                getElement('1_${max_col_pos}').height = elementDimensions('swap_row_col').h;
                                                makeDroppablecol('1_${max_col_pos}');
                                            </script>
                                        </td>
                                        % endif
                                    </tr>
                                    % if cols_cross_drill:
                                    <tr style="background: #E0E0E0 none repeat scroll 0 0;">
                                        <%
                                            if rows[0][1]['cross_drill']:
                                                colspan = len(rows[0][1]['cross_drill'])+1
                                            else:
                                                colspan = 0
                                        %>
                                        <td colspan="${colspan}">
                                        </td>
                                        % for col_cross in cols_cross_drill:
                                        <td width="100%" >
                                            <table width="100%" class="column_style">
                                                <tr>
                                                    % for col_c in col_cross:
                                                    <td width="100%">
                                                        <table width="100%">
                                                            <tr>
                                                                <td width="87%">
                                                                    <div style="white-space: nowrap; cursor: pointer;" class="${col_c[2]}" onclick="cross_drill(1,'${col_c[1]}',${col_c[0]})">${col_c[1]}</div>
                                                                </td>
                                                                <td width="13%">
                                                                    <img title="Click to Remove Crossjoin from Columns" src="/tinybi/static/images/delete_inline.gif" height="10px" width="13px" style="cursor: pointer; vertical-align:middle;" onclick="remove_cross_joins(1,'${col_c[0]}')"/>
                                                                </td>
                                                            </tr>
                                                        </table>
                                                    </td>
                                                    % endfor
                                                </tr>
                                            </table>
                                        </td>
                                        % endfor
                                        <td style="border-top: 1px solid #b6b6b6;">
                                        </td>
                                    </tr>
                                    % endif
                                    <%
                                        prev_row=0
                                    %>
                                    % for row in rows:
                                    <tr id="${row[0]}" class="row_axis">
                                        <%
                                            test_row=row[0].split('.')
                                            len_row=len(test_row)
                                            if len_row > 1:
                                                class_row="row_style_child"
                                            else:
                                                class_row="row_style"
                                                
                                            if row[1]['data'] == ['']:
                                                row[1]['data'] = []
                                        %>
                                        % if row[1]['parent'] is None:
                                        <td width="100%" class="${class_row}">
                                            <div  id="0_${row[1]['pos']}" class="dropeleRow" title="Drop to add in to rows">
                                                        </div>
                                            <table width="100%">
                                                <tr>
                                                    <td width="90%">
                                                        
                                                        <script type="text/javascript">
                                                            makeDroppablerow("0_${row[1]['pos']}");
                                                            document.getElementById("mdx_output").align="left"
                                                        </script>
                                                        <div title="${row[1]['title']}" class="${row[1]['class']}" id="${row[0]}" style="white-space: nowrap; cursor: pointer;" onclick="if('${row[1]['class']}' == 'notdrilled') {drill('0_${row[0]}','${row[1]['key_value']}','${row[1]['on_remove']}','notdrilled')} else if('${row[1]['class']}' == 'drilled') {drill('0_${row[0]}','${row[1]['key_value']}','${row[1]['on_remove']}','drilled')}"> ${row[1]['text']}</div>
                                                    </td>
                                                    <td width="10%" align="right" valign="bottom">
                                                        <img id="${row[1]['text']}_${row[0]}" title="Click to Remove Element" style="cursor: pointer;" height="10px" width="13px" src="/tinybi/static/images/delete_inline.gif" onclick="del_element('${row[1]['on_remove']}','0')"/>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                        % endif
                                        % if not row[1]['parent'] is None:
                                        <td class="${class_row}" width="100%" style="white-space: nowrap; padding-left: ${row[1]['padding-left']};">
                                            <table width="100%">
                                                <tr>
                                                    <td width="100%">
                                                        <div title="${row[1]['title']}" class="${row[1]['class']}" id="${row[0]}" style="white-space: nowrap; cursor: pointer;" onclick="if('${row[1]['class']}' == 'notdrilled') {drill('0_${row[0]}','${row[1]['key_value']}','${row[1]['on_remove']}','notdrilled')} else if('${row[1]['class']}' == 'drilled') {drill('0_${row[0]}','${row[1]['key_value']}','${row[1]['on_remove']}','drilled')}"> ${row[1]['text']}</div>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                        % endif
                                        <%
                                            if not row[1]['cross_drill'] is None:
                                                row[1]['cross_drill'] = row[1]['cross_drill']
                                            else:
                                                row[1]['cross_drill'] = []
                                        %>
                                        % if not row[1]['cross_drill'] is None:
                                        %   for cross in row[1]['cross_drill']:
                                        <td class="cross_row_style" style="font-weight: bold; vertical-align:bottom;" align="left" width="100%">
                                            <table align="left" width="100%">
                                                <tr id="${cross[0]}">
                                                    <td align="left" width="90%">
                                                        <div style="white-space: nowrap; cursor: pointer;" class="${cross[2]}" onclick="cross_drill(0,'${cross[1]}',${cross[0]})">${cross[1]}</div>
                                                    </td>
                                                    <td width="10%" align="right">
                                                        <img title="Click to Remove Crossjoin from Rows" src="/tinybi/static/images/delete_inline.gif" height="10px" width="13px" style="cursor: pointer; " onclick="remove_cross_joins(0,'${cross[0]}')"/>
                                                    </td>
                                                </tr>
                                            </table>
                                            
                                        </td>
                                        %   endfor
                                        % endif
                                        % if row[1]['data']:
                                        %   for d in row[1]['data']:
                                        <td width="100%" id="data" class="data" align="right">
                                            <div align="right" class="mdx_data" id="mdx_data" style="display: inline;">${d}</div>
                                            <!-- <table width="100%">
                                                <tr>
                                                    <td width="100%">
                                                        <div align="right" class="mdx_data" id="mdx_data" style="display: inline;">${d}</div>
                                                    </td>
                                                </tr>
                                            </table> -->
                                        </td>
                                        %   endfor
                                        % endif
                                        <%
                                            prev_row = row[1]['pos'] + 1
                                            max_row_pos = max([max_pos[1]['pos'] for max_pos in rows]) +1
                                            
                                        %>
                                    </tr>
                                    % endfor
                                    <tr id="${max_row_pos}" style="background: #f6f6f6;">
                                        <%
                                            if rows[0][1]['cross_drill']:
                                                colspan = len(rows[0][1]['cross_drill'])+1
                                            
                                        %>
                                        % if not rows[0][1]['cross_drill']:
                                        <td width="100%">
                                            <div id="0_${max_row_pos}" class="dropeleRowextra" style="width: 100%;" title="Drop to add in to rows">
                                                <script language="javascript" type="text/javascript">
                                                    makeDroppablerow('0_${max_row_pos}');
                                                </script>
                                        	</div>
                                        </td>
                                        % endif
                                        % if rows[0][1]['cross_drill']:
                                        <td colspan="${colspan}" width="100%">
                                            <span align="left" style="width: 100%;">
                                                <div id="0_${max_row_pos}" class="dropeleRowextra" style="" title="Drop to add in to rows">
                                                    <script language="javascript" type="text/javascript"> 
                                                        makeDroppablerow('0_${max_row_pos}');
                                                    </script>
                                                </div>
                                            </span>
                                        </td>
                                        % endif
                                    </tr>
                                </tbody>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <script language="javascript" type="text/javascript">
                                makeDroppablepage('thirdAxis');
                            </script>
                        </td>
                        <td id="thirdAxis" class="thirdNewAxis" style="display: tablle-cell;" title="Drop to Add in Pages">
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        % endif
    </table>
</div>

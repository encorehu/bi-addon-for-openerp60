<div align="right" style=" width:100%; height: 100%;" width="100%">
    <table width="100%">
        <tr>
            % if sample and not rpc.session.bi_schema:
            <td width="50%">
                <select name="combo_schema" class="comboformat" id="combo_schema" onchange="${onselect}" width="150px" style="width:150px;">
                    <option>${firsttext}</option>
                    % for schema in schemalist:
                    <option selected="${tg.selector(schema[1] == selected_schema)}" value="${schema[0]}">${schema[1]}</option>
                    % endfor
                </select>
            </td>
            % endif
            % if not rpc.session.bi_schema and not sample:
            <td width="50%">
                <select name="combo_schema" class="comboformat" id="combo_schema" onchange="${onselect}" width="150px" style="width:150px;">
                    <option>${firsttext}</option>
                    % for schema in schemalist:
                    <option value="${schema[0]}">${schema[1]}</option>
                    % endfor
                </select>
            </td>
            % endif
            %if rpc.session.bi_schema:
            <td width="50%">
                <select name="combo_schema" class="comboformat" id="combo_schema" onchange="${onselect}" width="150px" style="width:150px;">
                    <option>Select Schema</option>
                    % for schema in schemalist:
                    %   if tg and tg.selector:
                    <option value="${schema[0] or rpc.session.bi_schemaid}" selected="${tg.selector(schema[1]==rpc.session.bi_schema)}">${schema[1]}</option>
                    %   endif
                    % endfor
<!--                    <option value="${rpc.session.bi_schemaid}">${rpc.session.bi_schema}</option>-->
                </select>
            </td>
            % endif
            % if sample:
            <td align="right" width="50%">
                <select name="combo_cube" class="comboformat" id="combo_cube" onchange="_combo_select(this.value)" width="150px" style="width:150px;">
                    % for cube in sample:
                    <option selected="${tg.selector(cube[1] == selected_cube)}" value="${cube[0]}">${cube[1]}</option>
                    % endfor
                        <script type="text/javascript">
                            _combo_select(getElement('combo_cube').value, false, '${selected_query}');
                        </script>
                </select>
            </td>
            % endif
            %if not rpc.session.bi_cube and not sample:
            <td align="right" width="50%">
                <select name="combo_cube" class="comboformat" id="combo_cube" onchange="_combo_select(this.value)" width="150px" style="width:150px;">
                </select>
            </td>
            % endif
            %if rpc.session.bi_cube and not sample:
            <td align="right" width="50%">
                <select name="combo_cube" class="comboformat" id="combo_cube" onchange="_combo_select(this.value)" width="150px" style="width:150px;">
                    <option value="${rpc.session.bi_cubeid}">${rpc.session.bi_cube}</option>
                </select>
            </td>
            % endif
        </tr>
    </table>
</div>

<table xmlns:py="http://purl.org/kid/ns#" cellpadding="2px" cellspacing="2px"  width="auto" class="mdx_table">
    <tr>
        <td py:if="filters">
            <span><b>Filters :</b> </span><br/>
            <div style="vertical-align:middle;">
                <div style="float:left;" py:for="filter in filters" >${filter[1]}</div>
                <div style="float:left;padding-top:3px;"><img src="/tinybi/static/images/delete_inline.gif" onclick="delete_filter('${filter[0]}');"/></div>
            </div>
        </td>
    </tr>
    <tr>
        <td><br/></td>
    </tr>
    <tr class="formats_head">
        <td py:for="d in header">
            <div class="mdx_header">${d}</div>    
        </td>
    </tr>
    <tr py:for="row in rows">
        <td py:for="r in row">
            <div py:if="type(r)==type(0.0)" class="mdx_data">${r}</div>
            <div py:if="type(r)==type(u'')" class="mdx_element">${r}</div>
        </td>
    </tr>
</table>

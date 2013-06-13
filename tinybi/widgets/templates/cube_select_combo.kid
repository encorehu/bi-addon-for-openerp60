<form xmlns:py="http://purl.org/kid/ns#" name="cubeselect" action = "/controller/cube_select">
    <table width="100%">
        <tr>
            <td></td>
            <td>
                <select name="combo_cube" class="comboformat" id="combo_cube" onchange="${onselect}" style="width: 100%; height:100%">
                    <option>${firsttext}</option>
                    <option py:for="cube in cubelist" value="${cube[0]}">${cube[1]}</option>
                </select>
            </td>
        </tr>
    </table>
</form>
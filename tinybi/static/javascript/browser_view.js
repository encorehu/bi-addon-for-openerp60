
var my_query_log
var url;
addLoadEvent(
    function() 
    {
        if (document.URL.indexOf('?') == -1) 
            clear_query();
//        document.oncontextmenu=multiple_Dragaable;
    }
    
);

function multiple_Dragaable(e) {
	var src = e.target;
		var tr =getFirstParentByTagAndClassName(src, 'tr', 'row') || getFirstParentByTagAndClassName(src, 'tr', 'row selected')
		if ((src.className=='row' ||(tr && tr.className=='row')) || (src.className=='row selected' ||(tr && tr.className=='row selected'))) {
	        if(getElement('context-menu').style.display =='none') {
				MochiKit.DOM.setElementPosition(getElement('context-menu'), {x: e.clientX, y: e.clientY});
				getElement('context-menu').style.display = '';
			}
		return false;	
		}
}

function clear_all() {
    var req = Ajax.JSON.post('/browser/mdx/clearCube', {});
}

// ------------------ Selection Function (Ex.  Schema, Cube). ------------------- //

// Functions For Schema Select
function _combo_select_schema(event,schema) {
    clear_query()
    var cube = 'Select Cube'
    _combo_select(cube)
    var params = {'combo_schema': schema};
    var req = Ajax.JSON.post('/browser/schema_select', params);
    a = req.addCallback
        (
            function(obj)
            {
                if (obj.error)
                {
                
                    var Ok = INPUT({'type': 'button','value': 'Ok'});
                    Ok.onclick = function () {setvisible.hide(this.event)}
                    var info = DIV({"id": "alert_box", "align": "center", "valign": "center", "style": "height: 125px"}, TABLE({"style": "height: 125px"}, TBODY(null, TR(null,
                        TD({"align": "center", "colspan": "2"}, SPAN({'align': 'center'},H5(null, "BI ERROR :"),SPAN(null,obj.error)))), 
                        TR(null, TD({"align": "center"}, Ok))))); 
                    setvisible.show(event, true, info);
                    getElement('combo_schema').selectedIndex = 0;

                }
                else
                {
                    var select = getElement('combo_cube');
                    
                    var options_1 = MochiKit.DOM.createDOM('OPTION')
                    options_1.innerHTML = 'Select Cube';
                    if(select.options.length == 0) {
                        select.appendChild(options_1)
                        for(i in obj.cube_list) {
                            var cubeID = obj.cube_list[i][0];
                            var cube = obj.cube_list[i][1];
                            var options = MochiKit.DOM.createDOM('OPTION',{'value': cubeID})
                            options.innerHTML = cube;
                            select.appendChild(options)
                        }
                    }
                    else {
                        var len = parseInt(select.options.length-1)
                        for(i=len;i>=0;i--) {
                            removeElement(select.options[i])
                        }
                        select.appendChild(options_1)
                        for(j in obj.cube_list) {
                            var cubeID = obj.cube_list[j][0];
                            var cube = obj.cube_list[j][1];
                            var options = MochiKit.DOM.createDOM('OPTION',{'value': cubeID})
                            options.innerHTML = cube;
                            select.appendChild(options);
                        }
                    }
                }    
            }
        );
}

// Used to make the ajax call for on db to fetch the cube detail in to the tree
function _combo_select(cube, test, qry)
{ 
    
    if('undefined' == typeof test) { 
        clear_query()
    }
    else {
        getElement('query').value = qry;
    }
        
    var params = {'combo_cube': cube};
    var req = Ajax.JSON.post('/browser/cube_select', params);
    a = req.addCallback
        (
            function(obj)
            {
                view_tree.reload();
            }
        );
}

// ----------------------- Query Display Function ------------- //

//To Create Query According To Cube
function mdx_get(run)
{
    if (run==null)
    {
        run = false;
    }
    var params = {'cubename': ''};
    if (Ajax.COUNT > 0) 
    {
         return MochiKit.Async.callLater(0.01, mdx_get,run);
    }
    var req = Ajax.JSON.post('/browser/mdx/mdx_get', params);
    Ajax.COUNT +=1
    a = req.addCallback
        (
            function(obj)
            {
                Ajax.COUNT -= 1;
                a = document.getElementById('query');
                a.value = obj.query;
                if(run)
                { 
                    check();
                }
            }
        );
}

function mdx_execute(query, event)
{
    var params = {'query': query};
    var req = Ajax.JSON.post('/browser/mdx/parseMDX', params);
    
    a = req.addCallback
        (
            function(obj)
            {
                b = document.getElementById('query');
                b.value = obj.query;
                check(query,'undefined','undefined','undefined',event);
                Ajax.COUNT -= 1;
            }
        );
    return 1;
}

//To Check The Droppable Element
var drop_event;
function check(query,draw,frm,check, event)
{
    if('undefined' == typeof event )
        drop_event = drop_event;
    else
        drop_event = event;

    if('undefined' == typeof frm )
    {
        // From Drag and Drop
        frm='0'
        //frm=1 if from Execute
    }
    if('undefined' == typeof query || query== '')
    {
        qd = getElement('query');
        if('undefined' == typeof check) 
        {
            query = qd.value;
        }
        else 
        {
            // THIS IS ta1_query for onclick by MDX_output button..for popup..
            td = getElement('ta1_query');
            query = td.value;
            qd.value = query;
        }
    }
    else 
    {
        qd = getElement('query');
        qd.value = query;
    }
    
    if('undefined' == typeof draw || draw=='')
    { 
        draw = true;
    }
    
    else
    {
        draw = false;	
    }
    
    needToAdd = true;
    
    var params = {'textquery': query, 'frompane': 'False', 'from': frm};
	var req = Ajax.post('/browser/exe', params);
    a = req.addCallback(function(xmlHttp) {
        var new_td = MochiKit.DOM.createDOM('TD', {'id': 'mdx_query_output','valign': 'top','align': 'left'});
        new_td.innerHTML = xmlHttp.responseText;
        
        var header = MochiKit.DOM.getElementsByTagAndClassName('table', 'header', new_td)[0]
        if(header) 
            header.style.display = 'none';
        
        var divs = MochiKit.DOM.getElementsByTagAndClassName('div', null, new_td)
        footer = divs[divs.length-1]       	
        if(footer.id == "footer")
            footer.style.display = 'none';
        MochiKit.DOM.setNodeAttribute(getElement('mdx_query_output').parentNode.parentNode.parentNode,'style', '');	
        swapDOM(getElement('mdx_query_output'), new_td);
       	document.getElementById('mdx_output').align = "left";

       //----------------------------- FOR IE FIXED DROPPABLE ELEMENT --------------- //
        var ua = navigator.userAgent.toLowerCase();

       if ((navigator.appName != 'Netscape') || (ua.indexOf('safari') != -1)) {
            // execute JavaScript
            var scripts = getElementsByTagAndClassName('script', null, document.getElementById('mdx_output'));
            forEach(scripts, function(s){
                eval(s.innerHTML);
            });
        }
    });
}

function rfrshcalls()
{
    _list_slicer_items()
    _list_query_items()
}

/*Functionality of Buttons in BI WebClient*/
function interchanged(event, cols,run)
{
    if(run==null)
    {
        run = false
    }
    
    if (cols)
    {
//    var schema=  getElement('combo_schema').options[getElement('combo_schema').selectedIndex].innerHTML;
        var params = {};
    
        var req = Ajax.post('/browser/mdx/swap', params);
        a = req.addCallback(function(xmlHttp){
            mdx_get(run);
            var new_td = MochiKit.DOM.createDOM('TD', {
                'id': 'mdx_query_output',
                'valign': 'top'
            });
            new_td.innerHTML = xmlHttp.responseText;
            swapDOM(getElement('mdx_query_output'), new_td);
        });
    }
    else
    {
        var Ok = INPUT({'type': 'button','value': 'Ok'});
        Ok.onclick = function () {setvisible.hide(this.event)}

        var info = DIV({"id": "alert_box", "align": "center", "valign": "center", "style": "height: 125px"}, TABLE({"style": "height: 125px"}, TBODY(null, TR(null, 
            TD({"align": "center", "colspan": "2"}, SPAN({'align': 'center'},H5(null, "BI ERROR :(Swap not possible)"),SPAN(null,"We cannot have blank for on rows")))),
            TR(null, TD({"align": "center"}, Ok))))); 
        setvisible.show(event, true, info);
    }
}

function Trim(str)
{

  return LTrim(RTrim(str));

}

function LTrim(str)
{

  for (var i=0; str.charAt(i)==" "; i++)
  {
    str =  str.substring(i,str.length-1);
  }
  return str;
}

function RTrim(str)
{

    for (var i=str.length-1; str.charAt(i)==" "; i--)
    {
        str = str.substring(0,i);
    }
    return str;
}

// ------------- Make Tree Draggable ------------------------ //

// To make the elements draggable for the tree 
var make_tree_draggable = function(tree,node)
{
    if (node['element_i']!=null)
    {
        var childnodes = node['childNodes']
        for (node in childnodes)
        {
            if (childnodes[node]['element_i']['src'].indexOf('draggable.png')!='-1')
            {
            	var id;
                if (childnodes[node]['parentNode']['element_a'].innerHTML=='Measures')
                {
                    id = "[measures].[" + childnodes[node]['element_a'].innerHTML + "]";
                }
                else if (childnodes[node]['parentNode']['element_i']['src'].indexOf('draggable.png')!='-1')
                {
                
                    id = make_id_new(childnodes[node])
                }
                else
                {
                    id = "["+childnodes[node]['element_a'].innerHTML+'].[all]';
                }
                MochiKit.DOM.setNodeAttribute(childnodes[node]['element_a'],'id',id);
                MochiKit.DOM.setNodeAttribute(childnodes[node]['element_a'],'class','cubedraggables');
                
                new Draggable(childnodes[node]['element_a'], {revert:true,ghosting:true});
                var new_obj = MochiKit.DOM.getElementsByTagAndClassName('td','image',childnodes[node]['element'])
                MochiKit.DOM.setNodeAttribute(new_obj[0]['childNodes'][0],'id',id+"^slicer");
                id=''
            }
        }
    }
}

// Make id for each draggable
function make_id_new(current_node)
{
    if (current_node['parentNode']['element_i']['src'].indexOf("draggable.png")!='-1')
    {
        var temp = ''
        temp =  make_id_new(current_node['parentNode']);
        temp = temp + ".[" + current_node['element_a'].innerHTML + "]";
        return temp;
    }
    else
    {
        return("[" + current_node['element_a'].innerHTML + "]");
    }
}

function make_id(current_node)
{
    if (current_node['parentNode']['element_i']['src'].indexOf("draggable.png")!='-1')
    {
        var temp = ''
        temp =  make_id(current_node['parentNode']);
        temp = temp + ".[" + current_node['element_a'].innerHTML + "]";
        return temp;
    }
    else
    {
        return("[" + current_node['element_a'].innerHTML + "]");
    }
}

// --------------------- Droppable Functions(Ex. Drop On Axis(Rows,Cols,pages), Cross, First Drop) ------- //

//Function Used For Extract the String,number 
function extract_Number(st)
{
    var pars = '',rest = '';
    var x=st.indexOf("^");
    if( x!=-1)
    {
        st=st.substring(0,x);
    }
    var tempArray = new Array();
    
    for(i=0;st.length>i;i++)
    {
        if( Number(st[i])>=0 && Number(st[i])<=9)
        {
            pars = pars + st[i];
        }
        else
        rest = rest + st[i];
    }
    tempArray.push(rest);
    tempArray.push(Number(pars));
    return tempArray;
}

// To handle first drop event when the area is empty 
function handle_drop_first(draggable,droppable,event)
{
    drag_obj = MochiKit.DOM.getElement(draggable);
    add_axis_on_rows(0,drag_obj['id'],true, event);
}

//To Drop the First element
function DragDropLoader(item)
{   
    new Droppable
        (
            item, 
            {
                accept : ['cubedraggables'],
                hoverclass:'firstDropped',
                ondrop: handle_drop_first 
            }
        );
}

//Used For Make Row element
function makeDroppablerow(item)
{
    var pos = extract_Number(item);
    var hover_class = 'ready_catchrow';
    new Droppable
        (
            item, 
            {
                accept: ['cubedraggables'], 
                hoverclass: 'ready_catchrow',
                onhover: function() {getElement(item).title = 'Drop to add in to rows'},
                ondrop: function(element) {
                    element = element.id;
                    add_axis_on_rows(pos[1],element,true);
                }
            }
        );
}

//Used For Make Column element 
var dropdim;
function makeDroppablecol(item)
{
    var pos = item.split("_");
    var  hover_class = 'ready_catchcol';
    new Droppable
        (
            item, 
            {
                accept: ['cubedraggables'], hoverclass:hover_class,
                ondrop: function (element) 
                        {
                            element = element.id;
                            add_axis_on_cols(pos[1],element,true);
                        }
            }
        );
//    MochiKit.DOM.getElement(item).style.position = '';
}

//Used For Make Column element(Default Call) 
function makeDroppablecoll(item)
{
    var pos = extract_Number(item);
    hover_class = 'NewAxisHover';
    new Droppable
        (
            item, 
            {
                accept: ['cubedraggables'], hoverclass:hover_class,
                ondrop: function (element) 
                        {
                            classTo = 'cross';
                            var subpos = 1;
                            element = element.id;
                            add_axis_on_cols(pos[1],element,true);
                        }
            }
        );
        
}

function makeDroppablepage(item) {
    var pos = extract_Number(item);
    hover_class = 'thirdAxisPage';
    new Droppable
        (
            item, 
            {
                accept: ['cubedraggables'], hoverclass:hover_class,
                ondrop: function (element, event) 
                        {
                            add_axis_on_pages(pos[1],element.id,true)
                        }
            }
        );
}
//Used For Make Row element(Default Call)
function makeDroppableroww(item)
{
    var pos = extract_Number(item);
    hover_class = 'NewAxisHover';
    new Droppable
        (
            item, 
            {
                accept: ['cubedraggables'], hoverclass:hover_class,
                ondrop: function (element) 
                        {
                            
                            classTo = 'cross';
                            var subpos = 1;
                            element = element.id;
                            add_axis_on_rows(pos[1],element,true);
                        }
            }
        );
}

//To make Droppable For CrossJoin for Column
function makeDroppablecoll_cross(item)
{
    var pos = extract_Number(item);
    hover_class = 'NewAxisHover';
    new Droppable
        (
            item, 
            {
                accept: ['cubedraggables'], hoverclass:hover_class,
                ondrop: function (element) 
                        {
//                            cross_col(element.id)
                            var params = {'axis': '1', 'element': element.id}
                            var request = Ajax.JSON.post('/browser/mdx/add_axis_on_cross', params);
                            a = request.addCallback(
                            function(obj) 
                            {
                                Ajax.COUNT -= 1;
                                b = document.getElementById('query');
                                b.value = obj.query;
                                check();
                            }
                            );
                        }
            }
        );
}

//To Make Droppable For CrossJoin for Row
function makeDroppablerow_cross(item) 
{
    var pos = extract_Number(item);
    hover_class = 'NewAxisHover';
    new Droppable
        (
            item, 
            {
                accept: ['cubedraggables'], hoverclass:hover_class,
                ondrop: function (element) 
                        {
//                            cross_row(element.id);
                            var params = {'axis': '0', 'element': element.id}
                            var request = Ajax.JSON.post('/browser/mdx/add_axis_on_cross', params);
                            a = request.addCallback(
                            function(obj) 
                            {
                                Ajax.COUNT -= 1;
                                b = document.getElementById('query');
                                b.value = obj.query;
                                check();
                            }
                            );
                        }
            }
        );
}

// ------------------------ Add Functions(Ex. Add Axis(rows, cols, pages,) cross) -------/

//TO Add Droppable Axis on Rows
function add_axis_on_rows(pos,axis,run, event)
{
    var params = {'pos': pos, 'axis':axis};
    if (Ajax.COUNT > 0) 
    {
        return MochiKit.Async.callLater(0.01, add_axis_on_rows,pos,axis,run, event);
    }
    var req = Ajax.JSON.post('/browser/mdx/add_axis_on_rows', params);
    Ajax.COUNT +=1
    a = req.addCallback
        (
            function(obj)
            {
                a = document.getElementById('query');
                a.value = obj.query;
                Ajax.COUNT -= 1;
                id = axis + "^query"
                if(run)
                { 
                    check(obj.query,'undefined','undefined','undefined',event);
                }
            }
        );
}

//TO Add Droppable Axis on Columns
function add_axis_on_cols(pos,axis,run)
{
    var params = {'pos': pos, 'axis':axis};
    if (Ajax.COUNT > 0) 
    {
        return MochiKit.Async.callLater(0.01, add_axis_on_cols,pos,axis,run);
    }
    var req = Ajax.JSON.post('/browser/mdx/add_axis_on_cols', params);
    Ajax.COUNT +=1
    
    a = req.addCallback
        (
            function(obj)
            {
//                mdx_get(run);
                a = document.getElementById('query');
                a.value = obj.query;
                if(run)
                { 
                    check();
                 }
                id = axis + "^query";
                Ajax.COUNT -= 1;
            }
        );
}

//TO Add Droppable Axis on Pages
function add_axis_on_pages(pos,axis,run) {
	
	 var params = {'pos': pos, 'axis':axis};
    if (Ajax.COUNT > 0) 
    {
        return MochiKit.Async.callLater(0.01, add_axis_on_cols,pos,axis,run);
    }
    var req = Ajax.JSON.post('/browser/mdx/add_axis_on_pages', params);
    a = req.addCallback(
        function (obj)
        {
        	
            if (obj.error)
            {
                var Ok = INPUT({'type': 'button','value': 'Ok'});
                Ok.onclick = function () {setvisible.hide(drop_event)}
                var info = DIV({"id": "alert_box", "align": "center", "valign": "center", "style": "height: 125px"}, TABLE({"style": "height: 125px"}, TBODY(null, TR(null,
                    TD({"align": "center", "colspan": "2"}, SPAN({'align': 'center'},H5(null, "BI ERROR : (Please add on cols first)"),SPAN(null,obj.error)))),
                    TR(null, TD({"align": "center"}, Ok))))); 
                setvisible.show(drop_event, true, info);
            }
            else
            {
                getElement('query').value = obj.query
                check()
            }
        }
    )
}
// ------------------------- REMOVE FUNCTIONS(Ex. For Rows, Cols, Pages, Cross, Filters) --------- //


//To Remove Element(Rows, Cols)
function del_element(pos,ax)
{
    var params = {'pos': pos, 'ax' : ax};
    if (Ajax.COUNT > 0) {
    }

    var req = Ajax.JSON.post('/browser/mdx/del_element', params);
    Ajax.COUNT +=1;
    a = req.addCallback(
    function(obj)
    {
        Ajax.COUNT -=1;
        b = document.getElementById('query');
        b.value = obj.query;
        check();
    }
    );
}

//Function For Remove Pages Axis
function remove_page_axis(page_element_index) {
	var params = {'axis': 2, 'element_id' : page_element_index};
       
    var req = Ajax.JSON.post('/browser/mdx/remove_page_axis', params);
    
    Ajax.COUNT +=1;
    a = req.addCallback(
    function(obj)
    {
        Ajax.COUNT -=1;
        b = document.getElementById('query');
        b.value = obj.query;
        check();
    }
    );
}

//To Remove Cross_joins
function remove_cross_joins(axis, element) 
{
    var params = {'axis': axis, 'element' : element};
       
    var req = Ajax.JSON.post('/browser/mdx/remove_cross_joins', params);

    a = req.addCallback(function(obj) 
    {
        b = document.getElementById('query');
        b.value = obj.query;
        check();
    });
}

function clear_filter(element_id,parent_node) {
    temp = parent_node+"^slicer"
    el = getElement(temp)
    if(el) {
    el.src = '/static/tinybi/images/filter.png'
    }
    var elem = getElement(element_id)
    var params = {'pos': element_id}
    var request = Ajax.JSON.post('/browser/mdx/remove_slicer',params)
    request.addCallback(function(obj) {
        removeElement(getElement(element_id))
        qry = getElement('query')
        qry.value = obj.query;
        check()
    });
}

//Clear Reports
function clear_query() 
{
    var req = Ajax.post('/browser/initial_view', {});
    req.addCallback(function(xmlHttp) {
        document.getElementById('mdx_query_output').innerHTML = xmlHttp.responseText;
        new Droppable('drop_here', {accept: ['cubedraggables'], hoverclass: 'firstDropped', ondrop: handle_drop_first})
        document.getElementById('mdx_output').align = "center";
        qd = document.getElementById('query');
        qd.value = ''
        var req = Ajax.JSON.post('/browser/mdx/clearCube', {});
    });
}

//----------------------- Slicer Functions --------------------- //

//To check Slicer by Element
function check_slicer(elem, run, event) {
    slicer(elem.name,run, event);
}

//To Create Slicer by Element
function slicer(elem,run, event)
{
    if(document.getElementById('query').value == '') {
        var Ok = INPUT({'type': 'button','value': 'Ok'});
        Ok.onclick = function () {setvisible.hide(this.event)}
        var info = DIV({"id": "alert_box", "align": "center", "valign": "center", "style": "height: 125px"}, TABLE({"style": "height: 125px"}, TBODY(null, TR(null,
            TD({"align": "center", "colspan": "2"}, SPAN({'align': 'center'},H5(null, "BI ERROR :"),SPAN(null,"Blank query.cannot add filter.")))),
            TR(null, TD({"align": "center"}, Ok))))); 
        setvisible.show(event, true, info);
        return 1
    }
    else {
        if(run==null)
            run = false;
        var params = {'elem': elem};
        if (Ajax.COUNT > 0) 
        {
             return MochiKit.Async.callLater(0.01, slicer,elem,run);
        }
        el = getElement(elem+"^slicer")
        var x = el.src.indexOf('filter_d')
        if (x!=-1)
        {
            var Ok = INPUT({'type': 'button','value': 'Ok'});
            Ok.onclick = function () {setvisible.hide(this.event)}
            var info = DIV({"id": "alert_box", "align": "center", "valign": "center", "style": "height: 125px"}, TABLE({"style": "height: 125px"}, TBODY(null, TR(null,
                TD({"align": "center", "colspan": "2"}, SPAN({'align': 'center'},H5(null, "BI ERROR :"),SPAN(null,"Slicer already added")))),
                TR(null, TD({"align": "center"}, Ok))))); 
            setvisible.show(event, true, info);
            return 1
        }
        el.src='/static/tinybi/images/filter_d.png'
        var req = Ajax.JSON.post('/browser/mdx/slicer', params);
        Ajax.COUNT +=1;
        a = req.addCallback(
            function(obj)
            {
                    Ajax.COUNT -=1;
                    b = document.getElementById('query');
                    b.value = obj.query;
                    if(run)
                    { 
                        _list_slicer_items()
                        check(obj.query);
                     }
            }
        );
    }
}

//To disply Query By Slicer 
function _list_slicer_items()
{
    var params = {};
    if (Ajax.COUNT > 0) 
    {
         return MochiKit.Async.callLater(0.01, _list_slicer_items);
    }
    var req = Ajax.JSON.post('/browser/mdx/listsliceritems', params);
    Ajax.COUNT += 1
    a = req.addCallback(
        function(obj)
        {
            list_slicer_items = obj.list;
            Ajax.COUNT -= 1
        }
    );
}

//To Activate Droppable Element For (Query,Slicer) 
var browser_onButtonClick = function(evt,node) {
    var src = evt.src();
    switch (src.name) 
    {
        case 'slicer': 
            return check_slicer(node, true, evt);
    }
}

//------------------------------------ DRILL FUNCTIONS( Ex. For Axis Drill, Page Drill, Cross Drill ----------- //

//Function For Page Drill
function drill_page(axis, element, pos) {
    var params = {'axis':axis, 'pos': pos,'element':element};
    var req = Ajax.JSON.post('/browser/mdx/page_drill',params);
    req.addCallback(function(obj) {
        b = document.getElementById('query');
        b.value = obj.query;
        check();
})

}

//Function For Axis Drill(rows, Columns, Pages)
function drill(axis, element, pos, drilling) 
{
    axis = axis.split("_")
    if (Ajax.COUNT > 0) 
    {
        return MochiKit.Async.callLater(0.01, drill,axis,element,pos,drilling);
    }
    axis = axis[0]
    var params = {'axis':axis, 'pos': pos,'element':element, 'drilling':drilling};
    var req = Ajax.JSON.post('/browser/mdx/drill',params);
    Ajax.COUNT +=1
    a = req.addCallback
        (
            function(obj)
            {
                b = document.getElementById('query');
                b.value = obj.query;
                check();
                Ajax.COUNT -= 1;
            }
        );
}

// Function For Cross_drill
function cross_drill(axis, element, pos) 
{
//	if (Ajax.COUNT > 0) 
//    {
//         return MochiKit.Async.callLater(0.01, cross_drill,axis, element, pos);
//    }
    var params = {'axis': axis, 'element': element, 'pos': pos};

    var req = Ajax.JSON.post('/browser/mdx/cross_drill', params);
    a = req.addCallback(
        function(obj)
        {  
//            Ajax.COUNT -=1;
            b = document.getElementById('query');
            b.value = obj.query;
            check();
        }
    );
}

function swap_cross()
{
    

    var req = Ajax.JSON.post('/browser/mdx/swap_cross', {});
    a = req.addCallback(
        function(obj)
        {  
            if (obj.error)
            {
                alert(obj.error);
                return
            }
            else
            {
                b = document.getElementById('query');
                b.value = obj.query;
                check();
            }
        }
    );
}

document.onmousemove = make_report_scrollable;
function make_report_scrollable(e) {
        var src = e.target;
        var tr = getFirstParentByTagAndClassName(src, 'tr', 'row')
        if (src.className=='row' ||(tr && tr.className=='row')) {
            if(getElement('mdx_result_output')!= null) {
            getElement('mdx_result_output').style.position = "relative"
            getElement('mdx_result_output').top = window.pageYOffset;
            getElement('mdx_result_output').style.top = window.pageYOffset+"px"
            }
        }
}
// vim: ts=4 ts=4 sw=4 si et

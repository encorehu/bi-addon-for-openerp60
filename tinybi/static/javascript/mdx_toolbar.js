//Function For Save Mdx Query Result
var setvisible
addLoadEvent(function () { 
 setvisible = new setVisible()
})
var prev_element
function save_query(event)
{
    var query = getElement('query').value;
    if (query)
    {
        flag = true
        if (document.URL.indexOf('?') > 1)
        {
            flag = false
            
            var Ok = INPUT({'type': 'button','value': 'Ok'});
			Ok.onclick = function () {setvisible.execute(this.event, false)}
	        var Cancel = INPUT({'class': 'button', 'type': 'button','value': 'Cancel'});
			Cancel.onclick = function () {setvisible.cancel(this.event)}
		    var info = DIV({"id": "alert_box", "align": "center", "valign": "center", "style": "height: 125px"}, TABLE(null, TBODY(null, TR(null, 
				TD({"align": "center", "colspan": "2"}, SPAN(null,"Do you want to overwrite the open query"))),TR(null, TD({"align": "left"}, Cancel), TD({"align": "right"}, Ok)))));      
            
           setvisible.show(event, true, info);

        }
        if (flag)
        {
        	var Ok = INPUT({'type': 'button','value': 'Ok'});
			Ok.onclick = function () {setvisible.execute(this.event)}
	        var Cancel = INPUT({'class': 'button', 'type': 'button','value': 'Cancel'});
			Cancel.onclick = function () {setvisible.hide(this.event)}
		    var info = DIV({"id": "alert_box", "align": "center", "valign": "center", "style": "height: 125px"}, TABLE(null, TBODY(null, TR(null, 
				TD({"align": "center", "colspan": "2"}, SPAN(null,"Enter The Name Of Query"))),TR(null, TD({"align": "center", "colspan": "2"}, INPUT({"id": "saved_query_name", "type": "text"}))),TR(null, TD({"align": "left"}, Cancel), TD({"align": "right"}, Ok)))));      
            
           setvisible.show(event, true, info);
        }
    }
    else
    {
    	var Ok = INPUT({'type': 'button','value': 'Ok'});
		Ok.onclick = function () {setvisible.hide(this.event)}
		var info = DIV({"id": "alert_box", "align": "center", "valign": "center", "style": "height: 125px"}, TABLE({"style": "height: 125px"}, TBODY(null, TR(null, 
			TD({"align": "center", "colspan": "2"}, SPAN({'align': 'center'},H5(null, "BI ERROR :"),SPAN(null,"Blank query cannot be saved")))),
			TR(null, TD({"align": "center"}, Ok))))); 
		setvisible.show(event, true, info);
    }
}

// Function Performing Redo Operation For Mdx Output
function redo(event)
{
    var query  = getElement('query').value;
    var params = {'query': query};
    var request = Ajax.JSON.post("/browser/redo", params)

    a = request.addCallback(function(obj)
    {
        if(obj.query) {
            var query = obj.query;
            mdx_execute(query);
            check(query,'undefined','undefined','undefined',event);
        }
        if(obj.error) {
	    	var Ok = INPUT({'type': 'button','value': 'Ok'});
			Ok.onclick = function () {setvisible.hide(this.event)}
			var info = DIV({"id": "alert_box", "align": "center", "valign": "center", "style": "height: 125px"}, TABLE({"style": "height: 125px"}, TBODY(null, TR(null, 
				TD({"align": "center", "colspan": "2"}, SPAN({'align': 'center'},H5(null, "BI ERROR :"),SPAN(null,obj.error)))),
				TR(null, TD({"align": "center"}, Ok))))); 
			
			setvisible.show(event, true, info, "redo_box");
        }
    });
}

// Function Performing Redo Operation For Mdx Output
function undo_step(event) {
    undo(event)
}
// Function Performing Redo Operation For Mdx Output
function undo(event)
{
    var query  = getElement('query').value;
    var params = {'query': query};
    var request = Ajax.JSON.post("/browser/undo", params)
    a = request.addCallback(function(obj)
    {
        if(obj.query)
        {
            var query = obj.query;
            mdx_execute(query);
            check(query,'undefined','undefined','undefined',event);
        }
        if(obj.error)
        {
    	var Ok = INPUT({'type': 'button','value': 'Ok'});
		Ok.onclick = function () {setvisible.hide(this.event)}
		var info = DIV({"id": "alert_box", "align": "center", "valign": "center", "style": "height: 125px"}, TABLE({"style": "height: 125px"}, TBODY(null, TR(null, 
			TD({"align": "center", "colspan": "2"}, SPAN({'align': 'center'},H5(null,"BI ERROR :"),SPAN(null, obj.error)))),
			TR(null, TD({"align": "center"}, Ok))))); 
		setvisible.show(event, true, info);
        }
    });
}


function switch_empty_view() {
    var parent_table = getElement('result_format');
    
    var dytable = MochiKit.DOM.getElementsByTagAndClassName('table', 'stats', parent_table);
    for(var i=0; i<dytable.length;i++) {
        var row_trs = MochiKit.DOM.getElementsByTagAndClassName('tr','row_axis', dytable[i])
        for(var j=0;j<row_trs.length;j++) {
            var data_Ar = new Array;
            var value = MochiKit.DOM.getElementsByTagAndClassName('div','mdx_data',row_trs[j])
            
            for(var k=0;k<value.length;k++) {
                if(value[k].innerHTML.indexOf("0.00") == 0 || value[k].innerHTML.indexOf("0") == 0)
                    data_Ar.push(value[k].innerHTML)
            }
            if(data_Ar.length == value.length)
                row_trs[j].style.display = '';
        }
        
    }
    var view = getElement('non_empty_view');
    if (view.style.display == 'none')
        view.style.display = ''
    var empty_view = getElement('empty_view');
    if (empty_view.style.display == '' || empty_view.style.display == 'block')
        empty_view.style.display = 'none';
}

function switch_non_empty_view() {
    var parent_table = getElement('result_format');
    
    var dytable = MochiKit.DOM.getElementsByTagAndClassName('table', 'stats', parent_table);
    for(var i=0; i<dytable.length;i++) {
        var row_trs = MochiKit.DOM.getElementsByTagAndClassName('tr','row_axis', dytable[i])
        for(var j=0;j<row_trs.length;j++) {
            var data_Ar = new Array;
            var value = MochiKit.DOM.getElementsByTagAndClassName('div','mdx_data',row_trs[j])
            
            for(var k=0;k<value.length;k++) {
                if(value[k].innerHTML.indexOf("0.00") == 0 || value[k].innerHTML.indexOf("0") == 0)
                    data_Ar.push(value[k].innerHTML)
            }
            if(data_Ar.length == value.length)
                row_trs[j].style.display = 'none';
        }
        
    }
    var view = getElement('non_empty_view');
    if (view.style.display == '' || view.style.display == 'block')
        view.style.display = 'none'
    var empty_view = getElement('empty_view');
    if (empty_view.style.display == 'none')
        empty_view.style.display = '';

}

function hide_show_tree()
{
    var i = getElement("grip_button").src.indexOf("sidebar_show")
    if (i!=-1)
    {
        getElement("column_1").style.display="none"
        getElement("grip_button").src = "/tinybi/static/images/sidebar_hide.gif"
        getElement("grip_button").title = "Click to show tree"
    }
    else
    {
        getElement("column_1").style.display=""
        getElement("column_1").align="left"
        getElement("grip_button").src = "/tinybi/static/images/sidebar_show.gif"
        getElement("grip_button").title = "Click to hide tree"
    }
}


//Function For execute Or Change The Query Result
function mdx_query(event) {
    var query = MochiKit.DOM.getElement('query').value;
    new Query().show(event,query);
}

//Function Expand The Query Result
function expand_all(event) {

    var query = getElement('query').value.toString();
    var rows = query.indexOf("on rows");
    if (rows==-1)
    {
    	var Ok = INPUT({'type': 'button','value': 'Ok'});
		Ok.onclick = function () {setvisible.hide(this.event)}
		var info = DIV({"id": "alert_box", "align": "center", "valign": "center", "style": "height: 125px"}, TABLE({"style": "height: 125px"}, TBODY(null, TR(null, 
			TD({"align": "center", "colspan": "2"}, SPAN({'align': 'center'},H5(null, "BI ERROR :"),SPAN(null,"Expand All not possible in this scenario")))),
			TR(null, TD({"align": "center"}, Ok))))); 
		
		setvisible.show(event, true, info, "expand_box");
        return
    }
    var request = Ajax.JSON.post("/browser/mdx/expand_all", {})
    a = request.addCallback(function(obj)
    {
        if(obj.query)
        {
            var query = obj.query;
            check(query);
        }
    });
}

//Function Collapse The Query Result
function collapse_all(event)
{
    var query = getElement('query').value.toString();
    var rows = query.indexOf("on rows");
    if (rows==-1)
    {
    	var Ok = INPUT({'type': 'button','value': 'Ok'});
		Ok.onclick = function () {setvisible.hide(this.event)}
		var info = DIV({"id": "alert_box", "align": "center", "valign": "center", "style": "height: 125px"}, TABLE({"style": "height: 125px"}, TBODY(null, TR(null, 
			TD({"align": "center", "colspan": "2"}, SPAN({'align': 'center'},H5(null, "BI ERROR :"),SPAN(null,"Collapse All not possible in this scenario")))),
			TR(null, TD({"align": "center"}, Ok))))); 
		
		setvisible.show(event, true, info, "collapse_box");
        
        return
    }
    var request = Ajax.JSON.post("/browser/mdx/collapse_all", {})
    a = request.addCallback(function(obj)
    {
        if(obj.query)
        {
            var query = obj.query;
            check(query);
        }
    });
}

//Function For Table_View Of Output
var Table = function()
{

    if(getElement(prev_element)) {
            if(getElement(prev_element).style.display == 'none')
                getElement(prev_element).style.display = '';
            if(prev_element == 'non_empty_view') {
                switch_empty_view()
            }

            if(prev_element == 'empty_view') {
                switch_non_empty_view()
            }
    }

    var graph = getElement('mdx_graph');

    if(graph.style.display == '' || graph.style.display == 'block') {
        graph.style.display = 'none';
        if(getElement('undo_graph'))
            swapDOM(getElement('undo_graph'), IMG({'id': 'undo', 'title':'Undo Step', 'class': 'bi_toolbar', 'src': '/tinybi/static/images/toolbar_img/back.png', 'onclick': 'undo()'}))
    }

    var mdx = getElement('mdx_output');
    mdx.style.display = '';
}

//Function for Graph View of MDX result(Stack Bar)
var counter = 1
var element;
var max_y = 0;
var Graph = function(event, column, elem, y_max)
{
    if(getElement('non_empty_view').style.display == '' || getElement('non_empty_view').style.display == 'block')
        {
            prev_element = 'non_empty_view';
            getElement('non_empty_view').style.display = 'none';
        }

    if(getElement('empty_view').style.display == '' || getElement('empty_view').style.display == 'block')
        {
            prev_element = 'empty_view';
            getElement('empty_view').style.display = 'none';
        }


    if ('undefined' == typeof(column) && 'undefined' == typeof(elem))
    {
        if(getElement('query').value == '')
        {
        	var Ok = INPUT({'type': 'button','value': 'Ok'});
			Ok.onclick = function () {setvisible.hide(this.event)}
			var info = DIV({"id": "alert_box", "align": "center", "valign": "center", "style": "height: 125px"}, TABLE({"style": "height: 125px"}, TBODY(null, TR(null,
				TD({"align": "center", "colspan": "2"}, SPAN({'align': 'center'},H5(null, "BI ERROR :"),SPAN(null,"Graph is not possible in this scenario")))),
				TR(null, TD({"align": "center"}, Ok))))); 
			
			setvisible.show(event, true, info, "graph_box");
        	return
        }
        else
        {
            var req = Ajax.JSON.post("/browser/check_condtiotion", {'query': getElement('query').value});
            req.addCallback(function(obj) {
                if(obj.data) {
                    getElement('mdx_graph').innerHTML = '';
                    var table = TABLE(null, TBODY(null));
                    for(var i=0; i<obj.data.length;i++) {
                        var r_dt = new Array();
                        
                        for(var j=0;j<obj.data[i][1].length;j++) {
                            var dt = new Array();
                            for(var k=0;k<obj.data[i][1][j][1].length;k++ ) {
                                dt.push(obj.data[i][1][j][1][k][1])
                            }
                        }
                        var data = obj.data[i][0]+"*" + dt.join('>');
                        url = urlEncode("/browser/page_stack_bar?data="+data+'&query='+getElement('query').value);
                        var params = {"width": "300", "height": "220", "name": "bi_chart", "url": url}
                        var p_request = Ajax.post("/browser/graph", params);
                        p_request.addCallback(function(xmlhttp) {
                            
                            if(getElement('mdx_output').style.display == '' || getElement('mdx_output').style.display == 'block')
                                getElement('mdx_output').style.display = 'none';
                                
                            if(getElement('mdx_graph').style.display == 'none')
                                getElement('mdx_graph').style.display = '';
                           
                           var div = MochiKit.DOM.createDOM('DIV');
                            div.innerHTML = xmlhttp.responseText;
                            table.appendChild(TR(null,TD(null,div)));
                            getElement('mdx_graph').appendChild(table);
                            
                        });
                    }
                }
                else {
                	if(obj.error) {
                		var Ok = INPUT({'type': 'button','value': 'Ok'});
						Ok.onclick = function () {setvisible.hide(this.event)}
						var info = DIV({"id": "alert_box", "align": "center", "valign": "center", "style": "height: 125px"}, TABLE({"style": "height: 125px"}, TBODY(null, TR(null,
							TD({"align": "center", "colspan": "2"}, SPAN({'align': 'center'},H5(null, "BI ERROR :"),SPAN(null,obj.error)))), 
							TR(null, TD({"align": "center"}, Ok))))); 
						
						setvisible.show(event, true, info, "graph_box");
                	}
                	else {
	                    var params = {"width": "450", "height": "360", "name": "bi_chart", "url": "/browser/stack_bar?query="+getElement('query').value}
	                    var request = Ajax.post("/browser/graph", params);
	                    request.addCallback(function(xmlhttp)
	                    {
	                        if(getElement('mdx_output').style.display == '' || getElement('mdx_output').style.display == 'block')
	                            getElement('mdx_output').style.display = 'none';
	                            
	                        if(getElement('mdx_graph').style.display == 'none')
	                            getElement('mdx_graph').style.display = '';
	                            
	                        getElement('mdx_graph').innerHTML = xmlhttp.responseText;
	                        
	                    });
                	}
                }
                var undo = getElement('undo');
                if(undo)
                    swapDOM(undo, IMG({'id': 'undo_graph', 'class': 'bi_toolbar', 'title':'Undo Graph', 'src': '/tinybi/static/images/toolbar_img/back.png', 'onclick': 'Table()'}))
                else
                    swapDOM(getElement('undo_graph'), IMG({'id': 'undo_graph', 'title':'Undo Graph', 'class': 'bi_toolbar', 'src': '/tinybi/static/images/toolbar_img/back.png', 'onclick': 'Table()'}))
            });
        }
    }

    else
    {
        var schema=  getElement('combo_schema').options[getElement('combo_schema').selectedIndex].innerHTML;
        var cube=  getElement('combo_cube').options[getElement('combo_cube').selectedIndex].innerHTML;
        
        url  = urlEncode('/browser/stack_by_element?schema='+schema+'&cube='+cube+'&rows='+elem+'&columns='+column+"&y_max="+y_max);

        var params = {"width": "450", "height": "360", "name": "bi_chart", "url": url}
        var request = Ajax.post("/browser/graph", params);

        request.addCallback(function(xmlhttp)
        {
            var parent_node = getElement('mdx_graph').parentNode;
            removeElement(getElement('mdx_graph'));
            var splitable = elem.split(",");
            if(splitable.length>1)
            {
//                var button = MochiKit.DOM.createDOM('BUTTON', {"align": "center", "valign": "top", 'onclick': "Graph('"+column+"', '"+splitable[0]+"', '"+max_y+"')"});
                swapDOM(getElement('undo_graph'), IMG({'id': 'undo_graph','title':'Undo Graph' , 'class': 'bi_toolbar', 'src': '/tinybi/static/images/toolbar_img/back.png', 'onclick': "Graph('"+'event'+"', '"+column+"', '"+splitable[0]+"', '"+max_y+"')"}))
                max_y = y_max;
            }
            else
            {
                max_y = y_max;
//                var button = MochiKit.DOM.createDOM('BUTTON', {"align": "center", "valign": "top", 'onclick': 'Graph()'});
                swapDOM(getElement('undo_graph'), IMG({'id': 'undo_graph','title':'Undo Graph', 'class': 'bi_toolbar', 'src': '/tinybi/static/images/toolbar_img/back.png', 'onclick': 'Graph()'}))
            }
        
//            button.innerHTML = 'Back';

            var chart = MochiKit.DOM.createDOM('TD');
            chart.innerHTML = xmlhttp.responseText;

//            var info = TD({'id': 'mdx_graph', "align": "center", "valign": "center"},TABLE(null,TBODY(null,
//                                TR(null,chart,TD(null, button)))));
            var info = TD({'id': 'mdx_graph', "align": "center", "valign": "center"},TABLE(null,TBODY(null,
                                TR(null,chart,TD(null)))));
            parent_node.appendChild(info);
        });

    }
}

//Function for Pie Chart View of MDX result
var element;

var Pie = function(event, rows, column)
{
    if(getElement('non_empty_view').style.display == '' || getElement('non_empty_view').style.display == 'block')
        {
            prev_element = 'non_empty_view';
            getElement('non_empty_view').style.display = 'none';
        }

    if(getElement('empty_view').style.display == '' || getElement('empty_view').style.display == 'block')
        {
            prev_element = 'empty_view';
            getElement('empty_view').style.display = 'none';
        }

    var schema=  getElement('combo_schema').options[getElement('combo_schema').selectedIndex].innerHTML;
    var query = getElement('query').value.toString();
    if ('undefined' == typeof(column) && 'undefined' == typeof(rows))
    {
        if(getElement('query').value == '')
        {
        	var Ok = INPUT({'type': 'button','value': 'Ok'});
			Ok.onclick = function () {setvisible.hide(this.event)}
			var info = DIV({"id": "alert_box", "align": "center", "valign": "center", "style": "height: 125px"}, TABLE({"style": "height: 125px"}, TBODY(null, TR(null,
				TD({"align": "center", "colspan": "2"}, SPAN({'align': 'center'},H5(null, "BI ERROR :"),SPAN(null,"Pie Chart is not possible in this scenario")))), 
				TR(null, TD({"align": "center"}, Ok))))); 
			
			setvisible.show(event, true, info, "pie_box");
            
            return
        }

        else
        {
            getElement('mdx_graph').innerHTML = '';
            var req = Ajax.JSON.post("/browser/check_condtiotion", {"Pie": true, "query": getElement('query').value})
            req.addCallback(function(obj) {
            	
            	if (obj.error) {
            		var Ok = INPUT({'type': 'button','value': 'Ok'});
					Ok.onclick = function () {setvisible.hide(this.event)}
					var info = DIV({"id": "alert_box", "align": "center", "valign": "center", "style": "height: 125px"}, TABLE({"style": "height: 125px"}, TBODY(null, TR(null,
						TD({"align": "center", "colspan": "2"}, SPAN({'align': 'center'},H5(null, "BI ERROR :"),SPAN(null,obj.error)))),
						TR(null, TD({"align": "center"}, Ok))))); 
					
					setvisible.show(event, true, info, "pie_box");
            	}
            	
                if(obj.cols) {
                    for(var i=0;i<obj.cols.length;i++) {
                        var dt = obj.cols[i].join("*")
                        var url  = urlEncode('/browser/pie_chart?schema='+schema+'&query='+query+'&cols_d='+dt);
                        var params = {"width": "400", "height": "240", "name": "pie_chart", "url": url}
                        var request = Ajax.post("/browser/graph", params);
                        request.addCallback(function(xmlhttp) {
                            if(getElement('mdx_output').style.display == '' || getElement('mdx_output').style.display == 'block')
                                getElement('mdx_output').style.display = 'none';
                                
                            if(getElement('mdx_graph').style.display == 'none')
                                getElement('mdx_graph').style.display = '';
                                
                           var chart = MochiKit.DOM.TD({"id": "pie-chart"});
                           chart.innerHTML = xmlhttp.responseText
                           var info = TABLE(null, TBODY(null, TR(null, chart)));
                           getElement('mdx_graph').appendChild(info);
                        });
                    }
                }
                if(obj.data) {
                    for(var i=0; i<obj.data.length;i++) {
                        var r_dt = new Array();
                        for(var j=0;j<obj.data[i][1].length;j++) {
                            var dt = new Array();
                            for(var k=0;k<obj.data[i][1][j][1].length;k++ ) {
                                dt.push(obj.data[i][1][j][1][k][1])
                            }
                        }
                        var dt = obj.data[i][0]+"*" + dt.join('>');
                        url = urlEncode("/browser/page_pie_chart?data="+dt+'&query='+getElement('query').value);
                        var params = {"width": "450", "height": "160", "name": "bi_chart", "url": url}
                        var request = Ajax.post("/browser/graph", params);
                        request.addCallback(function(xmlhttp)
                        {
                            if(getElement('mdx_output').style.display == '' || getElement('mdx_output').style.display == 'block')
                                getElement('mdx_output').style.display = 'none';
                            if(getElement('mdx_graph').style.display == 'none')
                                getElement('mdx_graph').style.display = '';
                             
                            var div = MochiKit.DOM.createDOM('DIV');
                            div.innerHTML = xmlhttp.responseText;
                            getElement('mdx_graph').appendChild(div);
                        });
                        
                    }
                }
                if(obj.page_cols) {
                    var info = TABLE(null, TBODY(null));
                    for(var i=0; i<obj.page_cols.length;i++) {
                        var tr = TR({'id': 'chart_tr'})
                        info.appendChild(tr);
                        for(var v=0;v<obj.page_cols[i][1].length;v++) {
                            var dt = new Array();
                            for(var k=0;k<obj.page_cols[i][1][v][1].length;k++ ) {
                                var dt = obj.page_cols[i][0]+"*"+obj.page_cols[i][1][v][1][k][1]
                                url = urlEncode("/browser/page_pie_chart?data="+dt+'&column_d='+obj.page_cols[i][1][v][1][k][0]+'&query='+getElement('query').value);
                                var params = {"width": "300", "height": "160", "name": "bi_chart", "url": url}
                                var request = Ajax.post("/browser/graph", params);
                                request.addCallback(function(xmlhttp)
                                {
                                    if(getElement('mdx_output').style.display == '' || getElement('mdx_output').style.display == 'block')
                                        getElement('mdx_output').style.display = 'none';
                                    if(getElement('mdx_graph').style.display == 'none')
                                        getElement('mdx_graph').style.display = '';
                                    var div = MochiKit.DOM.createDOM('DIV');
                                    div.innerHTML = xmlhttp.responseText;
                                    var td = MochiKit.DOM.TD()
                                    tr.appendChild(td)
                                    td.appendChild(div)
                                    getElement('mdx_graph').appendChild(info);
                                });
                            }
                        }
                    }
                }
                var undo = getElement('undo')
                if(undo)
                    swapDOM(undo, IMG({'id': 'undo_graph', 'title':'Undo Graph', 'class': 'bi_toolbar', 'src': '/tinybi/static/images/toolbar_img/back.png', 'onclick': 'Table()'}))
                else
                    swapDOM(getElement('undo_graph'), IMG({'id': 'undo_graph', 'title':'Undo Graph', 'class': 'bi_toolbar', 'src': '/tinybi/static/images/toolbar_img/back.png', 'onclick': 'Table()'}))
            });
        }
    }

    else
    {
        var cube=  getElement('combo_cube').options[getElement('combo_cube').selectedIndex].innerHTML;
        url  = urlEncode('/browser/pie_by_element?schema='+schema+'&rows='+rows+'&columns='+column+'&cube='+cube);
        var params = {"width": "450", "height": "360", "name": "pie_chart", "url": url}
        var request = Ajax.post("/browser/graph", params);
        request.addCallback(function(xmlhttp)
        {
            if(getElement('mdx_output').style.display == '' || getElement('mdx_output').style.display == 'block')
                    getElement('mdx_output').style.display = 'none';

            var parent_node = getElement('mdx_graph').parentNode;
            removeElement(getElement('mdx_graph'));
            
            var splitable = rows.split(".");
           if(splitable.length>2)
           {
//                var button = MochiKit.DOM.createDOM('BUTTON', {"align": "center", "valign": "top", 'onclick': "Pie('"+element+"', '"+column+"')"});
                element = rows;
                swapDOM(getElement('undo_graph'), IMG({'id': 'undo_graph', 'title':'Undo Graph', 'class': 'bi_toolbar', 'src': '/tinybi/static/images/toolbar_img/back.png', 'onclick': "Pie('"+'event'+"','"+element+"', '"+column+"')"}))
            }
            else
            {
               element = rows;
//               var button = MochiKit.DOM.createDOM('BUTTON', {"align": "center", "valign": "top", 'onclick': "Pie()"});
               swapDOM(getElement('undo_graph'), IMG({'id': 'undo_graph', 'title':'Undo Graph', 'class': 'bi_toolbar', 'src': '/tinybi/static/images/toolbar_img/back.png', 'onclick': 'Pie()'}))
               
            }
//            button.innerHTML = 'Back';

            var chart = MochiKit.DOM.createDOM('TD');
            chart.innerHTML = xmlhttp.responseText;

//            var info = TD({'id': 'mdx_graph', "align": "center", "valign": "center"},TABLE(null,TBODY(null,
//                                TR(null,chart,TD(null, button)))));
            var info = TD({'id': 'mdx_graph', "align": "center", "valign": "center"},TABLE(null,TBODY(null,
                                TR(null,chart,TD(null)))));
            parent_node.appendChild(info);
        });
    }
}

//Function For execute Or Change The Query Result
function mdx_query(event) {
    var query = MochiKit.DOM.getElement('query').value;
    new Query().show(event,query);
}

var Query  = function() {
    this.__init__();
}

Query.prototype = {
    __init__ : function(){
        this.layer = $('biLayer');
        this.box = $('biBox');

        var mdx_query = SPAN({'id': 'mdx_query','style':'font-weight:bold;color: red; background: url(/tinybi/static/images/button_bg2.png) repeat-x top left;'},'MDX_QUERY');
        var form_query = MochiKit.DOM.createDOM('TEXTAREA',{'name':'textquery','class':'queryarea','id':'ta1_query','rows':'4', 'cols': '12','style':'width: 98%; border-color: #E3E3E3;'})

        MochiKit.DOM.setNodeAttribute(form_query,'onmousedown',"if (this.value == 'Query Here') this.value = ''")

        var Execute = BUTTON({'class': 'button', 'type': 'button'}, 'Execute');
        MochiKit.Signal.connect(Execute, 'onclick', this, 'execute');

        var Cancel = BUTTON({'class': 'button', 'type': 'button'}, 'Cancel');
        MochiKit.Signal.connect(Cancel, 'onclick', this, 'hide');

        var Save = BUTTON({'class': 'button', 'type': 'button'}, 'Save');
        MochiKit.Signal.connect(Save, 'onclick', this, 'save');

        var info = DIV(null,TABLE({'class': 'Query', 'width':'100%'},TBODY(null,
                                TR(null,TD({'align': 'center','width':'100%','colspan':'4'},mdx_query)),
                                TR(null,TD({'align': 'left','width':'100%','colspan':'4'},form_query)),
                                TR(null,TD({'align': 'right', 'width': '100%'}, Save),
                                TD({'align': 'right', 'width': '100%'}, Execute),
                                TD({'align': 'right', 'width': '100%'}, Cancel)))));

         if (!this.layer) {
            this.layer = DIV({id: 'biLayer'});
            appendChildNodes(document.body, this.layer);
            setOpacity(this.layer, 0.5);
            connect(this.layer, 'onclick', this, 'hide');
        }

        if (!this.box) {
            this.box = DIV({id: 'biBox'});
            appendChildNodes(document.body, this.box);
        }

        this.box.innerHTML = "";
        appendChildNodes(this.box, info);
       },

    show : function(event,query) {
        getElement('ta1_query').value = query;
        setElementDimensions(this.layer, elementDimensions(document.body));

        var w = 550;
        var h = 325;

        setElementDimensions(this.box, {w: w, h: h});
        var x = event.clientX;
        var y = event.clientY;

        x -= w / 2;
        y -= h - h / 3;

        var vd = elementDimensions(document.body);
        var md = elementDimensions(this.box);

        if ((x + md.w) > vd.w) {
            x -= x + md.w - vd.w;
        }
        x = 295 ;
        y = 180 ;

        setElementPosition(this.box, {x: x, y: y});

        showElement(this.layer);
        showElement(this.box);
    },

    hide : function(event) {
        hideElement(this.box);
        hideElement(this.layer);
    },

    execute : function(event) {
        var p = getElement('Filter')
        var c= MochiKit.DOM.getElementsByTagAndClassName('td','filter', p);
        var qry = getElement('ta1_query').value;

        if(qry.indexOf('where') == '-1') {
            //So Remove The Filter
        }
        mdx_execute(qry,event);
//        check('','','1',true);
        hideElement(this.box);
        hideElement(this.layer);

    },

    save : function(event) {
    	hideElement(this.box);
        hideElement(this.layer);
        var schema = getElement('combo_schema').value;
        var cube=getElement('combo_cube').value;
        var query = getElement('ta1_query').value;
        
        var Ok = INPUT({'type': 'button','value': 'Ok'});
		Ok.onclick = function () {setvisible.execute(this.event)}
        var Cancel = INPUT({'class': 'button', 'type': 'button','value': 'Cancel'});
		Cancel.onclick = function () {setvisible.hide(this.event)}
	    var info = DIV({"id": "alert_box", "align": "center", "valign": "center", "style": "height: 125px"}, TABLE(null, TBODY(null, TR(null, 
			TD({"align": "center", "colspan": "2"}, SPAN(null,"Enter The Name Of Query"))),TR(null, TD({"align": "center", "colspan": "2"}, INPUT({"id": "saved_query_name", "type": "text"}))),TR(null, TD({"align": "left"}, Cancel), TD({"align": "right"}, Ok)))));      
        
       setvisible.show(event,true, info);
    }
}
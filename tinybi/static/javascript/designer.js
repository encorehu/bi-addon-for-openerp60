// Code for handling the designer code over here 
//To Handle Event on Edit 
var onEdit = function(node) {
    var tree = view_tree;
    var selected = node || tree.selection[0] || null;
    var record = selected.record;
    var data = record.items;
    
    var url = record['action'];
    
    //Split Url Action(Model,Context,Id)
    var st_index = url.indexOf('(');
    var count = url.substring(st_index+1);
    var end_index = url.indexOf(')');
    var new_count = url.substring(st_index+1,end_index);
    var split_Var  = new_count.split(",");
    
    //Split Model
    var model = split_Var[0];
    var st_model = model.indexOf('"');
    var set_count = model.substring(st_model+1);
    var end_model = set_count.indexOf('"');
    var md = set_count.substring(st_model,end_model);
    
    //Split Context
    var ctx = split_Var[1];
    var ctx_index = ctx.indexOf('"');
    var ctx_count = ctx.substring(ctx_index+1);
    var end_ctx = ctx_count.indexOf('}');
    var context = ctx_count.substring(ctx_index,end_ctx+1);
    
    //Split Id
    var id = split_Var[2];
    var id_index = id.indexOf('"');
    var id_count = id.substring(id_index+1);
    var end_index = id_count.indexOf('"');
    var Id = id_count.substring(id_index,end_index);
    
    open_form_popup(md,context,Id);
}

//To Handle Event On Delete
var onDelete = function(node) {
    var tree = view_tree;
    var selected = node || tree.selection[0] || null;
    var record = selected.record;
    var data = record.items;
    var url = record['action'];
    var st_index = url.indexOf('(');
    var count = url.substring(st_index+1);
    var end_index = url.indexOf(')');
    var new_count = url.substring(st_index+1,end_index);
    var split_Var  = new_count.split(",");

    //Split Model
    var model = split_Var[0];
    var st_model = model.indexOf('"');
    var set_count = model.substring(st_model+1);
    var end_model = set_count.indexOf('"');
    var md = set_count.substring(st_model,end_model);
    
    //Split id
    var id = split_Var[2];
    var id_index = id.indexOf('"');
    var id_count = id.substring(id_index+1);
    var end_index = id_count.indexOf('"');
    var Id = id_count.substring(id_index,end_index);
    
    delete_bi(md,Id, selected);
    
}

//To Delete The Element Like(Schema,Cube,Dimension,Hierarchy,Level,Measure)
function delete_bi(model,id, selected) {
    var selected = selected;
    var model = model;
    var params = {'model': model,'id':id};
    var request = Ajax.JSON.post('/designer/bi_form/delete_bi', params);
    request.addCallback(function(obj) {
        var x_array=model.split(".");
        alert("All the childrens of selected "+x_array[1]+" deleted.");
        find_node(model, selected);
        //window.location.reload(true);
    });
}

function find_node(model,node) {
    var tree = view_tree;
    var total_row = MochiKit.DOM.getElementsByTagAndClassName('tr','row', getElement('view_tree'));
    if(model == "olap.schema") {
        
        if(node.lastChild) {
        
            var elem = node.element;
            var elem_index = elem.rowIndex;
            var elem_child = node.lastChild.element;
            var elem_child_index = elem_child.rowIndex;
            
            for(var i = elem_child_index -1; i>= elem_index -1; i--) 
            {
                MochiKit.DOM.removeElement(total_row[i]);
            }
        }
        
        else {
            MochiKit.DOM.removeElement(node.element);
        }
    }
    
    else if(model == "olap.cube") {
        
        if(node.lastChild) {
            
            var elem = node.element;
            var elem_index = elem.rowIndex;
            var elem_child = node.lastChild.element;
            var elem_child_index = elem_child.rowIndex;

            if(node.lastChild.childNodes.length>0) {
                var firstchild = node.lastChild.firstChild.element.rowIndex;
                var lastchild = node.lastChild.lastChild.element.rowIndex;
                
                for(var i =lastchild -1;i>=firstchild -1;i--) {
                    MochiKit.DOM.removeElement(total_row[i]);
                }
            }
            
            for(var i = elem_child_index -1; i>= elem_index -1; i--) 
            {
                MochiKit.DOM.removeElement(total_row[i]);
            }
        }
        else {
            MochiKit.DOM.removeElement(node.element);
        }
        
    }
    
    else if(model == "olap.dimension") {
        if(node.lastChild) {
            var elem = node.element;
            var elem_index = elem.rowIndex;
            var elem_child = node.lastChild.element;
            var elem_child_index = elem_child.rowIndex;
            
            for(var i = elem_child_index -1; i>= elem_index -1; i--) 
            {
                MochiKit.DOM.removeElement(total_row[i]);
            }
        }
        
        else {
            MochiKit.DOM.removeElement(node.element);
        }
    }
    
    else if(model == "olap.hierarchy") {
        
        if(node.lastChild) {
            var elem = node.element;
            var elem_index = elem.rowIndex;
            var elem_child = node.lastChild.element;
            var elem_child_index = elem_child.rowIndex;
            
            for(var i = elem_child_index -1; i>= elem_index -1; i--) 
            {
                MochiKit.DOM.removeElement(total_row[i]);
            }
            
        }
        
        else {
            MochiKit.DOM.removeElement(node.element);
    }
    
    }
    
    else if(model == "olap.level") {
        //if(node.lastChild) {
        //var elem = node.element;
        //var elem_index = elem.rowIndex;
        //var elem_child = node.lastChild.element;
        //var elem_child_index = elem_child.rowIndex;
        //}
        //else {
//    }
        MochiKit.DOM.removeElement(node.element);
    }
    
    else if(model == "olap.measure") {
        MochiKit.DOM.removeElement(node.element);
    }
}

//To Handle Event on Button OnClick (Edit or Delete)
var onButtonClick = function(evt, node) {
    var src = evt.src();
        switch (src.name) {
            case 'edit': 
                return onEdit(node);
            case 'delete': 
                return onDelete(node);
        }
}

//To Open BI Forms  in Popup Forms
function open_form_popup(model,context,id,type)
{
    // Model     : specifies the model
    // Mode      : new / edit
    // key_name  : linked field in the model 
    // parent_id : to be filled by
    if (id) 
    {
        if (browser.isGecko19)
        {
            window.open(getURL('/designer/bi_form/edit', {
                model: model, context:context, id:id, type: type
                }));
        }
        
        else
        {
            openWindow(getURL('/designer/bi_form/edit', {
                model: model, context:context, id:id, type: type
            }));
        }
    }
    
    else 
    {
        if (browser.isGecko19)
        {
            window.open(getURL('/designer/bi_form/edit', {
                model: model, context:context, id:id
            }));
        }
        
        else
        {
            openWindow(getURL('/designer/bi_form/edit', {
                model: model,
                context: context
            }));
        }
    }
}

var change_view = function(tree,pnode,selected,record,name,id,model,context, b_type) {
    var items = {
            'edit': '/tinybi/static/images/listgrid/edit_inline.gif',
            'delete': '/tinybi/static/images/listgrid/delete_inline.gif',
            'name': name, 'string': name
            }
            
    var icon = 	'/tinybi/static/images/tree_img/close_folder.png'
    
    if (model == 'olap.cube')
    {
        var make_dimension;
        var make_measure;
        var cube_id = 'cube_id';
        //var dim_action = 'javascript:open_form_popup("olap.dimension","{u"cube_id+'":"'+id+'"}")';
        var dim_1 = "javascript:open_form_popup";
        var dim_2 = "olap.dimension";
        var cube_id = "{u"+"'cube_id'"+':'+"'"+id+"'}";
        var dim_action = dim_1+"("+ '"'+dim_2+'"'+',' + '"'+cube_id+'"'+")";
        
        var mes_1 = "javascript:open_form_popup";
        var mes_2 = "olap.measure";
        var mes_action = mes_1+"("+ '"'+mes_2+'"'+',' + '"'+cube_id+'"'+")";
        
        make_dimension = {
            'target':'',
            'items':{'name': 'Dimension', 'string': 'Dimension'},
            'id':'New Dim',
            'action':'',
            'children':[
                {
                    'target':'',
                    'items':{'name': 'Add New Dimension', 'string': 'Add New Dimension'},
                    'id':'New Dim',
                    'action':dim_action,
                    'children':[],
                    'icon':'/openerp/static/images/stock/gtk-new.png'
                }
                ],
            'icon':icon
        }
        
        make_measure = {
            'target':'',
            'items':{'name': 'Measure', 'string': 'Measure'},
            'id':'New Mes',
            'action':'',
            'children':[
                {
                    'target':'',
                    'items':{'name': 'Add New Measure', 'string': 'Add New Measure'},
                    'id':'New Measure',
                    'action':mes_action,
                    'children':[],
                    'icon':'/openerp/static/images/stock/gtk-new.png'
                }
                ],
            'icon':icon
        }
        
    var action = 'javascript:open_form_popup("'+model+'","'+context+'","'+id+'")'
    
    var record_new = {
        'target':'',
        'items':items,
        'id':id,
        'action':action,
        'children':[make_dimension,make_measure],
        'icon':icon
    }
        
    if(b_type) {
        MochiKit.DOM.setNodeAttribute(selected.element_a, 'innerHTML', name)
        window.close();
        pnode.updateDOM(selected);
    }
    
    else {
        var node = tree.createNode(record_new);
        window.close();
        pnode.insertBefore(node, selected);
    }
    
    }
    
    else if (model == 'olap.dimension')
    {
        var action = 'javascript:open_form_popup("'+model+'","'+context+'","'+id+'")'
        var hier_1 = "javascript:open_form_popup";
        var hier_2 = "olap.hierarchy";
        var hier_id = "{u"+"'dimension_id'"+':'+"'"+id+"'}";
        var hier_action = hier_1+"("+ '"'+hier_2+'"'+',' + '"'+hier_id+'"'+")";
        var record_new = {
            'target':'',
            'items':items,
            'id':id,
            'action':action,
            'children':[
                {
                    'target':'',
                    'items':{'name': 'Add New Hierarchy', 'string': 'Add New Hierarchy'},
                    'id':'New Hierarchy',
                    'action':hier_action,
                    'children':[],
                    'icon':'/openerp/static/images/stock/gtk-new.png'
                }
                ],
            'icon':icon
        }
        
        if(b_type) {
            MochiKit.DOM.setNodeAttribute(selected.element_a, 'innerHTML', name)
            window.close();
            pnode.updateDOM(selected);
        }
        
        else {
            var node = tree.createNode(record_new);
            window.close();
            pnode.insertBefore(node, selected);
        }
        
    }
    
    else if(model == 'olap.hierarchy') {
        var action = 'javascript:open_form_popup("'+model+'","'+context+'","'+id+'")'
        var level_1 = "javascript:open_form_popup";
        var level_2 = "olap.level";
        var level_id = "{u"+"'hierarchy_id'"+':'+"'"+id+"'}";
        var level_action = level_1+"("+ '"'+level_2+'"'+',' + '"'+level_id+'"'+")";
        var record_new = {
            'target':'',
            'items':items,
            'id':id,
            'action':action,
            'children':[
                {
                    'target':'',
                    'items':{'name': 'Add New Level', 'string': 'Add New Level'},
                    'id':'New Level',
                    'action':level_action,
                    'children':[],
                    'icon':'/openerp/static/images/stock/gtk-new.png'
                }
                ],
            'icon':icon
        }
        
        if(b_type) {
            MochiKit.DOM.setNodeAttribute(selected.element_a, 'innerHTML', name)
            window.close();
            pnode.updateDOM(selected);
        }
        
        else {
            var node = tree.createNode(record_new);
            window.close();
            pnode.insertBefore(node, selected);
        }
        
    }
    
    else if(model == 'olap.level') {
        var action = 'javascript:open_form_popup("'+model+'","'+context+'","'+id+'")'
        var record_new = {
            'target':'',
            'items':items,
            'id':id,
            'action':action,
            'children':[],
            'icon':icon
        }
        
        if(b_type) {
            MochiKit.DOM.setNodeAttribute(selected.element_a, 'innerHTML', name)
            window.close();
            pnode.updateDOM(selected);
        }
        
        else {
            var node = tree.createNode(record_new);
            window.close();
            pnode.insertBefore(node, selected);
        }
    }
    
    else if(model == 'olap.measure') {
        var action = 'javascript:open_form_popup("'+model+'","'+context+'","'+id+'")'
        var record_new = {
            'target':'',
            'items':items,
            'id':id,
            'action':action,
            'children':[],
            'icon':icon
        }
        
        if(b_type) {
            MochiKit.DOM.setNodeAttribute(selected.element_a, 'innerHTML', name)
            window.close();
            pnode.updateDOM(selected);
        }
        
        else {
            var node = tree.createNode(record_new);
            window.close();
            pnode.insertBefore(node, selected);
        }
    }
    
    //var record_new = make_node(null,items,id,'',[],icon,'','')
}

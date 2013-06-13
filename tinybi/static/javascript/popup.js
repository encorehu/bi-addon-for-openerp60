/* -----------------------------------------------
   All alerts are in Popup(Div)
  ------------------------------------------------ */


var setVisible  = function() {
    this.__init__();
}

setVisible.prototype = {
    __init__ : function(){
        this.layer = $('biLayer');
        this.box = $('biBox');
	
	
//		 var Ok = INPUT({'type': 'button','value': 'Ok'});
//        MochiKit.Signal.connect(Ok, 'onclick', this, 'execute');
//
//        var Cancel = INPUT({'class': 'button', 'type': 'button','value': 'Cancel'});
//        MochiKit.Signal.connect(Cancel, 'onclick', this, 'hide');
//
//        
//        
//	    var info = DIV({"id": "alert_box", "align": "center", "valign": "center", "style": "height: 125px"}, TABLE(null, TBODY(null, TR(null, 
//		TD({"align": "center", "colspan": "2"}, SPAN(null,"Enter The Name Of Query"))
//		),
//		TR(null, TD({"align": "center", "colspan": "2"}, INPUT({"id": "saved_query_name", "type": "text"}))),
//		
//		TR(null, TD({"align": "left"}, Cancel), TD({"align": "right"}, Ok))
//		)));      

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
       },

    show : function(event, flag, msg) {
    	this.box.innerHTML = '';
    	appendChildNodes(this.box, msg);
    	if('undefined' == typeof flag) {
    		hideElement(getElement('error_box'));
    		showElement(getElement('alert_box'));
    		
    	}
    	else {
    		if(getElement('error_box')) {
    			hideElement(getElement('error_box'));
    		}
    	}
        setElementDimensions(this.layer, elementDimensions(document.body));
        var w = 220;
        var h = 125;

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
        x = 395 ;
        y = 180 ;

        setElementPosition(this.box, {x: x, y: y});

        showElement(this.layer);
        showElement(this.box);
    },

    hide : function(event) {
        hideElement(this.box);
        hideElement(this.layer);
    },
    
    cancel: function() {
    	var Ok = INPUT({'type': 'button','value': 'Ok'});
		Ok.onclick = function () {setvisible.execute(this.event)}
        var Cancel = INPUT({'class': 'button', 'type': 'button','value': 'Cancel'});
		Cancel.onclick = function () {setvisible.hide(this.event)}
	    var info = DIV({"id": "alert_box", "align": "center", "valign": "center", "style": "height: 125px"}, TABLE(null, TBODY(null, TR(null, 
			TD({"align": "center", "colspan": "2"}, SPAN(null,"Enter The Name Of Query"))),TR(null, TD({"align": "center", "colspan": "2"}, INPUT({"id": "saved_query_name", "type": "text"}))),TR(null, TD({"align": "left"}, Cancel), TD({"align": "right"}, Ok)))));
			
		this.box.innerHTML = ""
		appendChildNodes(this.box, info);
    },
    
    execute : function(event, flag) {
    	if('undefined' == typeof flag) {
	    	if(getElement('saved_query_name').value == "") {
	    		hideElement(getElement('alert_box'))
	    		var Ok = BUTTON({'type': 'button', 'class': 'button'}, 'Ok');
	        	MochiKit.Signal.connect(Ok, 'onclick', this, 'show');
	        	if(getElement('error_box') == null) {
					var error = DIV({'id': 'error_box', "align": "center", "valign": "center"},
								TABLE(null, TBODY(null, TR(null, TD({"align": "center", "colspan": "2"}, SPAN(null,"Please try again by giving some meaningful name for the query") )),
								TR(null, TD({"align": "center", "colspan": "2"}, Ok))))
					);
					appendChildNodes(this.box, error);
	        	}
				
				else {
					showElement(getElement('error_box'))
				}
	    	}
	    	else {
	        	var schema = getElement('combo_schema').value;
	            var cube = getElement('combo_cube').value;
	            var params = {'name': getElement('saved_query_name').value, 'query': getElement('query').value, 'cube': cube, 'schema': schema};
	           	var Ok = BUTTON({'type': 'button', 'class': 'button'}, 'Ok');
	        	MochiKit.Signal.connect(Ok, 'onclick', this, 'hide');
	            var request = Ajax.JSON.post('/browser/save_query', params);
	            request.addCallback(function(obj){
	    			var complete = DIV({'id': 'complete', "align": "center", "valign": "center"},
							TABLE(null, TBODY(null, TR(null, TD({"align": "center", "colspan": "2"}, SPAN(null,"Your Query has been saved.") )),
							TR(null, TD(null, Ok))))
					);
	    			swapDOM(getElement('alert_box'), complete)
					
					
	        	});
	        	
	    	}
    	}
    	else {
    		
    		var Ok = BUTTON({'type': 'button', 'class': 'button'}, 'Ok');
        	MochiKit.Signal.connect(Ok, 'onclick', this, 'hide');
    		
            var params = {'query': getElement('query').value,'overwrite':'1'};
            var request = Ajax.JSON.post('/browser/save_query', params);
            request.addCallback(function(obj){
                var complete = DIV({'id': 'complete', "align": "center", "valign": "center"},
						TABLE(null, TBODY(null, TR(null, TD({"align": "center", "colspan": "2"}, SPAN(null,"Your Query has been saved.") )),
						TR(null, TD(null, Ok))))
				);
    			swapDOM(getElement('alert_box'), complete)
            });  
    	}
    }  
}
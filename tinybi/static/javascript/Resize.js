
var ResizableArea = function(ta,grip){
    this.__init__(ta,grip);
}

ResizableArea.prototype = {

    __init__ : function(ta,grip){

        this.textarea = MochiKit.DOM.getElement(ta);
        this.gripper = MochiKit.DOM.getElement(grip)
        this.draggin = false;

        this.evtMouseDn = MochiKit.Signal.connect(this.gripper, 'onmousedown', this, "dragStart");
    },

    __delete__ : function(){
        MochiKit.Signal.disconnect(this.evtMouseDn);
    },

    dragStart : function(evt){
        if (!evt.mouse().button.left)
            return;

        this.offset = elementDimensions(this.textarea).w - evt.mouse().page.x;

        this.evtMouseMv = MochiKit.Signal.connect(document, 'onmousemove', this, "dragUpdate");
        this.evtMouseUp = MochiKit.Signal.connect(document, 'onmouseup', this, "dragStop");
    },

    dragUpdate : function(evt){
        var w = Math.max(10, this.offset + evt.mouse().page.x);
        this.textarea.style.width = w + 'px';
        set_cookie('panewidth',w)
	evt.stop();
    },

    dragStop : function(evt){
        MochiKit.Signal.disconnect(this.evtMouseMv);
        MochiKit.Signal.disconnect(this.evtMouseUp);
        MochiKit.Signal.disconnectAll(document, 'onmousemove', this, "dragUpdate");
        MochiKit.Signal.disconnectAll(document, 'onmouseup', this, "dragStop");
		evt.stop();
    }
}

function ActivateResize(toresize_ele,grip_ele)
{
	new ResizableArea(toresize_ele,grip_ele)
}
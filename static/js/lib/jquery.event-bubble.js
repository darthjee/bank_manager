/*global jQuery, window, Ranking*/
(function ($) {
	window.EventBubble = function(list, ele){
		if (this.constructor != window.EventBubble)
		{
			return new window.EventBubble(list);
		}
		else
		{
			if (list.constructor.toString().indexOf(" Array()") == -1)
				list = [list];
			
			this.watcher = null;
			var self = this;
			$(list).each(function(){
				var param = {element:ele};
				param = $.extend(param,this);
				self.bind(param);
			});
		}
	};
	
	window.EventBubble.prototype.clear = function(){
		if (this.watcher != null)
			window.clearInterval(this.watcher);
		this.watcher = null;
	};
	
	window.EventBubble.prototype.bind = function(param)
	{
		var self = this;
		param = $.extend({
			timeout : 0,
			evt : 'click',
			call : function(){}
		},param);
		$ele = $(param.element);
		
		$ele.bind(param.evt, function(evt, params){
			self.clear();
			var ele = this;
			var evtParam = arguments;
			Array.prototype.unshift.apply(evtParam,[self]);
			self.watcher = window.setTimeout(function (){
				param.call.apply(ele,evtParam);
				self.clear();
			}, param.timeout);
		});
	}
	
	window.EventBubble.prototype.add = function(param, ele){
		var self = this;
		
		if (typeof(param) == "object" && param.constructor == Array)
		{
			var list = param;
			$(list).each(function(){
				var param = {element:ele};
				param = $.extend(param,this);
				self.add(param);
			});
		}
		else{
			if (ele){
				param.element = ele;
			}
			self.bind(param);
		}
		
	}
	
	
	$.fn.eventBubble = function(list, bubble){
		var ele = this;
		
		if (bubble){
			bubble.add(list, ele);
		}
		else{
			bubble = new EventBubble(list, ele);
		}
		return bubble;
	};
	
	
	
	$.fn.bindShowHide = function(options){
		var defopt = {
			show:{callback:function(){}},
			hide:{callback:function(){}},
			timeout:0
		};
		options = $.extend(defopt,options);
		defopt.show.timeout = options.timeout;
		defopt.hide.timeout = options.timeout;
		var show = $.extend(defopt.show,options);
		options.show = $.extend(defopt.show,options.show);
		options.hide = $.extend(defopt.hide,options.hide);
		
		var $this = this;
		var bubble = $this.data('Bubble');
		if (!bubble){
			bubble = $this.eventBubble([
		    {
		    	timeout:options.show.timeout,
		    	evt:'show',
		    	call:function(bubble, evt, params){
		    		var args = arguments;
		    		var $this = $(this);
		    		$this.fadeIn(function(){
		    			$this.trigger('showtrigger', params);
		    			options.show.callback.apply(this, arg);
		    		});
		    	}
		    },
		    {
		    	timeout:options.hide.timeout,
		    	evt:'hide',
		    	call:function(bubble, evt, params){
		    		var args = arguments;
		    		var $this = $(this);
		    		$this.fadeOut(function(){
		    			$this.trigger('hidetrigger', params);
		    			options.hide.callback.apply(this, arg);
		    		});
		    	}
		    }]);
			$this.data('Bubble', bubble)
		}
	}
})(jQuery);
(function ($) {
	$.EventCounter = function(limit, f, caller)
	{
		if (this.constructor != $.EventCounter)
			return new $.EventCounter(limit, f, caller);
		else
		{
			this.limit = limit;
			this.counter = 0;
			this.fn = f;
			this.caller = caller ? caller : this;
		}
	};
	
	$.EventCounter.prototype.count = function(i, caller)
	{
		if (typeof i == "undefined")
			i = 1;
		this.counter += i;
		if (this.counter >= this.limit)
			this.call(caller);
	};
	
	$.EventCounter.prototype.call = function(caller)
	{
		if (typeof caller == "undefined")
			caller = this.caller;
		this.fn.apply(caller);
	};
	
	$.fn.eventCounter = function(limit, f)
	{
		$self = this;
		return new $.EventCounter(limit, f, $self);
	};
	
})(jQuery);
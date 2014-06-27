function JsonToStr(o) {
	if (o === undefined) {
		return "";
	}
	var r = [];
	if (typeof o === "string") return "\"" + o.replace(/([\"\\])/g, "\\$1").replace(/(\n)/g, "\\n").replace(/(\r)/g, "\\r").replace(/(\t)/g, "\\t") + "\"";
	if (typeof o === "object") {
		if (!o.sort) {
			for (var i in o)
				r.push("\"" + i + "\":" + JsonToStr(o[i]));
			if (!!document.all && !/^\n?function\s*toString\(\)\s*\{\n?\s*\[native code\]\n?\s*\}\n?\s*$/.test(o.toString)) {
				r.push("toString:" + o.toString.toString());
			}
			r = "{" + r.join() + "}"
		} else {
			for (var i = 0; i < o.length; i++)
				r.push(JsonToStr(o[i]))
			r = "[" + r.join() + "]";
		}
		return r;
	}
	return o.toString().replace(/\"\:/g, '":""');
}
window.encodeJSON = JSON.stringify||JsonToStr;
window.decodeJSON = JSON.parse||function(d){eval('('+d+')')};

Object.clone = function(sObj){ 
	if(typeof sObj !== "object"){   
		return sObj;   
	}   
	var s = {};   
	if(sObj.constructor == Array){  
		s = [];   
	}   
	for (var i in sObj) {   
		s[i] = Object.clone(sObj[i]);   
	}   
	return s;   
} 

Object.extend = function(tObj,sObj){   
		for(var i in sObj){   
			if(typeof sObj[i] !== "object"){   
				tObj[i] = sObj[i];   
			} else if (sObj[i]&&sObj[i].constructor == Array){   
				tObj[i] = Object.clone(sObj[i]);   
			} else {   
				tObj[i] = tObj[i] || {};   
				Object.extend(tObj[i],sObj[i]);   
			}   
		}   
}  

String.prototype.render = function(context) {
	return this.replace(/{([^{}]+)}/g, function (word) {
		var words=word.slice(1,-1).split('.'),obj=context;
		for (var i=0,l=words.length;i<l;i++){
			obj=obj[words[i]];
			if (obj===undefined) return '';
		}
		return obj
	});
};

$.fn.serializeObject = function() {
	var o={}, a=this.serializeArray();
	$.each(a, function(){
		var value=this.hasOwnProperty('value')?this.value:'';
		if (typeof o[this.name]==="Array") {
			o[this.name].append(value)
		} else 
			(o[this.name]===undefined)?o[this.name]=value:o[this.name]=[o[this.name],value];
	});
	return o;
};

$.fn.error = function () {
	var $this = $(this);
	$this
	.addClass('blank')
	.one('keypress', function () {
		$(this).removeClass('blank');
	})
	.focus();
};

$.fn.captcha = function() {
	var $this = $(this);
	$this.css("max-width", "100%");
	if ($this.is('img')){
		function change(){
			$this.attr("src", "/captcha/");
		}
		change();
		$this.click(change);
	} else if ($this.is('form')) {
		$this.find('img').captcha();
	}
};

$.fn.render = function(data) {
	var $this = $(this), template;
	if (!$this.data("rawtext")){
		template = $this.text();
		$this.data("rawtext", template);
	} else template = $this.data("rawtext");
	$this.text(template.render(data));
};

$.fn.clearForm = function() {
	$(':input', '#'+$(this).attr("id"))  
	 .not(':button, :submit, :reset, :hidden')  
	 .val('')  
	 .removeAttr('checked')  
	 .removeAttr('selected'); 
};

$.fn.formAjaxSubmit = function(config) {
	var $form = $(this), 
		apiUrl = config.apiUrl, verifyFunc = config.verfiy||function(){return true}, callback = config.callback||function(){},
	captcha = $form.find('img[name="captcha"]'), captchaInput;
	if (captcha.length) {
		captcha.captcha();
		captchaInput = $form.find('input[name="captcha"]');
	}
	$form.submit(function(e){
		e.preventDefault();
		if (!verifyFunc()) return false;
		var deferred = apiUrl.post($form.serializeObject());
		deferred.captchaError(function(){
			if (captchaInput) captchaInput.error();
		}).done(function(){
			if (captcha) captcha.captcha();
		});
		callback(deferred);
		return false;
	});
};

(function(){
	function ajax(url, data, method) {
		if (typeof data === 'object') data = encodeJSON(data);
		return $.ajax({
			url: url,
			type: method,
			contentType:"application/json",
			data: data,
			dataType: 'json'
		});
	};
	function Resource(name, _url, type, params) {
		this.type = type?type:'action';
		this.name = name;
		this.noSupport = [];
		this.params = Object.clone(params)||{};
		this._url = (_url||'/api/')+name+'/';
	}
	Resource.prototype.param = function () {
		var obj = {};
		if (arguments.length === 1) {
			obj = arguments[0];
	  } else 
	  	obj[arguments[0]] = arguments[1];
	  typeof obj==='object'&&Object.extend(this.params, obj);
	  return this;
	};
	Resource.prototype.url = function (name) {
		if (this.hasOwnProperty(name)) return this[name];
		return this[name] = new Resource(name, this._url);
	};
	Resource.prototype.id = function (id) {
		return new Resource(id, this._url, 'id');
	};
	methods = ['get', 'post', 'delete', 'patch'];
	for (var i=0;i<methods.length;i++)
		(function(method) {
			Resource.prototype[method] = function (data) {
				var errors = {
						404: "notFound", 
						403: "forbidden", 
						400:"paramError", 
						405:"methodNotAllowed", 
						420:"captchaError",
						200: "ok"
				}, callbacks = {};
				if (this.paramStr===undefined) {
					if (this.type==='raw') {
						this.paramStr = '';
					} else {
						var params = [];
						for (var i in this.params) params.push(i+'='+this.params[i]);
						this.paramStr = '?'+encodeURI(params.join('&'));
					}
				}
				
				var statusActions = {};
				for (var i in errors)
					if (i != 200)
					(function(code){ 
						statusActions[code] = function (data) {
							callbacks[code].fire(decodeJSON(data.responseText));
						}
					})(i);
				
				var self = this,
			  res = ajax(this._url+this.paramStr, data, method).statusCode(statusActions)
			  .done(function(data) {
							callbacks[200].fire(data);
					});
				for (var i in errors) {
					var callback = callbacks[i] = $.Callbacks("once memory");
					res[errors[i]] = callback.add;
				}
				return res;
			}
		})(methods[i]);
	API = {
		url: function (name) {return this[name]?this[name]:this[name] = new Resource(name); },
		raw: function (url) {
			var res = new Resource('', url, 'raw');
			res._url = url;
			return res;
		},
		list: function (config) {
			function adjustPager($btn, url) {
				if (url===null) {
					$btn.hide();
				} else {
					$btn.show().data('url', url);
				}
			}
			function loadData(data) {
				var elements = [];
				adjustPager($next, data.next);
				adjustPager($prev, data.previous);
				$(data.results).each(function(){
					var context = this;
					processData(context);
					elements.push(template.render(context));
				});
				$container.html("");
				$(elements.join('')).appendTo($container);			
			}
			function click() {
				API.raw($(this).data('url')).get().ok(loadData);
			}
			function execute() {
				apiUrl.get().ok(loadData);
			}
			var apiUrl = config.apiUrl, 
				$next = $("#"+config.next), $prev = $("#"+config.prev), $container= $("#"+config.container), 
				processData = config.processData||function(){}, template = config.template||'';
			$next.click(click).hide();
			$prev.click(click).hide();
			execute();
			return execute;
		}
	};
})();

$.validator.setDefaults({
	debug: true,
	onfocusout: false,
	onkeyup: false,
	onclick: false,
	errorPlacement: function(error, element){
		element.error();
	}
});
$("form").submit(function(e){
	e.preventDefault();
	return false;
});
(function($){
$.getUrlParam = function(name){
var reg = new RegExp("(^|&)"+ name +"=([^&]*)(&|$)");
var r = window.location.search.substr(1).match(reg);
if (r!=null) return unescape(r[2]);return null;
}
$.getAnchor = function(){
	return window.location.hash;
}
})(jQuery);
emptyFunc = function(_){return _};
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
window.decodeJSON = JSON.parse||function(d){return Function('return '+d)();};

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
			if (obj===undefined||obj===null) return '';
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

$.fn.clearForm = function() {
	$(':input', '#'+$(this).attr("id"))  
	 .not(':button, :submit, :reset, :hidden')  
	 .val('')  
	 .removeAttr('checked')  
	 .removeAttr('selected')
	 .removeClass('blank')
	 .find('div.alert-login').hide();
};

$.fn.placeError = function(msg){
	if (!this.is('form')) return this;
	this.find('div.alert-login').addClass('visible').html(msg.html&&msg.html()||msg);
	return this;
};

$.fn.errors = function(data) {
	if (!this.is('form')) return this;
	for (var name in data) {
		$("input[name='"+name+"']").error();
		this.placeError(data[name]);
	}
	return this;
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
					if (this.type==='raw') {
						this.paramStr = '';
					} else {
						var params = [];
						for (var i in this.params) params.push(i+'='+this.params[i]);
						this.paramStr = '?'+encodeURI(params.join('&'));
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
				processData = config.processData||emptyFunc, template = config.template||'';
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
		var parent = element;
		while (!parent.is('form')) parent = parent.parent();
		parent.placeError(error);
	}
});
$.validator.addMethod('gt', function(value, element, params){
	if (typeof params==='string'&&params[0]==="#"){
		params = parseFloat($(element.form).find('[name='+params.slice(1)+']').val());
	}
	return this.optional(element)||parseFloat(value)>params;
}, $.validator.format("输入的数值必须大于{0}"));
$.validator.addMethod('lt', function(value, element, params){
	if (typeof params==='string'&&params[0]==="#"){
		params = parseFloat($(element.form).find('[name='+params.slice(1)+']').val());
	}
	return this.optional(element)||parseFloat(value)<params;
}, $.validator.format("输入的数值必须小于{0}"));

$.fn.initForm = function (config) {
	if (!(this.is('form'))) return;
	this.data('callback', config.callback||{});
	this.data('processData', config.processData||emptyFunc);
};

$(function(){
//process forms
	$("form.mese").each(function(){
		function getColClassName(n) {return 'col-sm-'+n;}
		var $form = $(this).addClass('form-horizontal'), isCaptcha = $form.attr("captcha")!==undefined, 
			$inputWidth = parseInt($form.attr("input-width"))||9,
			$inputCol = getColClassName($inputWidth), $labelCol = getColClassName(12-$inputWidth),
			$inputs = $form.find("input, select, textarea").not(":submit"),
			$submits = $form.find("input[type=submit]"),
			submitsCount = $submits.length;
			
		if (isCaptcha) {
			var $captchaInput = $('<input>').addClass('form-control').attr({name: 'captcha', type: 'text'});
			$('<div/>')
			.addClass($inputCol)
			.append($('<div class="col-sm-4"></div>').addClass('no-padding').append($captchaInput))
			.append($("<div/>").addClass("col-sm-8").append($("<img title='看不清？点击换一张'/>").addClass("captcha")))
			.wrap($("<div/>").addClass("form-group")).parent()
			.prepend($("<label>验证码</div>").addClass("control-label "+$labelCol))
			.insertBefore($submits.first());
			$form.captcha();
		}
		
		$('<div/>')
		.addClass('alert alert-danger alert-login')
		.wrap('<div class="form-group"></div>')
		.insertBefore($submits.first());
		
		var rules = {};
		
		$inputs.each(function(){
			var $input = $(this).addClass('form-control'), $data = $input.data(),
			validator = {};
			$(($input.attr("validator")||"").split(" ")).each(function(){
				if (this.indexOf(':')>=0) {
					var _ = this.split(':'), val = isNaN(parseFloat(_[1]))?_[1]:parseFloat(_[1]);
					validator[_[0]] = val;
				} else if (this.length) {
					validator[this] = true;
				}
			});
			rules[$input.attr('name')] = validator;
			$input
			.wrap($("<div/>").addClass($inputCol))
			.parent()
			.wrap($("<div/>").addClass("form-group"))
			.before($("<label>{label}</div>".render($data)).addClass("control-label "+$labelCol));
			
		});
		$form.validate({rules: rules});
		$submits.wrapAll('<div class="form-group"/>').each(function(){
			var $submit = $(this);
			$submit.addClass("btn btn-login").wrap($("<div/>").addClass(getColClassName(Math.round(12/submitsCount))));
		});
		
		if (submitsCount===1) {
			$form.submit(function(){
				$form.validate();
				if (!$form.valid()) return false;
				var func = $form.data('processData')||emptyFunc, data = $form.serializeObject(), 
					callback = $form.data('callback')||emptyFunc, method = $form.attr('method')||'post', action = $form.attr('action');
				func(data), $submit = $form.find('input[type=submit]');
				$submit.button('loading');
				API.raw(action)[method](data)
				.ok(function(data){
					$form.clearForm();
					callback(data);
					$submit.button('reset');
				})
				.paramError(function(data){
					$form.errors(data);
					$submit.button('reset');
				})
				.captchaError(function(){
					$captchaInput.error();
					$submit.button('reset');
				});
			});
		} else {
			$submits.click(function(){
				var $this = $(this), action = $this.attr('action'), method = $form.attr('method')||'post';
				$form.validate();
				if (!$form.valid()) return false;
				var func = $form.data('processData')||emptyFunc, data = $form.serializeObject(), 
					callback = $form.data('callback');
				callback = callback?callback[$this.attr('name')]:emptyFunc;
				func(data);
				$this.button('loading');
				API.raw(action)[method](data)
				.ok(function(data){
					$form.clearForm();
					callback(data);
					$this.button('reset');
				})
				.paramError(function(data){
					$form.errors(data);
					$this.button('reset');
				})
				.captchaError(function(){
					$captchaInput.error();
					$this.button('reset');
				});
			});		
		}
		$(".btn-mese2014, .btn-login").attr('data-loading-text', '请稍候...');
	});

	var allows = [];
	function logic(date) {
		if (date.getDayOfYear()===(new Date()).getDayOfYear()) {
			this.setOptions({minTime: 0});
		} else this.setOptions({minTime: undefined});
	}
	for (var i=8;i<24;i++) allows.push(i+':00');
	$("input.time").mask("99:99");
	$("input.datetime").datetimepicker({
		format: 'Y-m-d H:i:s',
		minDate: 0,
		lang: 'ch',
		allowTimes: allows,
		showSeconds: true
	});
});

window.tips = function(text) {
	toastr.success(text, "提示", {timeOut:3000});
};

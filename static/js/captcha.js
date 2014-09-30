$.fn.captcha = function() {
	var $this = $(this);
	function change(){
		$this.attr("src", "/captcha/");
	}
	change();
	$this.click(change);
}

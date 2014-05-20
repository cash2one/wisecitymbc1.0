
function loadList(p_argu) {
	var argu = p_argu.substr(1);
	if (argu!=null) {
		$.ajax({
			type:"GET",
			url:"/api/passages/?type="+argu,
			success: function(data){
				$.each(data.results, function(){
					$(p_argu+'C').append('<div class="panel panel-default"><div class="panel-heading"><h4 class="'+
					'panel-title"><a data-toggle="collapse" data-parent="#'+argu+'C" href="#ps'+
					+this.id+'">'+this.title+'</a>'+'<span class="pull-right">'+this.created_time+'by@'+this.author.profile.display_name+
					'</span></h4></div></div>')
					})
			}
		})
	}
}


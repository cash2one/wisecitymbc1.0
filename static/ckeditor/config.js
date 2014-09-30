CKEDITOR.editorConfig = function( config )
{
	config.toolbar=[[ 'Bold', 'Italic', '-', 'NumberedList', 'BulletedList', 'Font', 'FontSize', 'img'],
	['NumberedList','BulletedList','-','Outdent','Indent','Blockquote'],
    ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
	['TextColor','BGColor'],
	['Undo', 'Redo'],
	];
	config.removePlugins = 'elementspath';
	config.resize_enabled = false;
};

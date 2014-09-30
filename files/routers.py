import views

routes = (
	(r'files/public', views.PublicFileAPIViewSet),
	(r'files/private(/(?P<field_name>[^/]+))?', views.PrivateFileAPIViewSet),
)

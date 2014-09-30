import views

routes = (
	(r'users', views.UserAPIViewSet),
	(r'companies/$', views.companies),
)

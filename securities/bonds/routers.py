import views

routes = (
	(r'bonds(/(?P<bond_pk>\d+))?/shares', views.ShareAPIViewSet),	
	(r'bonds', views.BondAPIViewSet),
)

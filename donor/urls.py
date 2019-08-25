from django.urls import path, include
from . import views
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

router = routers.DefaultRouter()
router.register('donors', views.DonorView)
router.register('users', views.UserView)
router.register('recipients', views.RecipientView)
router.register('stores', views.StoreView)
router.register('purchases', views.PurchaseView)

urlpatterns = [
	path('login/donor/', views.DonorLogin.as_view()),
    path('login/recipient/', views.RecipientLogin.as_view()),
    path('reimburse/', views.Reimburse.as_view()),
    path('scan/', views.ScanPurchase.as_view()),
    path('new-purchase/', views.NewPurchase.as_view()),
    path('purchases/', views.GetPurchases.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns.append(path('', include(router.urls)))

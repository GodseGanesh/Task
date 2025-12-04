from django.urls import path
from .views import (
    OrderListCreateAPIView, 
    OrderRetrieveUpdateAPIView,
    MenuGroupListCreateAPIView,
    MenuGroupDetailAPIView,
    CategoryListCreateAPIView,
    CategoryDetailAPIView,
    ItemListCreateAPIView,
    ItemDetailAPIView,
    PaymentListCreateAPIView,
    PaymentDetailAPIView,
    OrderPaymentListCreateAPIView
    )

urlpatterns = [
    
     # Menu Group
    path("menu-groups/", MenuGroupListCreateAPIView.as_view(), name="menu-group-list"),
    path("menu-groups/<int:id>/", MenuGroupDetailAPIView.as_view(), name="menu-group-detail"),

    # Category
    path("categories/", CategoryListCreateAPIView.as_view(), name="category-list"),
    path("categories/<int:id>/", CategoryDetailAPIView.as_view(), name="category-detail"),

    # Item
    path("items/", ItemListCreateAPIView.as_view(), name="item-list"),
    path("items/<int:id>/", ItemDetailAPIView.as_view(), name="item-detail"),

    # Orders
    path("orders/", OrderListCreateAPIView.as_view(), name="order-list"),
    path("orders/<int:id>/", OrderRetrieveUpdateAPIView.as_view(), name="order-detail"),

    path("payments/", PaymentListCreateAPIView.as_view(), name="payment-list"),
    path("payments/<int:id>/", PaymentDetailAPIView.as_view(), name="payment-detail"),

    path("orders/<int:order_id>/payments/", OrderPaymentListCreateAPIView.as_view(), name="order-payments")
]

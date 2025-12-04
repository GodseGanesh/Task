from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from api.utils.response import ResponseHandler
from .models import Order, MenuGroup, Category, Item, Payment
from .serializers import OrderSerializer, MenuGroupSerializer, CategorySerializer, ItemSerializer, PaymentSerializer
import logging
from django.core.cache import cache

logger = logging.getLogger("api")


# ---------------- ORDER ----------------
class OrderListCreateAPIView(ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            Order.objects.all()
            .prefetch_related("items__item__category__menu_group", "payments")
            .order_by("-created_at")
        )

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        formatted, status = ResponseHandler.success(
            message="Orders retrieved successfully",
            data=response.data
        )
        return Response(formatted, status=status)

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response(*ResponseHandler.success(
                message="Order created successfully",
                data=response.data,
                status_code=201
            ))
        except Exception as e:
            logger.error(f"Order creation failed: {e}")
            return Response(*ResponseHandler.error(
                message="Order creation failed",
                error_detail=str(e),
                status_code=400
            ))

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(f"Order created successfully: ID={instance.id}")


class OrderRetrieveUpdateAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    def get_queryset(self):
        return Order.objects.all().prefetch_related(
            "items__item__category__menu_group", "payments"
        )

    def retrieve(self, request, *args, **kwargs):
        cache_key = f"order:{self.kwargs['id']}"
        cached = cache.get(cache_key)

        if cached:
            logger.debug(f"CACHE HIT → Order {self.kwargs['id']}")
            return Response(*ResponseHandler.success(
                message="Order retrieved from cache",
                data=cached
            ))

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60)

        return Response(*ResponseHandler.success(
            message="Order retrieved successfully",
            data=response.data
        ))

    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete(f"order:{instance.id}")
        logger.info(f"Order updated → cache invalidated: {instance.id}")

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response(*ResponseHandler.success(
            message="Order updated successfully",
            data=response.data
        ))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        cache.delete(f"order:{instance.id}")
        super().destroy(request, *args, **kwargs)
        return Response(*ResponseHandler.success(
            message="Order deleted successfully",
            data=None
        ))


# ---------------- MENU GROUP ----------------
class MenuGroupListCreateAPIView(ListCreateAPIView):
    queryset = MenuGroup.objects.all().order_by("name")
    serializer_class = MenuGroupSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        cache.delete("items:list")  # cascade cache invalidation
        return Response(*ResponseHandler.success(
            message="Menu group created successfully",
            data=response.data,
            status_code=201
        ))

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(f"Menu group created: {instance.name}")


class MenuGroupDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = MenuGroup.objects.all()
    serializer_class = MenuGroupSerializer
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        cache.delete("items:list")
        return Response(*ResponseHandler.success(
            message="Menu group updated successfully",
            data=response.data
        ))

    def destroy(self, request, *args, **kwargs):
        cache.delete("items:list")
        super().destroy(request, *args, **kwargs)
        return Response(*ResponseHandler.success(
            message="Menu group deleted successfully"
        ))


# ---------------- CATEGORY ----------------
class CategoryListCreateAPIView(ListCreateAPIView):
    queryset = Category.objects.select_related("menu_group").all()
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        cache.delete("items:list")  # keep item cache fresh
        return Response(*ResponseHandler.success(
            message="Category created successfully",
            data=response.data,
            status_code=201
        ))


class CategoryDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        cache.delete("items:list")
        return Response(*ResponseHandler.success(
            message="Category updated successfully",
            data=response.data
        ))

    def destroy(self, request, *args, **kwargs):
        cache.delete("items:list")
        super().destroy(request, *args, **kwargs)
        return Response(*ResponseHandler.success(
            message="Category deleted successfully"
        ))


# ---------------- ITEM ----------------
class ItemListCreateAPIView(ListCreateAPIView):
    queryset = Item.objects.select_related("category__menu_group").all()
    serializer_class = ItemSerializer

    def get_queryset(self):
        cache_key = "items:list"
        items = cache.get(cache_key)

        if not items:
            items = list(super().get_queryset())
            cache.set(cache_key, items, timeout=300)
            logger.debug("CACHE MISS → Items loaded")
        else:
            logger.debug("CACHE HIT → Items")

        return items

    def perform_create(self, serializer):
        instance = serializer.save()
        cache.delete("items:list")
        logger.info(f"Item created → cache invalidated: {instance.id}")


class ItemDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = "id"


# ---------------- PAYMENT ----------------
class PaymentListCreateAPIView(ListCreateAPIView):
    queryset = Payment.objects.select_related("order").order_by("-created_at")
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]


class PaymentDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"


class OrderPaymentListCreateAPIView(ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Payment.objects.filter(order_id=self.kwargs["order_id"]).order_by("-created_at")

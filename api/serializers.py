from rest_framework import serializers
from .models import MenuGroup, Category, Item, Order, OrderItem, Payment
import logging

logger = logging.getLogger("api")


class MenuGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuGroup
        fields = ["id", "name", "created_at", "updated_at"]

    def validate_name(self, value):
        logger.debug(f"Validating MenuGroup name: {value}")
        if MenuGroup.objects.filter(name__iexact=value).exists():
            logger.warning(f"Duplicate MenuGroup name attempted: {value}")
            raise serializers.ValidationError("Menu group already exists.")
        return value





class CategorySerializer(serializers.ModelSerializer):
    menu_group = MenuGroupSerializer(read_only=True)
    menu_group_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "menu_group", "menu_group_id"]

    def validate(self, data):
        logger.debug(f"Validating category data: {data}")
        if not MenuGroup.objects.filter(id=data["menu_group_id"]).exists():
            logger.error(f"Invalid menu_group_id: {data['menu_group_id']}")
            raise serializers.ValidationError("Invalid menu_group_id — Menu group does not exist.")
        return data






class ItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Item
        fields = ["id", "name", "pricing", "category", "category_id"]

    def validate_pricing(self, value):
        logger.debug(f"Validating pricing: {value}")
        if not isinstance(value, dict):
            logger.error("Invalid pricing structure type.")
            raise serializers.ValidationError("Pricing must be a valid JSON object.")

        if len(value.keys()) == 0:
            logger.error("Pricing contains no values.")
            raise serializers.ValidationError("Item must have at least one price option.")

        for k, v in value.items():
            if not isinstance(v, (int, float)) or v <= 0:
                logger.warning(f"Invalid price detected: {k} -> {v}")
                raise serializers.ValidationError(f"Price for size '{k}' must be a positive number.")

        return value

    def validate(self, data):
        logger.debug(f"Validating Item: {data}")
        if not Category.objects.filter(id=data["category_id"]).exists():
            logger.error("Category ID does not exist.")
            raise serializers.ValidationError("Invalid category_id — Category does not exist.")
        return data





class OrderItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    item_id = serializers.IntegerField(write_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "item", "item_id", "size", "quantity", "price", "total_price"]

    def validate(self, data):
        logger.debug(f"Validating OrderItem: {data}")

        item_id = data.get("item_id")
        size = data.get("size")
        quantity = data.get("quantity")

        if not Item.objects.filter(id=item_id).exists():
            raise serializers.ValidationError("Item does not exist.")

        item = Item.objects.get(id=item_id)

        if size not in item.pricing:
            raise serializers.ValidationError(
                f"Invalid size '{size}'. Available: {list(item.pricing.keys())}"
            )

        if quantity <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")

        # instead of setting total_price, compute price only
        data["price"] = item.pricing[size]
        return data

    def create(self, validated_data):
        # calculate using model logic, DO NOT set total_price manually
        return OrderItem.objects.create(**validated_data)
  
    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Flatten Item Details
        rep["item_id"] = instance.item.id
        rep["name"] = instance.item.name

        # Remove nested item blob
        rep.pop("item", None)

        return rep






class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order_id",
            "method",
            "status",
            "amount_due",
            "total_paid",
            "tips",
            "discount",
            "created_at"
        ]

    def validate(self, data):
        logger.debug(f"Validating payment data: {data}")

        if data.get("total_paid") < 0:
            raise serializers.ValidationError("total_paid cannot be negative.")

        if data.get("amount_due") < 0:
            raise serializers.ValidationError("amount_due cannot be negative.")

        return data

    def create(self, validated_data):
        logger.debug(f"Creating payment with validated data: {validated_data}")
        return Payment.objects.create(**validated_data)



class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=True)
    payments = PaymentSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_date",
            "status",
            "total_amount",
            "items",
            "payments",
            "created_at",
        ]

    def validate(self, data):
        items = self.initial_data.get("items")

        logger.debug(f"Validating Order items: {items}")

        if not items or not isinstance(items, list) or len(items) == 0:
            logger.error("Order must contain at least one item.")
            raise serializers.ValidationError({"items": "Order must contain at least one item."})

        return data

    def create(self, validated_data):
        items_data = self.initial_data.get("items")

        order = Order.objects.create(
            order_date=validated_data.get("order_date"),
            status=validated_data.get("status")
        )

        logger.info(f"Order created with ID={order.id}")

        for item_data in items_data:
            serializer = OrderItemSerializer(data=item_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(order=order)

        return order

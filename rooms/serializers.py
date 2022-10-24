from rest_framework.serializers import ModelSerializer, SerializerMethodField
from categories.serializers import CategorySerializer
from users.serializers import TinyUserSerializer
from .models import Room, Amenity


class AmenitySerializer(ModelSerializer):
    class Meta:
        model = Amenity
        fields = "__all__"


class RoomListSerializer(ModelSerializer):
    rating = SerializerMethodField()

    class Meta:
        model = Room
        fields = ("pk", "name", "country", "city", "price", "rating")

    def get_rating(self, room):
        return room.rating()


class RoomDetailSerializer(ModelSerializer):
    owner = TinyUserSerializer(read_only=True)
    amenities = AmenitySerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = SerializerMethodField()

    class Meta:
        model = Room
        fields = "__all__"

    def get_rating(self, room):
        return room.rating()

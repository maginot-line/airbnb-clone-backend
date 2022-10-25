from django.utils import timezone
from rest_framework.serializers import DateField, ModelSerializer, ValidationError
from .models import Booking


class PublicBookingSerializer(ModelSerializer):
    class Meta:
        model = Booking
        fields = ("pk", "check_in", "check_out", "experience_time", "guests")


class CreateRoomBookingSerializer(ModelSerializer):
    check_in = DateField()
    check_out = DateField()

    class Meta:
        model = Booking
        fields = ("check_in", "check_out", "guests")

    def validate_check_in(self, value):
        now = timezone.localtime(timezone.now()).date()
        if now > value:
            raise ValidationError("Can't book in the past!")
        return value

    def validate_check_out(self, value):
        now = timezone.localtime(timezone.now()).date()
        if now > value:
            raise ValidationError("Can't book in the past!")
        return value

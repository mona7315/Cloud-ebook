from rest_framework.serializers import ModelSerializer
from .models import Room, Room_type
class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class RoomTypeSerializer(ModelSerializer):
    class Meta:
        model = Room_type
        fields = '__all__'
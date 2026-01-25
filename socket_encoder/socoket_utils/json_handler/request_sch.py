# scheme for the request from the client

from rest_framework import serializers
from socket_encoder.socoket_utils.massege_serialzer import MessageSerializer


class ClassRoomConnectSerializer(serializers.Serializer):
  classroom_id = serializers.IntegerField()



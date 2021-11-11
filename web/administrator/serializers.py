from rest_framework import serializers
from .models import *

class PostPointSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = '__all__'


class ObserveLogSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Observe
        fields = '__all__'

    def create(self, validated_data):
        print('#####')
        print(validated_data)

       



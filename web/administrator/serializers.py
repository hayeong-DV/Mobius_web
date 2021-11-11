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

    def create(self, record_data):
        print('#####')
        print(record_data)



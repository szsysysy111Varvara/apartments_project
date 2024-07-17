from django.contrib.auth.models import User, Group
from django.db import IntegrityError
from rest_framework import serializers

class UserRegistrationSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True, required=False)
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'groups']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):
        try:
            groups_data = validated_data.pop('groups', [])
            user = User.objects.create_user(**validated_data)
            for group in groups_data:
                user.groups.add(group)
            return user
        except IntegrityError:
            raise serializers.ValidationError("User with this email already exists.")


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

    def create(self, validated_data):
        return Group.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance
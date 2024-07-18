from django.contrib.auth.models import User, Group
from rest_framework import serializers
from users.models import Profile


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=[('Renter', 'Renter'), ('Landlord', 'Landlord')], write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password',  'user_type')

    def create(self, validated_data):
        user_type = validated_data.pop('user_type', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']

        )
        Profile.objects.create(user=user, user_type=user_type)
        return user

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

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'user_type']
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from .models import User
from apps.tenants.serializers import MunicipalitySerializer

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    municipality_detail = MunicipalitySerializer(source='municipality', read_only=True)
    is_merchant = serializers.BooleanField(read_only=True)
    is_admin = serializers.BooleanField(read_only=True)

    def get_full_name(self, obj):
        return obj.get_full_name()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'phone', 'avatar', 'cover', 'municipality', 'municipality_detail',
            'bio', 'location', 'birth_date', 'gender', 'is_verified', 'is_active',
            'is_merchant', 'is_admin', 'date_joined', 'last_login',
            'notification_preferences', 'language', 'theme',
            'facebook', 'instagram', 'twitter', 'linkedin'
        ]
        read_only_fields = ['date_joined', 'last_login', 'is_verified']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 
                  'last_name', 'phone', 'municipality']
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Las contraseÃ±as no coinciden'})
        return data
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('El nombre de usuario ya existe')
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('El correo ya esta registrado')
        return value
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            # Update login stats
            user.login_count += 1
            user.last_login_ip = self.context.get('request').META.get('REMOTE_ADDR')
            user.save(update_fields=['login_count', 'last_login_ip'])
            return {'user': user}
        raise serializers.ValidationError('Credenciales invalidas')

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar', 'cover', 'bio', 
                  'location', 'birth_date', 'gender', 'language', 'theme',
                  'facebook', 'instagram', 'twitter', 'linkedin']
    
    def validate_phone(self, value):
        if value and User.objects.filter(phone=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError('Este telefono ya esta registrado')
        return value

class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Las contraseÃ±as no coinciden'})
        return data

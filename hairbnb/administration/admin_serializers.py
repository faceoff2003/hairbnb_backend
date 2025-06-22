from rest_framework import serializers
from hairbnb.models import TblUser, TblRole


class AdminUserActionSerializer(serializers.Serializer):
    """Serializer pour les actions admin sur les utilisateurs"""
    user_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['deactivate', 'activate', 'change_role'])
    new_role_id = serializers.IntegerField(required=False)

    def validate(self, data):
        if data['action'] == 'change_role' and 'new_role_id' not in data:
            raise serializers.ValidationError("new_role_id requis pour change_role")

        if data.get('new_role_id'):
            if not TblRole.objects.filter(idTblRole=data['new_role_id']).exists():
                raise serializers.ValidationError("Rôle inexistant")

        return data


class AdminUserListSerializer(serializers.ModelSerializer):
    """Serializer pour lister les utilisateurs (vue admin)"""
    role_name = serializers.CharField(source='get_role', read_only=True)
    type_name = serializers.CharField(source='get_type', read_only=True)

    class Meta:
        model = TblUser
        fields = ['idTblUser', 'uuid', 'nom', 'prenom', 'email', 'is_active', 'role_name', 'type_name']
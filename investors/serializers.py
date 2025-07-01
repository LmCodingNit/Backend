from rest_framework import serializers
from .models import InvestorProfile
from startups.serializers import TagSerializer, StartupListSerializer

class InvestorProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    interested_in_tags = TagSerializer(many=True, read_only=True)
    liked_startups = StartupListSerializer(many=True, read_only=True)

    class Meta:
        model = InvestorProfile
        fields = ('user', 'company_name', 'interested_in_tags', 'liked_startups')
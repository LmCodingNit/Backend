from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import InvestorProfile
from .serializers import InvestorProfileSerializer
from startups.models import Startup
from startups.serializers import StartupListSerializer

class InvestorProfileViewSet(viewsets.GenericViewSet):
    queryset = InvestorProfile.objects.all()
    serializer_class = InvestorProfileSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get', 'put'])
    def me(self, request):
        """
        Get or update the profile for the current logged-in investor.
        """
        profile, created = InvestorProfile.objects.get_or_create(user=request.user)
        if request.method == 'GET':
            serializer = InvestorProfileSerializer(profile)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = InvestorProfileSerializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='recommendations')
    def get_recommendations(self, request):
        """
        Get startup recommendations based on investor's interested tags.
        """
        profile = get_object_or_404(InvestorProfile, user=request.user)
        interested_tags = profile.interested_in_tags.all()
        liked_startup_ids = profile.liked_startups.values_list('id', flat=True)

        if not interested_tags.exists():
            # If no interests, recommend the newest startups they haven't liked
            recommended_startups = Startup.objects.exclude(id__in=liked_startup_ids)[:10]
        else:
            # Recommend startups with matching tags that they haven't liked
            recommended_startups = Startup.objects.filter(
                tags__in=interested_tags
            ).exclude(
                id__in=liked_startup_ids
            ).distinct()[:10]

        serializer = StartupListSerializer(recommended_startups, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='like')
    def like_startup(self, request, pk=None):
        """
        Like a startup. The 'pk' in the URL is the startup's ID.
        """
        profile = get_object_or_404(InvestorProfile, user=request.user)
        startup_to_like = get_object_or_404(Startup, pk=pk)
        
        profile.liked_startups.add(startup_to_like)
        return Response({'status': 'startup liked'}, status=status.HTTP_200_OK)
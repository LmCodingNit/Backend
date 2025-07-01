from rest_framework import serializers
from .models import Tag, Startup, StartupDocument, AnalysisReport

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')

class StartupDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StartupDocument
        fields = ('id', 'document', 'description', 'uploaded_at')

class StartupListSerializer(serializers.ModelSerializer):
    """Serializer for list view - less detail."""
    tags = TagSerializer(many=True, read_only=True)
    founder = serializers.StringRelatedField()

    class Meta:
        model = Startup
        fields = ('id', 'name', 'founder', 'description_short', 'tags', 'founding_year')

class StartupDetailSerializer(serializers.ModelSerializer):
    """Serializer for detail view - more detail."""
    tags = TagSerializer(many=True, read_only=True)
    documents = StartupDocumentSerializer(many=True, read_only=True)
    founder = serializers.StringRelatedField() # Show username, not ID
    # Show how many investors liked this startup
    likes_count = serializers.IntegerField(source='liked_by_investors.count', read_only=True)

    class Meta:
        model = Startup
        fields = (
            'id', 'name', 'founder', 'description_short', 'description_long',
            'website_url', 'founding_year', 'tags', 'documents', 'likes_count'
        )


class AnalysisReportSerializer(serializers.ModelSerializer):
    # Make the user field read-only as it will be set from the request context
    user = serializers.StringRelatedField(read_only=True)
    
    # Make the 'initial_query' write-only. The user POSTs this but doesn't need it back in the list view.
    initial_query_input = serializers.CharField(write_only=True, source='initial_query')

    class Meta:
        model = AnalysisReport
        fields = [
            'id', 
            'user', 
            'status', 
            'report_content_md',
            'initial_query_input', # The field for POSTing data
            'created_at', 
            'updated_at',
            'error_message'
        ]
        read_only_fields = [
            'id', 
            'user', 
            'status', 
            'report_content_md',
            'created_at', 
            'updated_at',
            'error_message'
        ]

class AnalysisReportListSerializer(serializers.ModelSerializer):
    """
    A lightweight serializer for listing reports.
    It does NOT include the full report content for performance.
    """
    # Create a truncated version of the initial query for display in a list
    short_query = serializers.SerializerMethodField()

    class Meta:
        model = AnalysisReport
        fields = [
            'id', 
            'status', 
            'short_query',
            'created_at', 
            'error_message'
        ]
    
    def get_short_query(self, obj):
        # Truncate the initial query to the first 75 characters
        return (obj.initial_query[:75] + '...') if len(obj.initial_query) > 75 else obj.initial_query

class AnalysisReportDetailSerializer(serializers.ModelSerializer):
    """
    A detailed serializer for retrieving a single report.
    Includes the full markdown content.
    """
    user = serializers.StringRelatedField(read_only=True)
    initial_query_input = serializers.CharField(write_only=True, source='initial_query')

    class Meta:
        model = AnalysisReport
        fields = [
            'id', 
            'user', 
            'status', 
            'initial_query', # Show the full query in detail view
            'report_content_md',
            'initial_query_input',
            'created_at', 
            'updated_at',
            'error_message'
        ]
        read_only_fields = [
            'id', 
            'user', 
            'status', 
            'initial_query',
            'report_content_md',
            'created_at', 
            'updated_at',
            'error_message'
        ]
import json
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Startup, Tag, AnalysisReport
from .serializers import StartupListSerializer, StartupDetailSerializer, TagSerializer, AnalysisReportSerializer , AnalysisReportListSerializer, AnalysisReportDetailSerializer
from permissions import IsOwnerOrReadOnly
from .tasks import generate_startup_description_task, generate_analysis_report_task
import markdown2
from weasyprint import HTML


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing tags.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

class StartupViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing startup instances.
    """
    queryset = Startup.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return StartupListSerializer
        return StartupDetailSerializer

    def perform_create(self, serializer):
        # Automatically assign the logged-in user as the founder
        serializer.save(founder=self.request.user)

    @action(detail=True, methods=['post'])
    def generate_description(self, request, pk=None):
        """
        An endpoint to trigger the AI description generation.
        """
        startup = self.get_object()
        
        # Check permissions again to be safe
        if startup.founder != request.user:
            return Response(
                {'error': 'You do not have permission to perform this action.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Get key points from the request to guide the AI
        prompt_data = request.data.get('prompt_data', '')
        if not prompt_data:
            return Response(
                {'error': 'prompt_data is required to generate a description.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Trigger the background task
        generate_startup_description_task.delay(startup.id, prompt_data)

        return Response(
            {'status': 'Description generation has started in the background.'},
            status=status.HTTP_202_ACCEPTED
        )
    
class AnalysisReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for creating and viewing Analysis Reports.
    - POST /api/reports/ -> Creates a new report and starts analysis.
    - GET /api/reports/ -> Lists all reports for the logged-in user.
    - GET /api/reports/{id}/ -> Retrieves a single detailed report.
    - GET /api/reports/{id}/download/ -> Downloads the report as a PDF.
    """
    # queryset and permission_classes remain the same
    queryset = AnalysisReport.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Dynamically selects the serializer based on the action.
        - Use lightweight serializer for 'list' action.
        - Use detailed serializer for all other actions ('retrieve', 'create', etc.).
        """
        if self.action == 'list':
            return AnalysisReportListSerializer
        return AnalysisReportDetailSerializer # Default for retrieve, create, update

    def get_queryset(self):
        """
        This is the key security feature. It ensures a user can ONLY ever see
        their own reports, never anyone else's.
        """
        return AnalysisReport.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        """
        This is called on POST. It correctly assigns the user
        and triggers the background task.
        """
        report = serializer.save(user=self.request.user, status=AnalysisReport.Status.PENDING)
        print(f"Report created: {report.id}")
#        generate_analysis_report_task.delay(report.id)
        generate_analysis_report_task(report.id)


    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Download the report PDF after converting Markdown to styled PDF.
        """
        report = self.get_object()

        if report.status != AnalysisReport.Status.COMPLETED:
            return Response(
                {"error": "Report is not completed yet."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # If the field is already a dict, use it directly
            if isinstance(report.report_content_md, dict):
                markdown_string = report.report_content_md.get("response", "")
            else:
                # Otherwise, it's a JSON string and needs decoding
                parsed = json.loads(report.report_content_md)
                markdown_string = parsed.get("response", "")

            html_content = markdown2.markdown(markdown_string)

            styled_html = f"""
<html>
<head>
    <meta charset="utf-8">
    <style>
        @page {{
            margin: 2cm;
        }}
        body {{
            font-family: "Segoe UI", "Helvetica Neue", sans-serif;
            line-height: 1.7;
            color: #2c3e50;
            background-color: #fff;
            padding: 0;
            margin: 0;
        }}
        h1, h2, h3, h4 {{
            color: #1a237e;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        p {{
            margin: 12px 0;
            font-size: 14px;
        }}
        ul, ol {{
            padding-left: 25px;
            margin-bottom: 20px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        a {{
            color: #0d47a1;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        code {{
            background-color: #f5f5f5;
            padding: 2px 4px;
            font-family: monospace;
            border-radius: 4px;
        }}
        pre {{
            background: #f0f0f0;
            padding: 12px;
            overflow-x: auto;
            border-left: 4px solid #2196f3;
            font-family: Consolas, monospace;
            border-radius: 6px;
        }}
        blockquote {{
            border-left: 4px solid #90caf9;
            margin: 20px 0;
            padding: 10px 20px;
            background: #f9f9f9;
            font-style: italic;
            color: #555;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""


            pdf = HTML(string=styled_html).write_pdf()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="startup_report_{report.id}.pdf"'
            return response

        except Exception as e:
            return Response(
                {"error": f"Failed to generate PDF: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

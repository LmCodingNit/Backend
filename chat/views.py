import requests
from django.conf import settings
from rest_framework import viewsets, status, serializers # Added serializers for ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer, MessageInputSerializer

class ChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling chat sessions and messages.
    This version is adapted to work with an external AI agent that
    manages its own context via a `user_id`.
    """
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Users can only see their own chat sessions."""
        return ChatSession.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Creates a new ChatSession for the user. This is called on POST /api/chat/sessions/.
        We will also handle the first message if provided.
        """
        prompt = self.request.data.get('prompt')
        if not prompt:
            # If no prompt is provided, just create an empty session
            serializer.save(user=self.request.user)
            return

        # If a prompt is provided, create the session AND handle the first message exchange
        session = serializer.save(user=self.request.user)
        self._handle_send_message(session, prompt)

    @action(detail=True, methods=['post'], url_path='send-message')
    def send_message(self, request, pk=None):
        """
        Handles sending a new message to an existing chat session.
        Endpoint: POST /api/chat/sessions/{id}/send-message/
        """
        session = self.get_object() # Ensures the session exists and user has permission
        input_serializer = MessageInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        prompt = input_serializer.validated_data['prompt']

        ai_response_message = self._handle_send_message(session, prompt)
        
        # Return the AI's response to the frontend
        response_serializer = ChatMessageSerializer(ai_response_message)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def _handle_send_message(self, session, prompt):
        """
        Private helper method to encapsulate the logic of sending a message
        and getting a response from the AI agent.

        This method is now corrected to match the agent's expected API.
        """
        # 1. Save the user's message to our database. This step is unchanged.
        ChatMessage.objects.create(session=session, role=ChatMessage.Role.USER, content=prompt)

        # 2. Call the external AI agent with the required payload.
        #    We no longer need to build a history object.
        try:
            # CORRECTED PAYLOAD: Send only user_id and the current prompt.
            payload = {
                "user_id": str(self.request.user.id),
                "prompt": prompt
            }

            response = requests.post(
                settings.CHATBOT_AGENT_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            response.raise_for_status()

            # The agent's response format is not specified, so we assume it's JSON
            # with a key like 'response' or 'answer'. We'll check for common ones.
            response_data = response.json()
            ai_content = response_data.get('response', response_data.get('answer', 'Sorry, I received an unexpected response.'))

        except requests.exceptions.RequestException as e:
            # Handle network errors, timeouts, etc.
            ai_content = f"Sorry, I'm having trouble connecting right now. (Error: {e})"
        except ValueError:
            # Handle cases where the response is not valid JSON
            ai_content = "Sorry, I received a response I couldn't understand from my brain."
        
        # 3. Save the AI's response to our database. This step is unchanged.
        ai_message = ChatMessage.objects.create(
            session=session,
            role=ChatMessage.Role.AI,
            content=ai_content
        )
        return ai_message
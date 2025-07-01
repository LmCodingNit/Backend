import time
from celery import shared_task
from .models import Startup,AnalysisReport
from django.conf import settings
import requests

# You would import your actual AI service here
# from your_ai_module import AIEngine

#@shared_task(bind=True) # `bind=True` to get task instance
def generate_analysis_report_task( report_id):
    """
    A background task that calls the external AI agent to generate a report.
    
    """
    print(f"Generating analysis report for report_id: {report_id}")
    try:
        report = AnalysisReport.objects.get(id=report_id)
        report.status = AnalysisReport.Status.PROCESSING
        report.save()

        # Prepare the request to the AI agent
        agent_url = settings.AI_AGENT_URL
        payload = {"query": report.initial_query}
        headers = {"Content-Type": "application/json"}

        # Make the blocking HTTP call within the async task
        response = requests.post(agent_url, json=payload, headers=headers, timeout=30000) # 5-min timeout
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes

        # Success! Update the report.
        report.report_content_md = response.text # Assuming agent returns raw markdown
        report.status = AnalysisReport.Status.COMPLETED
        report.save()

        return f"Successfully generated report for ID: {report_id}"

    except requests.exceptions.RequestException as exc:
        # Handle network errors, timeouts, etc.
        report.status = AnalysisReport.Status.FAILED
        report.error_message = f"Network error communicating with AI Agent: {exc}"
        report.save()
        # Retry the task if it's a transient network issue
        raise self.retry(exc=exc)
        
    except AnalysisReport.DoesNotExist:
        # This shouldn't happen, but good to handle
        print(f"CRITICAL: AnalysisReport with ID {report_id} not found in task.")
        return f"Error: Report with ID {report_id} not found."
        
    except Exception as exc:
        # Handle any other unexpected errors
        report.status = AnalysisReport.Status.FAILED
        report.error_message = f"An unexpected error occurred: {exc}"
        report.save()
        # You might not want to retry for unknown errors
        return f"Failed report generation for ID {report_id} due to unexpected error."


# Note: No need for 'time' import anymore

@shared_task(bind=True, max_retries=3, default_retry_delay=180) # `bind=True` to get task instance
def generate_startup_description_task(self, startup_id, prompt_data):
    """
    A background task to generate a startup description by calling the external AI agent.
    """
    try:
        startup = Startup.objects.get(id=startup_id)
        print(f"Starting AI description generation for {startup.name}...")
        
        # --- REAL AI CALL ---
        # Replace the mock call with a real HTTP request.
        
        agent_url = settings.DESCRIPTION_AGENT_URL
        payload = {"query": prompt_data} # This matches your agent's expected input
        
        response = requests.post(
            agent_url, 
            json=payload, 
            headers={"Content-Type": "application/json"},
            timeout=90 # 90-second timeout is reasonable for a description generation task
        )
        
        # This will raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()
        
        # Parse the JSON response and get the content from the 'response' key
        response_data = response.json()
        generated_text = response_data.get('response')

        if not generated_text:
            # Handle case where the agent returns a 200 OK but with no content
            raise ValueError("AI agent returned an empty response.")
        
        # --- END REAL AI CALL ---
        
        startup.description_long = generated_text
        startup.save()
        
        print(f"Successfully generated and saved description for {startup.name}.")
        return f"Success for startup_id {startup_id}"

    except requests.exceptions.RequestException as exc:
        # Handle network-related errors (e.g., agent is down, DNS issues)
        print(f"Network error calling description agent for startup {startup_id}: {exc}")
        # Retry the task, as this might be a temporary issue
        raise self.retry(exc=exc)

    except ValueError as exc:
        # Handle errors in parsing the response (e.g., not valid JSON, or empty response key)
        print(f"Invalid response from agent for startup {startup_id}: {exc}")
        # We probably should not retry this, as the agent might be broken.
        return f"Failed due to invalid response for startup_id {startup_id}."
        
    except Startup.DoesNotExist:
        # This case is already handled well
        print(f"Error: Startup with ID {startup_id} not found.")
        return f"Error: Startup with ID {startup_id} not found."
        
    except Exception as exc:
        # A general catch-all for any other unexpected errors
        print(f"An unexpected error occurred for startup_id {startup_id}: {exc}")
        return f"An unexpected error occurred for startup_id {startup_id}: {exc}"
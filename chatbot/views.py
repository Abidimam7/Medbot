from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.timezone import now
from .models import Conversation
import google.generativeai as genai
import os
import json
import logging
import pytesseract
import fitz  # PyMuPDF
from PIL import Image, ImageOps
from dotenv import load_dotenv
import nltk
import time



# Load environment variables
load_dotenv()

# Initialize API keys
GENAI_API_KEY = os.getenv('API_KEY')

# Configure Generative AI
genai.configure(api_key=GENAI_API_KEY)

# Configure logger
logger = logging.getLogger(__name__)

# Specify Tesseract-OCR path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# --------------- Views --------------- #

def index(request):
    """
    Redirect users to the appropriate page based on authentication status.
    """
    return redirect('chatbot_page' if request.user.is_authenticated else 'login')

@login_required
def chatbot_page(request):
    """
    Render the chatbot page and include chat histories for the user.
    """
    try:
        conversations = Conversation.objects.filter(user=request.user).order_by("-timestamp")
        chat_histories = [{"id": c.id, "messages": c.messages} for c in conversations]
    except Exception as e:
        logger.error(f"Error fetching chat histories: {str(e)}")
        chat_histories = []

    return render(request, 'chatbot/chatbot.html', {"chat_histories": chat_histories})

@csrf_exempt
@login_required
def chatbot_response(request):
    """
    Handle user messages for medical diagnosis assistance using Gemini Pro API.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        # Parse the request body
        body = json.loads(request.body)
        user_message = body.get("message", "").strip()

        # Ensure the message is not empty
        if not user_message:
            return JsonResponse({"error": "Message cannot be empty"}, status=400)

        # Retrieve or create a medical conversation for the user
        conversation = Conversation.objects.filter(user=request.user).first()
        if not conversation:
            conversation = Conversation.objects.create(user=request.user)

        # Dynamically update the title if not manually renamed
        if (not conversation.title or conversation.title == "New Conversation") and not conversation.title_manually_renamed:
            conversation.title = generate_title_from_message(user_message)
            conversation.save()  # Save the updated title

        # Add the user message to the conversation history
        conversation.messages.append({"role": "user", "content": user_message})

        # Prepare the prompt for Gemini Pro API
        conversation_history = "\n".join(
            f"{msg['role']}: {msg['content']}" for msg in conversation.messages
        )

        prompt = f"""
        You are a medical assistant. Your role is to:
        ask users name age gender and past medical history first then start asking about there health related questions
        1. Identify symptoms mentioned in the user's input.
        2. Ask follow-up questions one by one to gather more details about their condition.
        3. Suggest possible conditions based on the symptoms.
        4. Recommend a relevant specialist to consult.
        4.Suggested medications (if safe without prescription)
		Diet suggestions based on the diagnosis


        User Input: {user_message}

        Conversation History: {conversation_history}

        Respond with:
        - A follow-up question if more details are needed.
        - A possible condition and specialist recommendation if sufficient information is available.
        """

        # Generate a response using the Gemini Pro API
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        bot_message = response.text.strip()

        # Save the bot response in the conversation
        conversation.messages.append({"role": "assistant", "content": bot_message})
        conversation.save()

        return JsonResponse({"response": bot_message, "title": conversation.title})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        logger.error(f"Error in chatbot_response: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@login_required
def rename_chat(request, chat_id):
    """
    Handle the renaming of a chat conversation.
    """
    try:
        # Find the conversation by ID
        conversation = Conversation.objects.get(id=chat_id, user=request.user)
        
        if request.method == 'PUT':
            data = json.loads(request.body)
            new_title = data.get('title', '').strip()

            if new_title:
                # Mark the conversation as manually renamed
                conversation.title = new_title
                conversation.title_manually_renamed = True
                conversation.save()
                return JsonResponse({"success": True, "message": "Chat renamed successfully"})
            else:
                return JsonResponse({"error": "New title cannot be empty"}, status=400)

        else:
            return JsonResponse({"error": "Invalid request method"}, status=405)

    except Conversation.DoesNotExist:
        return JsonResponse({"error": "Conversation not found"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def generate_title_from_message(user_message):
    words = user_message.split()
    meaningful_words = [word.capitalize() for word in words if len(word) > 2]
    title = " ".join(meaningful_words[:5]) or "New Conversation"
    return title




@login_required
def delete_conversation(request, conversation_id):

    try:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        conversation.delete()
        return JsonResponse({"message": "Conversation deleted successfully"}, status=200)
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def chat_history(request):
    """
    Retrieve all chat histories for the logged-in user.
    """
    try:
        conversations = Conversation.objects.filter(user=request.user).order_by("-timestamp")
        chat_histories = [{"id": c.id, "messages": c.messages, "title": c.title, "timestamp": c.timestamp} for c in conversations]
        return JsonResponse({"histories": chat_histories}, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



@csrf_exempt
@login_required
def start_new_chat(request):
    """
    Start a new chat by clearing the current session's conversation.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)

    try:
        # Create a new conversation for the user
        Conversation.objects.create(user=request.user)
        return JsonResponse({"message": "New chat started successfully."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# Preprocess image for better OCR
def preprocess_image(image):
    try:
        # Convert to grayscale
        image = ImageOps.grayscale(image)

        # Resize for better clarity using LANCZOS resampling
        base_width = 1024
        w_percent = (base_width / float(image.size[0]))
        h_size = int((float(image.size[1]) * float(w_percent)))
        image = image.resize((base_width, h_size), Image.Resampling.LANCZOS)

        # Apply binary thresholding
        image = image.point(lambda x: 0 if x < 128 else 255, '1')
        return image
    except Exception as e:
        raise ValueError(f"Error in image preprocessing: {str(e)}")

# Process image with OCR
def process_image(file):
    try:
        image = Image.open(file)
        preprocessed_image = preprocess_image(image)
        text = pytesseract.image_to_string(preprocessed_image)
        return text
    except Exception as e:
        raise ValueError(f"Error processing image: {str(e)}")

# Process PDF
def process_pdf(file):
    try:
        doc = fitz.open(file)
        text = ''
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        raise ValueError(f"Error processing PDF: {str(e)}")

import logging

# Summarize the extracted text
def summarize_text(text):
    if not text.strip():
        logger.warning("No text available for summarization.")
        return "No text available for summarization."

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(f"Summarize the following text: {text}")
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error during summarization: {str(e)}")
        return f"Error during summarization: {str(e)}"




@csrf_exempt
@login_required
def upload_file(request):
    """
    Handle file uploads, process them, summarize content, and store in conversation.
    """
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            uploaded_file = request.FILES['file']
            file_name = uploaded_file.name
            file_extension = os.path.splitext(file_name)[1].lower()
            fs = FileSystemStorage()

            # Save the file and get the URL
            new_filename = f"file_{int(time.time())}{file_extension}"
            filename = fs.save(new_filename, uploaded_file)
            file_url = fs.url(filename)

            # Process file and summarize
            summary = "Unsupported file format for summarization."
            if file_extension in ['.jpg', '.jpeg', '.png']:
                text = process_image(fs.path(filename))
                summary = summarize_text(text)
            elif file_extension == '.pdf':
                text = process_pdf(fs.path(filename))
                summary = summarize_text(text)

            # Save file summary in the conversation
            conversation = Conversation.objects.filter(user=request.user).first()
            if not conversation:
                conversation = Conversation.objects.create(user=request.user)

            # Add file upload details to the conversation
            conversation.messages.append({
                "role": "user",
                "content": f"Uploaded file: {file_name}",
                "type": "file",
                "file_url": file_url
            })
            conversation.messages.append({
                "role": "assistant",
                "content": summary,
                "type": "text"
            })
            conversation.save()

            return JsonResponse({
                'success': True,
                'file_url': file_url,
                'summary': summary
            })

        except Exception as e:
            logger.error(f"File upload error: {str(e)}")
            return JsonResponse({'success': False, 'error': f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({'success': False, 'error': 'No file uploaded or invalid request.'}, status=400)


@csrf_exempt
@login_required
def get_conversation(request, conversation_id):
    """
    Fetch a specific conversation based on conversation_id.
    """
    try:
        conversation = Conversation.objects.get(id=conversation_id, user=request.user)

        if not conversation.messages:
            return JsonResponse({"error": "No messages found for this conversation."}, status=400)

        messages = [
            {"role": msg["role"], "content": msg["content"], "type": msg.get("type", "text"), "file_url": msg.get("file_url", "")}
            for msg in conversation.messages
        ]

        return JsonResponse({"messages": messages}, status=200)

    except Conversation.DoesNotExist:
        return JsonResponse({"error": "Conversation not found."}, status=404)
    except Exception as e:
        logger.error(f"Error fetching conversation: {str(e)}")
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)



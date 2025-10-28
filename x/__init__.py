"""
Compatibility layer for imports from 'x' package.
Redirects to mvc_view structure.
"""
from mvc_view.models.image_service import app as image_service_app
from mvc_view.models import image_final_consumer
from mvc_view.controllers import image_agent
from mvc_view.views import gradio_ui

# Create a mock module object for image_service with app attribute
class ImageServiceModule:
    def __init__(self):
        self.app = image_service_app

image_service = ImageServiceModule()

__all__ = ['image_service', 'image_agent', 'image_final_consumer', 'gradio_ui']

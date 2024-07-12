from rest_framework.decorators import permission_classes, api_view, parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from PIL import Image, ImageDraw, ImageOps
from django.http import HttpResponse
import io

@api_view(['POST'])
@parser_classes([MultiPartParser])
@permission_classes([AllowAny])
def remove_bg(request):
    image = request.FILES.get('image')
    background_image_path = 'image.png'  # Path to the background image
    
    if not image:
        return HttpResponse({"error": "Image file must be provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Open the uploaded image file and apply EXIF orientation
        img = Image.open(image)
        img = ImageOps.exif_transpose(img)
        
        # Convert to RGBA if it isn't already
        img = img.convert("RGBA")
        
        # Create a new image with rounded corners
        size = img.size
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), size], radius=100, fill=255)
        
        # Apply the mask to the original image
        output = Image.new('RGBA', size, (0, 0, 0, 0))
        output.paste(img, (0, 0), mask)
        
        # Open the background image
        background = Image.open(background_image_path)
        
        # Resize the processed image to fit within the background image while maintaining aspect ratio
        output.thumbnail((1080//2, 1080//2), Image.LANCZOS)
        
        # Calculate the position to center the processed image on the background
        bg_width, bg_height = background.size
        img_width, img_height = output.size
        x = (bg_width - img_width) // 2
        y = (bg_height - img_height) // 2
        
        # Paste the processed image onto the background image
        background.paste(output, (x, y), output)
        
        # Save the resulting image to a BytesIO object
        final_output = io.BytesIO()
        background.save(final_output, format='PNG')
        final_output.seek(0)
        
        # Return the result as an image file
        response = HttpResponse(final_output.read(), content_type='image/png')
        response['Content-Disposition'] = 'attachment; filename="output.png"'
        return response
    
    except Exception as e:
        return HttpResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

"""
gunicorn bg_remover.wsgi  -t 60 --keep-alive 1000
"""
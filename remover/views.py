from rest_framework.decorators import permission_classes, api_view, parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from rembg import remove
from PIL import Image
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
        # Open the uploaded image file
        before = Image.open(image)
        
        # Remove the background
        after = remove(before)
        
        # Open the background image
        background = Image.open(background_image_path)
        
        # Resize the processed image to fit within the background image while maintaining aspect ratio
        after.thumbnail((1080//2, 1080//2), Image.LANCZOS)
        
        # Calculate the position to center the processed image on the background
        bg_width, bg_height = background.size
        img_width, img_height = after.size
        x = (bg_width - img_width) // 2
        y = (bg_height - img_height) // 2
        
        # Paste the processed image onto the background image
        background.paste(after, (x, y), after)
        
        # Save the resulting image to a BytesIO object
        output = io.BytesIO()
        background.save(output, format='PNG')
        output.seek(0)
        
        # Return the result as an image file
        response = HttpResponse(output.read(), content_type='image/png')
        response['Content-Disposition'] = 'attachment; filename="output.png"'
        return response
    
    except Exception as e:
        return HttpResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

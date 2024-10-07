import os
from PIL import Image
import io

def save_image(image_file):
    # Si deseas guardar en sistema de archivos
    # file_path = os.path.join('static/uploads', image_file.filename)
    # image_file.save(file_path)
    
    # Si guardas en la base de datos como binario
    return image_file.read()  # Guardar la imagen como binario


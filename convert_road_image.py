import base64

with open('Gemini_Generated_Image_sxl3jusxl3jusxl3.png', 'rb') as f:
    encoded = base64.b64encode(f.read()).decode('utf-8')
    print(encoded)

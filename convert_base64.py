import base64

with open('assets/Road Safety Commission - Website Banner - 850x425 pixles - Resources Page - FINAL FILE.png', 'rb') as f:
    encoded = base64.b64encode(f.read()).decode('utf-8')
    print(encoded)

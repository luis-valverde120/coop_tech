import requests
from bs4 import BeautifulSoup

def obtener_titulares_noticias():
    """
    Realiza scraping a la sección de noticias de Diario El Norte
    y retorna los titulares principales.
    """
    url = "https://elnorte.ec/noticias/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # Asegurar codificación utf-8 para tildes y caracteres especiales
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        titulares = []
        # Generalmente los titulares están en h2 o h3
        for tag in soup.find_all(['h2', 'h3']):
            texto = tag.get_text(strip=True)
            if texto and len(texto) > 15:
                titulares.append(texto)
                
        # Limitar a los 15 titulares más recientes
        return titulares[:15]
    except Exception as e:
        print(f"Error extrayendo noticias: {e}")
        return []

if __name__ == "__main__":
    tits = obtener_titulares_noticias()
    for t in tits:
        print("-", t)

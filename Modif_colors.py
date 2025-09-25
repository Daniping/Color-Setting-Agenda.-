import os
import os.path
import datetime
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Les mots-clés et les couleurs de votre calendrier
MOTS_CLES_COULEURS = {
    'sport': '9',  # Bleu foncé
    'rdv': '10',   # Vert
    'important': '3' # Violet
}

def get_google_calendar_service():
    """
    Configure la connexion à l'API Google Agenda en utilisant le secret.
    """
    try:
        creds_info = json.loads(os.environ.get("GCP_CREDENTIALS"))
        creds = service_account.Credentials.from_service_account_info(creds_info, scopes=['https://www.googleapis.com/auth/calendar'])
    except Exception as e:
        print(f"Erreur lors de la lecture des identifiants : {e}")
        return None
    
    return build('calendar', 'v3', credentials=creds)

def main():
    """
    Vérifie les événements récents et change leur couleur.
    """
    service = get_google_calendar_service()
    if not service:
        return
    
    # Récupérer les événements des 10 dernières minutes
    now = datetime.datetime.utcnow().isoformat() + 'Z'  
    ten_minutes_ago = (datetime.datetime.utcnow() - datetime.timedelta(minutes=10)).isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=ten_minutes_ago,
        timeMax=now,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    if not events:
        print("Aucun événement récent trouvé.")
        return
        
    for event in events:
        summary = event.get('summary', '').lower()
        event_id = event.get('id')
        current_color_id = event.get('colorId')
        
        for keyword, new_color in MOTS_CLES_COULEURS.items():
            if keyword in summary:
                if current_color_id != new_color:
                    print(f"Mise à jour de l'événement '{summary}' avec la couleur '{new_color}'.")
                    event['colorId'] = new_color
                    service.events().update(
                        calendarId='primary',
                        eventId=event_id,
                        body=event
                    ).execute()
                break # Arrêter après avoir trouvé le premier mot-clé

if __name__ == '__main__':
    main()

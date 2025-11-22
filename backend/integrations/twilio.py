import os
from twilio.rest import Client


def create_call():
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    client = Client(account_sid, auth_token)
    
    twiml = """<Response>
              <Say voice="alice" language="es-ES">Hola abuelo, recuerda tomar tu dosis de 500mg de paracetamol.</Say>
              <Gather input="speech" language="es-ES" action="https://webhook.site/2aa03dd3-f1b5-4bdd-97a9-08379c8822d4">
                <Say voice="alice" language="es-ES">
                  Si ya la tomaste, di "sí".
                </Say>
              </Gather>
           </Response>"""
    
    call = client.calls.create(
        from_='+19895752358',
        to='+56979745451',
        twiml=twiml
    )
    
    return call.sid


if __name__ == "__main__":
    create_call()

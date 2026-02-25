from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        payload = json.loads(post_data)

        # Verificar si el evento es un pago exitoso
        if payload.get('type') == 'checkout.session.completed':
            session = payload['data']['object']
            customer_email = session.get('customer_details', {}).get('email')
            
            print(f"💰 ¡VENTA DETECTADA! Cliente: {customer_email}")
            
            # Aquí Felix-Z enviaría el producto/instrucciones
            # (Podemos conectar con el script de gmail_outreach)
            
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'success'}).encode())

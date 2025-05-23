#type: ignore
import os
import pika
import ssl
import json
import logging
from urllib.parse import urlparse
from django.conf import settings

logger = logging.getLogger(__name__)

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        
    def connect(self):
        """Connect to CloudAMQP"""
        try:
            rabbitmq_url = os.getenv('CLOUDAMQP_URL')
            if not rabbitmq_url:
                raise ValueError("CLOUDAMQP_URL environment variable not set")
            
            # Parse the CloudAMQP URL
            url = urlparse(rabbitmq_url)
            
            # Create SSL context for secure connection
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Connection parameters
            connection_params = pika.ConnectionParameters(
                host=url.hostname or 'localhost',
                port=url.port or 5671,
                virtual_host=url.path[1:] if url.path else '/',
                credentials=pika.PlainCredentials(url.username or 'guest', url.password or 'guest'),
                ssl_options=pika.SSLOptions(context),
                heartbeat=30,
                connection_attempts=3,
                retry_delay=5
            )
            
            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()
            
            # Declare the queue (create if doesn't exist)
            self.channel.queue_declare(queue='low_stock_notifications', durable=True)
            
            logger.info("Connected to CloudAMQP successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to CloudAMQP: {e}")
            return False
    
    def send_low_stock_notification(self, inventory_data):
        """Send low stock notification message"""
        try:
            if not self.connection or self.connection.is_closed:
                if not self.connect():
                    return False
            
            # Prepare message
            message = {
                'type': 'low_stock_alert',
                'inventory_id': inventory_data['inventory_id'],
                'product_name': inventory_data['product_name'],
                'store_name': inventory_data['store_name'],
                'current_quantity': inventory_data['current_quantity'],
                'threshold': inventory_data['threshold'],
                'store_id': inventory_data['store_id'],
                'company_id': inventory_data['company_id'],
                'timestamp': inventory_data.get('timestamp')
            }
            
            # Send message to queue
            
            self.channel.basic_publish(
                exchange='',
                routing_key='low_stock_notifications',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Low stock notification sent for product: {inventory_data['product_name']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False
    
    def close(self):
        """Close connection"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
        except Exception as e:
            logger.error(f"Error closing connection: {e}")

# Global instance
rabbitmq_client = RabbitMQClient()
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
        """Connect to CloudAMQP with improved SSL handling"""
        try:
            rabbitmq_url = os.getenv('CLOUDAMQP_URL')
            if not rabbitmq_url:
                raise ValueError("CLOUDAMQP_URL environment variable not set")
            
            # Parse the CloudAMQP URL
            url = urlparse(rabbitmq_url)
            
            # Create SSL context with more permissive settings for cloud deployment
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Additional SSL options for better compatibility
            context.set_ciphers('DEFAULT@SECLEVEL=1')
            
            # Connection parameters with retry and timeout settings
            connection_params = pika.ConnectionParameters(
                host=url.hostname,
                port=url.port or 5671,
                virtual_host=url.path[1:] if url.path else '/',
                credentials=pika.PlainCredentials(url.username, url.password),
                ssl_options=pika.SSLOptions(context),
                heartbeat=600,  # Increased heartbeat for cloud deployment
                blocked_connection_timeout=300,
                connection_attempts=5,  # More retry attempts
                retry_delay=2,
                socket_timeout=10
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
    
    def send_low_stock_notification(self, inventory_data, max_retries=3):
        """Send low stock notification message with retry logic"""
        for attempt in range(max_retries):
            try:
                # Ensure we have a fresh connection
                if not self.connection or self.connection.is_closed:
                    if not self.connect():
                        logger.error(f"Failed to connect on attempt {attempt + 1}")
                        continue
                
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
                
                logger.info(f"Low stock notification sent for product: {inventory_data['product_name']} (attempt {attempt + 1})")
                return True
                
            except (pika.exceptions.ConnectionClosed, 
                    pika.exceptions.StreamLostError, 
                    ssl.SSLEOFError) as e:
                logger.warning(f"Connection lost on attempt {attempt + 1}: {e}")
                self.close()  # Close the broken connection
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    logger.error(f"Failed to send notification after {max_retries} attempts: {e}")
                    return False
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    continue
                else:
                    return False
        
        return False
    
    def close(self):
        """Close connection safely"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
        except Exception as e:
            logger.error(f"Error closing connection: {e}")

# Global instance
rabbitmq_client = RabbitMQClient()
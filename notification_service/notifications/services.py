#type: ignore
import os
import pika
import ssl
import json
import logging
import requests
from urllib.parse import urlparse
from django.core.mail import send_mail
from django.template import Template, Context
from django.conf import settings
from django.utils import timezone
from .models import NotificationTemplate, NotificationLog

logger = logging.getLogger(__name__)

class NotificationService:
    
    def __init__(self):
        self.user_service_url = os.getenv('USER_SERVICE_URL', 'http://localhost:8001')
    
    def get_users_for_notification(self, company_id, store_id):
        """Get users who should receive low stock notifications"""
        try:
            # Call user management service to get ALL users
            response = requests.get(
                f"{self.user_service_url}/users/",
                timeout=10
            )
            print(self.user_service_url, company_id, store_id)
            
            if response.status_code == 200:
                all_users = response.json()
                # Filter users client-side based on company_id and role
                relevant_users = []
                for user in all_users:
                    user_company_id = str(user.get('company_id', ''))
                    user_role = user.get('role', '').lower()
                    user_store = user.get('assigned_store')
                    
                    # Check if user belongs to the same company
                    if user_company_id == str(company_id):
                        # Include admins and super_admins from any store in the company
                        if user_role in ['admin', 'super_admin']:
                            relevant_users.append(user)
                        # Include stock_manager only if assigned to this specific store
                        elif user_role == 'stock_manager' and str(user_store) == str(store_id):
                            relevant_users.append(user)
                
                logger.info(f"Found {len(relevant_users)} relevant users for company {company_id}, store {store_id}")
                return relevant_users
            else:
                logger.error(f"Failed to fetch users: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching users: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return []
    
    def send_low_stock_email(self, recipient_email, product_name, store_name, 
                           current_quantity, threshold, metadata=None):
        """Send low stock email notification"""
        try:
            # Get or create email template
            template = NotificationTemplate.objects.filter(
                type='low_stock', 
                is_active=True
            ).first()
            
            if not template:
                template = self.create_default_low_stock_template()
            
            # Prepare template context
            context = Context({
                'product_name': product_name,
                'store_name': store_name,
                'current_quantity': current_quantity,
                'threshold': threshold,
                'recipient_email': recipient_email
            })
            
            # Render templates
            subject_template = Template(template.subject)
            html_template = Template(template.html_body)
            text_template = Template(template.text_body)
            
            subject = subject_template.render(context)
            html_body = html_template.render(context)
            text_body = text_template.render(context)
            
            # Create notification log
            notification_log = NotificationLog.objects.create(
                recipient_email=recipient_email,
                subject=subject,
                message_body=html_body,
                metadata=metadata or {}
            )
            
            # Send email
            send_mail(
                subject=subject,
                message=text_body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[recipient_email],
                html_message=html_body,
                fail_silently=False
            )
            
            # Update log as sent
            notification_log.status = 'sent'
            notification_log.sent_at = timezone.now()
            notification_log.save()
            
            logger.info(f"Low stock email sent to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {e}")
            
            # Update log with error
            if 'notification_log' in locals():
                notification_log.status = 'failed'
                notification_log.error_message = str(e)
                notification_log.save()
            
            return False
    
    def create_default_low_stock_template(self):
        """Create default low stock email template"""
        template = NotificationTemplate.objects.create(
            name="Default Low Stock Alert",
            type="low_stock",
            subject="🚨 Low Stock Alert: {{ product_name }}",
            html_body="""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #d32f2f; margin-top: 0;">🚨 Low Stock Alert</h2>
                    <p>Dear Team,</p>
                    <p>The following product is running low on stock and needs immediate attention:</p>
                    
                    <div style="background-color: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px 0; font-weight: bold; color: #495057;">Product:</td>
                                <td style="padding: 8px 0; color: #212529;">{{ product_name }}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: bold; color: #495057;">Store:</td>
                                <td style="padding: 8px 0; color: #212529;">{{ store_name }}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: bold; color: #495057;">Current Quantity:</td>
                                <td style="padding: 8px 0; color: #d32f2f; font-weight: bold;">{{ current_quantity }}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; font-weight: bold; color: #495057;">Alert Threshold:</td>
                                <td style="padding: 8px 0; color: #495057;">{{ threshold }}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 0; color: #1976d2;"><strong>Action Required:</strong> Please restock this item as soon as possible to avoid stockouts and potential sales loss.</p>
                    </div>
                    
                    <p style="margin-top: 30px;">Best regards,<br>
                    <strong>NgEdease Inventory Management System</strong></p>
                </div>
            </body>
            </html>
            """,
            text_body="""
🚨 LOW STOCK ALERT

Dear Team,

The following product is running low on stock:

Product: {{ product_name }}
Store: {{ store_name }}
Current Quantity: {{ current_quantity }}
Alert Threshold: {{ threshold }}

ACTION REQUIRED: Please restock this item as soon as possible to avoid stockouts.

Best regards,
NgEdease Inventory Management System
            """
        )
        return template

class RabbitMQConsumer:
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.notification_service = NotificationService()
    
    def connect(self):
        """Connect to CloudAMQP"""
        try:
            rabbitmq_url = os.getenv('CLOUDAMQP_URL')
            print(rabbitmq_url)
            if not rabbitmq_url:
                raise ValueError("CLOUDAMQP_URL environment variable not set")
            
            # Parse URL
            url = urlparse(rabbitmq_url)
            
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Connection parameters
            connection_params = pika.ConnectionParameters(
                host=url.hostname,
                port=url.port or 5671,
                virtual_host=url.path[1:] if url.path else '/',
                credentials=pika.PlainCredentials(url.username, url.password),
                ssl_options=pika.SSLOptions(context),
                heartbeat=30,
                connection_attempts=3,
                retry_delay=5
            )
            
            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue='low_stock_notifications', durable=True)
            
            logger.info("Connected to CloudAMQP successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to CloudAMQP: {e}")
            return False
    
    def process_low_stock_message(self, ch, method, properties, body):
        """Process incoming low stock notification"""
        try:
            print('processing message')
            message = json.loads(body)
            logger.info(f"Processing message: {message}")
            
            # Validate message
            required_fields = ['product_name', 'store_name', 'current_quantity', 'threshold', 'company_id', 'store_id']
            if not all(field in message for field in required_fields):
                logger.error(f"Invalid message format: {message}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return
            
            # Get users to notify
            users = self.notification_service.get_users_for_notification(
                message['company_id'],
                message['store_id']
            )
            
            if not users:
                logger.warning(f"No users found for company {message['company_id']}, store {message['store_id']}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            # Send email to each user
            success_count = 0
            for user in users:
                user_email = user.get('email')
                if not user_email:
                    logger.warning(f"User {user.get('id')} has no email address")
                    continue
                    
                success = self.notification_service.send_low_stock_email(
                    recipient_email=user_email,
                    product_name=message['product_name'],
                    store_name=message['store_name'],
                    current_quantity=message['current_quantity'],
                    threshold=message['threshold'],
                    metadata={
                        'inventory_id': message.get('inventory_id'),
                        'store_id': message['store_id'],
                        'company_id': message['company_id'],
                        'user_id': user.get('id'),
                        'user_role': user.get('role'),
                        'timestamp': message.get('timestamp')
                    }
                )
                
                if success:
                    success_count += 1
                    logger.info(f"Notification sent to {user_email} ({user.get('role')})")
                else:
                    logger.error(f"Failed to send notification to {user_email}")
            
            logger.info(f"Processed notification: {success_count}/{len(users)} emails sent successfully")
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Requeue for retry
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start_consuming(self):
        """Start consuming messages"""
        if not self.connect():
            logger.error("Failed to connect to RabbitMQ")
            return
            
        try:
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue='low_stock_notifications',
                on_message_callback=self.process_low_stock_message
            )
            
            logger.info("Starting to consume messages from CloudAMQP...")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.channel.stop_consuming()
            self.close()
        except Exception as e:
            logger.error(f"Consumer error: {e}")
            self.close()
    
    def close(self):
        """Close connection"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
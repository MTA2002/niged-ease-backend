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
            subject="🚨 Low Stock Alert: {{ product_name }} - {{ store_name }}",
            html_body="""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Low Stock Alert</title>
                <style>
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f4f4f4;
                    }
                    .email-container {
                        background-color: #ffffff;
                        border-radius: 10px;
                        padding: 40px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        border-top: 4px solid #f44336;
                    }
                    .header {
                        text-align: center;
                        margin-bottom: 30px;
                    }
                    .logo {
                        font-size: 28px;
                        font-weight: bold;
                        color: #f44336;
                        margin-bottom: 10px;
                    }
                    .title {
                        font-size: 24px;
                        color: #2c3e50;
                        margin-bottom: 20px;
                    }
                    .alert-badge {
                        background: linear-gradient(135deg, #ff5722 0%, #f44336 100%);
                        color: white;
                        padding: 8px 16px;
                        border-radius: 20px;
                        font-size: 14px;
                        font-weight: bold;
                        display: inline-block;
                        margin-bottom: 20px;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                    }
                    .greeting {
                        font-size: 16px;
                        color: #555;
                        margin-bottom: 25px;
                    }
                    .product-info {
                        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
                        border-radius: 10px;
                        padding: 30px;
                        margin: 30px 0;
                        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.2);
                        color: white;
                    }
                    .product-name {
                        font-size: 24px;
                        font-weight: bold;
                        margin-bottom: 20px;
                        text-align: center;
                        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                    }
                    .info-grid {
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 20px;
                        margin-top: 20px;
                    }
                    .info-item {
                        background-color: rgba(255, 255, 255, 0.1);
                        padding: 15px;
                        border-radius: 8px;
                        text-align: center;
                        backdrop-filter: blur(10px);
                    }
                    .info-label {
                        font-size: 12px;
                        opacity: 0.9;
                        margin-bottom: 5px;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                    }
                    .info-value {
                        font-size: 20px;
                        font-weight: bold;
                    }
                    .quantity-critical {
                        font-size: 28px !important;
                        color: #ffeb3b;
                        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
                    }
                    .action-section {
                        background-color: #fff3e0;
                        border-left: 4px solid #ff9800;
                        padding: 20px;
                        margin: 25px 0;
                        border-radius: 5px;
                    }
                    .action-title {
                        color: #e65100;
                        margin-top: 0;
                        font-size: 18px;
                        display: flex;
                        align-items: center;
                        gap: 10px;
                    }
                    .action-list {
                        margin: 15px 0;
                        padding-left: 20px;
                    }
                    .action-list li {
                        margin: 10px 0;
                        color: #bf360c;
                        font-weight: 500;
                    }
                    .urgency-meter {
                        background-color: #ffebee;
                        border-radius: 10px;
                        padding: 20px;
                        margin: 20px 0;
                        text-align: center;
                        border: 2px solid #ffcdd2;
                    }
                    .urgency-title {
                        color: #c62828;
                        font-size: 16px;
                        font-weight: bold;
                        margin-bottom: 10px;
                    }
                    .urgency-bar {
                        width: 100%;
                        height: 10px;
                        background-color: #ffcdd2;
                        border-radius: 5px;
                        overflow: hidden;
                        margin: 10px 0;
                    }
                    .urgency-fill {
                        height: 100%;
                        background: linear-gradient(90deg, #ff5722, #f44336);
                        width: 85%;
                        border-radius: 5px;
                    }
                    .footer {
                        text-align: center;
                        margin-top: 40px;
                        padding-top: 20px;
                        border-top: 1px solid #eee;
                        color: #777;
                        font-size: 14px;
                    }
                    .support {
                        background-color: #e8f5e8;
                        border-radius: 5px;
                        padding: 15px;
                        margin: 20px 0;
                        text-align: center;
                    }
                    .support a {
                        color: #4CAF50;
                        text-decoration: none;
                    }
                    .contact-info {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 20px;
                        border-radius: 8px;
                        margin: 20px 0;
                        text-align: center;
                    }
                    .contact-title {
                        font-size: 16px;
                        margin-bottom: 10px;
                        opacity: 0.9;
                    }
                    .contact-details {
                        font-weight: bold;
                    }
                    @media (max-width: 600px) {
                        .email-container {
                            padding: 20px;
                        }
                        .info-grid {
                            grid-template-columns: 1fr;
                            gap: 10px;
                        }
                        .product-name {
                            font-size: 20px;
                        }
                        .info-value {
                            font-size: 18px;
                        }
                        .quantity-critical {
                            font-size: 24px !important;
                        }
                    }
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="header">
                        <div class="logo">📦 NgedEase</div>
                        <div class="alert-badge">🚨 Stock Alert</div>
                        <h1 class="title">Low Inventory Warning</h1>
                    </div>
                    
                    <div class="greeting">
                        Dear Inventory Team,
                    </div>
                    
                    <p>We've detected that one of your products has reached a critically low stock level and requires immediate attention to prevent stockouts.</p>
                    
                    <div class="product-info">
                        <div class="product-name">{{ product_name }}</div>
                        <div class="info-grid">
                            <div class="info-item">
                                <div class="info-label">Store Location</div>
                                <div class="info-value">{{ store_name }}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Alert Threshold</div>
                                <div class="info-value">{{ threshold }}</div>
                            </div>
                        </div>
                        <div style="margin-top: 20px; text-align: center;">
                            <div class="info-label">Current Stock Level</div>
                            <div class="info-value quantity-critical">{{ current_quantity }}</div>
                        </div>
                    </div>
                    
                    <div class="urgency-meter">
                        <div class="urgency-title">⏰ Urgency Level: HIGH</div>
                        <div class="urgency-bar">
                            <div class="urgency-fill"></div>
                        </div>
                        <div style="font-size: 14px; color: #c62828; margin-top: 5px;">
                            Stock level is 85% below recommended threshold
                        </div>
                    </div>
                    
                    <div class="action-section">
                        <h3 class="action-title">
                            <span>🎯</span>
                            <span>Immediate Actions Required</span>
                        </h3>
                        <ul class="action-list">
                            <li>Review current supplier availability and lead times</li>
                            <li>Place urgent restock order to prevent stockouts</li>
                            <li>Consider temporary product substitutions if available</li>
                            <li>Notify sales team of potential inventory constraints</li>
                            <li>Update customers about potential delivery delays</li>
                        </ul>
                    </div>
                    
                    <div class="contact-info">
                        <div class="contact-title">Need assistance with restocking?</div>
                        <div class="contact-details">
                            📞 Contact Supply Chain: +251-929-146-352<br>
                            📧 Email: mahfouzteyib57@gmail.com
                        </div>
                    </div>
                    
                    <div class="support">
                        For technical support or system issues, contact us at 
                        <a href="mailto:mahfouzteyib57@gmail.com">mahfouzteyib57@gmail.com</a>
                    </div>
                    
                    <div class="footer">
                        <p><strong>NgedEase Inventory Management System</strong></p>
                        <p>This is an automated alert. Please take immediate action to prevent stockouts.</p>
                        <p>&copy; 2024 NgedEase. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            text_body="""
🚨 LOW STOCK ALERT - URGENT ACTION REQUIRED

Dear Inventory Team,

CRITICAL STOCK LEVEL DETECTED
=================================

Product: {{ product_name }}
Store: {{ store_name }}
Current Quantity: {{ current_quantity }}
Alert Threshold: {{ threshold }}

⏰ URGENCY LEVEL: HIGH
Stock level is critically low and requires immediate attention.

🎯 IMMEDIATE ACTIONS REQUIRED:
• Review current supplier availability and lead times
• Place urgent restock order to prevent stockouts
• Consider temporary product substitutions if available
• Notify sales team of potential inventory constraints


For technical support: mahfouzteyib57@gmail.com

This is an automated alert from NgedEase Inventory Management System.
Please take immediate action to prevent stockouts.

© 2025 NgedEase. All rights reserved.
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
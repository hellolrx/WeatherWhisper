import emails
from emails.template import JinjaTemplate
from app.core.config import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class EmailService:
    """邮件服务类"""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.smtp_use_tls = settings.smtp_use_tls
        
    async def send_plain_email(self, to_email: str, subject: str, content: str) -> bool:
        """发送纯文本邮件（简单通用）"""
        try:
            message = emails.Message(
                subject=subject,
                text=content,
                mail_from=(settings.app_name, self.smtp_user)
            )
            response = message.send(
                to=to_email,
                smtp={
                    "host": self.smtp_host,
                    "port": self.smtp_port,
                    "user": self.smtp_user,
                    "password": self.smtp_password,
                    "tls": self.smtp_use_tls,
                    "timeout": 10
                }
            )
            return response.status_code == 250
        except Exception as e:
            logger.error(f"Error sending plain email to {to_email}: {e}")
            return False
    
    async def send_verification_email(self, to_email: str, verification_code: str, 
                                    username: Optional[str] = None) -> bool:
        """发送验证码邮件"""
        try:
            # 邮件模板
            subject = "WeatherWhisper - 邮箱验证"
            
            # 简单的HTML模板
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>邮箱验证</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #74b9ff 0%, #0984e3 50%, #6c5ce7 100%); 
                              color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; }}
                    .verification-code {{ background: #e9ecef; padding: 15px; text-align: center; 
                                        font-size: 24px; font-weight: bold; color: #495057; 
                                        border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #6c757d; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🌤️ WeatherWhisper</h1>
                        <p>您的个人天气助手</p>
                    </div>
                    <div class="content">
                        <h2>您好{f'，{username}' if username else ''}！</h2>
                        <p>感谢您注册 WeatherWhisper！请使用以下验证码完成邮箱验证：</p>
                        
                        <div class="verification-code">
                            {verification_code}
                        </div>
                        
                        <p><strong>重要提醒：</strong></p>
                        <ul>
                            <li>验证码有效期为10分钟</li>
                            <li>请勿将验证码告诉他人</li>
                            <li>如果这不是您的操作，请忽略此邮件</li>
                        </ul>
                        
                        <p>验证成功后，您就可以开始使用我们的天气服务了！</p>
                    </div>
                    <div class="footer">
                        <p>此邮件由系统自动发送，请勿回复</p>
                        <p>&copy; 2025 WeatherWhisper. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # 发送邮件
            message = emails.Message(
                subject=subject,
                html=html_content,
                mail_from=(settings.app_name, self.smtp_user)
            )
            
            # 配置SMTP
            response = message.send(
                to=to_email,
                smtp={
                    "host": self.smtp_host,
                    "port": self.smtp_port,
                    "user": self.smtp_user,
                    "password": self.smtp_password,
                    "tls": self.smtp_use_tls,
                    "timeout": 10
                }
            )
            
            if response.status_code == 250:
                logger.info(f"Verification email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email to {to_email}. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending verification email to {to_email}: {e}")
            return False
    
    async def send_password_reset_email(self, to_email: str, reset_code: str) -> bool:
        """发送密码重置邮件"""
        try:
            subject = "WeatherWhisper - 密码重置"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>密码重置</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #e74c3c 0%, #c0392b 50%, #a93226 100%); 
                              color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; }}
                    .reset-code {{ background: #e9ecef; padding: 15px; text-align: center; 
                                  font-size: 24px; font-weight: bold; color: #495057; 
                                  border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #6c757d; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 WeatherWhisper</h1>
                        <p>密码重置服务</p>
                    </div>
                    <div class="content">
                        <h2>密码重置请求</h2>
                        <p>我们收到了您的密码重置请求。请使用以下验证码完成密码重置：</p>
                        
                        <div class="reset-code">
                            {reset_code}
                        </div>
                        
                        <p><strong>安全提醒：</strong></p>
                        <ul>
                            <li>验证码有效期为10分钟</li>
                            <li>如果您没有请求密码重置，请忽略此邮件</li>
                            <li>请勿将验证码告诉他人</li>
                        </ul>
                        
                        <p>验证成功后，您就可以设置新密码了。</p>
                    </div>
                    <div class="footer">
                        <p>此邮件由系统自动发送，请勿回复</p>
                        <p>&copy; 2025 WeatherWhisper. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            message = emails.Message(
                subject=subject,
                html=html_content,
                mail_from=(settings.app_name, self.smtp_user)
            )
            
            response = message.send(
                to=to_email,
                smtp={
                    "host": self.smtp_host,
                    "port": self.smtp_port,
                    "user": self.smtp_user,
                    "password": self.smtp_password,
                    "tls": self.smtp_use_tls,
                    "timeout": 10
                }
            )
            
            if response.status_code == 250:
                logger.info(f"Password reset email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send password reset email to {to_email}. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending password reset email to {to_email}: {e}")
            return False

# 创建全局邮件服务实例
email_service = EmailService()

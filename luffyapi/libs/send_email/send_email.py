from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def send_email(link, random_code, subject, text_content, html_content, recv_email):
    """
    random_code:随机验证码
    subject:主题摘要
    text_content:文本信息
    html_content:网页信息
    recv_email:接收者的邮箱

    send_mail(subject, message, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None,
              connection=None, html_message=None):
    """
    mail = EmailMultiAlternatives(subject, text_content,
                                  from_email=settings.EMAIL_HOST_USER, to=[recv_email, ])
    mail.attach_alternative(html_content % {'code': random_code, 'link': link}, 'text/html')
    mail.send()

import os
from typing import Tuple
import requests
from random import randrange
import urllib
import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

from shared import setup
from shared.types import story_types

sender_email = os.getenv("GMAIL_ADDRESS")
password = os.getenv("GMAIL_PASSWORD")


def send_user_init_email(to_email: str):
  """Sends an email to the newly created User to confirm their email address

    Args:
        to_email: The user's provided email.
        url: A url that can be used to reset the user's password.

    """

  url = setup.get_client_domain_name() + "/email"
  text = f"""\
    Hello,
    You have just created an account at truba.news, kindly use the following link to confirm your email address.: {url}"""
  html = f"""\
    <html>
    <head>
        <meta charset="utf-8">
        <title>truba.news</title>
    </head>
    <body>
        <div>
            <h3>Hello,</h3>
            <p>You have just created an account at truba.news, kindly use this <a href="{url}">link</a> to confirm your email address.</p>
            <br>
            <p>Thanks!</p>
        </div>
    </body>
    </html>
    """

  message = MIMEMultipart("alternative")
  message["Subject"] = "Confirm Account Creation - " + setup.get_client_domain_name()
  message["From"] = formataddr((os.getenv("GMAIL_SENDER_NAME"), sender_email))
  message["To"] = to_email
  part1 = MIMEText(text, "plain")
  part2 = MIMEText(html, "html")
  message.attach(part1)
  message.attach(part2)

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, to_email, message.as_string())


def send_forgot_password_email(to_email: str, url: str):
  """Sends an email to the user with a url to reset their password

    Args:
        to_email: The user's provided email.
        url: A url that can be used to reset the user's password.

    """

  text = f"""\
    Hello,
    You requested for a password reset, kindly use the following link to reset your password: {url}"""
  html = f"""\
    <html>
    <head>
        <meta charset="utf-8">
        <title>truba.news</title>
    </head>
    <body>
        <div>
            <h3>Hello,</h3>
            <p>You requested for a password reset, kindly use this <a href="{url}">link</a> to reset your password.</p>
            <br>
            <p>Cheers!</p>
        </div>
    </body>
    </html>
    """

  message = MIMEMultipart("alternative")
  message["Subject"] = "Password help - " + setup.get_client_domain_name()
  message["From"] = formataddr((os.getenv("GMAIL_SENDER_NAME"), sender_email))
  message["To"] = to_email
  part1 = MIMEText(text, "plain")
  part2 = MIMEText(html, "html")
  message.attach(part1)
  message.attach(part2)

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, to_email, message.as_string())


def send_reset_password_email(to_email: str):
  """Sends an email to the user to confirm their password has been reset

    Args:
        to_email: Email address of the user.

    """

  text = """\
    Hello,
    Your password has been successful reset, you can now login with your new password."""
  html = """\
    <html>
    <head>
        <meta charset="utf-8">
        <title>truba.news</title>
    </head>
    <body>
        <div>
            <h3>Hello,</h3>
            <p>Your password has been successful reset, you can now login with your new password.</p>
            <br>
            <div>
                Cheers!
            </div>
        </div>
    </body>
    </html>
    """

  message = MIMEMultipart("alternative")
  message["Subject"] = "Pwd Reset Successful -" + setup.get_client_domain_name(
  )
  message["From"] = formataddr((os.getenv("GMAIL_SENDER_NAME"), sender_email))
  message["To"] = to_email
  part1 = MIMEText(text, "plain")
  part2 = MIMEText(html, "html")
  message.attach(part1)
  message.attach(part2)

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, to_email, message.as_string())


def send_daily_snap_emails(to_emails: Tuple[str, ...],
                           stories: Tuple[story_types.ShortStory, ...]):
  """Sends an email to the provided emails which contains n news stories.

    Args:
        to_emails: Address' to send emails to.
        stories: stories to be inserted into the emails.

    """

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    for to_email in to_emails:
      message = build_daily_snap_email(to_email, stories)
      server.sendmail(sender_email, to_email, message.as_string())


def build_daily_snap_email(
    to_email: str, stories: Tuple[story_types.ShortStory,
                                  ...]) -> MIMEMultipart:
  """Sends an email to the provided emails which contains n news stories.

  Args:
      to_email: Address to send the email to.
      stories: stories to be inserted into the email.

  Returns:
      The email message object with the news stories inside.

  """

  number_of_stories = 5

  message = MIMEMultipart("alternative")
  message["Subject"] = "The Daily Snap - " + setup.get_client_domain_name()
  message["From"] = sender_email
  message["To"] = to_email
  attach_image("truba_logo.png", message, number_of_stories + 0)
  attach_image("facebook_icon.png", message, number_of_stories + 1)
  attach_image("twitter_icon.png", message, number_of_stories + 2)

  text = """\
    The Daily Snap,

    """

  for index in range(number_of_stories):
    rank = index + 1
    text = text + short_stroy_to_text(stories[index], rank)

  text = text + """\
    Hope you enjoyed it!
    Thanks,
    truba
    """

  part1 = MIMEText(text, "plain")
  message.attach(part1)

  html = """\
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:v="urn:schemas-microsoft-com:vml">
    <head>
    <!--[if gte mso 9]><xml><o:OfficeDocumentSettings><o:AllowPNG/><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml><![endif]-->
    <meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>
    <meta content="width=device-width" name="viewport"/>
    <!--[if !mso]><!-->
    <meta content="IE=edge" http-equiv="X-UA-Compatible"/>
    <!--<![endif]-->
    <title></title>
    <!--[if !mso]><!-->
    <link href="https://fonts.googleapis.com/css?family=Merriweather" rel="stylesheet" type="text/css"/>
    <!--<![endif]-->
    <style type="text/css">
    		body {
    			margin: 0;
    			padding: 0;
    		}

    		table,
    		td,
    		tr {
    			vertical-align: top;
    			border-collapse: collapse;
    		}

    		* {
    			line-height: inherit;
    		}

    		a[x-apple-data-detectors=true] {
    			color: inherit !important;
    			text-decoration: none !important;
    		}
    	</style>
    <style id="media-query" type="text/css">
    		@media (max-width: 620px) {

    			.block-grid,
    			.col {
    				min-width: 320px !important;
    				max-width: 100% !important;
    				display: block !important;
    			}

    			.block-grid {
    				width: 100% !important;
    			}

    			.col {
    				width: 100% !important;
    			}

    			.col_cont {
    				margin: 0 auto;
    			}

    			img.fullwidth,
    			img.fullwidthOnMobile {
    				width: 100% !important;
    			}

    			.no-stack .col {
    				min-width: 0 !important;
    				display: table-cell !important;
    			}

    			.no-stack.two-up .col {
    				width: 50% !important;
    			}

    			.no-stack .col.num2 {
    				width: 16.6% !important;
    			}

    			.no-stack .col.num3 {
    				width: 25% !important;
    			}

    			.no-stack .col.num4 {
    				width: 33% !important;
    			}

    			.no-stack .col.num5 {
    				width: 41.6% !important;
    			}

    			.no-stack .col.num6 {
    				width: 50% !important;
    			}

    			.no-stack .col.num7 {
    				width: 58.3% !important;
    			}

    			.no-stack .col.num8 {
    				width: 66.6% !important;
    			}

    			.no-stack .col.num9 {
    				width: 75% !important;
    			}

    			.no-stack .col.num10 {
    				width: 83.3% !important;
    			}

    			.video-block {
    				max-width: none !important;
    			}

    			.mobile_hide {
    				min-height: 0px;
    				max-height: 0px;
    				max-width: 0px;
    				display: none;
    				overflow: hidden;
    				font-size: 0px;
    			}

    			.desktop_hide {
    				display: block !important;
    				max-height: none !important;
    			}

    			.img-container.big img {
    				width: auto !important;
    			}
    		}
    	</style>
    <style id="icon-media-query" type="text/css">
    		@media (max-width: 620px) {
    			.icons-inner {
    				text-align: center;
    			}

    			.icons-inner td {
    				margin: 0 auto;
    			}
    		}
    	</style>
    </head>
    """ + f"""\
    <body class="clean-body" style="margin: 0; padding: 0; -webkit-text-size-adjust: 100%; background-color: #fafafa;">
    <!--[if IE]><div class="ie-browser"><![endif]-->
    <table bgcolor="#fafafa" cellpadding="0" cellspacing="0" class="nl-container" role="presentation" style="table-layout: fixed; vertical-align: top; min-width: 320px; border-spacing: 0; border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; background-color: #fafafa; width: 100%;" valign="top" width="100%">
    <tbody>
    <tr style="vertical-align: top;" valign="top">
    <td style="word-break: break-word; vertical-align: top;" valign="top">
    <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td align="center" style="background-color:#fafafa"><![endif]-->
    <div style="background-color:transparent;">
    <div class="block-grid" style="min-width: 320px; max-width: 600px; overflow-wrap: break-word; word-wrap: break-word; word-break: break-word; Margin: 0 auto; background-color: #fafafa;">
    <div style="border-collapse: collapse;display: table;width: 100%;background-color:#fafafa;">
    <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:transparent;"><tr><td align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px"><tr class="layout-full-width" style="background-color:#fafafa"><![endif]-->
    <!--[if (mso)|(IE)]><td align="center" width="600" style="background-color:#fafafa;width:600px; border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent;" valign="top"><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 25px; padding-left: 25px; padding-top:30px; padding-bottom:0px;"><![endif]-->
    <div class="col num12" style="min-width: 320px; max-width: 600px; display: table-cell; vertical-align: top; width: 600px;">
    <div class="col_cont" style="width:100% !important;">
    <!--[if (!mso)&(!IE)]><!-->
    <div style="border-top:0px solid transparent; border-left:0px solid transparent; border-bottom:0px solid transparent; border-right:0px solid transparent; padding-top:30px; padding-bottom:0px; padding-right: 25px; padding-left: 25px;">
    <!--<![endif]-->
    <div align="center" class="img-container center fixedwidth" style="padding-right: 0px;padding-left: 0px;">
    <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr style="line-height:0px"><td style="padding-right: 0px;padding-left: 0px;" align="center"><![endif]-->
    <div style="font-size:1px;line-height:5px"> </div><a href="{setup.get_client_domain_name()}" style="outline:none" tabindex="-1" target="_blank"><img align="center" alt="Company Logo" border="0" class="center fixedwidth" src="cid:{number_of_stories}" style="text-decoration: none; -ms-interpolation-mode: bicubic; height: auto; border: 0; width: 550px; max-width: 100%; display: block;" title="Company Logo" width="550"/></a>
    <div style="font-size:1px;line-height:5px"> </div>
    <!--[if mso]></td></tr></table><![endif]-->
    </div>
    <!--[if (!mso)&(!IE)]><!-->
    </div>
    <!--<![endif]-->
    </div>
    </div>
    <!--[if (mso)|(IE)]></td></tr></table><![endif]-->
    <!--[if (mso)|(IE)]></td></tr></table></td></tr></table><![endif]-->
    </div>
    </div>
    </div>
    <div style="background-color:transparent;">
    <div class="block-grid" style="min-width: 320px; max-width: 600px; overflow-wrap: break-word; word-wrap: break-word; word-break: break-word; Margin: 0 auto; background-color: #fafafa;">
    <div style="border-collapse: collapse;display: table;width: 100%;background-color:#fafafa;background-image:url('images/Percentage-Baclground.png');background-position:top left;background-repeat:no-repeat">
    <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:transparent;"><tr><td align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px"><tr class="layout-full-width" style="background-color:#fafafa"><![endif]-->
    <!--[if (mso)|(IE)]><td align="center" width="600" style="background-color:#fafafa;width:600px; border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent;" valign="top"><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 0px; padding-left: 0px; padding-top:0px; padding-bottom:45px;"><![endif]-->
    <div class="col num12" style="min-width: 320px; max-width: 600px; display: table-cell; vertical-align: top; width: 600px;">
    <div class="col_cont" style="width:100% !important;">
    <!--[if (!mso)&(!IE)]><!-->
    <div style="border-top:0px solid transparent; border-left:0px solid transparent; border-bottom:0px solid transparent; border-right:0px solid transparent; padding-top:0px; padding-right: 0px; padding-left: 0px;">
    <!--<![endif]-->
    <table border="0" cellpadding="0" cellspacing="0" class="divider" role="presentation" style="table-layout: fixed; vertical-align: top; border-spacing: 0; border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; min-width: 100%; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%;" valign="top" width="100%">
    <tbody>
    <tr style="vertical-align: top;" valign="top">
    <td class="divider_inner" style="word-break: break-word; vertical-align: top; min-width: 100%; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px;" valign="top">
    <table align="center" border="0" cellpadding="0" cellspacing="0" class="divider_content" height="50" role="presentation" style="table-layout: fixed; vertical-align: top; border-spacing: 0; border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; border-top: 0px solid transparent; height: 50px; width: 100%;" valign="top" width="100%">
    <tbody>
    <tr style="vertical-align: top;" valign="top">
    <td height="50" style="word-break: break-word; vertical-align: top; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%;" valign="top"><span></span></td>
    </tr>
    </tbody>
    </table>
    </td>
    </tr>
    </tbody>
    </table>
    """

  for index in range(number_of_stories):
    html = html + short_stroy_to_html(stories[index], index)

  html = html + f"""\
    <div style="background-color:#2c2c2c;">
    <div class="block-grid" style="min-width: 320px; max-width: 600px; overflow-wrap: break-word; word-wrap: break-word; word-break: break-word; Margin: 0 auto; background-color: #2c2c2c;">
    <div style="border-collapse: collapse;display: table;width: 100%;background-color:#2c2c2c;">
    <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#2c2c2c;"><tr><td align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px"><tr class="layout-full-width" style="background-color:#2c2c2c"><![endif]-->
    <!--[if (mso)|(IE)]><td align="center" width="600" style="background-color:#2c2c2c;width:600px; border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent;" valign="top"><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 0px; padding-left: 0px; padding-top:50px; padding-bottom:25px;"><![endif]-->
    <div class="col num12" style="min-width: 320px; max-width: 600px; display: table-cell; vertical-align: top; width: 600px;">
    <div class="col_cont" style="width:100% !important;">
    <!--[if (!mso)&(!IE)]><!-->
    <div style="border-top:0px solid transparent; border-left:0px solid transparent; border-bottom:0px solid transparent; border-right:0px solid transparent; padding-top:50px; padding-bottom:25px; padding-right: 0px; padding-left: 0px;">
    <!--<![endif]-->
    <table cellpadding="0" cellspacing="0" class="social_icons" role="presentation" style="table-layout: fixed; vertical-align: top; border-spacing: 0; border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt;" valign="top" width="100%">
    <tbody>
    <tr style="vertical-align: top;" valign="top">
    <td style="word-break: break-word; vertical-align: top; padding-top: 0px; padding-right: 10px; padding-bottom: 0px; padding-left: 10px;" valign="top">
    <table align="center" cellpadding="0" cellspacing="0" class="social_table" role="presentation" style="table-layout: fixed; vertical-align: top; border-spacing: 0; border-collapse: collapse; mso-table-tspace: 0; mso-table-rspace: 0; mso-table-bspace: 0; mso-table-lspace: 0;" valign="top">
    <tbody>
    <tr align="center" style="vertical-align: top; display: inline-block; text-align: center;" valign="top">
    <td style="word-break: break-word; vertical-align: top; padding-bottom: 0; padding-right: 2.5px; padding-left: 2.5px;" valign="top"><a href="https://www.facebook.com/" target="_blank"><img alt="Facebook" height="32" src="cid:{number_of_stories + 1}" style="text-decoration: none; -ms-interpolation-mode: bicubic; height: auto; border: 0; display: block; color: #fafafa" title="Facebook" width="32"/></a></td>
    <td style="word-break: break-word; vertical-align: top; padding-bottom: 0; padding-right: 2.5px; padding-left: 2.5px;" valign="top"><a href="https://twitter.com/" target="_blank"><img alt="Twitter" height="32" src="cid:{number_of_stories + 2}" style="text-decoration: none; -ms-interpolation-mode: bicubic; height: auto; border: 0; display: block; color: #fafafa" title="Twitter" width="32"/></a></td>
    </tr>
    </tbody>
    </table>
    </td>
    </tr>
    </tbody>
    </table>
    <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 10px; padding-left: 10px; padding-top: 10px; padding-bottom: 10px; font-family: serif"><![endif]-->
    <div style="color:#fafafa;font-family:'Merriwheater', 'Georgia', serif;line-height:1.2;padding-top:10px;padding-right:10px;padding-bottom:10px;padding-left:10px;">
    <div class="txtTinyMce-wrapper" style="font-size: 12px; line-height: 1.2; color: #fafafa; font-family: 'Merriwheater', 'Georgia', serif; mso-line-height-alt: 14px;">
    <p style="margin: 0; font-size: 14px; text-align: center; line-height: 1.2; word-break: break-word; mso-line-height-alt: 17px; margin-top: 0; margin-bottom: 0;"><span id="f5c76119-6591-4a54-bb42-858e19560972" style="font-size: 14px;">@2021 Your Brand. All Rights Reserved</span></p>
    </div>
    </div>
    <!--[if mso]></td></tr></table><![endif]-->
    <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 10px; padding-left: 10px; padding-top: 10px; padding-bottom: 10px; font-family: serif"><![endif]-->
    <div style="color:#fafafa;font-family:'Merriwheater', 'Georgia', serif;line-height:1.2;padding-top:10px;padding-right:10px;padding-bottom:10px;padding-left:10px;">
    <div class="txtTinyMce-wrapper" style="font-size: 12px; line-height: 1.2; color: #fafafa; font-family: 'Merriwheater', 'Georgia', serif; mso-line-height-alt: 14px;">
    <p style="margin: 0; font-size: 12px; text-align: center; line-height: 1.2; word-break: break-word; mso-line-height-alt: 14px; margin-top: 0; margin-bottom: 0;"><a href="{setup.get_client_domain_name()}/unsubscribe?{urllib.parse.urlencode({'email': to_email})}" rel="noopener" style="text-de
    coration: none; color: #fff;" target="_blank"><span style="font-size: 14px;">Unsubscribe</span></a></p>
    </div>
    </div>
    <!--[if mso]></td></tr></table><![endif]-->
    <!--[if (!mso)&(!IE)]><!-->
    </div>
    <!--<![endif]-->
    </div>
    </div>
    <!--[if (mso)|(IE)]></td></tr></table><![endif]-->
    <!--[if (mso)|(IE)]></td></tr></table></td></tr></table><![endif]-->
    </div>
    </div>
    </div>
    <div style="background-color:transparent;">
    <div class="block-grid" style="min-width: 320px; max-width: 600px; overflow-wrap: break-word; word-wrap: break-word; word-break: break-word; Margin: 0 auto; background-color: transparent;">
    <div style="border-collapse: collapse;display: table;width: 100%;background-color:transparent;">
    <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:transparent;"><tr><td align="center"><table cellpadding="0" cellspacing="0" border="0" style="width:600px"><tr class="layout-full-width" style="background-color:transparent"><![endif]-->
    <!--[if (mso)|(IE)]><td align="center" width="600" style="background-color:transparent;width:600px; border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent;" valign="top"><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 0px; padding-left: 0px; padding-top:5px; padding-bottom:5px;"><![endif]-->
    <div class="col num12" style="min-width: 320px; max-width: 600px; display: table-cell; vertical-align: top; width: 600px;">
    <div class="col_cont" style="width:100% !important;">
    <!--[if (!mso)&(!IE)]><!-->
    <div style="border-top:0px solid transparent; border-left:0px solid transparent; border-bottom:0px solid transparent; border-right:0px solid transparent; padding-top:5px; padding-bottom:5px; padding-right: 0px; padding-left: 0px;">
    <!--<![endif]-->
    <table cellpadding="0" cellspacing="0" role="presentation" style="table-layout: fixed; vertical-align: top; border-spacing: 0; border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt;" valign="top" width="100%">
    <tr style="vertical-align: top;" valign="top">
    <td align="center" style="word-break: break-word; vertical-align: top; padding-top: 5px; padding-right: 0px; padding-bottom: 5px; padding-left: 0px; text-align: center;" valign="top">
    <!--[if vml]><table align="left" cellpadding="0" cellspacing="0" role="presentation" style="display:inline-block;padding-left:0px;padding-right:0px;mso-table-lspace: 0pt;mso-table-rspace: 0pt;"><![endif]-->
    <!--[if !vml]><!-->
    <table cellpadding="0" cellspacing="0" class="icons-inner" role="presentation" style="table-layout: fixed; vertical-align: top; border-spacing: 0; border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; display: inline-block; margin-right: -4px; padding-left: 0px; padding-right: 0px;" valign="top">
    <!--<![endif]-->
    <tr style="vertical-align: top;" valign="top">
    </tr>
    </table>
    </td>
    </tr>
    </table>
    <!--[if (!mso)&(!IE)]><!-->
    </div>
    <!--<![endif]-->
    </div>
    </div>
    <!--[if (mso)|(IE)]></td></tr></table><![endif]-->
    <!--[if (mso)|(IE)]></td></tr></table></td></tr></table><![endif]-->
    </div>
    </div>
    </div>
    <!--[if (mso)|(IE)]></td></tr></table><![endif]-->
    </td>
    </tr>
    </tbody>
    </table>
    <!--[if (IE)]></div><![endif]-->
    </body>
    </html>
    """

  part2 = MIMEText(html, "html")
  message.attach(part2)

  for index in range(number_of_stories):
    image_url = stories[index].image
    response = None
    if image_url:
      try:
        response = requests.get(image_url)
      except requests.exceptions.RequestException:
        pass
    if not response:
      image_url = setup.get_client_domain_name()
      image_url += f"""/assets/images/newspapers/{str(randrange(13))}.jpg"""
    response = requests.get(image_url)
    if not response:
      continue
    img_data = response.content
    part = MIMEBase("application", "octet-stream")
    part.set_payload(img_data)
    encoders.encode_base64(part)
    image_type = ".jpg"
    image_types = (".png", ".jpeg", ".gif")
    for possible_type in image_types:
      if image_url.find(possible_type) != -1:
        image_type = possible_type
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= newsimage{str(index + 1)}{image_type}",
    )
    part.add_header("X-Attachment-Id", f"{str(index)}")
    part.add_header("Content-ID", f"<{str(index)}>")
    message.attach(part)
  return message


def attach_image(filename: str, message: MIMEMultipart, index: int):
  """Attaches a static image to given email content. 

    Args:
        filename: Name of the image file to be attached to the email.
        message: The content of the email.
        index: A unique int used to identify the image in the attachment
          and the HTML.

    """

  with open(f"../../data/images/{filename}", "rb") as attachment:
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    part.add_header("X-Attachment-Id", str(index))
    part.add_header("Content-ID", f"<{str(index)}>")
    message.attach(part)


def short_stroy_to_text(story: story_types.ShortStory, rank: int) -> str:
  """Generate a string of text to be inserted into an email given the info
  found in a story.

    Args:
        story: Story to be used in the text.
        rank: The count of the news story to be incremented.

    Returns:
        The string to be inserted into the text of an email.

    """

  return f"""\
    # {str(rank)}
    {story.title}
    {story.url}

    """


def short_stroy_to_html(story: story_types.ShortStory, index: int) -> str:
  """Generate a string of HTML to be inserted into an email given the info
  found in a story.

    Args:
        story: Story to be used in the HTML.
        rank: The count of the news story to be incremented.

    Returns:
        The string to be inserted into the HTML of an email.

    """

  return f"""\
    <a href="{story.url}" rel="noopener" style="text-decoration: none;" target="_blank">
    <table border="0" cellpadding="0" cellspacing="0" class="divider" role="presentation" style="table-layout: fixed; vertical-align: top; border-spacing: 0; border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; min-width: 100%; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%;" valign="top" width="100%">
    <tbody>
    <tr style="vertical-align: top;" valign="top">
    <td class="divider_inner" style="word-break: break-word; vertical-align: top; min-width: 100%; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%; padding-top: 0px; padding-right: 0px; padding-bottom: 0px; padding-left: 0px;" valign="top">
    <table align="center" border="0" cellpadding="0" cellspacing="0" class="divider_content" height="30" role="presentation" style="table-layout: fixed; vertical-align: top; border-spacing: 0; border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; border-top: 0px solid transparent; height: 30px; width: 100%;" valign="top" width="100%">
    <tbody>
    <tr style="vertical-align: top;" valign="top">
    <td height="30" style="word-break: break-word; vertical-align: top; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%;" valign="top"><span></span></td>
    </tr>
    </tbody>
    </table>
    </td>
    </tr>
    </tbody>
    </table>
    <div align="center" class="img-container center fixedwidth fullwidthOnMobile big" style="padding-right: 20px;padding-left: 20px;">
    <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr style="line-height:0px"><td style="padding-right: 20px;padding-left: 20px;" align="center"><![endif]--><img align="center" border="0" class="center fixedwidth fullwidthOnMobile" src="cid:{str(index)}" style="text-decoration: none; -ms-interpolation-mode: bicubic; height: auto; border: 0; width: 560px; max-width: 100%; display: block;" title="News Article Image" width="560"/>
    <!--[if mso]></td></tr></table><![endif]-->
    </div>
    <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 25px; padding-left: 25px; padding-top: 20px; padding-bottom: 10px; font-family: Arial, sans-serif"><![endif]-->
    <div style="color:#636363;font-family:'Helvetica Neue', Helvetica, Arial, sans-serif;line-height:1.5;padding-top:20px;padding-right:25px;padding-bottom:10px;padding-left:25px;">
    <div class="txtTinyMce-wrapper" style="font-size: 12px; line-height: 1.5; color: #636363; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; mso-line-height-alt: 18px;">
    </div>
    </div>
    <!--[if mso]></td></tr></table><![endif]-->
    <!--[if (!mso)&(!IE)]><!-->
    </div>
    <!--<![endif]-->
    </div>
    </div>
    <!--[if (mso)|(IE)]></td></tr></table><![endif]-->
    <!--[if (mso)|(IE)]></td></tr></table></td></tr></table><![endif]-->
    </div>
    </div>
    </div>
    <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 0px; padding-left: 0px; padding-top: 0px; padding-bottom: 0px; font-family: serif"><![endif]-->
    <div style="color:#2c2c2c;font-family:'Merriwheater', 'Georgia', serif;line-height:1.2;padding-top:0px;padding-right:0px;padding-bottom:50px;padding-left:0px;">
    <div class="txtTinyMce-wrapper" style="font-size: 12px; line-height: 1.2; font-family: 'Merriwheater', 'Georgia', serif; color: #2c2c2c; mso-line-height-alt: 14px;">
    <p style="margin: 0; font-size: 26px; line-height: 1.2; word-break: break-word; text-align: center; mso-line-height-alt: 31px; margin-top: 0; margin-bottom: 0;"><span style="font-size: 26px;">{story.title}</span></p>
    <p style="margin: 0; font-size: 18px; line-height: 1.2; word-break: break-word; text-align: center; mso-line-height-alt: 31px; margin-top: 10px; margin-bottom: 0;"><span style="font-size: 18px;">{story.source}</span></p>
    </div>
    </div>
    <!--[if mso]></td></tr></table><![endif]-->
    </a>
    """

package user

import (
	"fmt"
	"io"
	"log"
	"math/rand/v2"
	"net/http"
	"os"
	"strconv"
	"strings"

	"core/internal/models"
	"core/internal/utils"

	gomail "gopkg.in/mail.v2"
)

var senderEmail = os.Getenv("GMAIL_ADDRESS")
var fromEmail = os.Getenv("GMAIL_SENDER_NAME") + " <" + os.Getenv("GMAIL_ADDRESS") + ">"
var password = os.Getenv("GMAIL_PASSWORD")

func SendUserInitEmail(toEmail string) error {
	url := os.Getenv("APP_URL") + "/email"
	text := fmt.Sprintf(`
		Hello,
		You have just created an account at truba.news, kindly use the following link to confirm your email address.: %s`, url)
	html := fmt.Sprintf(`
		<html>
		    <head>
		        <meta charset="utf-8">
		        <title>truba.news</title>
		    </head>
		    <body>
		        <div>
		            <h3>Hello,</h3>
		            <p>You have just created an account at truba.news, kindly use this <a href="%s">link</a> to confirm your email address.</p>
		            <br>
		            <p>Thanks!</p>
		        </div>
		    </body>
	    </html>`, url)
	message := gomail.NewMessage()
	message.SetHeader("From", fromEmail)
	message.SetHeader("To", toEmail)
	message.SetHeader("Subject", "Confirm Account Creation - "+os.Getenv("APP_URL"))
	message.SetBody("text/plain", text)
	message.AddAlternative("text/html", html)

	d := gomail.NewDialer("smtp.gmail.com", 465, senderEmail, password)
	if err := d.DialAndSend(message); err != nil {
		return utils.LogError("Failed to send Initial email")
	}
	return nil
}

func SendForgotPasswordEmail(toEmail string, url string) error {
	text := fmt.Sprintf(`
		Hello,
    	You requested for a password reset, kindly use the following link to reset your password: %s`, url)
	html := fmt.Sprintf(`
		<html>
		    <head>
		        <meta charset="utf-8">
		        <title>truba.news</title>
		    </head>
		    <body>
		        <div>
		            <h3>Hello,</h3>
		            <p>You requested for a password reset, kindly use this <a href="%s">link</a> to reset your password.</p>
		            <br>
		            <p>Cheers!</p>
		        </div>
		    </body>
	    </html>`, url)
	message := gomail.NewMessage()
	message.SetHeader("From", fromEmail)
	message.SetHeader("To", toEmail)
	message.SetHeader("Subject", "Password help - "+os.Getenv("APP_URL"))
	message.SetBody("text/plain", text)
	message.AddAlternative("text/html", html)

	d := gomail.NewDialer("smtp.gmail.com", 465, senderEmail, password)
	if err := d.DialAndSend(message); err != nil {
		utils.LogError("Failed to send forgot password email")
		return err
	}
	return nil
}

func SendResetPasswordEmail(toEmail string) error {
	text := `Hello,
    		Your password has been successful reset, you can now login with your new password.`
	html := `
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
	    </html>`
	message := gomail.NewMessage()
	message.SetHeader("From", fromEmail)
	message.SetHeader("To", toEmail)
	message.SetHeader("Subject", "Pwd Reset Successful - "+os.Getenv("APP_URL"))
	message.SetBody("text/plain", text)
	message.AddAlternative("text/html", html)

	d := gomail.NewDialer("smtp.gmail.com", 465, senderEmail, password)
	if err := d.DialAndSend(message); err != nil {
		utils.LogError("Failed to send forgot password email")
		return err
	}
	return nil
}

func SendDailySnapEmail(toEmails []string, stories []*models.ShortStory) {
	if len(toEmails) == 0 {
		log.Printf("There's not emails to email for the Daily Snap")
		return
	}
	numberOfStories := 5
	if len(stories) < numberOfStories {
		numberOfStories = len(stories)
	}
	didItSaveImage := make([]bool, numberOfStories)
	for index := range numberOfStories {
		didItSaveImage[index] = saveStoryImage(*stories[index])
	}
	message := buildDailySnapEmail(stories, didItSaveImage, numberOfStories)
	d := gomail.NewDialer("smtp.gmail.com", 465, senderEmail, password)
	for _, toEmail := range toEmails {
		newMessage := message
		newMessage.SetHeader("To", toEmail)
		if err := d.DialAndSend(&newMessage); err != nil {
			fmt.Printf("Failed to send Daily Snap email to %s", toEmail)
		}
	}
	for index := range numberOfStories {
		if didItSaveImage[index] {
			imageName := getImageNameFromUrl(stories[index].Url)
			er := os.Remove("/tmp/" + imageName)
			if er != nil {
				panic(er)
			}
		}
	}
}

func buildDailySnapEmail(stories []*models.ShortStory, didItSaveImage []bool, numberOfStories int) gomail.Message {
	message := gomail.NewMessage()
	message.SetHeader("From", fromEmail)
	message.SetHeader("Subject", "The Daily Snap - "+os.Getenv("APP_URL"))
	message.Embed("../../data/images/truba_logo.png")
	message.Embed("../../data/images/facebook_icon.png")
	message.Embed("../../data/images/twitter_icon.png")
	for index := range numberOfStories {
		if didItSaveImage[index] {
			message.Embed("/tmp/" + getImageNameFromUrl(stories[index].Url))
		} else {
			message.Embed("../../data/images/newspapers/"+strconv.Itoa(rand.IntN(12))+".jpg", gomail.Rename(strconv.Itoa(index)+".jpg"))
		}
	}
	text := `
    The Daily Snap,

    `
	for index := range numberOfStories {
		rank := index + 1
		text += shortStoryToText(*stories[index], rank)
	}
	text += `
    Hope you enjoyed it!
    Thanks,
    truba
    `
	message.SetBody("text/plain", text)

	html := fmt.Sprintf(`
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
    <div style="font-size:1px;line-height:5px"> </div><a href="%s" style="outline:none" tabindex="-1" target="_blank"><img align="center" alt="Company Logo" border="0" class="center fixedwidth" src="cid:truba_logo.png" style="text-decoration: none; -ms-interpolation-mode: bicubic; height: auto; border: 0; width: 550px; max-width: 100%; display: block;" title="Company Logo" width="550"/></a>
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
	`, os.Getenv("APP_URL"))

	for index := range numberOfStories {
		html += shortStoryToHTML(*stories[index], index, didItSaveImage)
	}

	html += fmt.Sprintf(`
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
    <td style="word-break: break-word; vertical-align: top; padding-bottom: 0; padding-right: 2.5px; padding-left: 2.5px;" valign="top"><a href="https://www.facebook.com/" target="_blank"><img alt="Facebook" height="32" src="cid:facebook_icon.png" style="text-decoration: none; -ms-interpolation-mode: bicubic; height: auto; border: 0; display: block; color: #fafafa" title="Facebook" width="32"/></a></td>
    <td style="word-break: break-word; vertical-align: top; padding-bottom: 0; padding-right: 2.5px; padding-left: 2.5px;" valign="top"><a href="https://twitter.com/" target="_blank"><img alt="Twitter" height="32" src="cid:twitter_icon.png" style="text-decoration: none; -ms-interpolation-mode: bicubic; height: auto; border: 0; display: block; color: #fafafa" title="Twitter" width="32"/></a></td>
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
    <p style="margin: 0; font-size: 12px; text-align: center; line-height: 1.2; word-break: break-word; mso-line-height-alt: 14px; margin-top: 0; margin-bottom: 0;"><a href="%s/unsubscribe?{urllib.parse.urlencode({'email': to_email})}" rel="noopener" style="text-de
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
    </html>`, os.Getenv("APP_URL"))

	message.AddAlternative("text/html", html)

	return *message
}

func shortStoryToText(currentStory models.ShortStory, rank int) string {
	return fmt.Sprintf(`
    # %[1]d
    %[2]s
    %[3]s

    `, rank, currentStory.Title, currentStory.Url)
}

func saveStoryImage(currentStory models.ShortStory) bool {
	if *currentStory.Image == "" {
		return false
	}
	response, e := http.Get(*currentStory.Image)
	if e != nil {
		return false
	}
	defer response.Body.Close()
	imageName := getImageNameFromUrl(*currentStory.Image)
	file, err := os.Create("/tmp/" + imageName)
	if err != nil {
		return false
	}
	defer file.Close()
	_, err = io.Copy(file, response.Body)
	return err == nil
}

func getImageNameFromUrl(url string) string {
	paths := strings.Split(url, `/`)
	return paths[len(paths)-1]
}

func shortStoryToHTML(currentStory models.ShortStory, index int, didItSave []bool) string {
	imageName := strconv.Itoa(index) + ".jpg"
	if didItSave[index] {
		imageName = getImageNameFromUrl(currentStory.Url)
	}
	return fmt.Sprintf(`
		"""\
    <a href="%[1]s" rel="noopener" style="text-decoration: none;" target="_blank">
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
    <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr style="line-height:0px"><td style="padding-right: 20px;padding-left: 20px;" align="center"><![endif]--><img align="center" border="0" class="center fixedwidth fullwidthOnMobile" src="cid:%[2]s" style="text-decoration: none; -ms-interpolation-mode: bicubic; height: auto; border: 0; width: 560px; max-width: 100%; display: block;" title="News Article Image" width="560"/>
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
    <p style="margin: 0; font-size: 26px; line-height: 1.2; word-break: break-word; text-align: center; mso-line-height-alt: 31px; margin-top: 0; margin-bottom: 0;"><span style="font-size: 26px;">%[3]s</span></p>
    <p style="margin: 0; font-size: 18px; line-height: 1.2; word-break: break-word; text-align: center; mso-line-height-alt: 31px; margin-top: 10px; margin-bottom: 0;"><span style="font-size: 18px;">%[4]s</span></p>
    </div>
    </div>
    <!--[if mso]></td></tr></table><![endif]-->
    </a>
    `, currentStory.Url, imageName, currentStory.Title, currentStory.Source)
}

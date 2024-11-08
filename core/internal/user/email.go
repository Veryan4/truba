package user

import (
	"errors"
	"math/rand/v2"
	"net/http"
	"net/url"
	"os"
	"strconv"

	"core/internal/models"
	"core/internal/utils"

	ht "html/template"
	tt "text/template"

	"github.com/wneessen/go-mail"
)

type MailUrl struct {
	Url string
}

const (
	userInitTextTemplate = `
	Hello,
	You have just created an account at truba.news, kindly use the following link to confirm your email address.: {{.Url}}`

	userInitHtmlTemplate = `<html>
	<head>
		<meta charset="utf-8">
		<title>truba.news</title>
	</head>
	<body>
		<div>
			<h3>Hello,</h3>
			<p>You have just created an account at truba.news, kindly use this <a href="{{.Url}}">link</a> to confirm your email address.</p>
			<br>
			<p>Thanks!</p>
		</div>
	</body>
	</html>`
)

func SendUserInitEmail(toEmail string) error {
	appUrl := MailUrl{
		Url: os.Getenv("APP_URL") + "/email",
	}
	textTpl, err := tt.New("texttpl").Parse(userInitTextTemplate)
	if err != nil {
		return utils.LogError(err)
	}
	htmlTpl, err := ht.New("htmltpl").Parse(userInitHtmlTemplate)
	if err != nil {
		return utils.LogError(err)
	}
	message := mail.NewMsg()
	message.FromFormat(os.Getenv("MAIL_SENDER_NAME"), os.Getenv("MAIL_ADDRESS"))
	message.To(toEmail)
	message.Subject("Confirm Account Creation - " + os.Getenv("APP_URL"))
	message.SetBodyTextTemplate(textTpl, appUrl)
	message.AddAlternativeHTMLTemplate(htmlTpl, appUrl)
	client, err := mail.NewClient("smtp.resend.com",
		mail.WithSMTPAuth(mail.SMTPAuthPlain), mail.WithTLSPortPolicy(mail.TLSMandatory),
		mail.WithUsername("resend"), mail.WithPassword(os.Getenv("MAIL_PASSWORD")),
	)
	if err != nil {
		return utils.LogError(err)
	}
	if err := client.DialAndSend(message); err != nil {
		return utils.LogError(err)
	}
	return nil
}

const (
	forgotPasswordTextTemplate = `
	Hello,
    You requested for a password reset, kindly use the following link to reset your password: {{.Url}}`

	forgotPasswordHtmlTemplate = `<html>
	<head>
		<meta charset="utf-8">
		<title>truba.news</title>
	</head>
	<body>
		<div>
			<h3>Hello,</h3>
			<p>You requested for a password reset, kindly use this <a href="{{.Url}}">link</a> to reset your password.</p>
			<br>
			<p>Cheers!</p>
		</div>
	</body>
	</html>`
)

func SendForgotPasswordEmail(toEmail string, appUrl string) error {
	textTpl, err := tt.New("texttpl").Parse(forgotPasswordTextTemplate)
	if err != nil {
		return utils.LogError(err)
	}
	htmlTpl, err := ht.New("htmltpl").Parse(forgotPasswordHtmlTemplate)
	if err != nil {
		return utils.LogError(err)
	}
	message := mail.NewMsg()
	message.FromFormat(os.Getenv("MAIL_SENDER_NAME"), os.Getenv("MAIL_ADDRESS"))
	message.To(toEmail)
	message.Subject("Password help - " + os.Getenv("APP_URL"))
	message.SetBodyTextTemplate(textTpl, appUrl)
	message.AddAlternativeHTMLTemplate(htmlTpl, appUrl)
	client, err := mail.NewClient("smtp.resend.com",
		mail.WithSMTPAuth(mail.SMTPAuthPlain), mail.WithTLSPortPolicy(mail.TLSMandatory),
		mail.WithUsername("resend"), mail.WithPassword(os.Getenv("MAIL_PASSWORD")),
	)
	if err != nil {
		return utils.LogError(err)
	}
	if err := client.DialAndSend(message); err != nil {
		return utils.LogError(err)
	}
	return nil
}

const (
	resetPasswordTextTemplate = `
	Hello,
    Your password has been successful reset, you can now login with your new password.`

	resetPasswordHtmlTemplate = `<html>
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
)

func SendResetPasswordEmail(toEmail string) error {
	appUrl := MailUrl{
		Url: os.Getenv("APP_URL"),
	}
	textTpl, err := tt.New("texttpl").Parse(resetPasswordTextTemplate)
	if err != nil {
		return utils.LogError(err)
	}
	htmlTpl, err := ht.New("htmltpl").Parse(resetPasswordHtmlTemplate)
	if err != nil {
		return utils.LogError(err)
	}
	message := mail.NewMsg()
	message.FromFormat(os.Getenv("MAIL_SENDER_NAME"), os.Getenv("MAIL_ADDRESS"))
	message.To(toEmail)
	message.Subject("Password Reset Successful - " + os.Getenv("APP_URL"))
	message.SetBodyTextTemplate(textTpl, appUrl)
	message.AddAlternativeHTMLTemplate(htmlTpl, appUrl)
	client, err := mail.NewClient("smtp.resend.com",
		mail.WithSMTPAuth(mail.SMTPAuthPlain), mail.WithTLSPortPolicy(mail.TLSMandatory),
		mail.WithUsername("resend"), mail.WithPassword(os.Getenv("MAIL_PASSWORD")),
	)
	if err != nil {
		return utils.LogError(err)
	}
	if err := client.DialAndSend(message); err != nil {
		return utils.LogError(err)
	}
	return nil
}

func SendDailySnapEmail(toEmails []string, stories []*models.ShortStory) error {
	if len(toEmails) == 0 {
		return utils.LogError(errors.New("there's not emails to email for the Daily Snap"))
	}
	numberOfStories := 3
	if len(stories) < numberOfStories {
		numberOfStories = len(stories)
	}
	didItSaveImage := make([]bool, numberOfStories)
	for index := range numberOfStories {
		didItSaveImage[index] = saveStoryImage(*stories[index])
	}
	messages := make([]*mail.Msg, 0)
	for _, toEmail := range toEmails {
		message := buildDailySnapEmail(stories, didItSaveImage, numberOfStories, toEmail)
		messages = append(messages, message)
	}
	client, err := mail.NewClient("smtp.resend.com",
		mail.WithSMTPAuth(mail.SMTPAuthPlain), mail.WithTLSPortPolicy(mail.TLSMandatory),
		mail.WithUsername("resend"), mail.WithPassword(os.Getenv("MAIL_PASSWORD")),
	)
	if err != nil {
		return utils.LogError(err)
	}
	if err := client.DialAndSend(messages...); err != nil {
		return utils.LogError(err)
	}
	return nil
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
	return true
}

func buildDailySnapEmail(stories []*models.ShortStory, didItSaveImage []bool, numberOfStories int, toEmail string) *mail.Msg {
	textTpl, err := tt.New("texttpl").Parse(dailySnapTextTemplate)
	if err != nil {
		panic(err)
	}
	htmlTpl, err := ht.New("htmltpl").Parse(dailySnapHtmlTemplate)
	if err != nil {
		panic(err)
	}
	message := mail.NewMsg()
	dailySnap := DailySnap{
		AppUrl:  os.Getenv("APP_URL"),
		ToEmail: url.QueryEscape(toEmail),
		Stories: make([]EmailStory, numberOfStories),
	}
	for ind := range numberOfStories {
		dailySnap.Stories[ind] = EmailStory{
			Title:  stories[ind].Title,
			Url:    stories[ind].Url,
			Source: *stories[ind].Source,
			Rank:   ind + 1,
		}
		if didItSaveImage[ind] {
			dailySnap.Stories[ind].Image = *stories[ind].Image
		} else {
			dailySnap.Stories[ind].Image = "https://truba.news/newspapers/" + strconv.Itoa(rand.IntN(12)) + ".jpg"
		}
	}
	message.FromFormat(os.Getenv("MAIL_SENDER_NAME"), os.Getenv("MAIL_ADDRESS"))
	message.To(toEmail)
	message.Subject("The Daily Snap - " + os.Getenv("APP_URL"))
	message.SetBodyTextTemplate(textTpl, dailySnap)
	message.AddAlternativeHTMLTemplate(htmlTpl, dailySnap)
	return message
}

type DailySnap struct {
	AppUrl  string
	ToEmail string
	Stories []EmailStory
}
type EmailStory struct {
	Title  string
	Url    string
	Source string
	Image  string
	Rank   int
}

const (
	dailySnapTextTemplate = `
	The Daily Snap,

	{{range $story := .Stories}}
	# {{$story.Rank}}
	{{$story.Title}}
    {{$story.Url}}
	{{end}}


    Hope you enjoyed it!
    Thanks,
    truba`

	dailySnapHtmlTemplate = `<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
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
    <div style="font-size:1px;line-height:5px"> </div><a href="{{.AppUrl}}" style="outline:none" tabindex="-1" target="_blank"><img align="center" alt="Company Logo" border="0" class="center fixedwidth" src="https://truba.news/newspapers/truba_logo.png" style="text-decoration: none; -ms-interpolation-mode: bicubic; height: auto; border: 0; width: 550px; max-width: 100%; display: block;" title="Company Logo" width="550"/></a>
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

	{{range $story := .Stories}}
	<a href="{{$story.Url}}" rel="noopener" style="text-decoration: none;" target="_blank">
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
    <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr style="line-height:0px"><td style="padding-right: 20px;padding-left: 20px;" align="center"><![endif]--><img align="center" border="0" class="center fixedwidth fullwidthOnMobile" src="{{$story.Image}}" style="text-decoration: none; -ms-interpolation-mode: bicubic; height: auto; border: 0; width: 560px; max-width: 100%; display: block;" title="News Article Image" width="560"/>
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
    <p style="margin: 0; font-size: 26px; line-height: 1.2; word-break: break-word; text-align: center; mso-line-height-alt: 31px; margin-top: 0; margin-bottom: 0;"><span style="font-size: 26px;">{{$story.Title}}</span></p>
    <p style="margin: 0; font-size: 18px; line-height: 1.2; word-break: break-word; text-align: center; mso-line-height-alt: 31px; margin-top: 10px; margin-bottom: 0;"><span style="font-size: 18px;">{{$story.Source}}</span></p>
    </div>
    </div>
    <!--[if mso]></td></tr></table><![endif]-->
    </a>
	{{end}}
	
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
    <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 10px; padding-left: 10px; padding-top: 10px; padding-bottom: 10px; font-family: serif"><![endif]-->
    <div style="color:#fafafa;font-family:'Merriwheater', 'Georgia', serif;line-height:1.2;padding-top:10px;padding-right:10px;padding-bottom:10px;padding-left:10px;">
    <div class="txtTinyMce-wrapper" style="font-size: 12px; line-height: 1.2; color: #fafafa; font-family: 'Merriwheater', 'Georgia', serif; mso-line-height-alt: 14px;">
    <p style="margin: 0; font-size: 14px; text-align: center; line-height: 1.2; word-break: break-word; mso-line-height-alt: 17px; margin-top: 0; margin-bottom: 0;"><span id="f5c76119-6591-4a54-bb42-858e19560972" style="font-size: 14px;">There's a narnia under the keyboard</span></p>
    </div>
    </div>
    <!--[if mso]></td></tr></table><![endif]-->
    <!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 10px; padding-left: 10px; padding-top: 10px; padding-bottom: 10px; font-family: serif"><![endif]-->
    <div style="color:#fafafa;font-family:'Merriwheater', 'Georgia', serif;line-height:1.2;padding-top:10px;padding-right:10px;padding-bottom:10px;padding-left:10px;">
    <div class="txtTinyMce-wrapper" style="font-size: 12px; line-height: 1.2; color: #fafafa; font-family: 'Merriwheater', 'Georgia', serif; mso-line-height-alt: 14px;">
    <p style="margin: 0; font-size: 12px; text-align: center; line-height: 1.2; word-break: break-word; mso-line-height-alt: 14px; margin-top: 0; margin-bottom: 0;"><a href="{{.AppUrl}}/unsubscribe?email={{.ToEmail}}" rel="noopener" style="text-de
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
    </html>`
)

import { LitElement, html } from "lit";
import { customElement } from "lit/decorators.js";
import { TranslationController } from "@veryan/lit-spa";
import { styles } from "./privacy.styles";

@customElement("app-privacy")
class Privacy extends LitElement {
  static styles = [styles];

  private i18n = new TranslationController(this, {scope:"auth"});

  render() {
    return html`
      <div class="privacy-container">
        <div class="privacy-wrap">
          <div class="privacy-title">${this.i18n.t("privacy.title")}</div>
          <textarea .readonly=${true} rows="200" cols="100">
1.	Introduction

  1.1	Truba.News, as provided by Technologies Trouvado Ltd, are committed to safeguarding the privacy of our website visitors and news service users.

  1.2	This policy applies where we are acting as a data controller with respect to the personal data of our website visitors and news service users; in other words, where we determine the purposes and means of the processing of that personal data.

  1.3	We use cookies on our website. These cookies are set only when you log in to the site. These cookies are necessary for the provision of our website and services, because they enable us to use the correct user profile when we process your searches and send you the results for your search and not another user’s. We will ask you to consent to our use of cookies when you sign up for our services. 

  1.4	When you signed up for our services we will ask you to give us your consent to process your personal data for specific purposes. You can specify whether you would like to receive the Daily Snap only, personalized news service only, or direct marketing communications from us. You can also set the privacy level of your account yourself, by logging in to your account on the truba.news website and you can delete your account. You can also contact us directly.

  1.5	In this policy, "we", "us" and "our" refer to Technologies Trouvado.


2.	Credit

  2.1	This document was created using a template from SEQ Legal (https://seqlegal.com).


3.	How we use your personal data

  3.1	In this Section 3 we have set out:
    (a)	the general categories of personal data that we may process;
    (b)	in the case of personal data that we did not obtain directly from you, the source and specific categories of that data;
    (c)	the purposes for which we may process personal data; and
    (d)	the legal bases of the processing.

  3.2	We may process data about your use of our website and services ("usage data"). The usage data may include your IP address, geographical location, browser type and version, operating system, referral source, length of visit, page views and website navigation paths, as well as information about the timing, frequency and pattern of your service use. The source of the usage data is Google Analytics. This usage data may be processed for the purposes of analysing the use of the website and services. The legal basis for this processing is our legitimate interests, namely monitoring and improving our website and services.

  3.3	We may process your account data ("account data").The account data may include your name and email address. The source of the account data is the data you entered when signing up for our services. The account data may be processed for the purposes of operating our website, providing our services – i.e. personalizing your search results, ensuring the security of our website and services, maintaining back-ups of our databases and communicating with you. The legal basis for this processing is consent.

  3.4	We may process your information included in your personal profile on our website ("profile data"). The profile data may include your name, email address, profile pictures, and any other information that you enter. The profile data may be processed for the purposes of enabling and monitoring your use of our website and services. The legal basis for this processing is consent.

  3.5	We may process your personal data that are provided in the course of the use of our services ("service data"). The service data may include articles that you click on, articles that you select, actions that you perform while using the search results, marking an article to read later, comments, posts, shares, and other actions that you take while you are logged in to the site. The source of the service data is you. The service data may be processed for the purposes of operating our website, providing our services, ensuring the security of our website and services, maintaining back-ups of our databases and communicating with you. The legal basis for this processing is consent.

  3.6	We may process information that you post for publication on our website or through our services ("publication data"). The publication data may be processed for the purposes of enabling such publication and administering our website and services. The legal basis for this processing is consent.

  3.7	We may process information contained in any enquiry you submit to us regarding goods and/or services ("enquiry data"). The enquiry data may be processed for the purposes of offering, marketing and selling relevant goods and/or services to you. The legal basis for this processing is our legitimate interests, namely the proper management of our customer relationships.

  3.8	We may process information relating to our customer relationships, including customer contact information ("customer relationship data"). The customer relationship data may include your name, your employer, your job title or role, your contact details. The source of the customer relationship data is you. The customer relationship data may be processed for the purposes of managing our relationships with customers, communicating with customers, keeping records of those communications and promoting our products and services to customers. The legal basis for this processing is our legitimate interests, namely the proper management of our customer relationships.

  3.9	We may in future process information relating to transactions, including purchases of goods and services, that you enter into with us and/or through our website ("transaction data"). The transaction data may include your contact details, your card details and the transaction details. The transaction data may be processed for the purpose of supplying the purchased goods and services and keeping proper records of those transactions. The legal basis for this processing is the performance of a contract between you and us and/or taking steps, at your request, to enter into such a contract and our legitimate interests, namely the proper administration of our website and business.

  3.10	We may process information that you provide to us for the purpose of subscribing to our email notifications and/or newsletters ("notification data"). The notification data may be processed for the purposes of sending you the relevant notifications and/or newsletters. The legal basis for this processing is consent.

  3.11	We may process information contained in or relating to any communication that you send to us ("correspondence data"). The correspondence data may include the communication content and metadata associated with the communication. Our website will generate the metadata associated with communications made using the website contact forms. The correspondence data may be processed for the purposes of communicating with you and record-keeping. The legal basis for this processing is our legitimate interests, namely the proper administration of our website and business and communications with users.

  3.12	We may process behavioral data. This data may include actions that you take interacting with our newsletters, website, or other communications, e.g. opening an email, clicking on a link within an email. The source of this data is you. This data may be processed for the purpose of us understanding your interactions with our content in order to personalize our services to you. The legal basis for this processing is our legitimate interests, namely provision of services.


  3.13	We may process any of your personal data identified in this policy where necessary for the establishment, exercise or defence of legal claims, whether in court proceedings or in an administrative or out-of-court procedure. The legal basis for this processing is our legitimate interests, namely the protection and assertion of our legal rights, your legal rights and the legal rights of others.

  3.14	We may process any of your personal data identified in this policy where necessary for the purposes of obtaining or maintaining insurance coverage, managing risks, or obtaining professional advice. The legal basis for this processing is our legitimate interests, namely the proper protection of our business against risks.

  3.15	In addition to the specific purposes for which we may process your personal data set out in this Section 3, we may also process any of your personal data where such processing is necessary for compliance with a legal obligation to which we are subject, or in order to protect your vital interests or the vital interests of another natural person.

  3.16	Please do not supply any other person's personal data to us, unless we prompt you to do so.


4.	Providing your personal data to others

  4.1	We may in future disclose your personal data to any member of our group of companies (this means our subsidiaries, our ultimate holding company and all its subsidiaries) insofar as reasonably necessary for the purposes, and on the legal bases, set out in this policy. At the moment, there are no other companies in our group of companies.

  4.2	We may disclose your personal data to our insurers and/or professional advisers insofar as reasonably necessary for the purposes of obtaining or maintaining insurance coverage, managing risks, obtaining professional advice, or the establishment, exercise or defence of legal claims, whether in court proceedings or in an administrative or out-of-court procedure.

  4.3	We may disclose usage data, account data, profile data, service data, publication data, enquiry data, customer relationship data, transaction data, notification data, correspondence data, behavioral data to our suppliers or subcontractors identified in Appendix A insofar as reasonably necessary for them to carry out their contract with us (e.g. we may disclose publication data to UX designers, customer relationship data to client and community managers).

  4.4	Financial transactions relating to our website and services may be handled by our payment services providers. We will share transaction data with our payment services providers only to the extent necessary for the purposes of processing your payments, refunding such payments and dealing with complaints and queries relating to such payments and refunds. We are not currently using any external payment service providers.

  4.5	If you enquire about one of our third-party suppliers we may disclose your enquiry data to one or more of those selected third party suppliers of goods and services identified on our website for the purpose of enabling them to contact you so that they can offer, market and sell to you relevant goods and/or services. Each such third party will act as a data controller in relation to the enquiry data that we supply to it; and upon contacting you, each such third party will supply to you a copy of its own privacy policy, which will govern that third party's use of your personal data.

  4.6	In addition to the specific disclosures of personal data set out in this Section 4, we may disclose your personal data where such disclosure is necessary for compliance with a legal obligation to which we are subject, or in order to protect your vital interests or the vital interests of another natural person. We may also disclose your personal data where such disclosure is necessary for the establishment, exercise or defence of legal claims, whether in court proceedings or in an administrative or out-of-court procedure.


5.	International transfers of your personal data

  5.1	In this Section 5, we provide information about the circumstances in which your personal data may be transferred to countries outside the European Economic Area (EEA).

  5.2	We are based in Canada. The European Commission has made an "adequacy decision" with respect to the data protection laws of Canada (https://ec.europa.eu/info/law/law-topic/data-protection/data-transfers-outside-eu/adequacy-protection-personal-data-non-eu-countries_en). 

  5.3	The hosting facilities for our website are situated in Canada. The European Commission has made an "adequacy decision" with respect to the data protection laws of Canada. 

  5.4	Google Analytics, Webflows, WordPress, and MailerLite are situated in the USA. The European Commission has made an "adequacy decision" with respect to the data protection laws of the USA. Transfers to the USA will be protected by appropriate safeguards, namely the use of standard data protection clauses adopted or approved by the European Commission, a copy of which can be obtained from https://ec.europa.eu/info/law/law-topic/data-protection/data-transfers-outside-eu/model-contracts-transfer-personal-data-third-countries_en.

  5.5	You acknowledge that personal data that you submit for publication through our website or services may be available, via the internet, around the world. We cannot prevent the use (or misuse) of such personal data by others.


6.	Retaining and deleting personal data

  6.1	This Section 6 sets out our data retention policies and procedure, which are designed to help ensure that we comply with our legal obligations in relation to the retention and deletion of personal data.

  6.2	Personal data that we process for any purpose or purposes shall not be kept for longer than is necessary for that purpose or those purposes.

  6.3	We will retain your personal data as follows:
    (a)	account data
    enquiry data
    customer relationship data
    transaction data
    correspondence data
    These data will be retained for a minimum period of 1 day following acquisition, and for a maximum period of 7 years if required to comply with financial reporting regulations. 

  6.4	In some cases it is not possible for us to specify in advance the periods for which your personal data will be retained. In such cases, we will determine the period of retention based on the following criteria:
    (a)	the period of retention of 
    usage data
    profile data
    service data
    publication data
    notification data
    behavioural data 
    will be determined based on lifetime of customer account.

  6.5	Notwithstanding the other provisions of this Section 6, we may retain your personal data where such retention is necessary for compliance with a legal obligation to which we are subject, or in order to protect your vital interests or the vital interests of another natural person.


7.	Amendments

  7.1	We may update this policy from time to time by publishing a new version on our website.

  7.2	You should check this page occasionally to ensure you are happy with any changes to this policy.

  7.3	We may notify you of significant changes to this policy by email or through the private messaging system on our website.


8.	Your rights

  8.1	In this Section 8, we have summarised the rights that you have under data protection law. Some of the rights are complex, and not all of the details have been included in our summaries. Accordingly, you should read the relevant laws and guidance from the regulatory authorities for a full explanation of these rights.

  8.2	Your principal rights under data protection law are:
    (a)	the right to access;
    (b)	the right to rectification;
    (c)	the right to erasure;
    (d)	the right to restrict processing;
    (e)	the right to object to processing;
    (f)	the right to data portability;
    (g)	the right to complain to a supervisory authority; and
    (h)	the right to withdraw consent.

  8.3	You have the right to confirmation as to whether or not we process your personal data and, where we do, access to the personal data, together with certain additional information. That additional information includes details of the purposes of the processing, the categories of personal data concerned and the recipients of the personal data. Providing the rights and freedoms of others are not affected, we will supply to you a copy of your personal data. The first copy will be provided free of charge, but additional copies may be subject to a reasonable fee. You can access your personal account by visiting the personal account section when logged into our website.

  8.4	You have the right to have any inaccurate personal data about you rectified and, taking into account the purposes of the processing, to have any incomplete personal data about you completed.

  8.5	In some circumstances you have the right to the erasure of your personal data without undue delay. Those circumstances include: the personal data are no longer necessary in relation to the purposes for which they were collected or otherwise processed; you withdraw consent to consent-based processing; you object to the processing under certain rules of applicable data protection law; the processing is for direct marketing purposes; and the personal data have been unlawfully processed. However, there are exclusions of the right to erasure. The general exclusions include where processing is necessary: for exercising the right of freedom of expression and information; for compliance with a legal obligation; or for the establishment, exercise or defence of legal claims.

  8.6	In some circumstances you have the right to restrict the processing of your personal data. Those circumstances are: you contest the accuracy of the personal data; processing is unlawful but you oppose erasure; we no longer need the personal data for the purposes of our processing, but you require personal data for the establishment, exercise or defence of legal claims; and you have objected to processing, pending the verification of that objection. Where processing has been restricted on this basis, we may continue to store your personal data. However, we will only otherwise process it: with your consent; for the establishment, exercise or defence of legal claims; for the protection of the rights of another natural or legal person; or for reasons of important public interest.

  8.7	You have the right to object to our processing of your personal data on grounds relating to your particular situation, but only to the extent that the legal basis for the processing is that the processing is necessary for: the performance of a task carried out in the public interest or in the exercise of any official authority vested in us; or the purposes of the legitimate interests pursued by us or by a third party. If you make such an objection, we will cease to process the personal information unless we can demonstrate compelling legitimate grounds for the processing which override your interests, rights and freedoms, or the processing is for the establishment, exercise or defence of legal claims.

  8.8	You have the right to object to our processing of your personal data for direct marketing purposes (including profiling for direct marketing purposes). If you make such an objection, we will cease to process your personal data for this purpose.

  8.9	You have the right to object to our processing of your personal data for scientific or historical research purposes or statistical purposes on grounds relating to your particular situation, unless the processing is necessary for the performance of a task carried out for reasons of public interest.

  8.10	To the extent that the legal basis for our processing of your personal data is:
    (a)	consent; or
    (b)	that the processing is necessary for the performance of a contract to which you are party or in order to take steps at your request prior to entering into a contract,
	    and such processing is carried out by automated means, you have the right to receive your personal data from us in a structured, commonly used and machine-readable format. However, this right does not apply where it would adversely affect the rights and freedoms of others.
  8.11	If you consider that our processing of your personal information infringes data protection laws, you have a legal right to lodge a complaint with a supervisory authority responsible for data protection. You may do so in the EU member state of your habitual residence, your place of work or the place of the alleged infringement.

  8.12	To the extent that the legal basis for our processing of your personal information is consent, you have the right to withdraw that consent at any time. Withdrawal will not affect the lawfulness of processing before the withdrawal.

  8.13	You may exercise any of your rights in relation to your personal data by written notice to us, in addition to the other methods specified in this Section 8.


9.	About cookies

  9.1	A cookie is a file containing an identifier (a string of letters and numbers) that is sent by a web server to a web browser and is stored by the browser. The identifier is then sent back to the server each time the browser requests a page from the server.

  9.2	Cookies may be either "persistent" cookies or "session" cookies: a persistent cookie will be stored by a web browser and will remain valid until its set expiry date, unless deleted by the user before the expiry date; a session cookie, on the other hand, will expire at the end of the user session, when the web browser is closed.

  9.3	Cookies do not typically contain any information that personally identifies a user, but personal information that we store about you may be linked to the information stored in and obtained from cookies.


10.	Cookies that we use

  10.1	We use cookies for the following purposes:
    (a)	Authentication - we use cookies to identify you when you visit our website and as you navigate our website (cookies used for this purpose are: authentication session cookies).
    (b)	Status - we use cookies to help us to determine if you are logged into our website (cookies used for this purpose are: status session cookies);
    (c)	Personalization - we use cookies to store information about your preferences and to personalise the website for you (cookies used for this purpose are: personalization cookies);
    (d)	Security - we use cookies as an element of the security measures used to protect user accounts, including preventing fraudulent use of login credentials, and to protect our website and services generally (cookies used for this purpose are: security cookies).

11.	Cookies used by our service providers

  11.1	Our service providers use cookies and those cookies may be stored on your computer when you visit our website.

  11.2	We use Google Analytics to analyse the use of our website. Google Analytics gathers information about website use by means of cookies. The information gathered relating to our website is used to create reports about the use of our website. Google's privacy policy is available at: https://www.google.com/policies/privacy/. The relevant cookies are: Google Analytics cookies.
    We do not collect any personally identifiable information through Google Analytics.

12.	Managing cookies

  12.1	Most browsers allow you to refuse to accept cookies and to delete cookies. The methods for doing so vary from browser to browser, and from version to version. You can however obtain up-to-date information about blocking and deleting cookies via these links:
    (a)	https://support.google.com/chrome/answer/95647?hl=en (Chrome);
    (b)	https://support.mozilla.org/en-US/kb/enable-and-disable-cookies-website-preferences (Firefox);
    (c)	http://www.opera.com/help/tutorials/security/cookies/ (Opera);
    (d)	https://support.microsoft.com/en-gb/help/17442/windows-internet-explorer-delete-manage-cookies (Internet Explorer);
    (e)	https://support.apple.com/kb/PH21411 (Safari); and
    (f)	https://privacy.microsoft.com/en-us/windows-10-microsoft-edge-and-privacy (Edge).

  12.2	Blocking all cookies will have a negative impact upon the usability of many websites.

  12.3	If you block cookies, you will not be able to use all the features on our website.


13.	Our details

  13.1	This website is owned and operated by Technologies Trouvado.

  13.2	We are registered in Quebec, Canada, under registration number 1173047060, and our registered office is at 202-2020 Rue Centre, Montreal, H3K 1J3.

  13.3	Our principal place of business is at CenTech, 400 Rue Montfort, Montreal, H3C 4J9.

  13.4	You can contact us:
    (a)	by post, to the postal address given above;
    (b)	using our website contact form;
    (c)	by telephone, on (514) 396-8800 ext.8480, the contact number published on our website from time to time; or
    (d)	by email, using the email address published on our website from time to time.


14.	Data protection officer

  14.1	We do not have a data protection officer, but you may contact CTO Fran Alexander fran.alexander@openreg.ca about any data-related issue.


Appendix A

  Suppliers and subcontractors we are using as at June 25th 2018:
    Google Analytics - GDPR compliant. 
    DigitalOcean - GDPR compliant
    Sendgrid - GDPR compliant. 
    Quickbooks - GDPR compliant. 
    GSuite Gmail - GDPR compliant. 
    Dropbox - GDPR compliant. 
</textarea
          >
        </div>
      </div>
    `;
  }
}

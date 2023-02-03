import { LitElement, html } from "lit";
import { customElement } from "lit/decorators.js";
import { TranslationController } from "@veryan/lit-spa";
import { styles } from "./terms.styles";

@customElement("app-terms")
class Terms extends LitElement {
  static styles = [styles];

  private i18n = new TranslationController(this);

  render() {
    return html`
      <div class="terms-container">
        <div class="terms-wrap">
          <div class="terms-title">${this.i18n.t("terms.title")}</div>
          <textarea .readonly=${true} rows="200" cols="100">
Truba.news is a news search service available on the World Wide Web and through other digital means. The service provides links to content on the original publishers' websites. Truba.news is a product owned by Technologies Trouvado Inc.


1. Language

  The parties acknowledge that they have requested and agree that this Agreement and all legal proceedings, notices, correspondence and other documents directly or indirectly related to the Agreement will be written in English.

  Les parties reconnaissent qu'elles ont exigé et consenti à ce que le présent Contrat ainsi que toute procédure, tout avis, toute communication et tout autre document s'y rapportant, directement ou indirectement, soient rédigés en anglais.


2. Your agreement with truba.news
  You understand and agree that, by visiting truba.news and its affiliated sites and by using the truba.news mobile apps, you are accepting, without modification, these Terms of Service. 
  
  If you do not agree with any portion of these Terms of Service, your only option is to discontinue use of truba.news and its mobile apps.
  
  In agreeing with these Terms of Service, you represent and warrant that you are at least eighteen (18) years of age or otherwise capable of entering into and performing legal agreements. If you are under eighteen (18) then you may only use truba.news with the consent of a parent or legal guardian.
  
  These Terms of Service include truba.news's Privacy Policy, located here: https://www.truba.news/privacy-policy, which is incorporated into these Terms of Service by reference and together with the Terms of Service governs your visit to truba.news and your use of its mobile apps. 
  
  The Privacy Policy explains truba.news's position on information gathering and how it intends to use and share any information it collects. Please read the Privacy Policy as you are agreeing to it when you agree to these Terms of Service.


3. Revisions to Terms of Service
  
  These Terms of Service are subject to revision from time to time by truba.news and your continued use of truba.news means you agree to, without modification, the revised Terms of Service. You can review revisions to these Terms of Service by regularly checking this page. Material revisions to these Terms of Service may be indicated by an updated effective date. 
  
  As a subscriber truba.news, it is your responsibility to remain apprised of any revisions to these Terms of Service and to remain in compliance with them. Should you object to any such revisions to these Terms of Service or become dissatisfied with truba.news in any way, your only recourse is to immediately terminate your membership and discontinue use of truba.news. 
  
  Otherwise, continuing to use the service and continuing to visit truba.news after the effective date means that you agree to be bound by any and all revisions.


4. Cost

  From time to time, and at truba.news's sole discretion, there may be certain content available via additional subscription or surcharge, and you will be alerted when any such charges apply if you have not already subscribed or agreed to the charges. 
      
  Charges for services may be changed at any time and at the sole discretion of truba.news or Technologies Trouvado Inc.
      
  
5. Registration and access; cancellation and automated renewal
  
  Access to most of the content, services and features on truba.news requires users to subscribe to truba.news and pay subscription fees. If you are subscribed to truba.news, you accept responsibility for all activities that occur under your account whether or not you expressly authorize such activities. 
      
  You are responsible for maintaining the confidentiality of your password and for restricting access to your computer so others may not access truba.news using your username or account in whole or in part. 
      
  You must notify us in writing immediately if you become aware of any disclosure of your password. You are responsible for any activity on our website arising out of any failure to keep your password confidential, and may be held liable for any losses arising out of such a failure. 
      
  Your user ID must not be liable to mislead; you must not use your account or user ID for or in connection with the impersonation of any person. 
      
  Truba.news may terminate your subscription and deny access to truba.news to any person for any reason at its sole discretion. 
      
  You will not compromise, or attempt to compromise, the security of your account. 
      
  Additionally and without limiting the generality of the preceding sentence, truba.news may terminate membership and deny access to truba.news to any person who, in truba.news's sole discretion, violates these Terms of Service. Such termination or denial of access shall be in addition to any remedies available to Truba.news and Technologies Trouvado Inc. in law and equity.
      
  For your convenience, your subscription will automatically renew after the initial term at the current rate unless you tell us to cancel. Notices of rate changes will be emailed or mailed to the subscriber billing address prior to the rate change effective date. You can cancel at any time by contacting us at info@truba.news or by selecting "Cancel Subscription" in the subject line at  HYPERLINK "http://www.truba.news/contact" www.truba.news/contact and submitting a completed form.
 

6. Copyright and other intellectual property rights
  
  Material published on truba.news and through other digital channels such as mobile apps, including articles, photos, Content Feeds, graphics, forum postings, audio and video clips, trademarks, service marks, and other content ("Content"), is copyrighted by Truba.news, or by other information providers. 
      
  You may not reproduce, republish or redistribute Content or any portions thereof, including, without limitation, Content provided by licensors and others, including member-submitted content, without the written consent of the copyright owner.
      
7. Permissions

  Subject to these Terms of Service, truba.news grants you permission to access truba.news and view the Content solely for your personal, non-commercial use. In addition to viewing Content online, you may electronically store a reasonable portion of truba.news Content for your personal, non-commercial use by making a single electronic copy on your computer's hard drive, or a single copy on a disk or other media or a single copy in printed form. You agree, however, that you will not store or archive a significant portion of the Content or create a database using the Content.


8.	Acceptable use

  8.1	You must not:
    (a)	use our website in any way or take any action that causes, or may cause, damage to the website or impairment of the performance, availability or accessibility of the website;
    (b)	use our website in any way that is unlawful, illegal, fraudulent or harmful, or in connection with any unlawful, illegal, fraudulent or harmful purpose or activity;
    (c)	use our website to copy, store, host, transmit, send, use, publish or distribute any material which consists of (or is linked to) any spyware, computer virus, Trojan horse, worm, keystroke logger, rootkit or other malicious computer software;
    (d)	conduct any systematic or automated data collection activities (including without limitation scraping, data mining, data extraction and data harvesting) on or in relation to our website without our express written consent;
    (e)	access or otherwise interact with our website using any robot, spider or other automated means, except for the purpose of search engine indexing;
    (f)	violate the directives set out in the robots.txt file for our website; or
    (g)	use data collected from our website for any direct marketing activity (including without limitation email marketing, SMS marketing, telemarketing and direct mailing).
  
  8.2	You must not use data collected from our website to contact individuals, companies or other persons or entities.
      
  8.3	You must ensure that all the information you supply to us through our website, or in relation to our website, is true, accurate, current, complete and non-misleading.
      
  8.4  You will not in any way infringe or misappropriate any of the intellectual property in and to the Content accessible through truba.news. This means you agree not to copy, modify, publish, transmit, create derivative works from, transfer, sell or display the Content, including logos, trademarks or service marks, or otherwise violate the proprietary rights of truba.news or others except as expressly permitted herein.
      
  8.5 You will not reuse, republish or otherwise distribute the Content or any modified or altered versions of it, whether over the World Wide Web or otherwise, and whether or not for payment, without the express written permission of Truba.news or a third-party copyright holder. The appearance of content on the truba.news site does not imply any transfer of rights from the original copyright holder. Truba.news provides links to access content directly from the original copyright holder according to their terms and conditions. The appearance of a link to content on truba.news does not automatically grant to subscribers any licensing or other rights, such rights and licenses needing to be obtained directly from the copyright holder.
      
  8.6 You will cooperate promptly and completely with any reasonable request by Technologies Trouvado Inc. or truba.news or any third party content provider related to an investigation of infringement of copyright or other proprietary right.
      
    To obtain permission to reuse or republish truba.news copyrighted material in any format, please contact info@truba.news.
      
    Truba.news cannot grant permission to reuse or republish material from other information providers. These information providers are intended third party beneficiaries of these terms and conditions and they may exercise all rights and remedies available to them. Please contact them directly to obtain permission. 
      
  8.7 If you believe that truba.news or any user of truba.news has infringed your copyright, please notify us and provide the following information:
    
    An identification of the copyrighted work that you claim has been infringed, or, if multiple copyrighted works at a single online site are covered by a single notification, a representative list of such works at that site.
      
    An identification of the material on truba.news that you claim is infringing or is subject to infringing activity that is to be removed or access to which is to be disabled, with enough detail (including without limitation the URL of the material) to allow us to locate the material on our site.
      
    Your name, address, telephone number and e-mail address.
      
    A statement by you that you have a good-faith belief that the disputed use is not authorized by the copyright owner, its agent or the law.
      
    A statement by you declaring that the above information in your Notice is accurate, made under penalty of perjury, and that you are authorized to act on behalf of the owner of an exclusive copyright interest involved.
      
    A physical or electronic signature of a person authorized to act on behalf of the owner of an exclusive right that is allegedly infringed.


9. Disclaimer and Limitation of Liability

  9.1 Disclaimer
    While truba.news strives for accuracy, it does not warrant or guarantee the accuracy or completeness of any information or database on our service. Nor does truba.news warrant or guarantee that any files available for downloading will be free of defects. Neither Truba.news nor any of the third party information providers will be liable in any way to you or to other parties for delays, inaccuracies, errors or omissions in material published in truba.news.
      
    The content, services, and features of truba.news are subject to change without notice. The inclusion of any content, services, and features on truba.news at a particular time does not imply or warrant that these products or services will be available at any time.
      
    While we take reasonable steps to ensure that no viruses, worms, Trojan horses or other destructive properties are present, the entire risk as to the quality and performance of truba.news and the accuracy and completeness of any information is with you.
      
  9.2 Opinions, advice and all other information expressed on truba.news represent the author's own views and are not necessarily those of truba.news.
    
    Truba.news does not endorse and is not responsible for statements, advice and opinions made by anyone other than authorized Technologies Trouvado Inc. spokespersons.
      
  9.3 Truba.news is not a regulated financial or legal advice service. Any investment decisions or other actions that users take based on information available on truba.news or in its mobile apps should first be reviewed by a competent and licensed financial adviser or other suitably qualified professional. 
      
  9.4 The truba.news service is provided on an "as is" and "as available" basis. we make no warranty of any kind, either express or implied, including without limitation, warranties of merchantability or fitness for a particular purpose or noninfringement, or warranties regarding the accuracy, reliability or completeness of the content or any other service or product on or related to the service (including any link to another web site or resource). 
      
  9.5 Limitation of Liability

    In no event will truba.news, Technologies Trouvado Inc., or their parents or affiliates be liable for (i) any incidental, consequential, or indirect damages (including, but not limited to, damages for loss of business profits, business interruption, loss of programs or information, and the like) arising out of the use of or inability to use truba.news, or any information or services provided on truba.news or in its mobile apps, even if truba.news has been advised of the possibility of such damages, or (ii) any claim attributable to errors, omissions, or other inaccuracies published on truba.news or in its mobile apps. 
      
    Technologies Trouvado Inc. and truba.news are not liable for any loss or damage caused, in whole or in part, by any errors or omissions that it may make when entering, compiling, interpreting, presenting, drafting, communicating, updating or delivering the information contained in any truba.news product. Without limiting the effect of the foregoing, Technologies Trouvado Inc. and truba.news's cumulative liability for any claim arising from the direct or indirect use of any truba.news service arising out of or in connection with these terms of service or the site, whether in contract, tort (including negligence, product liability or other theory), warranty or otherwise,  may not exceed the cost of the subscription.
 

10. Indemnity
      
  You will defend, indemnify, and hold harmless truba.news, Technologies Trouvado Inc. and their parents and affiliates from: (i) your use of and access of truba.news; (ii) your violation of any of these Terms of Service; (iii) your violation of any third-party right including any copyright, trademark, trade secret, or privacy right related to any content submitted by you (if applicable) or your use of the website. This defense and indemnification obligation will survive the term and your use of truba.news.


11. Miscellaneous

  11.1 Termination

    We may terminate these Terms of Service, your account, or your access to truba.news at any time with or without notice to you. You may terminate these Terms of Service or your account by discontinuing your use of truba.news and cancelling your subscription payments.
      
  11.2 Jurisdiction

    This agreement between truba.news and its users will be governed and interpreted under the laws of the province of Quebec, Canada. Courts located in Quebec, Canada have jurisdiction in any dispute arising from these Terms of Service.
      
    In the event that any provision of these Terms of Service is found to be in conflict with the law, such provision shall be restated to reflect the original intent, and all other terms and conditions shall remain in full force and effect.
      
  11.3 Dispute Resolution and Arbitration

    You and Truba.news agree to the following dispute resolution process for any legal controversy or legal claim arising out of or relating to these Terms of Service, truba.news, any subscription to Truba.news or truba.news or any other aspect of our relationship ("Subject Legal Claim").
    
    In an attempt to find the quickest and most efficient resolution of our issues, you and Truba.news agree to first discuss any issue informally for at least 30 days. To do that, please send your full name and contact information, your concern and your proposed solution by mail to us at: Truba.news, Technologies Trouvado Inc, CenTech, 400 Rue Montfort, Montreal, QC, H3C 4J9. If we should need to discuss an issue with you, we will contact you using the email or mailing address on your account.
    
    If the dispute cannot be resolved through good faith negotiations between the parties within a reasonable time, the parties agree that their dispute will be submitted to mediation in accordance with the mediation rules as agreed to by the parties. 
    
    Any dispute settled by the parties through mediation must be documented in writing. Should such mediation settlement modify the terms of the Agreement, the amendment must be recorded in writing, signed by the parties and appended to the Agreement. 
    
    Should the mediation process set out above herein fail, any claim arising from the Agreement that is contested, any dispute relating to its performance, including its cancellation as well as any litigation arising from the interpretation of the Agreement must be submitted to arbitration to the exclusion of the courts of law. The parties agree that the provisions of articles 620 et seq. of the Quebec Code of Civil Procedure, CQLR c C-25.01 that are currently in force will govern any arbitration held under this Section.
  
  11.4 Electronic Signature
    
    The parties agree that the Agreement may be transmitted by facsimile, e-mail or similar forms of communication. The parties further agree that signatures duplicated by facsimile, electronic signature or similar means of authentication will be treated as originals, it being understood that any party who does so must provide the other party with a copy of the Agreement bearing its original signature, immediately upon demand.
      
  11.5 Severability
  
    If any provision of these Terms of Service shall be deemed unlawful, void or for any reason unenforceable, then that provision shall be deemed severable from these Terms of Service and shall not affect the validity and enforceability of any remaining provisions.
      
    If any unlawful and/or unenforceable provision of these terms and conditions would be lawful or enforceable if part of it were deleted, that part will be deemed to be deleted, and the rest of the provision will continue in effect. 
      
  11.6 Complete Agreement

    These Terms of Service represents the complete agreement concerning the subject matter hereof between the parties and supersedes all prior and contemporaneous agreements and understandings between them, whether written or oral.
      
  11.7 Force Majeure

    Neither party will be liable for any failure to perform any obligation (other than payment obligations) hereunder, or from any delay in the performance thereof, due to causes beyond its control, including industrial disputes of whatever nature, acts of God, public enemy, acts of government, failure of telecommunications, fire or other casualty.
      
  11.8 Void Where Prohibited by Law

    These Terms of Service are void where prohibited by law, and the right to access truba.news is revoked in such jurisdictions.
      
  11.9 Independent Contractors

    The parties hereto are independent contractors, and these Terms of Service creates no partnership, joint venture, agency, franchise, sales representative or employment relationship between the parties. You have no authority to make or accept any offers or representations on our behalf and you shall not make any statement, on your Site (if any) or otherwise, that conflicts with these Terms of Service.

    A contract under these terms and conditions is for our benefit and your benefit, and is not intended to benefit or be enforceable by any third party.

    The exercise of the parties' rights under a contract under these terms and conditions is not subject to the consent of any third party.

  11.10 You hereby agree that we may assign, transfer, sub-contract or otherwise deal with our rights and/or obligations under these terms and conditions. 
    
    You may not without our prior written consent assign, transfer, sub-contract or otherwise deal with any of your rights and/or obligations under these terms and conditions. 
     

12.	Statutory and regulatory disclosures

  This website is owned and operated by Technologies Trouvado Inc. 
      
  We are registered in Quebec, Canada, under registration number 1173047060, and our registered office is at 202-2020 Rue Centre, Montreal, H3K 1J3. 
      
  Our principal place of business is at CenTech, 400 Rue Montfort, Montreal, H3C 4J9. 
      
  You can contact us: 
    (a) by post, to the postal address given above; 
    (b) using our website contact form; 
    (c) by telephone, on (514) 396-8800 ext.8480, the contact number published on our website from time to time; or 
    (d) by email, using the email address published on our website from time to time. 
    </textarea>
        </div>
      </div>
    `;
  }
}

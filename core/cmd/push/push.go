package main

import (
	"encoding/json"
	"log"
	"os"

	"core/internal/story"
	"core/internal/user"

	webpush "github.com/SherClockHolmes/webpush-go"
)

var languages = []string{"en", "fr"}

func main() {
	log.Printf("Started Push Service")
	for _, language := range languages {
		news := story.GetPublicStories(language)
		if len(news) == 0 {
			log.Printf("There's not stories to email for the Daily Snap")
			return
		}
		emails := user.GetUserEmails(language)
		user.SendDailySnapEmail(emails, news)
		subscriptions := user.GetUserSubscriptions(language)
		data := map[string]map[string]string{
			"notification": {
				"title": news[0].Title,
				"icon":  "assets/truba-logo-square.svg",
			},
		}
		message, err := json.Marshal(data)
		if err != nil {
			log.Println("error:", err)
			return
		}
		for _, subscription := range subscriptions {
			sendPushNotification(subscription, message)
		}
	}
}

func sendPushNotification(subscription string, notification []byte) {
	s := &webpush.Subscription{}
	json.Unmarshal([]byte(subscription), s)
	resp, err := webpush.SendNotification(notification, s, &webpush.Options{
		Subscriber:      "mailto:info@truba.news",
		VAPIDPublicKey:  os.Getenv("PUBLIC_VAPID"),
		VAPIDPrivateKey: os.Getenv("PRIVATE_VAPID"),
		TTL:             30,
	})
	if err != nil {
		return
	}
	defer resp.Body.Close()
}

package main

import (
	"encoding/json"
	"log"
	"os"

	"core/internal/story"
	"core/internal/user"
	"core/internal/utils"

	webpush "github.com/SherClockHolmes/webpush-go"
)

var languages = []string{"en", "fr"}

func main() {
	log.Printf("Started Push Service")
	for _, language := range languages {
		news, err := story.GetPublicStories(language)
		if err != nil {
			utils.LogError(err)
			return
		}
		if len(news) == 0 {
			log.Printf("There's no stories to email for the Daily Snap")
			return
		}
		emails := user.GetUserEmails(language)
		user.SendDailySnapEmail(emails, news)
		subscriptions, err := user.GetUserSubscriptions(language)
		if err != nil {
			utils.LogError(err)
			return
		}
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
		pushOptions := webpush.Options{
			Subscriber:      "mailto:info@truba.news",
			VAPIDPublicKey:  os.Getenv("PUBLIC_VAPID"),
			VAPIDPrivateKey: os.Getenv("PRIVATE_VAPID"),
			TTL:             30,
		}
		for _, userSub := range subscriptions {
			sendPushNotification(userSub.Subscription, message, &pushOptions)
		}
	}
}

func sendPushNotification(subscription *webpush.Subscription, notification []byte, pushOptions *webpush.Options) {
	resp, err := webpush.SendNotification(notification, subscription, pushOptions)
	if err != nil {
		utils.LogError(err)
		return
	}
	defer resp.Body.Close()
}

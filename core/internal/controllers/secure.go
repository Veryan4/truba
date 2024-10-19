package controllers

import (
	"log"
	"net/http"

	"core/internal/feedback"
	"core/internal/story"
	"core/internal/tasks"
	"core/internal/user"

	"github.com/golang-jwt/jwt"
	"github.com/google/uuid"
	"github.com/gorilla/mux"
	"github.com/hibiken/asynq"
)

func SecureRoutes(r *mux.Router, queueClient *asynq.Client) *mux.Router {

	r.HandleFunc("/users/me", Chain(func(w http.ResponseWriter, r *http.Request) {
		userId := r.Context().Value("tokenSub").(string)
		currentUser, err := user.GetUserById(userId)
		if err != nil {
			RespondWithError(w, 500, "User not found")
			return
		}
		RespondWithJSON(w, http.StatusOK, map[string]user.User{"user": currentUser})
	}, Secure(), Method("GET")))

	r.HandleFunc("/users", Chain(func(w http.ResponseWriter, r *http.Request) {
		userId := r.Context().Value("tokenSub").(string)
		var updateUser user.User
		ok := DecodeJSON(w, r, &updateUser)
		if !ok {
			return
		}
		if updateUser.UserId != userId {
			RespondWithError(w, 401, "You may only update your user")
			return
		}
		currentUser, err := user.UpdateUser(updateUser)
		if err != nil {
			RespondWithError(w, 500, "Failed to updated user")
			return
		}
		RespondWithJSON(w, http.StatusOK, map[string]user.User{"user": currentUser})
	}, Secure(), Method("PUT")))

	r.HandleFunc("/users/email", Chain(func(w http.ResponseWriter, r *http.Request) {
		userId := r.Context().Value("tokenSub").(string)
		currentUser, err := user.GetUserById(userId)
		if err != nil {
			RespondWithError(w, 500, "User not found")
			return
		}
		currentUser.IsEmailSubscribed = true
		updatedUser, err := user.UpdateUser(currentUser)
		if err != nil {
			RespondWithError(w, 500, "Failed to updated user")
			return
		}
		RespondWithJSON(w, http.StatusOK, map[string]user.User{"user": updatedUser})
	}, Secure(), Method("GET")))

	r.HandleFunc("/google/{token}", Chain(func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		token := vars["token"]
		currentUser, err := user.GoogleTokenCheck(token)
		if err != nil {
			RespondWithError(w, 401, "Failed token check")
			return
		}
		accessToken, er := user.CreateAccessToken(jwt.MapClaims{"sub": currentUser.UserId}, 0)
		if er != nil {
			RespondWithError(w, 500, "Failed to create access token")
			return
		}
		RespondWithJSON(w, http.StatusOK, map[string]any{"token": accessToken, "user": currentUser})
	}, Method("GET")))

	r.HandleFunc("/token", Chain(func(w http.ResponseWriter, r *http.Request) {
		username := r.FormValue("username")
		password := r.FormValue("passowrd")
		currentUser, err := user.AuthenticateUser(username, password)
		if err != nil {
			RespondWithError(w, 401, "Failed to Authenticate")
			return
		}
		accessToken, er := user.CreateAccessToken(jwt.MapClaims{"sub": currentUser.UserId}, 0)
		if er != nil {
			RespondWithError(w, 500, "Failed to create access token")
			return
		}
		RespondWithJSON(w, http.StatusOK, map[string]any{"token": accessToken, "user": currentUser})
	}, Secure(), Method("POST")))

	r.HandleFunc("/user/info/{language}", Chain(func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		language := vars["language"]
		userId := r.Context().Value("tokenSub").(string)
		personalization, err := user.GetPersonalization(userId, language)
		if err != nil {
			RespondWithError(w, 500, err.Error())
			return
		}
		RespondWithJSON(w, http.StatusOK, personalization)
	}, Secure(), Method("GET")))

	r.HandleFunc("/recommended-news/{language}", Chain(func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		language := vars["language"]
		userId := r.Context().Value("tokenSub").(string)
		stories, err := story.GetRecommendedStories(userId, language)
		if err != nil {
			RespondWithError(w, 500, err.Error())
			return
		}
		RespondWithJSON(w, http.StatusOK, stories)
	}, Secure(), Method("GET")))

	r.HandleFunc("/single-article/{language}", Chain(func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		language := vars["language"]
		var notIdList []uuid.UUID
		ok := DecodeJSON(w, r, &notIdList)
		if !ok {
			return
		}
		story, err := story.GetSingleStory(notIdList, language)
		if err != nil {
			RespondWithError(w, 204, "No story found")
			return
		}
		RespondWithJSON(w, http.StatusOK, story)
	}, Secure(), Method("POST")))

	r.HandleFunc("/feedback", Chain(func(w http.ResponseWriter, r *http.Request) {
		userId := r.Context().Value("tokenSub").(string)
		var userFeedback feedback.UserFeedback
		ok := DecodeJSON(w, r, &userFeedback)
		if !ok {
			return
		}
		userFeedback.UserId = userId
		task, err := tasks.NewStoreUserFeedbackTask(userFeedback)
		if err != nil {
			RespondWithError(w, 500, "Could not create NewStoreUserFeedbackTask")
			return
		}
		info, err := queueClient.Enqueue(task)
		if err != nil {
			RespondWithError(w, 500, "Could not enqueue NewStoreUserFeedbackTask")
			return
		}
		log.Printf("enqueued task: id=%s queue=%s", info.ID, info.Queue)
		RespondWithJSON(w, http.StatusOK, map[string]string{"StoreUserFeedback": "Job Queued"})
	}, Secure(), Method("POST")))

	r.HandleFunc("/favorite/{collection}", Chain(func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		collection := vars["collection"]
		dbCollection, err := user.GetFavoriteCollection(collection)
		if err != nil {
			RespondWithError(w, 404, "Favorite collection not found")
			return
		}
		var favorite user.Favorite
		ok := DecodeJSON(w, r, &favorite)
		if !ok {
			return
		}
		userId := r.Context().Value("tokenSub").(string)
		favorite.UserId = userId
		ok2 := user.UpdateFromUser(favorite, dbCollection)
		if !ok2 {
			RespondWithError(w, 500, "Failed to update favorite sources")
			return
		}
		RespondWithJSON(w, http.StatusOK, map[string]string{"result": "Updated user favortie sources"})
	}, Secure(), Method("POST")))

	return r
}

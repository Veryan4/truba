package controllers

import (
	"net/http"

	"core/internal/story"
	"core/internal/user"

	"github.com/golang-jwt/jwt"
	"github.com/gorilla/mux"
	"github.com/hibiken/asynq"
)

func PublicRoutes(r *mux.Router, queueClient *asynq.Client) *mux.Router {

	r.HandleFunc("/news/{language}", Chain(func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		language := vars["language"]
		subscriptions, err := story.GetPublicStories(language)
		if err != nil {
			RespondWithError(w, 500, err.Error())
			return
		}
		RespondWithJSON(w, http.StatusOK, subscriptions)
	}, Method("GET")))

	r.HandleFunc("/users", Chain(func(w http.ResponseWriter, r *http.Request) {
		var createUser user.CreateUser
		ok := DecodeJSON(w, r, &createUser)
		if !ok {
			return
		}
		createdUser, e := user.AddUser(createUser)
		if e != nil {
			RespondWithError(w, http.StatusBadRequest, "Failed to Create User")
			return
		}
		accessToken, er := user.CreateAccessToken(jwt.MapClaims{"sub": createdUser.UserId}, 0)
		if er != nil {
			RespondWithError(w, 500, "Failed to create access token")
			return
		}
		RespondWithJSON(w, http.StatusOK, map[string]any{"token": accessToken, "user": createdUser})
	}, Method("POST")))

	r.HandleFunc("/forgot_password", Chain(func(w http.ResponseWriter, r *http.Request) {
		var forgotPasswordRequest user.ForgotPasswordRequest
		ok := DecodeJSON(w, r, &forgotPasswordRequest)
		if !ok {
			return
		}
		e := user.ForgotPassword(forgotPasswordRequest.Email)
		if e != nil {
			RespondWithError(w, http.StatusBadRequest, "Failed to Handle forgot password request")
			return
		}
		RespondWithJSON(w, http.StatusOK, map[string]string{"message": "Succesfully Sent Frogot Password Email"})
	}, Method("POST")))

	r.HandleFunc("/reset_password", Chain(func(w http.ResponseWriter, r *http.Request) {
		var resetPasswordRequest user.ResetPasswordRequest
		ok := DecodeJSON(w, r, &resetPasswordRequest)
		if !ok {
			return
		}
		currentUser, e := user.ResetPassword(resetPasswordRequest.Token, resetPasswordRequest.NewPassword)
		if e != nil {
			RespondWithError(w, 401, "Failed to reset password")
			return
		}
		accessToken, er := user.CreateAccessToken(jwt.MapClaims{"sub": currentUser.UserId}, 0)
		if er != nil {
			RespondWithError(w, 500, "Failed to create access token")
			return
		}
		RespondWithJSON(w, http.StatusOK, map[string]any{"token": accessToken, "user": currentUser})
	}, Method("POST")))

	r.HandleFunc("/unsubscribe/{user_email}", Chain(func(w http.ResponseWriter, r *http.Request) {
		vars := mux.Vars(r)
		userEmail := vars["user_email"]
		ok := user.UnsubscribeUserEmail(userEmail)
		if ok {
			RespondWithError(w, 500, "Failed to unsubscribe user")
			return
		}
		RespondWithJSON(w, http.StatusOK, map[string]string{"message": "Succesfully Unsubscribed"})
	}, Method("GET")))

	return r
}

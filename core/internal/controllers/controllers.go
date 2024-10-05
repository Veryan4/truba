package controllers

import (
	"context"
	"core/internal/user"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"strings"
	"time"
)

var WwwDomain = os.Getenv("APP_WWW_URL")
var AppDomain = os.Getenv("APP_URL")
var IsProd = os.Getenv("ENVIRONMENT") == "production"

type Middleware func(http.HandlerFunc) http.HandlerFunc

func Chain(f http.HandlerFunc, middlewares ...Middleware) http.HandlerFunc {
	for _, m := range middlewares {
		f = m(f)
	}
	return f
}

func Method(m string) Middleware {
	return func(f http.HandlerFunc) http.HandlerFunc {
		return func(w http.ResponseWriter, r *http.Request) {
			if r.Method != m && r.Method != "OPTIONS" {
				http.Error(w, http.StatusText(http.StatusBadRequest), http.StatusBadRequest)
				return
			}
			f(w, r)
		}
	}
}

func LoggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		defer func() { log.Println(r.URL.Path, time.Since(start)) }()
		next.ServeHTTP(w, r)
	})
}

func CORSMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Add("Access-Control-Allow-Methods", "POST, GET, OPTIONS, PUT, DELETE")
		w.Header().Add("Access-Control-Allow-Headers", "content-type")
		w.Header().Add("Access-Control-Max-Age", "86400")
		origin := r.Header.Get("Origin")
		if origin == WwwDomain || origin == AppDomain {
			w.Header().Add("Access-Control-Allow-Origin", origin)
			next.ServeHTTP(w, r)
			return
		}
		if !IsProd && (origin == "localhost:3000" || origin == "localhost:4200") {
			w.Header().Add("Access-Control-Allow-Origin", origin)
		}
		next.ServeHTTP(w, r)
	})
}

func Secure() Middleware {
	return func(f http.HandlerFunc) http.HandlerFunc {
		return func(w http.ResponseWriter, r *http.Request) {
			reqToken := r.Header.Get("Authorization")
			splitToken := strings.Split(reqToken, "Bearer ")
			if len(splitToken) != 2 {
				RespondWithError(w, 401, "Invalid Token")
				return
			}
			tokenSub, err := user.GetTokenSub(splitToken[1])
			if err != nil {
				RespondWithError(w, 401, "Invalid Token")
				return
			}
			ctx := context.WithValue(r.Context(), "tokenSub", tokenSub)
			newReq := r.WithContext(ctx)
			f(w, newReq)
		}
	}
}

func RespondWithError(w http.ResponseWriter, code int, message string) {
	RespondWithJSON(w, code, map[string]string{"error": message})
}

func RespondWithJSON(w http.ResponseWriter, code int, payload interface{}) {
	response, _ := json.Marshal(payload)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	w.Write(response)
}

func DecodeJSON(w http.ResponseWriter, r *http.Request, value interface{}) bool {
	decoder := json.NewDecoder(r.Body)
	err := decoder.Decode(value)
	defer r.Body.Close()
	if err != nil {
		RespondWithError(w, http.StatusBadRequest, "Invalid request payload")
		return false
	}
	return true
}

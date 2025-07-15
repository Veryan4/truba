package controllers

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"core/internal/user"
	"core/internal/utils"

	"github.com/mark3labs/mcp-go/mcp"
)

var WwwDomain = os.Getenv("APP_WWW_URL")
var AppDomain = os.Getenv("APP_URL")
var IsProd = os.Getenv("ENVIRONMENT") == "production"

type Middleware func(http.HandlerFunc) http.HandlerFunc

type contextKey string

const contextTokenKey = contextKey("tokenSub")

func Chain(f http.HandlerFunc, middlewares ...Middleware) http.HandlerFunc {
	for _, m := range middlewares {
		f = m(f)
	}
	return f
}

func Method(m string) Middleware {
	return func(f http.HandlerFunc) http.HandlerFunc {
		return func(w http.ResponseWriter, r *http.Request) {
			if r.Method == "OPTIONS" {
				w.WriteHeader(http.StatusOK)
				return
			}
			if r.Method != m {
				http.Error(w, "Invalid Method", http.StatusBadRequest)
				return
			}
			f(w, r)
		}
	}
}

func LoggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		defer func() { log.Println(r.Method+" "+r.URL.Path, time.Since(start)) }()
		next.ServeHTTP(w, r)
	})
}

func CORSMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Add("Access-Control-Allow-Methods", "GET, PUT, POST, PATCH, DELETE, OPTIONS")
		w.Header().Add("Access-Control-Allow-Headers", "Origin, Content-Length, Content-Type, Authorization")
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
			splitToken := strings.Split(reqToken, "Bearer")
			if len(splitToken) != 2 {
				RespondWithError(w, 401, "Invalid Token")
				return
			}
			reqToken = strings.TrimSpace(splitToken[1])
			tokenSub, err := user.GetTokenSub(reqToken)
			if err != nil {
				RespondWithError(w, 401, "Invalid Token")
				return
			}
			ctx := context.WithValue(r.Context(), contextTokenKey, tokenSub)
			newReq := r.WithContext(ctx)
			f(w, newReq)
		}
	}
}

func TokenSubFromRequest(r *http.Request) string {
	return r.Context().Value(contextTokenKey).(string)
}

func RespondWithError(w http.ResponseWriter, code int, message string) {
	defer func() {
		s := fmt.Sprintf("%n "+message, code)
		log.Println(s)
	}()
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
	if err != nil {
		utils.LogError(err)
		RespondWithError(w, http.StatusBadRequest, "Invalid request payload: "+err.Error())
		return false
	}
	return true
}

func mcpResourceWithJSON(uri string, payload interface{}) (mcp.ResourceContents, error) {
	jsonBytes, _ := json.Marshal(payload)
	jsonString := string(jsonBytes[:])

	return mcp.TextResourceContents{
		URI:      uri,
		MIMEType: "application/json",
		Text:     jsonString,
	}, nil
}

func McpResourceResponseWithJSON(uri string, payload interface{}) ([]mcp.ResourceContents, error) {
	resourceResponse, _ := mcpResourceWithJSON(uri, payload)

	return []mcp.ResourceContents{
		resourceResponse,
	}, nil
}

func McpToolResponseWithJSON(text string, uri string, payload interface{}) (*mcp.CallToolResult, error) {
	resource, err := mcpResourceWithJSON(uri, payload)
	if err != nil {
		return mcp.NewToolResultError(err.Error()), nil
	}
	return mcp.NewToolResultResource(text, resource), nil
}

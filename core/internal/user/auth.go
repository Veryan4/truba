package user

import (
	"context"
	"crypto/rand"
	"os"
	"time"

	"core/internal/utils"

	"github.com/golang-jwt/jwt"
	"golang.org/x/crypto/bcrypt"
	"google.golang.org/api/idtoken"
)

const ENCRYPTION_ALGORITHM string = "HS256"
const RESET_PASSWORD_TOKEN_EXPIRE_MINUTES = 15
const ACCESS_TOKEN_EXPIRE_DAYS = 3

type ForgotPasswordRequest struct {
	Email string `bson:"email,omitempty" json:"email,omitempty"`
}

type ResetPasswordRequest struct {
	Token       string `bson:"token,omitempty" json:"token,omitempty"`
	NewPassword string `bson:"new_password,omitempty" json:"new_password,omitempty"`
}

func HashPassword(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), 14)
	return string(bytes), err
}

func AuthenticateUser(emailAddress string, password string) (User, error) {
	currentUser, err := GetUserByEmail(emailAddress)
	if err != nil {
		return User{}, err
	}
	err2 := bcrypt.CompareHashAndPassword([]byte(currentUser.HashedPassword), []byte(password))
	if err2 != nil {
		return User{}, err
	}
	return currentUser, nil
}

func CreateAccessToken(data jwt.MapClaims) (string, error) {
	claims := data
	claims["exp"] = time.Now().AddDate(0, 0, ACCESS_TOKEN_EXPIRE_DAYS).Unix()
	t := jwt.NewWithClaims(jwt.GetSigningMethod(ENCRYPTION_ALGORITHM), claims)
	return t.SignedString([]byte(os.Getenv("JWT_SECRET")))
}

func CreateAccessTokenWithExpiry(data jwt.MapClaims, expiresDelta time.Duration) (string, error) {
	claims := data
	claims["exp"] = time.Now().Add(expiresDelta).Unix()
	t := jwt.NewWithClaims(jwt.GetSigningMethod(ENCRYPTION_ALGORITHM), claims)
	return t.SignedString([]byte(os.Getenv("JWT_SECRET")))
}

func GoogleTokenCheck(token string) (User, error) {
	decodedToken, err := idtoken.Validate(context.Background(), token, os.Getenv("GOOGLE_CLIENT_ID"))
	if err != nil {
		return User{}, utils.LogError(err)
	}
	return FindOrCreateUser(decodedToken.Claims["email"].(string), decodedToken.Claims["name"].(string))
}

func ForgotPassword(userEmail string) error {
	currentUser, err := GetUserByEmail(userEmail)
	if err != nil {
		return utils.LogError(err)
	}
	resetPasswordTokenExpires := time.Duration(RESET_PASSWORD_TOKEN_EXPIRE_MINUTES) * time.Minute
	randomByteCount := 20
	randomBytes := make([]byte, randomByteCount)
	_, er := rand.Read(randomBytes)
	if er != nil {
		return utils.LogError(er)
	}
	randomByteString := string(randomBytes[:])
	resetPasswordToken, err := CreateAccessTokenWithExpiry(jwt.MapClaims{"sub": randomByteString}, resetPasswordTokenExpires)
	if err != nil {
		return utils.LogError(err)
	}
	updatedUser, e := UpdateResetPasswordToken(currentUser, resetPasswordToken)
	if e != nil {
		return utils.LogError(e)
	}
	url := os.Getenv("APP_URL") + "/password?token=" + resetPasswordToken
	err = SendForgotPasswordEmail(updatedUser.Email, url)
	if err != nil {
		return utils.LogError(err)
	}
	return nil
}

func ResetPassword(tokenString string, newPassword string) (User, error) {
	tokenSub, err := GetTokenSub(tokenString)
	if err != nil {
		return User{}, utils.LogError(err)
	}
	currentUser, er := ResetPasswordByToken(tokenSub, newPassword)
	if er != nil {
		return User{}, utils.LogError(er)
	}
	e := SendResetPasswordEmail(currentUser.Email)
	if e != nil {
		return User{}, utils.LogError(e)
	}
	return currentUser, nil
}

func GetTokenSub(tokenString string) (string, error) {
	token, err := jwt.ParseWithClaims(tokenString, jwt.MapClaims{}, func(token *jwt.Token) (interface{}, error) {
		return []byte(os.Getenv("JWT_SECRET")), nil
	})
	if err != nil {
		return "", utils.LogError(err)
	}
	claims := token.Claims.(jwt.MapClaims)
	return claims["sub"].(string), nil
}

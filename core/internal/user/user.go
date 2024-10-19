package user

import (
	"time"

	"core/internal/dbs"
	"core/internal/utils"

	"github.com/google/uuid"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
)

const userCollection string = "User"

type User struct {
	Id                 *primitive.ObjectID `bson:"_id,omitempty" json:"_id,omitempty"`
	UserId             string              `bson:"user_id,omitempty" json:"user_id,omitempty"`
	UserName           string              `bson:"username,omitempty" json:"username,omitempty"`
	Email              string              `bson:"email,omitempty" json:"email,omitempty"`
	Disabled           bool                `bson:"disabled,omitempty" json:"disabled,omitempty"`
	Language           string              `bson:"language,omitempty" json:"language,omitempty"`
	IsAdmin            bool                `bson:"is_admin,omitempty" json:"is_admin,omitempty"`
	IsPersonalized     bool                `bson:"is_personalized,omitempty" json:"is_personalized,omitempty"`
	HasPersonalization bool                `bson:"has_personalization,omitempty" json:"has_personalization,omitempty"`
	RatedCount         int                 `bson:"rated_count,omitempty" json:"rated_count,omitempty"`
	TermsConsent       *string             `bson:"terms_consent,omitempty" json:"terms_consent,omitempty"`
	Subscription       *interface{}        `bson:"subscription,omitempty" json:"subscription,omitempty"`
	IsEmailSubscribed  bool                `bson:"is_email_subscribed,omitempty" json:"is_email_subscribed,omitempty"`
	HashedPassword     string              `bson:"hashed_password,omitempty" json:"-"`
	ResetPasswordBytes string              `bson:"reset_password_bytes,omitempty" json:"-"`
}

type CreateUser struct {
	UserName     string  `bson:"username,omitempty" json:"username,omitempty"`
	Email        string  `bson:"email,omitempty" json:"email,omitempty"`
	Password     string  `bson:"password,omitempty" json:"password,omitempty"`
	TermsConsent *string `bson:"terms_consent,omitempty" json:"terms_consent,omitempty"`
	Language     string  `bson:"language,omitempty" json:"language,omitempty"`
}

func AddUser(createUser CreateUser) (User, error) {
	mongoFilter := bson.M{"email": createUser.Email}
	var currentUser User
	e := dbs.GetSingle(userCollection, mongoFilter, &currentUser)
	if e != nil {
		return User{}, utils.LogError("User already exists")
	}
	uid, err := uuid.NewUUID()
	if err != nil {
		return User{}, err
	}
	hasedPassword, err := HashPassword(createUser.Password)
	if err != nil {
		return User{}, err
	}
	newUser := User{
		UserId:         uid.String(),
		UserName:       createUser.UserName,
		Email:          createUser.Email,
		HashedPassword: hasedPassword,
		TermsConsent:   createUser.TermsConsent,
	}
	result := dbs.AddOrUpdateOne(userCollection, newUser)
	if result == 0 {
		return User{}, utils.LogError("Failed to creat User in DB")
	}
	SendUserInitEmail(createUser.Email)
	er := dbs.GetSingle(userCollection, bson.M{"email": createUser.Email}, &currentUser)
	return currentUser, er
}

func UpdateUser(userUpdate User) (User, error) {
	mongoFilter := bson.M{"user_id": userUpdate.UserId}
	var currentUser User
	err := dbs.GetSingle(userCollection, mongoFilter, &currentUser)
	if err != nil {
		return User{}, utils.LogError("User doesn't exist in DB")
	}
	currentUser.HasPersonalization = userUpdate.HasPersonalization
	currentUser.IsPersonalized = userUpdate.IsPersonalized
	currentUser.IsEmailSubscribed = userUpdate.IsEmailSubscribed
	if userUpdate.Language != "" {
		currentUser.Language = userUpdate.Language
	}
	if userUpdate.UserName != "" {
		currentUser.UserName = userUpdate.UserName
	}
	if userUpdate.Subscription != nil {
		currentUser.Subscription = userUpdate.Subscription
	}
	result := dbs.AddOrUpdateOne(userCollection, currentUser)
	if result == 0 {
		return User{}, utils.LogError("Failed to update User in DB")
	}
	return currentUser, nil
}

func FindOrCreateUser(userEmail string, userName string) (User, error) {
	mongoFilter := bson.M{"email": userEmail}
	var currentUsers []User
	err := dbs.GetMany(userCollection, mongoFilter, &currentUsers)
	if err != nil {
		return User{}, err
	}
	if len(currentUsers) > 0 {
		return currentUsers[0], nil
	}
	uid, err := uuid.NewUUID()
	if err != nil {
		return User{}, err
	}
	puid, err := uuid.NewUUID()
	if err != nil {
		return User{}, err
	}
	hasedPassword, err := HashPassword(puid.String())
	if err != nil {
		return User{}, err
	}
	now := time.Now().String()
	newUser := User{
		UserId:         uid.String(),
		UserName:       userName,
		Email:          userEmail,
		HashedPassword: hasedPassword,
		TermsConsent:   &now,
	}
	result := dbs.AddOrUpdateOne(userCollection, newUser)
	if result > 0 {
		SendUserInitEmail(userEmail)
		var currentUser User
		err := dbs.GetSingle(userCollection, mongoFilter, &currentUser)
		return currentUser, err
	}
	return User{}, utils.LogError("failed to create user")
}

func GetUserIds() []string {
	return dbs.GetDistinctValues(userCollection, bson.M{}, "user_id")
}

func GetUserEmails(language string) []string {
	mongoFilter := bson.M{"language": language, "is_email_subscribed": true}
	return dbs.GetDistinctValues(userCollection, mongoFilter, "email")
}

func GetUserSubscriptions(language string) []string {
	mongoFilter := bson.M{"language": language}
	return dbs.GetDistinctValues(userCollection, mongoFilter, "subscription")
}

func GetUserById(userId string) (User, error) {
	mongoFilter := bson.M{"user_id": userId}
	var currentUser User
	err := dbs.GetSingle(userCollection, mongoFilter, &currentUser)
	return currentUser, err
}

func GetUserByEmail(userEmail string) (User, error) {
	mongoFilter := bson.M{"email": userEmail}
	var currentUser User
	err := dbs.GetSingle(userCollection, mongoFilter, &currentUser)
	return currentUser, err
}

func UnsubscribeUserEmail(userEmail string) bool {
	currentUser, err := GetUserByEmail(userEmail)
	if err != nil {
		return false
	}
	currentUser.IsEmailSubscribed = false
	return dbs.AddOrUpdateOne(userCollection, currentUser) > 1
}

func UpdateResetPasswordToken(currentUser User, randomBytes string) (User, error) {
	currentUser.ResetPasswordBytes = randomBytes
	if dbs.AddOrUpdateOne(userCollection, currentUser) > 1 {
		return currentUser, nil
	}
	return User{}, utils.LogError("Failed to update User reset token")
}

func ResetPasswordByToken(randomBytes string, password string) (User, error) {
	mongoFilter := bson.M{"reset_password_bytes": randomBytes}
	hasedPassword, err := HashPassword(password)
	if err != nil {
		return User{}, err
	}
	var currentUser User
	er := dbs.GetSingle(userCollection, mongoFilter, &currentUser)
	if er != nil {
		return User{}, er
	}
	currentUser.HashedPassword = hasedPassword
	currentUser.ResetPasswordBytes = ""
	if dbs.AddOrUpdateOne(userCollection, currentUser) > 1 {
		return currentUser, nil
	}
	return User{}, utils.LogError("Failed to update User password")
}

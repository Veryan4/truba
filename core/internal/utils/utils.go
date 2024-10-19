package utils

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"
)

func LogError(str string, extras ...any) error {
	s := fmt.Sprintf(str, extras...)
	log.Print(s)
	return errors.New(s)
}

func LogJSON(data interface{}) {
	bytes, err := json.MarshalIndent(data, "", "    ")
	if err != nil {
		log.Print(err.Error())
		return
	}
	log.Print(string(bytes))
}

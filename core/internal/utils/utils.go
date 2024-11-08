package utils

import (
	"encoding/json"
	"log"
)

func LogError(err error) error {
	log.Print(err.Error())
	return err
}

func LogJSON(data interface{}) {
	bytes, err := json.MarshalIndent(data, "", "    ")
	if err != nil {
		log.Print(err.Error())
		return
	}
	log.Print(string(bytes))
}

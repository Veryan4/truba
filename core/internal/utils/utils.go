package utils

import (
	"errors"
	"fmt"
	"log"
)

func LogError(str string, extras ...any) error {
	s := fmt.Sprintf(str, extras...)
	log.Printf(s)
	return errors.New(s)
}

package dbs

import (
	"fmt"
	"os"

	"github.com/adjust/rmq/v5"
	"github.com/redis/go-redis/v9"
)

var rdb = redis.NewClient(&redis.Options{
	Addr:     os.Getenv("REDIS_HOSTNAME") + ":" + os.Getenv("REDIS_PORT"),
	Password: "", // no password set
	DB:       0,  // use default DB
})
var WorkerQueue = getWorkerQueueConnection()
var RedisWorkerErrorChannel = make(chan error)

func getWorkerQueueConnection() rmq.Connection {
	connection, err := rmq.OpenConnectionWithRedisClient(os.Getenv("REDIS_QUEUE"), rdb, RedisWorkerErrorChannel)
	if err != nil {
		close(RedisWorkerErrorChannel)
		fmt.Println("Failed to connect to Redis Queue")
		panic(err)
	}
	return connection
}

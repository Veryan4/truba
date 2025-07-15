package main

import (
    "context"
    "fmt"
    "github.com/mark3labs/mcphost/sdk"
)

func main() {
    ctx := context.Background()
    
    // Create MCPHost instance with default configuration
    host, err := sdk.New(ctx, nil)
    if err != nil {
        panic(err)
    }
    defer host.Close()
    
    // Send a prompt and get response
    response, err := host.Prompt(ctx, "What is 2+2?")
    if err != nil {
        panic(err)
    }
    
    fmt.Println(response)
}
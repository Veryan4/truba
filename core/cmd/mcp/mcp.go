package main

import (
	"fmt"

	"core/internal/controllers"

	"github.com/mark3labs/mcp-go/server"
)

func main() {
	s := server.NewMCPServer(
		"news",
		"1.0.0",
		server.WithToolCapabilities(true),
		server.WithRecovery(),
	)

	controllers.McpTools(s)

	if err := server.ServeStdio(s); err != nil {
		fmt.Printf("Server error: %v\n", err)
	}
}

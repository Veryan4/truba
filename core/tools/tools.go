//go:build tools
// +build tools

package main

import (
	"fmt"
	"os"
	"strings"

	"github.com/oapi-codegen/oapi-codegen/v2/pkg/codegen"
	"github.com/oapi-codegen/oapi-codegen/v2/pkg/util"
)

func main() {
	models := []string{
		"Source",
		"Author",
		"Keyword",
		"Entity",
		"Story",
		"DataSet",
		"ScrapedUrl",
	}
	for _, model := range models {
		GenerateModel(model)
	}
}

func GenerateModel(modelName string) {
	config := codegen.Configuration{
		PackageName: "models",
		Generate: codegen.GenerateOptions{
			Models: true,
		},
		OutputOptions: codegen.OutputOptions{
			SkipPrune: true,
		},
		ImportMapping: map[string]string{
			"./Author.yaml":     "-",
			"./DataSet.yaml":    "-",
			"./Entity.yaml":     "-",
			"./Keyword.yaml":    "-",
			"./ScrapedUrl.yaml": "-",
			"./Source.yaml":     "-",
			"./Story.yaml":      "-",
		},
	}
	swagger, err := util.LoadSwagger("../schemas/" + modelName + ".yaml")
	if err != nil {
		errExit("error loading swagger spec in %s\n: %s\n", modelName+".yaml", err)
	}

	for _, schema := range swagger.Components.Schemas {
		for propKey, prop := range schema.Value.Properties {
			tags := map[string]any{
				"bson": propKey + ",omitempty",
			}
			if prop.Value.Extensions == nil {
				prop.Value.Extensions = map[string]any{
					"x-oapi-codegen-extra-tags": tags,
				}
			} else {
				prop.Value.Extensions["x-oapi-codegen-extra-tags"] = tags
			}
		}
	}

	if strings.HasPrefix(swagger.OpenAPI, "3.1.") {
		fmt.Println("WARNING: You are using an OpenAPI 3.1.x specification, which is not yet supported by oapi-codegen (https://github.com/oapi-codegen/oapi-codegen/issues/373) and so some functionality may not be available. Until oapi-codegen supports OpenAPI 3.1, it is recommended to downgrade your spec to 3.0.x")
	}

	code, err := codegen.Generate(swagger, config)
	if err != nil {
		errExit("error generating code: %s\n", err)
	}

	err = os.WriteFile("./internal/models/"+strings.ToLower(modelName)+"_model.go", []byte(code), 0o644)
	if err != nil {
		errExit("error writing generated code to file: %s\n", err)
	}
}

func errExit(format string, args ...interface{}) {
	if !strings.HasSuffix(format, "\n") {
		format = format + "\n"
	}
	_, _ = fmt.Fprintf(os.Stderr, format, args...)
	os.Exit(1)
}

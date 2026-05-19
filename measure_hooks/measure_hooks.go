package main

import (
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"log"
)

func main() {
	// The path to Mattermost's public plugin hooks interface
	filePath := "./public/plugin/hooks.go"
	
	fset := token.NewFileSet()
	node, err := parser.ParseFile(fset, filePath, nil, 0)
	if err != nil {
		log.Fatalf("Failed to parse file: %v", err)
	}

	hookCount := 0

	// Traverse the Abstract Syntax Tree looking for the 'Hooks' interface
	ast.Inspect(node, func(n ast.Node) bool {
		typeSpec, ok := n.(*ast.TypeSpec)
		if ok && typeSpec.Name.Name == "Hooks" {
			if interfaceType, ok := typeSpec.Type.(*ast.InterfaceType); ok {
				// Count the number of methods defined in the interface
				hookCount = len(interfaceType.Methods.List)
				fmt.Println("======================================")
				fmt.Printf("Total Unique Plugin Hooks Supported: %d\n", hookCount)
				fmt.Println("======================================")
			}
		}
		return true
	})
}
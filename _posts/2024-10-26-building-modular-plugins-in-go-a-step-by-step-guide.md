---
title: "Building Modular Plugins in Go: A Step-by-Step Guide"
layout: single

description: "Learn how to build modular plugins in Go using Go modules with this step-by-step guide. Discover best practices for creating, organizing, and managing plugins to enhance application extensibility and maintainability."
tags:
- application extensibility
- building
- go
- go modules
- go plugins
- maintainability
- modular design
- modules
- plugins
---

## Introduction

Go modules have become the standard way to manage dependencies in Go projects, bringing a more robust and scalable approach to package management. While most developers use Go modules for standard applications, many are unaware that they can also be leveraged to build modular plugins—dynamic components that can extend the functionality of a core application without recompiling the main binary. In this blog post, we'll explore how to build plugins in Go using Go modules, and walk through a step-by-step example that demonstrates this powerful feature.

## What Are Go Plugins?

Go plugins allow you to build separate binaries that can be loaded at runtime into a Go application using the `plugin` package. Plugins are especially useful for building extensible systems where new features can be added without modifying or redeploying the main application. For example, text editors, IDEs, or frameworks often use plugins to enable third-party developers to add custom functionality.

However, Go plugins are currently only supported on Linux and macOS platforms (as of Go 1.21), and they require careful handling to ensure compatibility between the core application and the plugin binaries.

## Using Go Modules with Plugins

Go modules provide versioned dependency management, enabling you to modularize and maintain plugin packages effectively. When building plugins, Go modules help ensure that both the core application and plugins share compatible versions of dependencies. This becomes essential when multiple plugins are developed independently but must work together within the same host application.

Let's see how to structure a system that uses Go modules for building and managing plugins.

## Step 1: Define a Common Interface

To allow the main application to interact with plugins, we need to define a common interface that both the application and plugins will use. This interface should be in a separate Go module so it can be shared and versioned independently.

Create a new Go module called `github.com/yourusername/plugin-interface`:

```go
// plugin-interface/greeter.go
package greeter

type Greeter interface {
    Greet(name string) string
}
```

Then, publish or reference this module locally in your main application and plugins.

## Step 2: Set Up the Host Application

The host application will load plugins at runtime and invoke their methods. Let's create the main application module:

```bash
go mod init github.com/yourusername/host-app
```

Ensure it imports the interface module:

```go
import (
    "github.com/yourusername/plugin-interface/greeter"
)
```

Here's a simplified version of the host application:

```go
package main

import (
    "fmt"
    "plugin"
    "github.com/yourusername/plugin-interface/greeter"
)

func main() {
    // Open the plugin file
    plug, err := plugin.Open("greeter_plugin.so")
    if err != nil {
        panic(err)
    }

    // Lookup the Greeter symbol
    greeterSymbol, err := plug.Lookup("Greeter")
    if err != nil {
        panic(err)
    }

    // Type assert it to the Greeter interface
    greeter, ok := greeterSymbol.(greeter.Greeter)
    if !ok {
        panic("Unexpected type from module symbol")
    }

    fmt.Println(greeter.Greet("Alice"))
}
```

This code loads a plugin file named `greeter_plugin.so` and looks for a symbol called `Greeter` that implements the `greeter.Greeter` interface.

## Step 3: Build a Plugin Module

Now let's create a plugin that implements the `Greeter` interface. First, create a separate Go module:

```bash
go mod init github.com/yourusername/greeter-plugin
```

Ensure it imports the shared interface module:

```go
import (
    "github.com/yourusername/plugin-interface/greeter"
)
```

Implement the interface:

```go
package main

import (
    "github.com/yourusername/plugin-interface/greeter"
)

type EnglishGreeter struct{}

func (g EnglishGreeter) Greet(name string) string {
    return "Hello, " + name
}

// Greeter is the exported symbol
var Greeter greeter.Greeter = EnglishGreeter{}
```

To build the plugin, use the following command:

```bash
go build -o greeter_plugin.so -buildmode=plugin
```

This creates a shared object file that the host application can load at runtime.

## Step 4: Managing Dependencies with Go Modules

One of the key advantages of using Go modules is that both the host and the plugin can import the exact same version of the interface package. This ensures type compatibility at runtime.

If you're not publishing the interface module to a public repository, you can use Go's `replace` directive in your `go.mod` files to reference it locally:

```go
replace github.com/yourusername/plugin-interface => ../plugin-interface
```

This allows you to develop and test the interface and plugins simultaneously without needing a remote repository.

## Step 5: Plugin Discovery and Loading

In a real-world scenario, your host application may need to discover and load multiple plugins from a directory. Here's an example of how you could implement plugin discovery:

```go
func loadPlugins(dir string) []greeter.Greeter {
    var greeters []greeter.Greeter
    files, _ := os.ReadDir(dir)
    
    for _, file := range files {
        if !strings.HasSuffix(file.Name(), ".so") {
            continue
        }

        plug, err := plugin.Open(dir + "/" + file.Name())
        if err != nil {
            continue
        }

        symbol, err := plug.Lookup("Greeter")
        if err != nil {
            continue
        }

        if g, ok := symbol.(greeter.Greeter); ok {
            greeters = append(greeters, g)
        }
    }
    return greeters
}
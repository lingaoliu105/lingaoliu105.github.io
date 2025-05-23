---
title: "Minimal APIs versus Controllers in ASP.NET Core"
layout: single
description: "Explore the differences between Minimal APIs and Controllers in ASP.NET Core including performance structure and use cases for modern web development."
tags:
  - apis
  - asp.net
  - asp.net core
  - controllers
  - core
  - minimal
  - minimal apis
  - performance
  - web development
---

# Minimal APIs versus Controllers in ASP.NET Core

When building web APIs in ASP.NET Core, developers are presented with two primary styles of defining endpoints: the **traditional controller-based approach** and the newer **Minimal APIs** introduced in ASP.NET Core 6. Each has its own strengths, use cases, and developer experience trade-offs. In this post, we'll compare these two models, explore their benefits and drawbacks, and help you decide when to use each.

## Introduction to the Two Approaches

ASP.NET Core has long been known for its flexibility and performance, especially for building RESTful services. Traditionally, developers have built APIs using **Controllers** — classes that inherit from `ControllerBase` and define actions with attribute routing, model binding, filters, and other features. This model is powerful, scalable, and well-suited for large applications.

With the release of .NET 6, Microsoft introduced **Minimal APIs**, a lightweight and modern alternative that allows developers to define endpoints using a more functional and streamlined syntax. This model reduces boilerplate code and emphasizes convention-based routing and lambda-style handlers.

Let's explore the differences and see where each approach shines.

## Controllers: The Established Way

Controllers have been the backbone of ASP.NET MVC and Web API since the early days. In ASP.NET Core, they're still the preferred way to structure complex applications with a need for rich features like:

- Action filters (authorization, logging, etc.)
- Model validation and binding
- Dependency injection via constructors
- Built-in support for content negotiation (JSON/XML)
- Organized routing by controller and convention

Here's a simple controller example:

```csharp
[ApiController]
[Route("[controller]")]
public class WeatherForecastController : ControllerBase
{
    [HttpGet]
    public IActionResult Get()
    {
        return Ok(new { Message = "Hello from controller" });
    }
}
```

Controllers are great when:

- You have a large application with many endpoints
- You need to apply cross-cutting concerns like authentication or logging
- You're following a domain-driven or layered architecture
- You prefer separation of concerns and testability via dependency injection

With controllers, you can also take advantage of features like `ModelState` validation, action results, and middleware filters in a structured way.

## Minimal APIs: The Lightweight Alternative

Minimal APIs provide a new way to build HTTP endpoints with minimal ceremony. They're ideal for small services, microservices, or APIs with few endpoints, where you want to avoid the overhead of creating controller classes and action methods.

The same endpoint shown above can be written using Minimal APIs like this:

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/weather", () => Results.Ok(new { Message = "Hello from minimal API" }));

app.Run();
```

This concise syntax removes the need for controllers, actions, or attribute routing — everything is handled inline.

Minimal APIs are great when:

- You're building a small, focused API or microservice
- You want to avoid unnecessary boilerplate
- You're experimenting or building a prototype quickly
- You prefer a functional approach to defining endpoints

They're also useful for embedding API logic directly in `Program.cs`, making them ideal for projects using the new C# top-level statements model.

## Key Differences

### 1. **Boilerplate and Verbosity**

Controllers require multiple layers of setup: creating a class, inheriting from `ControllerBase`, applying attributes, and writing action methods. Minimal APIs eliminate this by allowing endpoint definitions directly in the app pipeline.

### 2. **Routing and Conventions**

Controller routing is typically attribute-based (`[HttpGet]`, `[Route]`, etc.) or convention-based via route templates in `Startup.cs` or `Program.cs`. Minimal APIs use **code-defined routes** with a fluent API like `app.MapGet()`, `app.MapPost()`, etc., which allows more control at runtime.

### 3. **Dependency Injection**

Controllers use constructor injection for dependencies:

```csharp
public class ProductsController : ControllerBase
{
    private readonly IProductService _productService;

    public ProductsController(IProductService productService)
    {
        _productService = productService;
    }

    [HttpGet]
    public async Task<IActionResult> GetAll() => Ok(await _productService.GetAllAsync());
}
```

Minimal APIs support parameter injection directly in the handler:

```csharp
app.MapGet("/products", async (IProductService service) => 
    Results.Ok(await service.GetAllAsync()));
```

This is a cleaner way to inject only the dependencies needed for a specific endpoint.

### 4. **Filters and Middleware**

Controllers support action filters and authorization attributes directly on methods or classes:

```csharp
[Authorize]
[HttpGet]
public IActionResult Get() => Ok(new { Message = "Secured endpoint" });
```

Minimal APIs use middleware and endpoint filters instead. You can add middleware globally or per-endpoint:

```csharp
app.MapGet("/secure", () => "Hello")
    .AddEndpointFilter(async (context, next) =>
    {
        // Custom filter logic
        return await next(context);
    });
```

For authentication, you can integrate policies via the `RequireAuthorization()` method:

```csharp
app.MapGet("/secure", () => "Authorized")
    .RequireAuthorization();
```

This makes security and cross-cutting logic more flexible but less declarative than controller attributes.

### 5. **Testability and Maintainability**

Controllers are more testable out of the box. Since they're classes with methods, you can easily instantiate them in unit tests, mock dependencies, and verify behavior.

Minimal APIs are more **inline and functional**, which can make unit testing a bit more challenging. However, with proper architectural patterns — like separating business logic from endpoint handlers — you can still maintain testability.

## Performance and Startup Time

Minimal APIs
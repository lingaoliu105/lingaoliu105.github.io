---
title: "new and override in C#"
layout: single

description: "Exploring the differences between `new` and `override` keywords in C# for method hiding and polymorphism."
tags:
  - c#
---

Credit: the contents are from [https://blog.csdn.net/jinsikui/article/details/5924841]().

For a programmer that's more familiar with the OOP in Java, the various behaviour controled by those keywords is quiet confusing. What's even more horrible, the official explanations from Microsoft ([https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/knowing-when-to-use-override-and-new-keywords]()) made it even more confusing for me. Luckily a table that I found helped to make things clear:

| `A child = new B()` | no modifier                                                                        | `abstract`                                    | `virtual`                                                       |
| --------------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------- | ----------------------------------------------------------------- |
| no modifier           | Warning. Recommend using `new`. Call `A.x()`                                   | Compile error. Abstract method not implemented. | Warning. Recommend using `override` or `new`. Call `A.x()` |
| `override`          | Compile error. Parent's method must be `virtual` / `abstract` / `override` | Call `B.x()`                                  | Call `B.x()`                                                    |
| `new`               | Call `A.x()`                                                                     | Compile error. Abstract method not implemented. | Call `A.x()`                                                    |

| `B child = new B()` | no modifier                                                                        | `abstract`                                    | `virtual`                                                       |
| --------------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------- | ----------------------------------------------------------------- |
| no modifier           | Warning. Recommend using `new`. Call `A.x()`                                   | Compile error. Abstract method not implemented. | Warning. Recommend using `override` or `new`. Call `A.x()` |
| `override`          | Compile error. Parent's method must be `virtual` / `abstract` / `override` | Call `B.x()`                                  | Call `B.x()`                                                    |
| `new`               | Call `B.x()`                                                                     | Compile error. Abstract method not implemented. | Call `B.x()`                                                    |

Before fully understanding the design phylosophy of C#, this table can be used for a quick reference.

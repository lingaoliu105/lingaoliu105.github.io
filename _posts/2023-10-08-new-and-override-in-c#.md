---
title: C# abstract? virtual? new? override? in one table


layout: single


post-image: "https://th.bing.com/th/id/R.36a6263d2b08e9f9e01ccec32002311a?rik=9Ch%2ffsDlGxw7cw&riu=http%3a%2f%2fwww.maxcsharp.com%2fwp-content%2fuploads%2f2021%2f07%2fcsharplogo.png&ehk=KM58kkhfP%2bHjMWsNUpVJv%2f9Tn0V2SaKDFiWm9rZ4T%2fA%3d&risl=&pid=ImgRaw&r=0"


description: Thanks for the original author to make things clear


tags:


- Unity


- C#
---
Credit: the contents are from [https://blog.csdn.net/jinsikui/article/details/5924841]().

For a programmer that's more familiar with the OOP in Java, the various behaviour controled by those keywords is quiet confusing. What's even more horrible, the official explanations from Microsoft ([https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/knowing-when-to-use-override-and-new-keywords]()) made it even more confusing for me. Luckily a table that I found helped to make things clear:

| `A child = new B()` | no modifier                                                                        | `abstract`                                    | `virtual`                                                       |
| --------------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------- | ----------------------------------------------------------------- |
| no modifier           | Warning. Recommend using `new`. Call `A.x()`                                   | Compile error. Abstract method not implemented. | Warning. Recommend using `override` or `new`. Call `A.x()` |
| `override`          | Compile error. Parent's method must be `virtual` / `abstract` / `override` | Call `B.x()`                                  | Call `B.x()`                                                    |
| `new`               | Call `A.x()`                                                                     | Compile error. Abstract method not implemented. | Call `A.x()`                                                    |

| `B child = new B()` | no modifier                                                                        | `abstract`                                    | `virtual`                                                       |
| --------------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------- | ----------------------------------------------------------------- |
| no modifier           | Warning. Recommend using `new`. Call `A.x()`                                   | Compile error. Abstract method not implemented. | Warning. Recommend using `override` or `new`. Call `A.x()` |
| `override`          | Compile error. Parent's method must be `virtual` / `abstract` / `override` | Call `B.x()`                                  | Call `B.x()`                                                    |
| `new`               | Call `B.x()`                                                                     | Compile error. Abstract method not implemented. | Call `B.x()`                                                    |

Before fully understanding the design phylosophy of C#, this table can be used for a quick reference.

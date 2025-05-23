---
title: "LNK2001 Encountered Again"
layout: single
description: "Troubleshooting another LNK2001 error in a C++ project."
tags:
  - c++
  - unreal engine
  - visual studio
---
An issue that's pretty much simillar as the previous one, where the log is like:



```
Module.ActionRogueLike.cpp.obj : error LNK2001: 无法解析的外部符号 "public: virtual void __cdecl IGameplayTaskOwnerInterface::OnGameplayTaskActivated(class UGameplayTask &)" (?OnGameplayTaskActivated@IGameplayTaskOwnerInterface@@UEAAXAEAVUGameplayTask@@@Z) [D:\MyProjects\FirstUnrealProject\Intermediate\ProjectFiles\ActionRogueLike.vcxproj]
Module.ActionRogueLike.cpp.obj : error LNK2001: 无法解析的外部符号 "public: virtual void __cdecl IGameplayTaskOwnerInterface::OnGameplayTaskDeactivated(class UGameplayTask &)" (?OnGameplayTaskDeactivated@IGameplayTaskOwnerInterface@@UEAAXAEAVUGameplayTask@@@Z) [D:\MyProjects\FirstUnrealProject\Intermediate\ProjectFiles\ActionRogueLike.vcxproj]

```


(No LNK 2009, only LNK 2001 this time).


Tried to find the issue in code just like yesterday, but the complaining code is from UE source code.
However, it turned out that it's a different cause this time:


* The module required is not included.
Add `"GameplayTasks"` in the `{projectName}.Build.cs` file resolves the issue:


```cpp
PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "InputCore","GameplayTasks","AIModule" });
```

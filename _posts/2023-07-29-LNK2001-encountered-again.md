---
title: LNK 2001 errors AGAIN? But different cause!

layout: single

post-image: "https://res.cloudinary.com/startup-grind/image/upload/c_fill,dpr_2.0,f_auto,g_center,h_1080,q_100,w_1080/v1/gcs/platform-data-epic/events/ue4.png"

description: Past experiences may not always apply.

tags:

- Unreal Engine

- C++

- Visual Studio
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

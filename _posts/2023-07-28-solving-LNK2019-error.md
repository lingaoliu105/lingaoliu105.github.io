---
title: Encountered LNK 2019 and LNK 2001 errors when building UE project

layout: single

post-image: "https://res.cloudinary.com/startup-grind/image/upload/c_fill,dpr_2.0,f_auto,g_center,h_1080,q_100,w_1080/v1/gcs/platform-data-epic/events/ue4.png"

description: A small problem for me as a fresh UE C++ developer

tags:

- Unreal Engine

- C++

- Visual Studio
---
I recently changed my projectiles hierachy of my Unreal game, moving some declarations of hit and overlap event handler into the base class. To enable polymophism, I declared those functions as `virtual` , but since UE doesn't allow UCLASS classes to have pure virtual functions, I did not give it a value or a definition. Just left them like:

```cpp
UFUNCTION()
virtual void OnActorOverLap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
                            UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep,
                            const FHitResult& SweepResult);
UFUNCTION()
virtual void OnActorHit(UPrimitiveComponent* HitComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
                        FVector NormalImpulse, const FHitResult& Hit);
```

That's why the issue occurs.

When trying to build, there are several error messages like:

```
LMagicProjectile.gen.cpp.obj : error LNK2019: 无法解析的外部符号 "protected: void __cdecl ALMagicProjectile::OnActorOverLap(class UPrimitiveComponent *,class AActor *,class UPrimitiveComponent *,int,bool,struct FHitResult const &)" (?OnActorOverLap@ALMagicProjectile@@IEAAXPEAVUPrimitiveComponent@@PEAVAActor@@0H_NAEBUFHitResult@@@Z)，函数 "public: static void __cdecl ALMagicProjectile::execOnActorOverLap(class UObject *,struct FFrame &,void * const)" (?execOnActorOverLap@ALMagicProjectile@@SAXPEAVUObject@@AEAUFFrame@@QEAX@Z) 中引用了该符号 [D:\MyProjects\FirstUnrealProject\Intermediate\ProjectFiles\ActionRogueLike.vcxproj]
LMagicProjectile.cpp.obj : error LNK2001: 无法解析的外部符号 "protected: void __cdecl ALMagicProjectile::OnActorOverLap(class UPrimitiveComponent *,class AActor *,class UPrimitiveComponent *,int,bool,struct FHitResult const &)" (?OnActorOverLap@ALMagicProjectile@@IEAAXPEAVUPrimitiveComponent@@PEAVAActor@@0H_NAEBUFHitResult@@@Z) [D:\MyProjects\FirstUnrealProject\Intermediate\ProjectFiles\ActionRogueLike.vcxproj]
LMagicProjectile.gen.cpp.obj : error LNK2019: 无法解析的外部符号 "protected: void __cdecl ALMagicProjectile::OnActorHit(class UPrimitiveComponent *,class AActor *,class UPrimitiveComponent *,struct UE::Math::TVector<double>,struct FHitResult const &)" (?OnActorHit@ALMagicProjectile@@IEAAXPEAVUPrimitiveComponent@@PEAVAActor@@0U?$TVector@N@Math@UE@@AEBUFHitResult@@@Z)，函数 "public: static void __cdecl ALMagicProjectile::execOnActorHit(class UObject *,struct FFrame &,void * const)" (?execOnActorHit@ALMagicProjectile@@SAXPEAVUObject@@AEAUFFrame@@QEAX@Z) 中引用了该符号 [D:\MyProjects\FirstUnrealProject\Intermediate\ProjectFiles\ActionRogueLike.vcxproj]
LMagicProjectile.cpp.obj : error LNK2001: 无法解析的外部符号 "protected: void __cdecl ALMagicProjectile::OnActorHit(class UPrimitiveComponent *,class AActor *,class UPrimitiveComponent *,struct UE::Math::TVector<double>,struct FHitResult const &)" (?OnActorHit@ALMagicProjectile@@IEAAXPEAVUPrimitiveComponent@@PEAVAActor@@0U?$TVector@N@Math@UE@@AEBUFHitResult@@@Z) [D:\MyProjects\FirstUnrealProject\Intermediate\ProjectFiles\ActionRogueLike.vcxproj]

```

Huge chunks of nonsense (at least for me right now)...

Thanks to the troubleshooting provided by Microsoft : [https://learn.microsoft.com/en-us/cpp/error-messages/tool-errors/linker-tools-error-lnk2019?view=msvc-170&amp;source=recommendations]()

I realized the function declarations above seem to be wrong: I cannot leave them without any definition.

So I added some simplest inline empty definition:

```cpp
UFUNCTION()
virtual void OnActorOverLap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
                            UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep,
                            const FHitResult& SweepResult)
{
}

UFUNCTION()
virtual void OnActorHit(UPrimitiveComponent* HitComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp,
                        FVector NormalImpulse, const FHitResult& Hit)
{
}
```


This time it finally works!

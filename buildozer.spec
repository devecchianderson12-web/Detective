[app]
title = División Especial de Detectives
package.name = detective
package.domain = org.ceibal.ded
source.dir = .
source.include_exts = py,png,jpg,gif,ogg,wav,ttf,dat,tcs,tcl,tcd,yaml,ico
source.exclude_dirs = .github,bin,.buildozer
version = 1.07
requirements = python3==3.10.12,hostpython3==3.10.12,pygame,numpy,pyyaml
orientation = landscape
fullscreen = 1
icon.filename = %(source.dir)s/android_icon.png
presplash.filename = %(source.dir)s/android_presplash.png
android.presplash_color = #000000
android.api = 34
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a, x86_64
android.accept_sdk_license = True
p4a.bootstrap = sdl2
# versión estable de python-for-android: la rama master usa Python 3.14 y su receta de pygame no compila
p4a.branch = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 0

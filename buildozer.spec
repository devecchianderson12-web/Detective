[app]
title = División Especial de Detectives
package.name = detective
package.domain = org.ceibal.ded
source.dir = .
source.include_exts = py,png,jpg,gif,ogg,wav,ttf,dat,tcs,tcl,tcd,yaml,ico
source.exclude_dirs = .github,bin,.buildozer
version = 1.07
requirements = python3,pygame,numpy,pyyaml
orientation = landscape
fullscreen = 1
icon.filename = %(source.dir)s/android_icon.png
presplash.filename = %(source.dir)s/android_presplash.png
android.presplash_color = #000000
android.api = 34
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 0

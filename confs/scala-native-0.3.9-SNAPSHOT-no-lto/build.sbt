scalaVersion := "2.11.12"
enablePlugins(ScalaNativePlugin)
nativeLinkStubs := true
nativeGC := "immix"
nativeMode := "release"
nativeLTO := "none"

scalaVersion := "2.11.12"
enablePlugins(ScalaNativePlugin)
nativeLinkStubs := true
nativeGC := "commix"
nativeMode := "release-fast"
nativeLTO := "thin"

name := "scala-native-benchmarks"
scalaVersion := "2.11.12"
enablePlugins(ScalaNativePlugin)
import scala.scalanative.build
nativeConfig ~= {
  _.withGC(build.GC.immix)
    .withMode(build.Mode.releaseFull)
    .withLTO(build.LTO.thin)
}

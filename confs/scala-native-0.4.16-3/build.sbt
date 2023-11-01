name := "scala-native-benchmarks"
scalaVersion := "3.3.1"
enablePlugins(ScalaNativePlugin)
import scala.scalanative.build
nativeConfig ~= {
  _.withGC(build.GC.immix)
    .withMode(build.Mode.releaseFast) //TODO
    .withLTO(build.LTO.full)
}

name := "scala-native-benchmarks"
scalaVersion := "3.2.2"
enablePlugins(ScalaNativePlugin)
import scala.scalanative.build
nativeConfig ~= {
  _.withGC(build.GC.immix)
    .withMode(build.Mode.releaseFast) //TODO
    .withLTO(build.LTO.full)
}
